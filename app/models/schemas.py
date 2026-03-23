from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid
from datetime import datetime


class AssetType(str, Enum):
    stock = "stock"
    crypto = "crypto"
    forex = "forex"
    real_estate = "real_estate"


class TimeFrame(str, Enum):
    m1 = "1m"
    m5 = "5m"
    m15 = "15m"
    h1 = "1h"
    h4 = "4h"
    d1 = "1d"
    w1 = "1w"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ── Analyze ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., example="AAPL")
    asset_type: AssetType = AssetType.stock
    timeframe: TimeFrame = TimeFrame.d1
    context: Optional[str] = Field(None, description="Additional user context or instructions")
    indicators: Optional[List[str]] = Field(
        default=["RSI", "MACD", "SMA_20", "SMA_50"],
        description="Technical indicators to include"
    )

class AnalyzeResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    asset_type: AssetType
    timeframe: TimeFrame
    analysis: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment: Literal["bullish", "bearish", "neutral"]


# ── Signal ───────────────────────────────────────────────────────────────────

class SignalRequest(BaseModel):
    symbol: str = Field(..., example="BTC-USD")
    asset_type: AssetType = AssetType.crypto
    timeframe: TimeFrame = TimeFrame.h4
    risk_level: RiskLevel = RiskLevel.medium
    capital: Optional[float] = Field(None, description="Available capital for position sizing")

class SignalResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    action: Literal["BUY", "SELL", "HOLD", "WAIT"]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[List[float]]
    position_size: Optional[float]
    risk_reward_ratio: Optional[float]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    invalidation: str


# ── Summarize ─────────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    content: str = Field(..., description="Raw text, data, or context to summarize")
    focus: Optional[str] = Field(None, description="What to focus the summary on")
    format: Literal["brief", "detailed", "bullets", "executive"] = "brief"
    output_tokens: Optional[int] = Field(300, ge=50, le=2000)

class SummarizeResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: str
    key_points: List[str]
    word_count: int
    sentiment: Optional[Literal["positive", "negative", "neutral"]]


# ── Recommend ─────────────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    goal: str = Field(..., description="What the user is trying to achieve")
    context: Optional[str] = Field(None, description="Background info, constraints, current state")
    asset_type: Optional[AssetType] = None
    risk_level: RiskLevel = RiskLevel.medium
    options: Optional[List[str]] = Field(None, description="Specific options to evaluate")

class Action(BaseModel):
    action: str
    priority: Literal["high", "medium", "low"]
    rationale: str
    expected_outcome: str

class RecommendResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    goal: str
    recommended_actions: List[Action]
    risk_assessment: str
    alternatives: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


# ── Webhooks ──────────────────────────────────────────────────────────────────

class WebhookEvent(str, Enum):
    signal_generated = "signal.generated"
    analysis_complete = "analysis.complete"
    alert_triggered = "alert.triggered"

class WebhookRegisterRequest(BaseModel):
    url: str = Field(..., description="HTTPS URL to POST events to")
    events: List[WebhookEvent]
    secret: Optional[str] = Field(None, description="HMAC signing secret for verification")

class WebhookRegisterResponse(BaseModel):
    webhook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    events: List[WebhookEvent]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
