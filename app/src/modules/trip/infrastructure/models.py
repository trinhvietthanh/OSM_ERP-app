import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base, TimestampMixin
from src.modules.trip.domain.value_objects.trip import TripStatus


class TripModel(Base, TimestampMixin):
    """Persistence model for the Trip aggregate (table: trips).

    Orders reference a trip via ``orders.trip_id`` (nullable FK); the trip row
    itself carries no order list.
    """

    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_trips_org_code"),
        Index("ix_trips_org_status", "organization_id", "status"),
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
    status: Mapped[TripStatus] = mapped_column(
        SAEnum(
            TripStatus,
            name="trip_status",
            values_callable=lambda statuses: [s.value for s in statuses],
        ),
        nullable=False,
        default=TripStatus.PLANNING,
    )
    shopper_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    departure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
