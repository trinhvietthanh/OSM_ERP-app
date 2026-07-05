from datetime import date

from fastapi import APIRouter, Depends

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.presentation.dependencies import get_customer_repository
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.presentation.dependencies import get_order_repository
from src.modules.report.application.dto.report import (
    ProfitReportRead,
    ReceivablesReportRead,
)
from src.modules.report.application.queries.profit_report import ProfitReport
from src.modules.report.application.queries.receivables_report import (
    ReceivablesReport,
)
from src.modules.trip.domain.value_objects.trip import TripId

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
