"""
Market data adapter.
Priority: live data (Alpha Vantage / Binance) → mock fallback for dev/testing.
"""
import os
import httpx
import random
from typing import Any

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
BINANCE_BASE = "https://api.binance.com/api/v3"
AV_BASE = "https://www.alphavantage.co/query"


def _mock_price(symbol: str) -> dict:
    """Deterministic-ish mock market data for development."""
    seed = sum(ord(c) for c in symbol)
    rng = random.Random(seed)
    price = round(rng.uniform(10, 50000), 2)
    change_pct = round(rng.uniform(-5, 5), 2)
    volume = rng.randint(100_000, 10_000_000)
    return {
        "symbol": symbol,
        "price": price,
        "change_pct_24h": change_pct,
        "volume_24h": volume,
        "high_24h": round(price * 1.03, 2),
        "low_24h": round(price * 0.97, 2),
        "market_cap": None,
        "source": "mock",
    }


async def get_crypto_price(symbol: str) -> dict:
    """Fetch from Binance; fallback to mock."""
    pair = symbol.replace("-", "").replace("/", "").upper()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": pair})
            if r.status_code == 200:
                d = r.json()
                return {
                    "symbol": symbol,
                    "price": float(d["lastPrice"]),
                    "change_pct_24h": float(d["priceChangePercent"]),
                    "volume_24h": float(d["volume"]),
                    "high_24h": float(d["highPrice"]),
                    "low_24h": float(d["lowPrice"]),
                    "source": "binance",
                }
    except Exception:
        pass
    return _mock_price(symbol)


async def get_stock_price(symbol: str) -> dict:
    """Fetch from Alpha Vantage; fallback to mock."""
    if not ALPHA_VANTAGE_KEY:
        return _mock_price(symbol)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(AV_BASE, params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol.upper(),
                "apikey": ALPHA_VANTAGE_KEY,
            })
            if r.status_code == 200:
                q = r.json().get("Global Quote", {})
                if q.get("05. price"):
                    return {
                        "symbol": symbol,
                        "price": float(q["05. price"]),
                        "change_pct_24h": float(q["10. change percent"].strip("%")),
                        "volume_24h": int(q["06. volume"]),
                        "high_24h": float(q["03. high"]),
                        "low_24h": float(q["04. low"]),
                        "source": "alpha_vantage",
                    }
    except Exception:
        pass
    return _mock_price(symbol)


async def get_market_data(symbol: str, asset_type: str) -> dict:
    if asset_type == "crypto":
        return await get_crypto_price(symbol)
    return await get_stock_price(symbol)
