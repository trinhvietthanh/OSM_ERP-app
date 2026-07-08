from datetime import date
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import ReceiptKind
from src.modules.report.application.dto.report import CashFlowReportRead, q2
from src.modules.report.application.queries._shared import in_period


class CashFlowReport:
    """Money in vs money out over a period (dòng tiền vào / ra).

    * ``cash_in``  — customer collections (deposits + payments) by receipt date.
    * ``cash_out`` — actual cost of goods bought, by line purchase date.
    * ``refunded`` — money returned to customers, by receipt date.
    * ``pending_purchase_cost`` — estimated spend left on ordered-but-unbought
      goods (remaining quantity × known unit cost).
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> CashFlowReportRead:
        orders = await self._orders.list(organization_id)

        cash_in = Decimal("0")
        cash_out = Decimal("0")
        refunded = Decimal("0")
        pending = Decimal("0")

        for order in orders:
            for receipt in order.receipts:
                if not in_period(receipt.received_at, date_from, date_to):
                    continue
                if receipt.kind is ReceiptKind.COLLECTION:
                    cash_in += receipt.amount.amount
                else:
                    refunded += receipt.amount.amount

            for line in order.lines:
                unit_cost = line.actual_unit_cost
                if unit_cost is None:
                    continue
                bought = unit_cost.amount * line.purchased_quantity
                if (
                    line.purchased_at is not None
                    and in_period(line.purchased_at, date_from, date_to)
                ):
                    cash_out += bought
                remaining_qty = line.quantity.value - line.purchased_quantity
                if remaining_qty > 0:
                    pending += unit_cost.amount * remaining_qty

        return CashFlowReportRead(
            cash_in=q2(cash_in),
            cash_out=q2(cash_out),
            refunded=q2(refunded),
            net=q2(cash_in - cash_out - refunded),
            pending_purchase_cost=q2(pending),
        )
