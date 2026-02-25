"""Gemini-based medical entity extraction service.

TEMPORARY: Modified to use flat E025 schema for testing.
"""

import json
import logging
from typing import Any, Dict

from google import genai
from google.genai import types

# --- ORIGINAL imports (commented out for testing) ---
# from backend.models.e025_document import E025Document
# from backend.models.extraction_result import EntityReference, ExtractionResult
# --- END ORIGINAL ---

from backend.models.transcript import TranscriptInput
from backend.prompts.extraction_prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class GeminiExtractor:
    """Service for extracting medical entities using Gemini."""

    def __init__(self, api_key: str, model_name: str = "models/gemini-3-pro-preview"):
        """Initialize the Gemini extractor.

        Args:
            api_key: Google AI API key
            model_name: Gemini model to use (with models/ prefix)
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    # --- TEMPORARY: returns raw dict instead of ExtractionResult ---
    async def extract(self, transcript_input: TranscriptInput) -> Dict[str, Any]:
        """Extract medical entities from a transcript.

        Args:
            transcript_input: The transcript to process

        Returns:
            Raw dict with 'document' and 'references' keys
        """
        user_prompt = build_user_prompt(transcript_input.transcript)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json",
                    # --- ORIGINAL (Pydantic schema) ---
                    # response_schema=ExtractionResult,
                    # --- END ORIGINAL ---
                    # TEMPORARY: No response_schema - rely on prompt schema
                ),
            )
            logger.info(f"Gemini response received, length: {len(response.text)}")
        except Exception as e:
            logger.error(f"Gemini API error: {type(e).__name__}: {e}")
            raise

        return self._parse_response(response.text)

        # --- ORIGINAL (Pydantic validation) ---
        # result_json = self._parse_response(response.text)
        # return self._build_extraction_result(result_json)
        # --- END ORIGINAL ---

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the JSON response from Gemini."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")

    # --- ORIGINAL (kept but unused during testing) ---
    # def _build_extraction_result(self, result_json: Dict[str, Any]) -> ExtractionResult:
    #     """Build an ExtractionResult from the parsed JSON."""
    #     document_data = result_json.get("document", {})
    #     references_data = result_json.get("references", [])
    #
    #     document = E025Document.model_validate(document_data)
    #
    #     references = [
    #         EntityReference.model_validate(ref)
    #         for ref in references_data
    #     ]
    #
    #     return ExtractionResult(document=document, references=references)
    # --- END ORIGINAL ---
