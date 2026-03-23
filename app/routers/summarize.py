from fastapi import APIRouter, HTTPException
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services import ai_service

router = APIRouter()


@router.post("", response_model=SummarizeResponse)
async def summarize_content(req: SummarizeRequest):
    """
    Summarize any text content: earnings reports, news, CRM notes, data dumps.
    Returns structured summary with key points and sentiment.
    """
    try:
        result = await ai_service.run_summarize(
            content=req.content,
            focus=req.focus,
            fmt=req.format,
            output_tokens=req.output_tokens or 300,
        )
        return SummarizeResponse(
            summary=result.get("summary", ""),
            key_points=result.get("key_points", []),
            word_count=result.get("word_count", len(result.get("summary", "").split())),
            sentiment=result.get("sentiment", "neutral"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
