from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.presentation.dependencies import get_customer_repository
from src.modules.purchase.application.dto.order import OrderRead
from src.modules.purchase.application.queries.list_orders import ListOrders
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId
from src.modules.purchase.presentation.dependencies import get_order_repository
from src.modules.trip.application.commands.attach_orders import (
    AttachOrders,
    DetachOrder,
)
from src.modules.trip.application.commands.change_trip_status import ChangeTripStatus
from src.modules.trip.application.commands.create_trip import CreateTrip
from src.modules.trip.application.commands.update_trip import UpdateTrip
from src.modules.trip.application.dto.trip import (
    AttachOrdersInput,
    ChangeTripStatusInput,
    CreateTripInput,
    TripRead,
    UpdateTripInput,
)
from src.modules.trip.application.queries.get_trip import GetTrip
from src.modules.trip.application.queries.list_trips import ListTrips
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId, TripStatus
from src.modules.trip.presentation.dependencies import get_trip_repository
from src.shared.domain.base import DomainError

router = APIRouter(prefix="/trips", tags=["trip"])


def _parse_trip_id(trip_id: str) -> TripId:
    """Parse a path trip id, mapping bad input to 404."""
    try:
        return TripId.from_string(trip_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _parse_order_id(order_id: str) -> OrderId:
    """Parse a path order id, mapping bad input to 404."""
    try:
        return OrderId.from_string(order_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=TripRead, status_code=201)
async def create_trip(
    inp: CreateTripInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractTripRepository = Depends(get_trip_repository),
) -> TripRead:
    return await CreateTrip(repo).execute(current_user.organization_id, inp)


@router.get("", response_model=list[TripRead])
async def list_trips(
    status_filter: str | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    repo: AbstractTripRepository = Depends(get_trip_repository),
) -> list[TripRead]:
    parsed_status: TripStatus | None = None
    if status_filter is not None:
        try:
            parsed_status = TripStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown trip status: {status_filter!r}.",
            )
    return await ListTrips(repo).execute(
        current_user.organization_id, status=parsed_status
    )


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractTripRepository = Depends(get_trip_repository),
) -> TripRead:
    read = await GetTrip(repo).execute(
        current_user.organization_id, _parse_trip_id(trip_id)
    )
    if read is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found."
        )
    return read


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: str,
    inp: UpdateTripInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractTripRepository = Depends(get_trip_repository),
) -> TripRead:
    return await UpdateTrip(repo).execute(
        current_user.organization_id, _parse_trip_id(trip_id), inp
    )


@router.post("/{trip_id}/status", response_model=TripRead)
async def change_trip_status(
    trip_id: str,
    inp: ChangeTripStatusInput,
    current_user: User = Depends(get_current_user),
    trips: AbstractTripRepository = Depends(get_trip_repository),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> TripRead:
    return await ChangeTripStatus(trips, orders).execute(
        current_user.organization_id, _parse_trip_id(trip_id), inp
    )


@router.get("/{trip_id}/orders", response_model=list[OrderRead])
async def list_trip_orders(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trips: AbstractTripRepository = Depends(get_trip_repository),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> list[OrderRead]:
    tid = _parse_trip_id(trip_id)
    if await GetTrip(trips).execute(current_user.organization_id, tid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found."
        )
    return await ListOrders(orders, customers).execute(
        current_user.organization_id, trip_id=tid
    )


@router.post("/{trip_id}/orders", status_code=204)
async def attach_orders(
    trip_id: str,
    inp: AttachOrdersInput,
    current_user: User = Depends(get_current_user),
    trips: AbstractTripRepository = Depends(get_trip_repository),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> None:
    await AttachOrders(trips, orders).execute(
        current_user.organization_id, _parse_trip_id(trip_id), inp
    )


@router.delete("/{trip_id}/orders/{order_id}", status_code=204)
async def detach_order(
    trip_id: str,
    order_id: str,
    current_user: User = Depends(get_current_user),
    trips: AbstractTripRepository = Depends(get_trip_repository),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> None:
    await DetachOrder(trips, orders).execute(
        current_user.organization_id,
        _parse_trip_id(trip_id),
        _parse_order_id(order_id),
    )
