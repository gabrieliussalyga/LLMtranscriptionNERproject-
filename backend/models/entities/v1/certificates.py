from backend.models.base import MedicalEntityBase
"""Certificates entity model."""

from datetime import date as date_type
from typing import Optional

from pydantic import Field


class Certificates(MedicalEntityBase):
    """Pažymos ir nedarbingumo dokumentai"""

    disability_certificate: Optional[bool] = Field(
        None,
        description="Ar išduotas nedarbingumo pažymėjimas"
    )
    maternity_certificate: Optional[bool] = Field(
        None,
        description="Ar išduotas nėštumo/gimdymo pažymėjimas"
    )
    medical_certificate: Optional[bool] = Field(
        None,
        description="Ar išduota medicininė pažyma (094/a)"
    )
    disability_number: Optional[str] = Field(
        None,
        description="Pažymėjimo numeris"
    )
    disability_start_date: Optional[date_type] = Field(
        None,
        description="Nedarbingumo pradžios data"
    )
    disability_end_date: Optional[date_type] = Field(
        None,
        description="Nedarbingumo pabaigos data"
    )
    disability_description: Optional[str] = Field(
        None,
        description="Nedarbingumo priežasties aprašymas"
    )
