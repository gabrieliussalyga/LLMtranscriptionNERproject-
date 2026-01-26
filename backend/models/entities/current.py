"""
Current version of medical entity models.

Re-exports the latest version (v1) of all entity classes.
To switch versions, change the import source below.
"""

from .v1 import (
    Allergy,
    Vaccination,
    VitalSigns,
    BodyMeasurements,
    Diagnosis,
    VisitMetadata,
    Referral,
    Ambulance,
    Treatment,
    Certificates,
    Restrictions,
    ClinicalNotes,
    Symptom,
    ObjectiveFindings,
    SymptomsAndFindings,
)

__all__ = [
    "Allergy",
    "Vaccination",
    "VitalSigns",
    "BodyMeasurements",
    "Diagnosis",
    "VisitMetadata",
    "Referral",
    "Ambulance",
    "Treatment",
    "Certificates",
    "Restrictions",
    "ClinicalNotes",
    "Symptom",
    "ObjectiveFindings",
    "SymptomsAndFindings",
]
