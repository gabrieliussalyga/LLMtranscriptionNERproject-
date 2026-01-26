from backend.models.base import MedicalEntityBase
"""Referral entity model."""

from typing import Optional

from pydantic import Field


class Referral(MedicalEntityBase):
    """Siuntimo informacija"""

    arrived_with_referral: Optional[bool] = Field(
        None,
        description="Ar atvyko su siuntimu"
    )
    referring_institution: Optional[str] = Field(
        None,
        description="Siuntusios įstaigos pavadinimas"
    )
    referring_physician: Optional[str] = Field(
        None,
        description="Siuntusio gydytojo vardas, pavardė"
    )
    referral_diagnosis: Optional[str] = Field(
        None,
        description="Siuntimo diagnozė su TLK-10-AM kodu"
    )
