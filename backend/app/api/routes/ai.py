from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from ...services.gemini_service import gemini_service

router = APIRouter(prefix="/ai", tags=["ai"])


class TextGenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 1000


class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "general"  # general, summary, sentiment


class ChatRequest(BaseModel):
    message: str
    context: str = "general"


class InsightsRequest(BaseModel):
    topic: str
    insights_type: str = "general"  # general, financial, technical


@router.post("/generate", response_model=Dict[str, Any])
async def generate_text(request: TextGenerationRequest):
    """Generate text using Gemini AI"""
    try:
        result = await gemini_service.generate_text(request.prompt, request.max_tokens)
        return {"generated_text": result, "prompt": request.prompt, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text using Gemini AI"""
    try:
        result = await gemini_service.analyze_text(request.text, request.analysis_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


@router.get("/status")
async def get_ai_status():
    """Check if Gemini service is configured and available"""
    return {
        "configured": gemini_service.is_configured(),
        "service": "Gemini AI",
        "status": "available" if gemini_service.is_configured() else "not_configured",
    }


@router.get("/health")
async def ai_health_check():
    """Health check for AI service"""
    return {
        "status": "healthy",
        "service": "AI (Gemini)",
        "configured": gemini_service.is_configured(),
    }
