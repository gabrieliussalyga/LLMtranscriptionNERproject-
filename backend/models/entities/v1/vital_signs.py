from backend.models.base import MedicalEntityBase
"""Vital signs entity model."""

from typing import List, Optional

from pydantic import Field


class VitalSignItem(MedicalEntityBase):
    """Individual vital sign measurement with transcript reference."""

    name: str = Field(
        ...,
        description="Rodiklio pavadinimas"
    )
    value: str = Field(
        ...,
        description="Rodiklio reikšmė su vienetais"
    )
    source_segments: List[int] = Field(
        default_factory=list,
        description="Transkripcijos segmentų indeksai"
    )


class VitalSigns(MedicalEntityBase):
    """Gyvybiniai rodikliai - masyvas matavimų su nuorodomis"""

    items: Optional[List[VitalSignItem]] = Field(
        None,
        description="Gyvybinių rodiklių sąrašas su nuorodomis į transkripciją"
    )
