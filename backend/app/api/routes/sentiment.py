from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ...models.sentiment import (
    AnalysisRequest,
    AnalysisResponse,
    SentimentSummary,
    ChatMessage,
    ChatResponse,
)
from ...services.sentiment_service import sentiment_service
from ...services.gemini_service import gemini_service

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_ticker(request: AnalysisRequest):
    """
    Analyze sentiment for a given stock ticker.

    This endpoint triggers the sentiment analysis pipeline:
    1. Scrapes social media and news data (mock data for now)
    2. Analyzes sentiment using Gemini API
    3. Generates summary and insights
    4. Stores results in MongoDB
    """
    try:
        if not request.ticker or len(request.ticker.strip()) == 0:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")

        # Normalize ticker symbol
        request.ticker = request.ticker.upper().strip()

        # Validate ticker format (basic validation)
        if not request.ticker.isalpha() or len(request.ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol format")

        result = await sentiment_service.analyze_ticker(request)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/latest/{ticker}", response_model=Optional[SentimentSummary])
async def get_latest_analysis(ticker: str):
    """
    Get the latest sentiment analysis for a ticker.

    Returns the most recent sentiment summary if available.
    """
    try:
        if not ticker or len(ticker.strip()) == 0:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")

        ticker = ticker.upper().strip()
        result = await sentiment_service.get_latest_analysis(ticker)

        if not result:
            raise HTTPException(
                status_code=404, detail=f"No analysis found for ticker {ticker}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{ticker}", response_model=List[SentimentSummary])
async def get_sentiment_history(ticker: str, days: int = 7):
    """
    Get sentiment analysis history for a ticker.

    Returns sentiment summaries for the specified number of days.
    """
    try:
        if not ticker or len(ticker.strip()) == 0:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")

        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")

        ticker = ticker.upper().strip()
        results = await sentiment_service.get_sentiment_history(ticker, days)

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(message: ChatMessage):
    """
    Chat with AI assistant about stock sentiment.

    The AI will provide insights based on available sentiment data for the ticker.
    """
    try:
        if not message.message or len(message.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message is required")

        # Get context data if ticker is provided
        context_data = None
        if message.ticker:
            latest_analysis = await sentiment_service.get_latest_analysis(
                message.ticker
            )
            if latest_analysis:
                context_data = {
                    "sentiment": latest_analysis.overall_sentiment.value,
                    "headlines": latest_analysis.top_headlines,
                    "geopolitical_events": latest_analysis.geopolitical_summary,
                    "macro_factors": latest_analysis.macro_summary,
                }

        response = await gemini_service.chat_response(
            message.message, message.ticker or "general", context_data
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic service status information.
    """
    return {"status": "healthy", "service": "sentiment-analysis", "version": "1.0.0"}
