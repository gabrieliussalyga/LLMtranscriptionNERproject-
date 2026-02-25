"""
Flat E025 schema loader.

Reads the document schema from a JSON file so users can modify it.
Wraps it with a references array for source segment tracking.
"""

import copy
import json
import os
from typing import Optional

SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), "e025_flat_schema.json")

_REFERENCES_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "field_name": {
                "type": "string",
                "description": "Top-level field name in the document, e.g. 'complaints_anamnesis', 'systolic_bp'"
            },
            "value": {
                "type": "string",
                "description": "The extracted value (as string)"
            },
            "source_segments": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Transcript segment indices supporting this extraction"
            },
        },
        "required": ["field_name", "value", "source_segments"],
        "additionalProperties": False,
    },
}


def _remove_diagnosis(schema: dict) -> dict:
    """Remove all diagnosis-related fields from schema."""
    keys_to_remove = [ent for ent in schema.get("required", []) if "diagno" in ent.lower()]
    schema["required"] = [ent for ent in schema.get("required", []) if ent not in keys_to_remove]
    for k in keys_to_remove:
        schema["properties"].pop(k, None)
    return schema


def load_document_schema(path: str = SCHEMA_FILE_PATH) -> dict:
    """Load the flat E025 document schema from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    schema = _remove_diagnosis(schema)
    return schema


def build_extraction_schema(doc_schema: Optional[dict] = None) -> dict:
    """Build the full extraction schema (document + references).

    Args:
        doc_schema: Optional pre-loaded document schema. If None, loads from file.
    """
    if doc_schema is None:
        doc_schema = load_document_schema()

    return {
        "type": "object",
        "properties": {
            "document": copy.deepcopy(doc_schema),
            "references": copy.deepcopy(_REFERENCES_SCHEMA),
        },
        "required": ["document", "references"],
        "additionalProperties": False,
    }


def get_extraction_schema_str(doc_schema: Optional[dict] = None) -> str:
    """Get the full extraction schema as a formatted JSON string (for prompts)."""
    schema = build_extraction_schema(doc_schema)
    return json.dumps(schema, indent=2, ensure_ascii=False)
