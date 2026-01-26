from backend.models.base import MedicalEntityBase
"""Allergy entity model."""

from datetime import date as date_type
from typing import List, Literal, Optional

from pydantic import Field


class Allergy(MedicalEntityBase):
    """Alergijos įrašas - vaistams, maistui ar kitoms medžiagoms"""

    type: Literal["vaistai", "maistas", "kita"] = Field(
        ...,
        description="Alergijos tipas"
    )
    description: str = Field(
        ...,
        description="Alergeno aprašymas"
    )
    date: Optional[date_type] = Field(
        None,
        description="Nustatymo data"
    )
    source_segments: List[int] = Field(
        default_factory=list,
        description="Transkripcijos segmentų indeksai"
    )
