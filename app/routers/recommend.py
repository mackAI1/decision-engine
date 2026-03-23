from fastapi import APIRouter, HTTPException
from app.models.schemas import RecommendRequest, RecommendResponse
from app.services import ai_service

router = APIRouter()


@router.post("", response_model=RecommendResponse)
async def get_recommendations(req: RecommendRequest):
    """
    AI-powered strategic recommendations: prioritized actions, risk assessment,
    and alternatives. Works for trading, business, real estate, and general decisions.
    """
    try:
        result = await ai_service.run_recommend(
            goal=req.goal,
            context=req.context,
            asset_type=req.asset_type.value if req.asset_type else None,
            risk_level=req.risk_level.value,
            options=req.options,
        )
        return RecommendResponse(
            goal=req.goal,
            recommended_actions=result.get("recommended_actions", []),
            risk_assessment=result.get("risk_assessment", ""),
            alternatives=result.get("alternatives", []),
            confidence=result.get("confidence", 0.7),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
