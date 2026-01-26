from backend.models.base import MedicalEntityBase
"""Restrictions entity model."""

from datetime import date as date_type
from typing import Optional

from pydantic import Field


class Restrictions(MedicalEntityBase):
    """Apribojimai - vairavimas, ginklai"""

    cannot_drive: Optional[bool] = Field(
        None,
        description="Draudimas vairuoti"
    )
    cannot_drive_date: Optional[date_type] = Field(
        None,
        description="Draudimo vairuoti data"
    )
    cannot_use_weapon: Optional[bool] = Field(
        None,
        description="Draudimas naudoti ginklą"
    )
