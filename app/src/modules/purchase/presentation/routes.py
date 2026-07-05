from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.presentation.dependencies import get_product_repository
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.customer.presentation.dependencies import get_customer_repository
from src.modules.purchase.application.commands.add_receipt import AddReceipt
from src.modules.purchase.application.commands.change_order_status import (
    ChangeOrderStatus,
)
from src.modules.purchase.application.commands.create_order import CreateOrder
from src.modules.purchase.application.commands.record_line_purchase import (
    RecordLinePurchase,
)
from src.modules.purchase.application.commands.remove_receipt import RemoveReceipt
from src.modules.purchase.application.commands.update_order import UpdateOrder
from src.modules.purchase.application.dto.order import (
    ChangeOrderStatusInput,
    CreateOrderInput,
    CreateReceiptInput,
    OrderRead,
    RecordLinePurchaseInput,
    UpdateOrderInput,
)
from src.modules.purchase.application.queries.get_order import GetOrder
from src.modules.purchase.application.queries.list_orders import ListOrders
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    OrderLineId,
    OrderStatus,
    PaymentReceiptId,
)
from src.modules.purchase.presentation.dependencies import get_order_repository
from src.modules.trip.domain.value_objects.trip import TripId
from src.shared.domain.base import DomainError

router = APIRouter(prefix="/orders", tags=["purchase"])


def _parse_order_id(order_id: str) -> OrderId:
    """Parse a path order id, mapping bad input to 404."""
    try:
        return OrderId.from_string(order_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _parse_line_id(line_id: str) -> OrderLineId:
    """Parse a path line id, mapping bad input to 404."""
    try:
        return OrderLineId.from_string(line_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _parse_receipt_id(receipt_id: str) -> PaymentReceiptId:
    """Parse a path receipt id, mapping bad input to 404."""
    try:
        return PaymentReceiptId.from_string(receipt_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    inp: CreateOrderInput,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
    products: AbstractProductRepository = Depends(get_product_repository),
) -> OrderRead:
    return await CreateOrder(orders, customers, products).execute(
        current_user.organization_id, inp
    )


@router.get("", response_model=list[OrderRead])
async def list_orders(
    status_filter: str | None = Query(None, alias="status"),
    customer_id: str | None = None,
    trip_id: str | None = None,
    unassigned: bool = False,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> list[OrderRead]:
    parsed_status: OrderStatus | None = None
    if status_filter is not None:
        try:
            parsed_status = OrderStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown order status: {status_filter!r}.",
            )
    return await ListOrders(orders, customers).execute(
        current_user.organization_id,
        status=parsed_status,
        customer_id=(
            CustomerId.from_string(customer_id) if customer_id is not None else None
        ),
        trip_id=TripId.from_string(trip_id) if trip_id is not None else None,
        unassigned=unassigned,
    )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> OrderRead:
    read = await GetOrder(orders, customers).execute(
        current_user.organization_id, _parse_order_id(order_id)
    )
    if read is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    return read


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: str,
    inp: UpdateOrderInput,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
    products: AbstractProductRepository = Depends(get_product_repository),
) -> OrderRead:
    return await UpdateOrder(orders, customers, products).execute(
        current_user.organization_id, _parse_order_id(order_id), inp
    )


@router.post("/{order_id}/status", response_model=OrderRead)
async def change_order_status(
    order_id: str,
    inp: ChangeOrderStatusInput,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> OrderRead:
    return await ChangeOrderStatus(orders, customers).execute(
        current_user.organization_id, _parse_order_id(order_id), inp
    )


@router.post("/{order_id}/receipts", response_model=OrderRead, status_code=201)
async def add_receipt(
    order_id: str,
    inp: CreateReceiptInput,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> OrderRead:
    return await AddReceipt(orders, customers).execute(
        current_user.organization_id, _parse_order_id(order_id), inp
    )


@router.delete("/{order_id}/receipts/{receipt_id}", status_code=204)
async def remove_receipt(
    order_id: str,
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
) -> None:
    await RemoveReceipt(orders).execute(
        current_user.organization_id,
        _parse_order_id(order_id),
        _parse_receipt_id(receipt_id),
    )


@router.post("/{order_id}/lines/{line_id}/purchase", response_model=OrderRead)
async def record_line_purchase(
    order_id: str,
    line_id: str,
    inp: RecordLinePurchaseInput,
    current_user: User = Depends(get_current_user),
    orders: AbstractOrderRepository = Depends(get_order_repository),
    customers: AbstractCustomerRepository = Depends(get_customer_repository),
) -> OrderRead:
    return await RecordLinePurchase(orders, customers).execute(
        current_user.organization_id,
        _parse_order_id(order_id),
        _parse_line_id(line_id),
        inp,
    )
