from datetime import UTC, date, datetime
from typing import Self

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.domain.value_objects.trip import (
    ALLOWED_TRIP_TRANSITIONS,
    TripCode,
    TripId,
    TripName,
    TripStatus,
)
from src.shared.domain.base import DomainError, Entity


class Trip(Entity[TripId]):
    """A buying trip ("chuyến hàng") that consolidates orders.

    Orders reference the trip via a nullable ``trip_id`` FK on their side —
    an order belongs to at most one trip. The shopper ("người xách tay") is
    free-text info on the trip, not a system user; the shop admin records
    purchases on their behalf. ``code`` and tenant are immutable.
    """

    def __init__(
        self,
        *,
        id_: TripId,
        organization_id: OrganizationId,
        code: TripCode,
        name: TripName,
        status: TripStatus = TripStatus.PLANNING,
        shopper_name: str = "",
        departure_date: date | None = None,
        arrival_date: date | None = None,
        note: str = "",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._code = code
        self._name = name
        self._status = status
        self._shopper_name = shopper_name
        self._departure_date = departure_date
        self._arrival_date = arrival_date
        self._note = note
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        code: TripCode,
        name: TripName,
        shopper_name: str = "",
        departure_date: date | None = None,
        arrival_date: date | None = None,
        note: str = "",
    ) -> Self:
        """Factory: create a new trip in PLANNING with a generated id."""
        return cls(
            id_=TripId.generate(),
            organization_id=organization_id,
            code=code,
            name=name,
            shopper_name=shopper_name,
            departure_date=departure_date,
            arrival_date=arrival_date,
            note=note,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def code(self) -> TripCode:
        return self._code

    @property
    def name(self) -> TripName:
        return self._name

    @property
    def status(self) -> TripStatus:
        return self._status

    @property
    def shopper_name(self) -> str:
        return self._shopper_name

    @property
    def departure_date(self) -> date | None:
        return self._departure_date

    @property
    def arrival_date(self) -> date | None:
        return self._arrival_date

    @property
    def note(self) -> str:
        return self._note

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def is_planning(self) -> bool:
        return self._status is TripStatus.PLANNING

    def rename(self, new_name: TripName) -> None:
        """Rename the trip. No-op if unchanged."""
        if new_name == self._name:
            return
        self._name = new_name
        self._touch()

    def change_status(self, new_status: TripStatus) -> None:
        """Advance the lifecycle. No-op if unchanged.

        :raises DomainError: if the transition is not allowed.
        """
        if new_status is self._status:
            return
        if new_status not in ALLOWED_TRIP_TRANSITIONS[self._status]:
            raise DomainError(
                f"Cannot change trip status from {self._status.value!r} "
                f"to {new_status.value!r}."
            )
        self._status = new_status
        self._touch()

    def change_shopper_name(self, shopper_name: str) -> None:
        """Set (or clear) the shopper's name. No-op if unchanged."""
        if shopper_name == self._shopper_name:
            return
        self._shopper_name = shopper_name
        self._touch()

    def set_departure_date(self, departure_date: date | None) -> None:
        """Set (or clear) the departure date. No-op if unchanged."""
        if departure_date == self._departure_date:
            return
        self._departure_date = departure_date
        self._touch()

    def set_arrival_date(self, arrival_date: date | None) -> None:
        """Set (or clear) the arrival date. No-op if unchanged."""
        if arrival_date == self._arrival_date:
            return
        self._arrival_date = arrival_date
        self._touch()

    def change_note(self, new_note: str) -> None:
        """Replace the free-text note. No-op if unchanged."""
        if new_note == self._note:
            return
        self._note = new_note
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
