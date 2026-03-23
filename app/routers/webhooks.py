from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import WebhookRegisterRequest, WebhookRegisterResponse
import httpx
import hmac
import hashlib
import json
import uuid
from datetime import datetime

router = APIRouter()

# In-memory store — swap for Postgres/Redis in production
_webhooks: dict[str, dict] = {}


@router.post("/register", response_model=WebhookRegisterResponse)
async def register_webhook(req: WebhookRegisterRequest):
    """Register a webhook URL to receive event notifications."""
    webhook_id = str(uuid.uuid4())
    _webhooks[webhook_id] = {
        "id": webhook_id,
        "url": req.url,
        "events": [e.value for e in req.events],
        "secret": req.secret,
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    }
    return WebhookRegisterResponse(
        webhook_id=webhook_id,
        url=req.url,
        events=req.events,
    )


@router.get("/{webhook_id}")
async def get_webhook(webhook_id: str):
    wh = _webhooks.get(webhook_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {k: v for k, v in wh.items() if k != "secret"}


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del _webhooks[webhook_id]
    return {"deleted": True}


async def _dispatch(webhook: dict, event: str, payload: dict):
    """Fire-and-forget webhook delivery with HMAC signing."""
    body = json.dumps({"event": event, "data": payload, "timestamp": datetime.utcnow().isoformat()})
    headers = {"Content-Type": "application/json", "X-Event-Type": event}
    if secret := webhook.get("secret"):
        sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        headers["X-Signature-SHA256"] = f"sha256={sig}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(webhook["url"], content=body, headers=headers)
    except Exception:
        pass


async def dispatch_event(event: str, payload: dict, background: BackgroundTasks):
    """Call this from any router to broadcast an event to registered webhooks."""
    for wh in _webhooks.values():
        if wh.get("active") and event in wh.get("events", []):
            background.add_task(_dispatch, wh, event, payload)
