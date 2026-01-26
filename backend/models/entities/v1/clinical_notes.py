from backend.models.base import MedicalEntityBase
"""Clinical notes entity model."""

from typing import List, Optional

from pydantic import Field


class ClinicalStatement(MedicalEntityBase):
    """Individual clinical statement with transcript reference."""

    statement: str = Field(
        ...,
        description="Vienas klinikinis teiginys"
    )
    source_segments: List[int] = Field(
        ...,
        description="Transkripcijos segmentų indeksai, iš kurių išgautas teiginys"
    )


class ClinicalNotes(MedicalEntityBase):
    """Klinikiniai užrašai ir tyrimai"""

    complaints_anamnesis: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Nusiskundimai ir anamnezė - atskiri teiginiai su nuorodomis"
    )
    objective_condition: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Objektyvus būklės įvertinimas - atskiri teiginiai su nuorodomis"
    )
    tests_consultations_plan: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Planuojami tyrimai ir konsultacijos - atskiri teiginiai su nuorodomis"
    )
    performed_tests_consultations: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Atliktų tyrimų rezultatai - atskiri teiginiai su nuorodomis"
    )
    condition_on_discharge: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Būklė konsultacijos pabaigoje - atskiri teiginiai su nuorodomis"
    )
    notes: Optional[List[ClinicalStatement]] = Field(
        None,
        description="Papildoma informacija - atskiri teiginiai su nuorodomis"
    )
