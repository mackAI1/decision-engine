import anthropic
import json
import os
import random

MODEL = "claude-sonnet-4-20250514"

# Check if real API key exists
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MOCK_MODE = not API_KEY or API_KEY in ("sk-ant-...", "")

def get_client():
    return anthropic.Anthropic(api_key=API_KEY)

def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

# ── MOCK DATA (no API key needed) ─────────────────────────────────────────────

def _mock_analysis(symbol: str, market_data: dict) -> dict:
    price = market_data.get("price", 100)
    rng = random.Random(symbol)
    sentiment = rng.choice(["bullish", "bearish", "neutral"])
    trend = rng.choice(["uptrend", "downtrend", "sideways"])
    return {
        "technical_summary": f"{symbol} is showing a {trend} pattern with {sentiment} momentum. Price is trading near key levels with moderate volume.",
        "indicators": {
            "RSI": f"{rng.randint(35,70)} — {'overbought' if rng.random()>0.7 else 'neutral'}",
            "MACD": rng.choice(["bullish crossover", "bearish crossover", "neutral"]),
            "SMA_20": f"Price {'above' if rng.random()>0.5 else 'below'} 20-day MA",
            "SMA_50": f"Price {'above' if rng.random()>0.5 else 'below'} 50-day MA",
        },
        "trend": trend,
        "support_levels": [round(price * 0.95, 2), round(price * 0.90, 2)],
        "resistance_levels": [round(price * 1.05, 2), round(price * 1.10, 2)],
        "key_observations": [
            f"Volume is {'above' if rng.random()>0.5 else 'below'} average",
            f"Price action near key {'support' if sentiment=='bullish' else 'resistance'}",
            f"Momentum indicators showing {sentiment} bias",
        ],
        "confidence": round(rng.uniform(0.55, 0.85), 2),
        "sentiment": sentiment,
        "mode": "demo"
    }

def _mock_signal(symbol: str, risk_level: str, market_data: dict) -> dict:
    price = market_data.get("price", 100)
    rng = random.Random(symbol + risk_level)
    action = rng.choice(["BUY", "SELL", "HOLD", "WAIT"])
    sl_pct = {"low": 0.02, "medium": 0.03, "high": 0.05}[risk_level]
    tp_pct = sl_pct * 2.5
    entry = round(price, 2)
    sl = round(price * (1 - sl_pct) if action == "BUY" else price * (1 + sl_pct), 2)
    tp1 = round(price * (1 + tp_pct) if action == "BUY" else price * (1 - tp_pct), 2)
    tp2 = round(price * (1 + tp_pct * 1.5) if action == "BUY" else price * (1 - tp_pct * 1.5), 2)
    return {
        "action": action,
        "entry_price": entry if action in ("BUY","SELL") else None,
        "stop_loss": sl if action in ("BUY","SELL") else None,
        "take_profit": [tp1, tp2] if action in ("BUY","SELL") else None,
        "position_size": {"low": 1.0, "medium": 2.0, "high": 3.0}[risk_level],
        "risk_reward_ratio": round(tp_pct / sl_pct, 1),
        "confidence": round(rng.uniform(0.55, 0.82), 2),
        "reasoning": f"Demo signal for {symbol}. Price at ${price} with {risk_level} risk settings. Add your Anthropic API key for real AI signals.",
        "invalidation": f"Close {'below' if action=='BUY' else 'above'} ${sl}",
        "mode": "demo"
    }

def _mock_summarize(content: str) -> dict:
    words = content.split()
    return {
        "summary": f"This content covers {len(words)} words discussing key topics. Add your Anthropic API key for real AI summaries.",
        "key_points": [
            "Content has been received and processed",
            "Demo mode active — real summaries need API key",
            "Structure and endpoints are working correctly",
        ],
        "word_count": len(words),
        "sentiment": "neutral",
        "mode": "demo"
    }

def _mock_recommend(goal: str, risk_level: str) -> dict:
    return {
        "recommended_actions": [
            {
                "action": "Set up your Anthropic API key to unlock real recommendations",
                "priority": "high",
                "rationale": "Real AI analysis requires the API key",
                "expected_outcome": "Full AI-powered recommendations for your goal"
            },
            {
                "action": f"Review your goal: '{goal[:60]}...' with a {risk_level} risk approach",
                "priority": "medium",
                "rationale": "Understanding your goal is the first step",
                "expected_outcome": "Clearer strategy framework"
            },
        ],
        "risk_assessment": f"Demo mode active. Risk level set to {risk_level}. Add API key for real analysis.",
        "alternatives": ["Get Anthropic API key", "Use mock mode for testing", "Review documentation"],
        "confidence": 0.5,
        "mode": "demo"
    }

