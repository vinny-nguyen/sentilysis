from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ...services.overview_service import OverviewService

router = APIRouter(prefix="/overview", tags=["overview"])

# Initialize the overview service
overview_service = OverviewService()


class SearchRequest(BaseModel):
    ticker: str
    date: str


@router.get("/search", response_model=Dict[str, Any])
async def search_overview_records(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL, TSLA)"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip for pagination"),
):
    """Search for existing overview records based on stock ticker and date"""
    try:
        # Validate ticker format
        if not ticker or not ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = ticker.strip().upper()

        # Validate date format
        try:
            from datetime import datetime

            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Search for records with the specific ticker and date
        filter_dict = {"ticker": ticker, "date": date}

        records = await overview_service.get_many(
            filter_dict=filter_dict, skip=skip, limit=limit
        )

        return {
            "ticker": ticker,
            "date": date,
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


@router.get("/search/range", response_model=Dict[str, Any])
async def search_overview_records_by_range(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL, TSLA)"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip for pagination"),
):
    """Search for existing overview records based on stock ticker and date range"""
    try:
        # Validate ticker format
        if not ticker or not ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = ticker.strip().upper()

        # Validate date formats
        try:
            from datetime import datetime

            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Search for records within the date range
        records = await overview_service.get_by_date_range(
            start_date=start_date,
            end_date=end_date,
            ticker=ticker,
            skip=skip,
            limit=limit,
        )

        return {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
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


@router.get("/ticker/{ticker}", response_model=Dict[str, Any])
async def get_overview_records_by_ticker(
    ticker: str,
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip for pagination"),
):
    """Get all overview records for a specific ticker"""
    try:
        # Validate ticker format
        if not ticker or not ticker.strip():
            raise HTTPException(status_code=400, detail="Ticker is required")

        ticker = ticker.strip().upper()

        # Get records for the ticker
        records = await overview_service.get_by_ticker(
            ticker=ticker, skip=skip, limit=limit
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
            "GET /overview/search - Search by ticker and date",
            "GET /overview/search/range - Search by ticker and date range",
            "GET /overview/ticker/{ticker} - Get all records for a ticker",
        ],
    }


@router.get("/health")
async def overview_health_check():
    """Health check for overview service"""
    return {"status": "healthy", "service": "Overview", "database": "connected"}
