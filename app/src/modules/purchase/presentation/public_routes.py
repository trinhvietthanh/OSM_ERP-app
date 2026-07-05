from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.purchase.application.dto.tracking import TrackingRead
from src.modules.purchase.application.queries.track_order import TrackOrder
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import TrackingCode
from src.modules.purchase.presentation.dependencies import get_order_repository
from src.shared.domain.base import DomainError

# Public router: NO auth dependency — customers look their order up by code.
router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/{code}", response_model=TrackingRead)
async def track_order(
    code: str,
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> TrackingRead:
    try:
        parsed = TrackingCode.from_string(code)
    except DomainError:
        # Malformed code → same 404 as unknown code (don't leak the format).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    read = await TrackOrder(orders).execute(parsed)
    if read is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    return read
