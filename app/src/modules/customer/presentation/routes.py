from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.customer.application.commands.create_customer import CreateCustomer
from src.modules.customer.application.commands.update_customer import UpdateCustomer
from src.modules.customer.application.dto.customer import (
    CreateCustomerInput,
    CustomerRead,
    UpdateCustomerInput,
)
from src.modules.customer.application.queries.get_customer import GetCustomer
from src.modules.customer.application.queries.list_customers import ListCustomers
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.customer.presentation.dependencies import get_customer_repository
from src.shared.domain.base import DomainError

router = APIRouter(prefix="/customers", tags=["customer"])


def _parse_customer_id(customer_id: str) -> CustomerId:
    """Parse a path customer id, mapping bad input to 404."""
    try:
        return CustomerId.from_string(customer_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=CustomerRead, status_code=201)
async def create_customer(
    inp: CreateCustomerInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractCustomerRepository = Depends(get_customer_repository),
) -> CustomerRead:
    return await CreateCustomer(repo).execute(current_user.organization_id, inp)


@router.get("", response_model=list[CustomerRead])
async def list_customers(
    search: str | None = None,
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    repo: AbstractCustomerRepository = Depends(get_customer_repository),
) -> list[CustomerRead]:
    return await ListCustomers(repo).execute(
        current_user.organization_id,
        search=search,
        active_only=not include_inactive,
    )


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractCustomerRepository = Depends(get_customer_repository),
) -> CustomerRead:
    read = await GetCustomer(repo).execute(
        current_user.organization_id, _parse_customer_id(customer_id)
    )
    if read is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found."
        )
    return read


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: str,
    inp: UpdateCustomerInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractCustomerRepository = Depends(get_customer_repository),
) -> CustomerRead:
    return await UpdateCustomer(repo).execute(
        current_user.organization_id, _parse_customer_id(customer_id), inp
    )
