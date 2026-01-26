"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Medical NER Extraction API",
    description="Extract medical entities from Lithuanian doctor-patient transcriptions",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical NER Extraction API",
        "docs": "/docs",
        "health": "/api/health"
    }