# ── REAL AI CALLS ──────────────────────────────────────────────────────────────

async def run_analysis(symbol: str, asset_type: str, timeframe: str,
                       indicators: list[str], context: str | None,
                       market_data: dict) -> dict:
    if MOCK_MODE:
        return _mock_analysis(symbol, market_data)

    prompt = f"""You are an expert financial analyst. Analyze this asset and return ONLY valid JSON.

Asset: {symbol} ({asset_type})
Timeframe: {timeframe}
Indicators requested: {', '.join(indicators)}
Market data: {json.dumps(market_data, indent=2)}
{f'User context: {context}' if context else ''}

Return JSON with keys:
- technical_summary (string)
- indicators (object with each indicator name as key, value/signal as value)
- trend (string: uptrend/downtrend/sideways)
- support_levels (array of floats)
- resistance_levels (array of floats)
- key_observations (array of strings, max 5)
- confidence (float 0.0-1.0)
- sentiment (string: bullish/bearish/neutral)
"""
    msg = get_client().messages.create(
        model=MODEL, max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json_response(msg.content[0].text)


async def run_signal(symbol: str, asset_type: str, timeframe: str,
                     risk_level: str, capital: float | None,
                     market_data: dict) -> dict:
    if MOCK_MODE:
        return _mock_signal(symbol, risk_level, market_data)

    prompt = f"""You are a professional trading signal generator. Return ONLY valid JSON.

Asset: {symbol} ({asset_type})
Timeframe: {timeframe}
Risk level: {risk_level}
Capital available: {capital or 'not specified'}
Market data: {json.dumps(market_data, indent=2)}

Return JSON with keys:
- action (string: BUY/SELL/HOLD/WAIT)
- entry_price (float or null)
- stop_loss (float or null)
- take_profit (array of 1-3 floats or null)
- position_size (float percentage of capital, or null)
- risk_reward_ratio (float or null)
- confidence (float 0.0-1.0)
- reasoning (string, 2-3 sentences)
- invalidation (string: what would invalidate this trade)
"""
    msg = get_client().messages.create(
        model=MODEL, max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json_response(msg.content[0].text)


async def run_summarize(content: str, focus: str | None,
                        fmt: str, output_tokens: int) -> dict:
    if MOCK_MODE:
        return _mock_summarize(content)

    format_instructions = {
        "brief": "Write a concise 2-3 sentence summary.",
        "detailed": "Write a thorough multi-paragraph summary.",
        "bullets": "Structure as bullet points.",
        "executive": "Write an executive summary with headline, context, and action items.",
    }
    prompt = f"""Summarize the following content. Return ONLY valid JSON.

{f'Focus on: {focus}' if focus else ''}
Format: {format_instructions.get(fmt, 'concise summary')}
Content: {content}

Return JSON with keys:
- summary (string)
- key_points (array of strings, max 7)
- word_count (integer)
- sentiment (string: positive/negative/neutral)
"""
    msg = get_client().messages.create(
        model=MODEL, max_tokens=output_tokens + 200,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json_response(msg.content[0].text)


async def run_recommend(goal: str, context: str | None, asset_type: str | None,
                        risk_level: str, options: list[str] | None) -> dict:
    if MOCK_MODE:
        return _mock_recommend(goal, risk_level)

    prompt = f"""You are a strategic advisor. Return ONLY valid JSON.

Goal: {goal}
{f'Context: {context}' if context else ''}
{f'Asset type focus: {asset_type}' if asset_type else ''}
Risk tolerance: {risk_level}
{f'Options to evaluate: {", ".join(options)}' if options else ''}

Return JSON with keys:
- recommended_actions (array of objects, each with: action, priority [high/medium/low], rationale, expected_outcome)
- risk_assessment (string)
- alternatives (array of strings)
- confidence (float 0.0-1.0)
"""
    msg = get_client().messages.create(
        model=MODEL, max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json_response(msg.content[0].text)