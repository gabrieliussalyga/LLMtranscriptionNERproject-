"""E025 Ambulatorinio apsilankymo aprašymas - main document model."""

from typing import List, Optional

from pydantic import Field

from backend.models.base import MedicalEntityBase
from .entities.v1.allergy import Allergy
from .entities.v1.ambulance import Ambulance
from .entities.v1.body_measurements import BodyMeasurements
from .entities.v1.certificates import Certificates
from .entities.v1.clinical_notes import ClinicalNotes
from .entities.v1.diagnosis import Diagnosis
from .entities.v1.referral import Referral
from .entities.v1.restrictions import Restrictions
from .entities.v1.treatment import Treatment
from .entities.v1.vaccination import Vaccination
from .entities.v1.visit_metadata import VisitMetadata
from .entities.v1.vital_signs import VitalSigns


class E025Document(MedicalEntityBase):
    """E025 Ambulatorinio apsilankymo aprašymas - pilnas dokumentas

    This document represents a complete outpatient visit description
    according to Lithuanian medical documentation standards.
    """

    # Single entity sections
    visit: Optional[VisitMetadata] = Field(
        None,
        description="Vizito metaduomenys (data, laikas, gydytojas)"
    )
    referral: Optional[Referral] = Field(
        None,
        description="Siuntimo informacija"
    )
    ambulance: Optional[Ambulance] = Field(
        None,
        description="GMP (greitosios) informacija"
    )
    diagnosis: Optional[Diagnosis] = Field(
        None,
        description="Diagnozė (pagrindinė, kodai, tikrumas)"
    )
    vital_signs: Optional[VitalSigns] = Field(
        None,
        description="Gyvybiniai rodikliai (temperatūra, spaudimas, pulsas ir kt.)"
    )
    body_measurements: Optional[BodyMeasurements] = Field(
        None,
        description="Kūno matavimai (svoris, ūgis, apimtys)"
    )
    clinical_notes: Optional[ClinicalNotes] = Field(
        None,
        description="Klinikiniai užrašai (nusiskundimai, objektyvi būklė, tyrimų planas)"
    )
    treatment: Optional[Treatment] = Field(
        None,
        description="Gydymo informacija (vaistai, rekomendacijos)"
    )
    certificates: Optional[Certificates] = Field(
        None,
        description="Pažymos ir nedarbingumo dokumentai"
    )
    restrictions: Optional[Restrictions] = Field(
        None,
        description="Apribojimai (vairavimas, ginklai)"
    )

    # Array sections
    allergies: Optional[List[Allergy]] = Field(
        None,
        description="Žinomos alergijos"
    )
    vaccinations: Optional[List[Vaccination]] = Field(
        None,
        description="Atlikti skiepai"
    )