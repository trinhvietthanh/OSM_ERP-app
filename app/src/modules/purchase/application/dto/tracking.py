from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel

from src.modules.purchase.application.dto.order import _q2
from src.modules.purchase.domain.entities.order import Order


class TrackingLineRead(BaseModel):
    """Safe line view for the public tracking page: what + how many, no costs."""

    product_name: str
    quantity: int


class TrackingRead(BaseModel):
    """Public, unauthenticated order view for the mã-Code lookup page.

    Deliberately excludes anything sensitive: no customer name/phone, no
    purchase costs, no tenant info — only what the customer already knows
    plus the current status and money balance.
    """

    tracking_code: str
    status: str
    lines: list[TrackingLineRead]
    total_amount: Decimal
    total_collected: Decimal
    remaining: Decimal
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, order: Order) -> Self:
        return cls(
            tracking_code=order.tracking_code.value,
            status=order.status.value,
            lines=[
                TrackingLineRead(
                    product_name=line.product_name, quantity=line.quantity.value
                )
                for line in order.lines
            ],
            total_amount=_q2(order.total_amount),
            total_collected=_q2(order.total_collected),
            remaining=_q2(order.remaining),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
