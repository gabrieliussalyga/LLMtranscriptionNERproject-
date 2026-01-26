from backend.models.base import MedicalEntityBase
"""Visit metadata entity model."""

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import Field


class VisitMetadata(MedicalEntityBase):
    """Vizito metaduomenys"""

    date: Optional[date_type] = Field(None, description="Apsilankymo data")
    time: Optional[str] = Field(
        None,
        pattern=r"^\d{2}:\d{2}$",
        description="Apsilankymo laikas VV:MM"
    )
    record_number: Optional[str] = Field(None, description="Įrašo numeris")
    status: Optional[Literal["darbinis", "galutinis"]] = Field(
        None,
        description="Įrašo būsena"
    )
    physician: Optional[str] = Field(
        None,
        description="Gydytojo vardas, pavardė ir pareigos"
    )
    help_type: Optional[Literal["butinoji", "planine", "kita"]] = Field(
        None,
        description="Pagalbos tipas"
    )
    consultation_type: Optional[Literal["tiesioginis", "nuotolinis", "kitas"]] = Field(
        None,
        description="Konsultacijos pobūdis"
    )
    service_method: Optional[str] = Field(
        None,
        description="Aptarnavimo ypatumai"
    )
