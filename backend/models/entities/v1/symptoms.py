from backend.models.base import MedicalEntityBase
"""Symptoms and findings entity model."""

from typing import List, Optional

from pydantic import Field


class Symptom(MedicalEntityBase):
    """Individual symptom or finding."""

    description: str = Field(
        ...,
        description="Simptomo ar radinio aprašymas"
    )
    reported_by: str = Field(
        ...,
        description="Kas pranešė: 'pacientas' arba 'gydytojas'"
    )
    is_present: bool = Field(
        True,
        description="Ar simptomas yra (True) ar jo nėra/normalus (False)"
    )


class ObjectiveFindings(MedicalEntityBase):
    """Objektyvūs radiniai - gydytojo nustatyti faktai apžiūros metu."""

    general_condition: Optional[str] = Field(
        None,
        description="Bendra būklė"
    )
    throat: Optional[str] = Field(
        None,
        description="Ryklė, tonzilės, žiočių lankas"
    )
    tongue: Optional[str] = Field(
        None,
        description="Liežuvis"
    )
    skin: Optional[str] = Field(
        None,
        description="Oda, spalva, drėgnumas"
    )
    lymph_nodes: Optional[str] = Field(
        None,
        description="Limfmazgiai"
    )
    lungs: Optional[str] = Field(
        None,
        description="Plaučiai, kvėpavimas"
    )
    heart: Optional[str] = Field(
        None,
        description="Širdis, tonai"
    )
    abdomen: Optional[str] = Field(
        None,
        description="Pilvas"
    )
    other: Optional[str] = Field(
        None,
        description="Kiti objektyvūs radiniai"
    )


class SymptomsAndFindings(MedicalEntityBase):
    """Simptomai ir radiniai - paciento skundai ir gydytojo nustatyti faktai."""

    patient_complaints: Optional[List[Symptom]] = Field(
        None,
        description="Paciento nusiskundimai ir simptomai"
    )
    objective_findings: Optional[ObjectiveFindings] = Field(
        None,
        description="Gydytojo objektyviai nustatyti radiniai apžiūros metu"
    )
