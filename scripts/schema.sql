-- Decision Engine — Postgres Schema
-- Run: psql $DATABASE_URL -f scripts/schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── API Keys ──────────────────────────────────────────────────────────────────
CREATE TABLE api_keys (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash    TEXT NOT NULL UNIQUE,
    label       TEXT,
    owner       TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_used   TIMESTAMPTZ,
    revoked     BOOLEAN DEFAULT FALSE
);

-- ── Request Log ───────────────────────────────────────────────────────────────
CREATE TABLE request_log (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id  TEXT NOT NULL,
    endpoint    TEXT NOT NULL,
    method      TEXT NOT NULL,
    status_code INT,
    latency_ms  FLOAT,
    api_key     TEXT,
    payload     JSONB,
    response    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_request_log_created ON request_log (created_at DESC);
CREATE INDEX idx_request_log_endpoint ON request_log (endpoint);

-- ── Signals ───────────────────────────────────────────────────────────────────
CREATE TABLE signals (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol          TEXT NOT NULL,
    asset_type      TEXT NOT NULL,
    timeframe       TEXT NOT NULL,
    action          TEXT NOT NULL,           -- BUY/SELL/HOLD/WAIT
    entry_price     NUMERIC(18,8),
    stop_loss       NUMERIC(18,8),
    take_profit     NUMERIC(18,8)[],
    confidence      FLOAT,
    reasoning       TEXT,
    invalidation    TEXT,
    triggered_at    TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    outcome         TEXT                     -- win/loss/expired
);

CREATE INDEX idx_signals_symbol ON signals (symbol, triggered_at DESC);

-- ── Webhooks ──────────────────────────────────────────────────────────────────
CREATE TABLE webhooks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url         TEXT NOT NULL,
    events      TEXT[] NOT NULL,
    secret_hash TEXT,
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_fired  TIMESTAMPTZ,
    fail_count  INT DEFAULT 0
);

-- ── Analysis Cache (optional TTL via pg_cron or application logic) ────────────
CREATE TABLE analysis_cache (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key   TEXT NOT NULL UNIQUE,        -- e.g. "AAPL:stock:1d"
    payload     JSONB NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cache_key ON analysis_cache (cache_key);
CREATE INDEX idx_cache_expires ON analysis_cache (expires_at);
