from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.report.application.dto.report import (
    ProductMetricRead,
    ProductReportRead,
    q2,
)
from src.modules.report.application.queries._shared import EXCLUDED, in_period


@dataclass
class _Product:
    """Mutable per-product accumulator (keyed by product_code snapshot)."""

    product_id: UUID
    product_name: str
    order_ids: set = field(default_factory=set)
    quantity: int = 0
    purchased: int = 0
    revenue: Decimal = field(default_factory=lambda: Decimal("0"))
    cost: Decimal = field(default_factory=lambda: Decimal("0"))
    cost_complete: bool = True


class ProductReport:
    """Best sellers and margin per product (top sản phẩm).

    Lines are grouped by the ``product_code`` snapshot (stable even if the
    catalog product is renamed); name/id shown are from the first line seen.
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ProductReportRead:
        orders = await self._orders.list(organization_id)

        acc: dict[str, _Product] = {}
        for order in orders:
            if order.status in EXCLUDED:
                continue
            if not in_period(order.created_at, date_from, date_to):
                continue
            for line in order.lines:
                product = acc.setdefault(
                    line.product_code,
                    _Product(
                        product_id=line.product_id.value,
                        product_name=line.product_name,
                    ),
                )
                product.order_ids.add(order.id_)
                product.quantity += line.quantity.value
                product.purchased += line.purchased_quantity
                product.revenue += line.line_total
                if line.actual_unit_cost is not None:
                    product.cost += (
                        line.actual_unit_cost.amount * line.purchased_quantity
                    )
                if (
                    line.purchased_quantity < line.quantity.value
                    or line.actual_unit_cost is None
                ):
                    product.cost_complete = False

        rows = [
            ProductMetricRead(
                product_id=p.product_id,
                product_code=code,
                product_name=p.product_name,
                orders_count=len(p.order_ids),
                quantity_sold=p.quantity,
                purchased_quantity=p.purchased,
                revenue=q2(p.revenue),
                cost=q2(p.cost),
                profit=q2(p.revenue - p.cost),
                margin_pct=(
                    q2((p.revenue - p.cost) / p.revenue * 100)
                    if p.revenue > 0
                    else None
                ),
                cost_complete=p.cost_complete,
            )
            for code, p in acc.items()
        ]
        rows.sort(key=lambda r: r.revenue, reverse=True)

        return ProductReportRead(
            products=rows,
            products_count=len(rows),
            total_quantity=sum(r.quantity_sold for r in rows),
            total_revenue=q2(sum((r.revenue for r in rows), Decimal("0"))),
            total_cost=q2(sum((r.cost for r in rows), Decimal("0"))),
            total_profit=q2(
                sum((r.profit for r in rows), Decimal("0"))
            ),
        )
