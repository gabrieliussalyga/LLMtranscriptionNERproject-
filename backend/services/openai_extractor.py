"""OpenAI-based medical entity extraction service."""

import json
import logging
from typing import Any, Dict

from openai import AsyncOpenAI

from backend.models.e025_document import E025Document
from backend.models.extraction_result import EntityReference, ExtractionResult
from backend.models.transcript import TranscriptInput
from backend.prompts.extraction_prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class OpenAIExtractor:
    """Service for extracting medical entities using OpenAI GPT."""

    def __init__(self, api_key: str, model_name: str = "gpt-5.2"):
        """Initialize the OpenAI extractor.

        Args:
            api_key: OpenAI API key
            model_name: GPT model to use (e.g., gpt-4o, gpt-4-turbo, gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    def _make_schema_strict(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process JSON schema to meet OpenAI Strict Structured Outputs requirements.
        1. 'additionalProperties': false
        2. All keys in 'properties' must be in 'required'
        3. No 'description' or 'title' if '$ref' is present
        """
        if "$ref" in schema:
            # If it's a ref, it cannot have other keywords like description or title
            keys_to_remove = ["description", "title", "default"]
            for k in keys_to_remove:
                if k in schema:
                    del schema[k]
            # We don't recurse into ref here, the ref definition will be handled in $defs
            return schema

        if "type" in schema and schema["type"] == "object":
            schema["additionalProperties"] = False
            
            properties = schema.get("properties", {})
            if properties:
                required = schema.get("required", [])
                # Add all properties to required
                for prop_name in properties.keys():
                    if prop_name not in required:
                        required.append(prop_name)
                schema["required"] = required
            
            # Recurse into properties
            for prop in properties.values():
                self._make_schema_strict(prop)
                
            # Recurse into definitions
            defs = schema.get("$defs", {})
            for def_schema in defs.values():
                self._make_schema_strict(def_schema)
                
        elif "type" in schema and schema["type"] == "array":
            items = schema.get("items", {})
            self._make_schema_strict(items)
            
        elif "anyOf" in schema:
            for sub_schema in schema["anyOf"]:
                self._make_schema_strict(sub_schema)
                
        return schema

    async def extract(self, transcript_input: TranscriptInput) -> ExtractionResult:
        """Extract medical entities from a transcript.

        Args:
            transcript_input: The transcript to process

        Returns:
            ExtractionResult with document and references
        """
        user_prompt = build_user_prompt(transcript_input.transcript)
        
        # Prepare strict schema
        json_schema = ExtractionResult.model_json_schema()
        strict_schema = self._make_schema_strict(json_schema)

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction_result",
                        "strict": True,
                        "schema": strict_schema
                    }
                },
            )
            response_text = response.choices[0].message.content
            logger.info(f"OpenAI response received, length: {len(response_text)}")
        except Exception as e:
            logger.error(f"OpenAI API error: {type(e).__name__}: {e}")
            raise

        result_json = self._parse_response(response_text)
        return self._build_extraction_result(result_json)

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the JSON response from OpenAI."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")

    def _build_extraction_result(self, result_json: Dict[str, Any]) -> ExtractionResult:
        """Build an ExtractionResult from the parsed JSON."""
        document_data = result_json.get("document", {})
        references_data = result_json.get("references", [])

        document = E025Document.model_validate(document_data)

        references = [
            EntityReference.model_validate(ref)
            for ref in references_data
        ]

        return ExtractionResult(document=document, references=references)