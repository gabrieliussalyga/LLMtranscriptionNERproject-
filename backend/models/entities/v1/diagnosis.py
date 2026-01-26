from backend.models.base import MedicalEntityBase
"""Diagnosis entity model."""

from typing import List, Literal, Optional

from pydantic import Field, field_validator


class DiagnosisItem(MedicalEntityBase):
    """Individual diagnosis with transcript reference."""

    diagnosis: str = Field(
        ...,
        description="Diagnozė lietuvių kalba"
    )
    diagnosis_code: Optional[str] = Field(
        None,
        description="TLK-10-AM kodas, pvz.: J45.0"
    )
    diagnosis_certainty: Optional[Literal["+", "-", "0"]] = Field(
        None,
        description="Tikrumas: '+' patvirtinta, '-' atmesta, '0' įtariama"
    )
    source_segments: List[int] = Field(
        default_factory=list,
        description="Transkripcijos segmentų indeksai"
    )

    @field_validator("diagnosis_code", mode="before")
    @classmethod
    def clean_diagnosis_code(cls, v):
        """Convert 'null' string to None."""
        if v in ("null", "None", ""):
            return None
        return v


class Diagnosis(MedicalEntityBase):
    """Diagnozės informacija - masyvas diagnozių su nuorodomis"""

    items: Optional[List[DiagnosisItem]] = Field(
        None,
        description="Diagnozių sąrašas su nuorodomis į transkripciją"
    )
