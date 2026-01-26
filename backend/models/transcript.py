"""Transcript input models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """A single segment of transcribed speech."""

    time: str = Field(
        ...,
        description="Timestamp of the segment, e.g., '00:01:23'"
    )
    speaker: str = Field(
        ...,
        description="Speaker identifier, e.g., 'Gydytojas', 'Pacientas'"
    )
    text: str = Field(
        ...,
        description="The transcribed text content"
    )


class TranscriptInput(BaseModel):
    """Input model for transcript extraction requests."""

    meta: Optional[dict] = Field(
        None,
        description="Optional metadata about the transcript"
    )
    transcript: List[TranscriptSegment] = Field(
        ...,
        description="Array of transcript segments"
    )
