"""Extraction result models with reference tracking."""

from typing import List, Optional, Union

from pydantic import Field

from backend.models.base import MedicalEntityBase
from .e025_document import E025Document


class EntityReference(MedicalEntityBase):
    """Reference linking an extracted field to source transcript segments."""

    field_name: str = Field(
        ...,
        description="Dot-notation path to the field, e.g., 'vital_signs.temperature'"
    )
    value: Union[str, int, float, bool] = Field(
        ...,
        description="The extracted value"
    )
    source_segments: List[int] = Field(
        ...,
        description="Indices into the transcript array that support this extraction"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0, le=1.0,
        description="Confidence score for the extraction (0.0 to 1.0)"
    )


class ExtractionResult(MedicalEntityBase):
    """Complete extraction result with document and references."""

    document: E025Document = Field(
        ...,
        description="The extracted E025 document"
    )
    references: List[EntityReference] = Field(
        default_factory=list,
        description="References linking extracted fields to source segments"
    )
