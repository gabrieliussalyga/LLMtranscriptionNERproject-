from backend.models.base import MedicalEntityBase
"""Body measurements entity model."""

from typing import Optional

from pydantic import Field


class BodyMeasurements(MedicalEntityBase):
    """Kūno matavimai - svoris, ūgis, apimtys"""

    weight: Optional[float] = Field(
        None,
        ge=1, le=300,
        description="Kūno svoris kg"
    )
    height: Optional[int] = Field(
        None,
        ge=50, le=250,
        description="Ūgis cm"
    )
    bmi: Optional[float] = Field(
        None,
        ge=10, le=60,
        description="Kūno masės indeksas kg/m². Norma: 18.5-24.9"
    )
    chest_circumference: Optional[int] = Field(
        None,
        description="Krūtinės apimtis cm"
    )
    hip_circumference: Optional[int] = Field(
        None,
        description="Klubų apimtis cm"
    )
    waist_circumference: Optional[int] = Field(
        None,
        description="Juosmens apimtis cm"
    )
    head_circumference: Optional[int] = Field(
        None,
        description="Galvos apimtis cm"
    )
