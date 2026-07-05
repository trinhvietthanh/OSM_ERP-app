# sale-intel — Promotion Tracking / Sale Intelligence MVP

Tracks public sale pages, coupon pages, top-offer pages, product listings,
prices and promotions for US retail sources:

- `macys_us` — Macy's US
- `tommy_us` — Tommy Hilfiger US
- `bbw_us` — Bath & Body Works US

**Compliance by design:** collectors only fetch public pages with a declared
User-Agent and per-source rate limits. No captcha/anti-bot bypass, no logins,
no checkout automation. Blocked responses (401/403/429) are recorded as-is and
never retried through the browser fallback.

## Architecture

```
configs/sources/*.yaml        source registry configs (entrypoints → parser)
src/collectors/               HTTP (httpx) + Playwright fallback; raw bytes only
src/storage/                  object storage abstraction (local FS / MinIO-S3)
src/services/snapshots.py     raw content → object storage + raw_snapshots row
src/parsers/                  HTML/JSON-LD → ParsedProduct/Promotion/Coupon DTOs
src/normalization/            DTO cleanup + promotion_type classification
src/services/ingest.py        upsert products, price snapshots, price-change
                              detection, deal events, alert evaluation
src/services/crawl.py         one crawl run = crawl_jobs row + full pipeline
src/api/main.py               FastAPI: sources CRUD, crawl trigger, read models
```

Hard rule kept throughout: **collectors never write business rows** — only the
ingest service does, from parsed+normalized DTOs.

## Setup

```bash
uv sync
docker exec app_erp_pg psql -U postgres -c 'CREATE DATABASE sale_intel'
uv run alembic upgrade head
uv run python -m src.seed                      # seed the 3 sources from YAML
uv run uvicorn src.api.main:app --port 8100    # API on :8100 (docs at /docs)
```

Optional Playwright fallback: `uv add playwright && uv run playwright install chromium`.

## Try it

```bash
uv run pytest                                  # parser + normalizer tests (fixtures)
uv run python scripts/demo_ingest.py           # full pipeline demo, no live crawling
curl -s localhost:8100/sources | jq
curl -s -X POST localhost:8100/crawl/tommy_us/coupons | jq   # live crawl (1 request)
curl -s localhost:8100/promotions | jq
curl -s localhost:8100/deal-events | jq
```

## Notes

- Prices land in `price_snapshots`; a drop ≥ `SALEINTEL_PRICE_DROP_THRESHOLD_PCT`
  (default 10%) creates a `deal_events` row and runs active `alert_rules`
  (MVP channel: `alert_logs`).
- Parsers are conservative: unknown markup ⇒ partial data + `errors[]`,
  never an exception. Each has fixture coverage in `tests/`.
- Promotion types: `percent_off`, `fixed_price`, `buy_x_get_y`,
  `free_shipping`, `coupon_code`, `clearance`, `limited_time`, `unknown`.
