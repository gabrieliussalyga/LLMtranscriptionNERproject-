"""API routes for medical entity extraction."""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from backend.config import Settings, get_settings
from backend.models.extraction_result import ExtractionResult
from backend.models.transcript import TranscriptInput
from backend.services.gemini_extractor import GeminiExtractor
from backend.services.openai_extractor import OpenAIExtractor

router = APIRouter(prefix="/api", tags=["extraction"])


def get_extractor(settings: Settings = Depends(get_settings)) -> Union[OpenAIExtractor, GeminiExtractor]:
    """Dependency to get configured extractor based on LLM_PROVIDER setting."""
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )
        return OpenAIExtractor(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
    else:
        if not settings.google_api_key:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured"
            )
        return GeminiExtractor(
            api_key=settings.google_api_key,
            model_name=settings.gemini_model
        )


@router.post("/extract", response_model=ExtractionResult)
async def extract_entities(
    transcript: TranscriptInput,
    extractor: GeminiExtractor = Depends(get_extractor)
) -> ExtractionResult:
    """Extract medical entities from a transcript.

    Args:
        transcript: The transcript input containing segments

    Returns:
        ExtractionResult with the extracted E025 document and references
    """
    try:
        result = await extractor.extract(transcript)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "medical-ner-extraction"}
