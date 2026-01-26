from backend.models.base import MedicalEntityBase
"""Vaccination entity model."""

from datetime import date as date_type
from typing import Optional

from pydantic import Field


class Vaccination(MedicalEntityBase):
    """Skiepų informacija"""

    name: str = Field(
        ...,
        description="Skiepo pavadinimas | vakcinos pavadinimas"
    )
    date: Optional[date_type] = Field(
        None,
        description="Skiepijimo data"
    )
