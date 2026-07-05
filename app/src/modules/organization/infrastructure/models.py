import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base, TimestampMixin
from src.modules.organization.domain.value_objects.organization import OrganizationStatus


class OrganizationModel(Base, TimestampMixin):
    """Persistence model for the Organization aggregate (table: organizations)."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OrganizationStatus] = mapped_column(
        SAEnum(
            OrganizationStatus,
            name="organization_status",
            values_callable=lambda statuses: [s.value for s in statuses],
        ),
        nullable=False,
        default=OrganizationStatus.ACTIVE,
    )
