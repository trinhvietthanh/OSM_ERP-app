from datetime import date

from fastapi import APIRouter, Depends

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.presentation.dependencies import get_customer_repository
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.presentation.dependencies import get_order_repository
from src.modules.report.application.dto.report import (
    CashFlowReportRead,
    CustomerReportRead,
    DailySummaryRead,
    OperationsReportRead,
    OverviewReportRead,
    PeriodComparisonRead,
    ProductReportRead,
    ProfitReportRead,
    ReceivablesReportRead,
    TripReportRead,
)
from src.modules.report.application.queries.cash_flow import CashFlowReport
from src.modules.report.application.queries.customer_report import CustomerReport
from src.modules.report.application.queries.daily_summary import DailySummary
from src.modules.report.application.queries.operations_report import (
    OperationsReport,
)
from src.modules.report.application.queries.overview import OverviewReport
from src.modules.report.application.queries.period_comparison import (
    PeriodComparison,
)
from src.modules.report.application.queries.product_report import ProductReport
from src.modules.report.application.queries.profit_report import ProfitReport
from src.modules.report.application.queries.receivables_report import (
    ReceivablesReport,
)
from src.modules.report.application.queries.trip_report import TripReport
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId
from src.modules.trip.presentation.dependencies import get_trip_repository

router = APIRouter(prefix="/reports", tags=["report"])


@router.get("/profit", response_model=ProfitReportRead)
async def profit_report(
    date_from: date | None = None,
    date_to: date | None = None,
    trip_id: str | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> ProfitReportRead:
    return await ProfitReport(orders, customers).execute(
        current_user.organization_id,
        date_from=date_from,
        date_to=date_to,
        trip_id=TripId.from_string(trip_id) if trip_id is not None else None,
    )


@router.get("/receivables", response_model=ReceivablesReportRead)
async def receivables_report(
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> ReceivablesReportRead:
    return await ReceivablesReport(orders, customers).execute(
        current_user.organization_id
    )


@router.get("/overview", response_model=OverviewReportRead)
async def overview_report(
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> OverviewReportRead:
    """Snapshot dashboard: pipeline funnel, money held, debt, deposits, profit."""
    return await OverviewReport(orders).execute(current_user.organization_id)


@router.get("/daily-summary", response_model=DailySummaryRead)
async def daily_summary_report(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> DailySummaryRead:
    """Orders grouped by creation date — the daily pulse, incl. 'đã chốt' count."""
    return await DailySummary(orders).execute(
        current_user.organization_id, date_from=date_from, date_to=date_to
    )


@router.get("/cash-flow", response_model=CashFlowReportRead)
async def cash_flow_report(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> CashFlowReportRead:
    """Money in (collections) vs out (purchase cost, refunds) over a period."""
    return await CashFlowReport(orders).execute(
        current_user.organization_id, date_from=date_from, date_to=date_to
    )


@router.get("/trips", response_model=TripReportRead)
async def trip_report(
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    trips: AbstractTripRepository = Depends(get_trip_repository),
) -> TripReportRead:
    """P&L per buying trip (lãi/lỗ theo chuyến hàng)."""
    return await TripReport(orders, trips).execute(current_user.organization_id)


@router.get("/products", response_model=ProductReportRead)
async def product_report(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> ProductReportRead:
    """Best sellers and margin per product over a period (top sản phẩm)."""
    return await ProductReport(orders).execute(
        current_user.organization_id, date_from=date_from, date_to=date_to
    )


@router.get("/customers", response_model=CustomerReportRead)
async def customer_report(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> CustomerReportRead:
    """Top customers by revenue over a period (top khách hàng)."""
    return await CustomerReport(orders, customers).execute(
        current_user.organization_id, date_from=date_from, date_to=date_to
    )


@router.get("/operations", response_model=OperationsReportRead)
async def operations_report(
    date_from: date | None = None,
    date_to: date | None = None,
    stale_days: int = 7,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> OperationsReportRead:
    """Cancellation / completion rates plus stuck orders (chỉ số vận hành)."""
    return await OperationsReport(orders).execute(
        current_user.organization_id,
        date_from=date_from,
        date_to=date_to,
        stale_days=stale_days,
    )


@router.get("/period-comparison", response_model=PeriodComparisonRead)
async def period_comparison_report(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> PeriodComparisonRead:
    """KPIs for a period vs the one right before it (so sánh kỳ)."""
    return await PeriodComparison(orders).execute(
        current_user.organization_id, date_from=date_from, date_to=date_to
    )
