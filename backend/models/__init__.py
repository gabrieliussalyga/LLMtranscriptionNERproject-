"""
Medical NER Extraction Models

This module contains Pydantic models for the E025 Ambulatorinio apsilankymo aprašymas
(Outpatient Visit Description) medical document schema.
"""

from .e025_document import E025Document
from .transcript import TranscriptSegment, TranscriptInput
from .extraction_result import EntityReference, ExtractionResult

__all__ = [
    "E025Document",
    "TranscriptSegment",
    "TranscriptInput",
    "EntityReference",
    "ExtractionResult",
]
