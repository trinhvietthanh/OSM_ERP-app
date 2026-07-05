import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base, TimestampMixin
from src.modules.campaign.domain.value_objects.sale_round import RoundStatus


class SaleRoundModel(Base, TimestampMixin):
    """Persistence model for the SaleRound aggregate (table: sale_rounds)."""

    __tablename__ = "sale_rounds"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_sale_rounds_org_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[RoundStatus] = mapped_column(
        SAEnum(
            RoundStatus,
            name="round_status",
            values_callable=lambda statuses: [s.value for s in statuses],
        ),
        nullable=False,
        default=RoundStatus.DRAFT,
    )
    opens_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closes_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CampaignProductModel(Base, TimestampMixin):
    """Persistence model for the CampaignProduct aggregate (table: campaign_products).

    ``organization_id`` is denormalized (equals the round's and product's
    tenant) so the repository can scope offerings directly by tenant.
    """

    __tablename__ = "campaign_products"
    __table_args__ = (
        UniqueConstraint(
            "sale_round_id", "product_id", name="uq_campaign_products_round_product"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    sale_round_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sale_rounds.id"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deposit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
