"""sale-intel API: source registry CRUD, crawl trigger, and read models."""

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import (
    Coupon,
    CrawlJob,
    DealEvent,
    PriceSnapshot,
    Product,
    Promotion,
    RawSnapshot,
    Source,
)
from src.db.session import get_session
from src.services.crawl import run_crawl

app = FastAPI(title="sale-intel", version="0.1.0")


# ------------------------------------------------------------------ sources


class SourceIn(BaseModel):
    source_id: str
    name: str
    country: str
    currency: str
    base_url: str
    crawl_type: str = "http_with_playwright_fallback"
    crawl_interval_minutes: int = 60
    is_active: bool = True


class SourcePatch(BaseModel):
    name: str | None = None
    base_url: str | None = None
    crawl_type: str | None = None
    crawl_interval_minutes: int | None = None
    is_active: bool | None = None


class SourceRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    name: str
    country: str
    currency: str
    base_url: str
    crawl_type: str
    crawl_interval_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@app.get("/sources", response_model=list[SourceRead])
async def list_sources(session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Source).order_by(Source.source_id))).all()


@app.post("/sources", response_model=SourceRead, status_code=201)
async def create_source(
    payload: SourceIn, session: AsyncSession = Depends(get_session)
):
    exists = (
        await session.scalars(
            select(Source).where(Source.source_id == payload.source_id)
        )
    ).one_or_none()
    if exists is not None:
        raise HTTPException(409, f"source {payload.source_id!r} already exists")
    source = Source(**payload.model_dump())
    session.add(source)
    await session.flush()
    await session.refresh(source)  # load server-side timestamps
    return source


@app.patch("/sources/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: str, payload: SourcePatch, session: AsyncSession = Depends(get_session)
):
    source = (
        await session.scalars(select(Source).where(Source.source_id == source_id))
    ).one_or_none()
    if source is None:
        raise HTTPException(404, "source not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(source, key, value)
    await session.flush()
    await session.refresh(source)
    return source


# -------------------------------------------------------------------- crawl


class CrawlJobRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    entrypoint: str
    url: str
    status: str
    snapshot_id: uuid.UUID | None
    stats: dict | None
    error: str | None
    started_at: datetime
    finished_at: datetime | None


@app.post("/crawl/{source_id}/{entrypoint}", response_model=CrawlJobRead)
async def trigger_crawl(
    source_id: str, entrypoint: str, session: AsyncSession = Depends(get_session)
):
    try:
        return await run_crawl(session, source_id, entrypoint)
    except KeyError as exc:
        raise HTTPException(404, str(exc))


@app.get("/crawl-jobs", response_model=list[CrawlJobRead])
async def list_crawl_jobs(
    limit: int = 50, session: AsyncSession = Depends(get_session)
):
    return (
        await session.scalars(
            select(CrawlJob).order_by(CrawlJob.created_at.desc()).limit(limit)
        )
    ).all()


# ------------------------------------------------------------- read models


class ProductRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    name: str
    brand: str | None
    url: str
    image_url: str | None
    currency: str
    first_seen_at: datetime
    last_seen_at: datetime


class PriceSnapshotRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    original_price: Decimal | None
    current_price: Decimal
    discount_percent: float | None
    currency: str
    collected_at: datetime


@app.get("/products", response_model=list[ProductRead])
async def list_products(
    source_id: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Product).order_by(Product.last_seen_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(Product.source_id == source_id)
    return (await session.scalars(stmt)).all()


@app.get("/products/{product_id}/prices", response_model=list[PriceSnapshotRead])
async def price_history(
    product_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    return (
        await session.scalars(
            select(PriceSnapshot)
            .where(PriceSnapshot.product_id == product_id)
            .order_by(PriceSnapshot.collected_at.desc())
        )
    ).all()


class PromotionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    title: str
    promotion_type: str
    code: str | None
    condition_text: str | None
    source_url: str | None
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime


@app.get("/promotions", response_model=list[PromotionRead])
async def list_promotions(
    source_id: str | None = None,
    promotion_type: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Promotion).order_by(Promotion.last_seen_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(Promotion.source_id == source_id)
    if promotion_type:
        stmt = stmt.where(Promotion.promotion_type == promotion_type)
    return (await session.scalars(stmt)).all()


class CouponRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    code: str | None
    discount_type: str | None
    discount_value: Decimal | None
    min_order_value: Decimal | None
    condition_text: str | None
    source_url: str | None
    is_active: bool


@app.get("/coupons", response_model=list[CouponRead])
async def list_coupons(
    source_id: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Coupon).order_by(Coupon.created_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(Coupon.source_id == source_id)
    return (await session.scalars(stmt)).all()


class DealEventRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    product_id: uuid.UUID | None
    event_type: str
    old_price: Decimal | None
    new_price: Decimal | None
    discount_percent: float | None
    payload: dict | None
    created_at: datetime


@app.get("/deal-events", response_model=list[DealEventRead])
async def list_deal_events(
    source_id: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(DealEvent).order_by(DealEvent.created_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(DealEvent.source_id == source_id)
    return (await session.scalars(stmt)).all()


class RawSnapshotRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_id: str
    url: str
    content_type: str
    storage_path: str
    content_hash: str
    status_code: int
    parser_version: str | None
    collected_at: datetime


@app.get("/raw-snapshots", response_model=list[RawSnapshotRead])
async def list_raw_snapshots(
    source_id: str | None = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(RawSnapshot).order_by(RawSnapshot.collected_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(RawSnapshot.source_id == source_id)
    return (await session.scalars(stmt)).all()
