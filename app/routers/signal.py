from fastapi import APIRouter, HTTPException
from app.models.schemas import SignalRequest, SignalResponse
from app.services import ai_service, market_data as md

router = APIRouter()


@router.post("", response_model=SignalResponse)
async def generate_signal(req: SignalRequest):
    """
    Generate actionable trade signals: BUY/SELL/HOLD with entry, stop-loss,
    take-profit targets, position sizing, and risk/reward ratio.
    """
    try:
        data = await md.get_market_data(req.symbol, req.asset_type.value)
        result = await ai_service.run_signal(
            symbol=req.symbol,
            asset_type=req.asset_type.value,
            timeframe=req.timeframe.value,
            risk_level=req.risk_level.value,
            capital=req.capital,
            market_data=data,
        )
        return SignalResponse(
            symbol=req.symbol,
            action=result.get("action", "HOLD"),
            entry_price=result.get("entry_price"),
            stop_loss=result.get("stop_loss"),
            take_profit=result.get("take_profit"),
            position_size=result.get("position_size"),
            risk_reward_ratio=result.get("risk_reward_ratio"),
            confidence=result.get("confidence", 0.6),
            reasoning=result.get("reasoning", ""),
            invalidation=result.get("invalidation", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
