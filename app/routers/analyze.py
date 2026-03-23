from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services import ai_service, market_data as md

router = APIRouter()


@router.post("", response_model=AnalyzeResponse)
async def analyze_asset(req: AnalyzeRequest):
    """
    Perform AI-powered technical + contextual analysis on any asset.
    Returns indicators, trend, support/resistance levels, and sentiment.
    """
    try:
        data = await md.get_market_data(req.symbol, req.asset_type.value)
        result = await ai_service.run_analysis(
            symbol=req.symbol,
            asset_type=req.asset_type.value,
            timeframe=req.timeframe.value,
            indicators=req.indicators or [],
            context=req.context,
            market_data=data,
        )
        return AnalyzeResponse(
            symbol=req.symbol,
            asset_type=req.asset_type,
            timeframe=req.timeframe,
            analysis=result,
            confidence=result.get("confidence", 0.7),
            sentiment=result.get("sentiment", "neutral"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
