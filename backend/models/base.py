"""
Base classes and utilities for medical entity models.
"""

from pydantic import BaseModel, ConfigDict


class MedicalEntityBase(BaseModel):
    """Base class for all medical entity models."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_default=True,
        extra='forbid'  # Required for OpenAI Strict Structured Outputs
    )