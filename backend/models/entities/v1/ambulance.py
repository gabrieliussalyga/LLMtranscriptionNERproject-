from backend.models.base import MedicalEntityBase
"""Ambulance entity model."""

from typing import Optional

from pydantic import Field


class Ambulance(MedicalEntityBase):
    """GMP (greitosios) informacija"""

    arrived_by_ambulance: Optional[bool] = Field(
        None,
        description="Ar atvežtas GMP"
    )
    ambulance_institution: Optional[str] = Field(
        None,
        description="GMP įstaigos pavadinimas"
    )
    ambulance_diagnosis: Optional[str] = Field(
        None,
        description="GMP nustatyta diagnozė"
    )
