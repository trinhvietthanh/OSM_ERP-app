from collections import defaultdict
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.report.application.dto.report import (
    TripPnlRead,
    TripReportRead,
    q2,
)
from src.modules.report.application.queries._shared import EXCLUDED, order_cost
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId


class TripReport:
    """P&L per buying trip (lãi/lỗ theo chuyến hàng).

    One row per trip: revenue, actual cost, profit, cash collected, debt and
    purchase progress across the trip's orders. Per-order drill-down is served
    by the existing profit report filtered by ``trip_id``.
    """

    def __init__(
        self,
        orders: AbstractOrderRepository,
        trips: AbstractTripRepository,
    ) -> None:
        self._orders = orders
        self._trips = trips

    async def execute(self, organization_id: OrganizationId) -> TripReportRead:
        trips = await self._trips.list(organization_id)
        orders = await self._orders.list(organization_id)

        by_trip: dict[TripId, list[Order]] = defaultdict(list)
        for order in orders:
            if order.trip_id is not None and order.status not in EXCLUDED:
                by_trip[order.trip_id].append(order)

        rows: list[TripPnlRead] = []
        total_revenue = Decimal("0")
        total_cost = Decimal("0")

        for trip in trips:
            group = by_trip.get(trip.id_, [])
            revenue = Decimal("0")
            cost = Decimal("0")
            collected = Decimal("0")
            outstanding = Decimal("0")
            total_qty = 0
            purchased_qty = 0
            complete = True

            for order in group:
                revenue += order.total_amount
                collected += order.total_collected
                remaining = order.remaining
                if remaining > 0:
                    outstanding += remaining
                order_spend, order_complete = order_cost(order)
                cost += order_spend
                complete = complete and order_complete
                for line in order.lines:
                    total_qty += line.quantity.value
                    purchased_qty += line.purchased_quantity

            profit = revenue - cost
            total_revenue += revenue
            total_cost += cost

            rows.append(
                TripPnlRead(
                    trip_id=trip.id_.value,
                    trip_code=trip.code.value,
                    trip_name=trip.name.value,
                    status=trip.status.value,
                    shopper_name=trip.shopper_name,
                    departure_date=trip.departure_date,
                    arrival_date=trip.arrival_date,
                    orders_count=len(group),
                    revenue=q2(revenue),
                    cost=q2(cost),
                    profit=q2(profit),
                    margin_pct=(
                        q2(profit / revenue * 100) if revenue > 0 else None
                    ),
                    collected=q2(collected),
                    outstanding=q2(outstanding),
                    total_quantity=total_qty,
                    purchased_quantity=purchased_qty,
                    purchase_progress_pct=(
                        q2(Decimal(purchased_qty) / Decimal(total_qty) * 100)
                        if total_qty > 0
                        else Decimal("0")
                    ),
                    cost_complete=complete,
                )
            )

        return TripReportRead(
            trips=rows,
            trips_count=len(rows),
            total_revenue=q2(total_revenue),
            total_cost=q2(total_cost),
            total_profit=q2(total_revenue - total_cost),
        )
