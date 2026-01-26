from backend.models.base import MedicalEntityBase
"""Treatment entity model."""

from typing import List, Optional

from pydantic import Field


class TreatmentItem(MedicalEntityBase):
    """Individual treatment item with transcript reference."""

    description: str = Field(
        ...,
        description="Gydymo aprašymas"
    )
    type: str = Field(
        ...,
        description="Gydymo tipas: 'medication', 'non_medication', 'prescription', 'referral', 'recommendation'"
    )
    source_segments: List[int] = Field(
        default_factory=list,
        description="Transkripcijos segmentų indeksai"
    )


class Treatment(MedicalEntityBase):
    """Gydymo informacija - masyvas su nuorodomis"""

    items: Optional[List[TreatmentItem]] = Field(
        None,
        description="Gydymo veiksmų sąrašas su nuorodomis į transkripciją"
    )
