# Decision Engine API

AI-powered backend for automated decision-making, signal generation, and data analysis. Built with FastAPI + Claude (Anthropic).

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/analyze` | Technical + AI analysis on any asset |
| `POST` | `/v1/signal` | Trade signal: BUY/SELL/HOLD with entry, SL, TP |
| `POST` | `/v1/summarize` | Summarize any text/data with key points |
| `POST` | `/v1/recommend` | Prioritized action recommendations |
| `POST` | `/v1/webhooks/register` | Register webhook for event delivery |
| `GET`  | `/health` | Health check |
| `GET`  | `/docs` | Swagger UI |

---

## Auth

All `/v1/*` endpoints require an API key:

```
X-API-Key: your-key-here
# or
Authorization: Bearer your-key-here
```

---

## Quick Start

### 1. Local Dev

```bash
cp .env.example .env
# Add ANTHROPIC_API_KEY and optionally ALPHA_VANTAGE_API_KEY

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

API available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

---

## Example Requests

### Analyze an asset

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "asset_type": "stock",
    "timeframe": "1d",
    "indicators": ["RSI", "MACD", "SMA_20"]
  }'
```

### Generate a trade signal

```bash
curl -X POST http://localhost:8000/v1/signal \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD",
    "asset_type": "crypto",
    "timeframe": "4h",
    "risk_level": "medium",
    "capital": 10000
  }'
```

### Summarize content

```bash
curl -X POST http://localhost:8000/v1/summarize \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Apple reported Q4 earnings of $1.64 EPS...",
    "format": "executive",
    "focus": "revenue growth and guidance"
  }'
```

### Get recommendations

```bash
curl -X POST http://localhost:8000/v1/recommend \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Diversify a $50k portfolio into crypto and real estate",
    "risk_level": "medium",
    "context": "Current allocation: 80% equities, 20% cash"
  }'
```

---

## Deploy to AWS / GCP

### AWS (ECS Fargate)

```bash
# Push image to ECR
aws ecr create-repository --repository-name decision-engine
docker tag decision-engine:latest <account>.dkr.ecr.<region>.amazonaws.com/decision-engine:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/decision-engine:latest

# Deploy via ECS task definition (set env vars as secrets in SSM Parameter Store)
```

### GCP (Cloud Run)

```bash
gcloud builds submit --tag gcr.io/<project>/decision-engine
gcloud run deploy decision-engine \
  --image gcr.io/<project>/decision-engine \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=... \
  --region us-central1
```

---

## Architecture

```
Client
  └── X-API-Key header
        └── APIKeyMiddleware
              └── LoggingMiddleware
                    ├── POST /v1/analyze  → market_data + ai_service → AnalyzeResponse
                    ├── POST /v1/signal   → market_data + ai_service → SignalResponse
                    ├── POST /v1/summarize           → ai_service → SummarizeResponse
                    ├── POST /v1/recommend           → ai_service → RecommendResponse
                    └── POST /v1/webhooks/register   → in-memory / Postgres
```

---

## Scaling Notes

- **Stateless**: All endpoints are stateless — safe to scale horizontally behind a load balancer.
- **Caching**: Add Redis caching on market data fetches (TTL 30–60s) to reduce latency and external API calls.
- **Rate limiting**: Add `slowapi` middleware for per-key rate limiting.
- **Webhook persistence**: Move `_webhooks` dict to Postgres for multi-instance deployments.
- **Async DB**: Use `asyncpg` + SQLAlchemy async for non-blocking Postgres queries.

---

## Dev API Keys (rotate before production)

```
dev-key-12345
test-key-67890
```

Set `API_KEYS=your-key-1,your-key-2` in `.env` to override.
