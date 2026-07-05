import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.postgres.base import Base, TimestampMixin
from src.modules.purchase.domain.value_objects.order import (
    OrderStatus,
    ReceiptKind,
    ReceiptMethod,
)


class OrderModel(Base, TimestampMixin):
    """Persistence model for the Order aggregate root (table: orders).

    ``tracking_code`` is globally unique (the public lookup page resolves it
    without a tenant context). ``trip_id`` is the nullable consolidation link.
    """

    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_org_status", "organization_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trips.id"),
        nullable=True,
        index=True,
    )
    tracking_code: Mapped[str] = mapped_column(
        String(8), nullable=False, unique=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(
            OrderStatus,
            name="order_status",
            values_callable=lambda statuses: [s.value for s in statuses],
        ),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    is_separate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    lines: Mapped[list["OrderLineModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderLineModel.created_at",
    )
    receipts: Mapped[list["OrderReceiptModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderReceiptModel.received_at",
    )


class OrderLineModel(Base, TimestampMixin):
    """Persistence model for order lines (table: order_lines).

    ``product_code``/``product_name`` are snapshots — no join back to the
    catalog is needed to render an order. No denormalized organization_id:
    lines are only ever reached through their order.
    """

    __tablename__ = "order_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_deposit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    purchased_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    actual_unit_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    purchased_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    order: Mapped[OrderModel] = relationship(back_populates="lines")


class OrderReceiptModel(Base, TimestampMixin):
    """Persistence model for payment receipts (table: order_receipts)."""

    __tablename__ = "order_receipts"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[ReceiptMethod] = mapped_column(
        SAEnum(
            ReceiptMethod,
            name="receipt_method",
            values_callable=lambda methods: [m.value for m in methods],
        ),
        nullable=False,
        default=ReceiptMethod.CASH,
    )
    kind: Mapped[ReceiptKind] = mapped_column(
        SAEnum(
            ReceiptKind,
            name="receipt_kind",
            values_callable=lambda kinds: [k.value for k in kinds],
        ),
        nullable=False,
        default=ReceiptKind.COLLECTION,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    order: Mapped[OrderModel] = relationship(back_populates="receipts")
