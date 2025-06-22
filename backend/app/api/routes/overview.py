from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ...services.overview_service import OverviewService

router = APIRouter(prefix="/overview", tags=["overview"])

# Initialize the overview service
overview_service = OverviewService()


class SearchRequest(BaseModel):
    ticker: str
    date: str
    limit: int = 100
    skip: int = 0


class SearchRangeRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    limit: int = 100
    skip: int = 0


class TickerRequest(BaseModel):
    limit: int = 100
    skip: int = 0


@router.post("/search", response_model=Dict[str, Any])
async def search_overview_records(request: SearchRequest):
    """Search for existing overview records based on stock ticker and date"""
    try:
        # Validate ticker format
        if not request.ticker or not request.ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = request.ticker.strip().upper()

        # Validate date format
        try:
            from datetime import datetime

            datetime.strptime(request.date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Search for records with the specific ticker and date
        filter_dict = {"ticker": ticker, "date": request.date}

        records = await overview_service.get_many(
            filter_dict=filter_dict, skip=request.skip, limit=request.limit
        )

        return {
            "ticker": ticker,
            "date": request.date,
            "records": records,
            "count": len(records),
            "status": "success",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching overview records: {str(e)}"
        )


@router.post("/search/range", response_model=Dict[str, Any])
async def search_overview_records_by_range(request: SearchRangeRequest):
    """Search for existing overview records based on stock ticker and date range"""
    try:
        # Validate ticker format
        if not request.ticker or not request.ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = request.ticker.strip().upper()

        # Validate date formats
        try:
            from datetime import datetime

            datetime.strptime(request.start_date, "%Y-%m-%d")
            datetime.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Search for records within the date range
        records = await overview_service.get_by_date_range(
            start_date=request.start_date,
            end_date=request.end_date,
            ticker=ticker,
            skip=request.skip,
            limit=request.limit,
        )

        return {
            "ticker": ticker,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "records": records,
            "count": len(records),
            "status": "success",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching overview records by range: {str(e)}",
        )


@router.post("/ticker/{ticker}", response_model=Dict[str, Any])
async def get_overview_records_by_ticker(ticker: str, request: TickerRequest):
    """Get all overview records for a specific ticker"""
    try:
        # Validate ticker format
        if not ticker or not ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = ticker.strip().upper()

        # Get records for the ticker
        records = await overview_service.get_by_ticker(
            ticker=ticker, skip=request.skip, limit=request.limit
        )

        return {
            "ticker": ticker,
            "records": records,
            "count": len(records),
            "status": "success",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting overview records for ticker {ticker}: {str(e)}",
        )


@router.get("/status")
async def get_overview_status():
    """Check if overview service is available"""
    return {
        "service": "Overview",
        "status": "available",
        "endpoints": [
            "POST /overview/search - Search by ticker and date",
            "POST /overview/search/range - Search by ticker and date range",
            "POST /overview/ticker/{ticker} - Get all records for a ticker",
        ],
    }


@router.get("/health")
async def overview_health_check():
    """Health check for overview service"""
    return {"status": "healthy", "service": "Overview", "database": "connected"}
