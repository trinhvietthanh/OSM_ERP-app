import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.infrastructure.postgres.lifespan import postgres_lifespan
from src.modules.authenticate.application.exceptions import InvalidCredentialsError
from src.modules.authenticate.presentation.routes import router as auth_router
from src.modules.catalog.application.exceptions import (
    ProductCodeAlreadyExistsError,
    ProductNotFoundError,
)
from src.modules.catalog.presentation.routes import router as catalog_router
from src.modules.campaign.application.exceptions import (
    CampaignProductAlreadyExistsError,
    CampaignProductNotFoundError,
    SaleRoundCodeAlreadyExistsError,
    SaleRoundNotFoundError,
)
from src.modules.campaign.presentation.routes import router as campaign_router
from src.modules.customer.application.exceptions import CustomerNotFoundError
from src.modules.customer.presentation.routes import router as customer_router
from src.modules.purchase.application.exceptions import (
    OrderLineNotFoundError,
    OrderNotFoundError,
    ReceiptNotFoundError,
)
from src.modules.purchase.presentation.public_routes import router as tracking_router
from src.modules.purchase.presentation.routes import router as order_router
from src.modules.report.presentation.routes import router as report_router
from src.modules.trip.application.exceptions import (
    OrderNotAttachableError,
    TripCodeAlreadyExistsError,
    TripNotFoundError,
)
from src.modules.trip.presentation.routes import router as trip_router
from src.shared.domain.base import DomainError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: verify Postgres connectivity (fail-fast). Shutdown: dispose engine."""
    async with postgres_lifespan(app):
        yield


def create_app() -> FastAPI:
    """Assemble the FastAPI application: lifespan, routers, exception handlers."""
    app = FastAPI(title="app_erp", lifespan=lifespan)

    # The browser frontend (../frontend, Next.js dev server on :3000) talks to
    # this API cross-origin, so CORS is required. Set CORS_ORIGINS (comma-
    # separated) to override the default local-dev origins.
    origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ] or ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(InvalidCredentialsError)
    async def _handle_invalid_credentials(
        _: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(ProductNotFoundError)
    async def _handle_product_not_found(
        _: Request, exc: ProductNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProductCodeAlreadyExistsError)
    async def _handle_product_code_exists(
        _: Request, exc: ProductCodeAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(SaleRoundNotFoundError)
    async def _handle_round_not_found(
        _: Request, exc: SaleRoundNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(CampaignProductNotFoundError)
    async def _handle_campaign_product_not_found(
        _: Request, exc: CampaignProductNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SaleRoundCodeAlreadyExistsError)
    async def _handle_round_code_exists(
        _: Request, exc: SaleRoundCodeAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(CampaignProductAlreadyExistsError)
    async def _handle_campaign_product_exists(
        _: Request, exc: CampaignProductAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(CustomerNotFoundError)
    async def _handle_customer_not_found(
        _: Request, exc: CustomerNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(OrderNotFoundError)
    async def _handle_order_not_found(
        _: Request, exc: OrderNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(OrderLineNotFoundError)
    async def _handle_order_line_not_found(
        _: Request, exc: OrderLineNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ReceiptNotFoundError)
    async def _handle_receipt_not_found(
        _: Request, exc: ReceiptNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(TripNotFoundError)
    async def _handle_trip_not_found(
        _: Request, exc: TripNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(TripCodeAlreadyExistsError)
    async def _handle_trip_code_exists(
        _: Request, exc: TripCodeAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(OrderNotAttachableError)
    async def _handle_order_not_attachable(
        _: Request, exc: OrderNotAttachableError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    # Catch-all for domain invariant violations (e.g. malformed code, negative
    # price). More specific subclass handlers above take precedence via MRO.
    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    app.include_router(auth_router)
    app.include_router(catalog_router)
    app.include_router(campaign_router)
    app.include_router(customer_router)
    app.include_router(order_router)
    app.include_router(trip_router)
    app.include_router(tracking_router)
    app.include_router(report_router)
    return app


app = create_app()
