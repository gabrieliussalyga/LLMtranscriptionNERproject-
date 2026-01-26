"""
Medical entity models package.

Entities are versioned - use `from .current import *` to get the latest version.
"""

from .current import (
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
]
