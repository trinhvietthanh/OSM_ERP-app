from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.catalog.application.commands.create_product import CreateProduct
from src.modules.catalog.application.commands.update_product import UpdateProduct
from src.modules.catalog.application.dto.product import (
    CreateProductInput,
    ProductRead,
    UpdateProductInput,
)
from src.modules.catalog.application.queries.get_product import GetProduct
from src.modules.catalog.application.queries.list_products import ListProducts
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.catalog.presentation.dependencies import get_product_repository
from src.shared.domain.base import DomainError

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _parse_product_id(product_id: str) -> ProductId:
    """Parse a path product id, mapping bad input to a 404 (not a 400 leak)."""
    try:
        return ProductId.from_string(product_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/products", response_model=ProductRead, status_code=201)
async def create_product(
    inp: CreateProductInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractProductRepository = Depends(get_product_repository),
) -> ProductRead:
    return await CreateProduct(repo).execute(current_user.organization_id, inp)


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user),
    repo: AbstractProductRepository = Depends(get_product_repository),
) -> list[ProductRead]:
    return await ListProducts(repo).execute(
        current_user.organization_id, active_only=not include_inactive
    )


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractProductRepository = Depends(get_product_repository),
) -> ProductRead:
    read = await GetProduct(repo).execute(
        current_user.organization_id, _parse_product_id(product_id)
    )
    if read is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return read


@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: str,
    inp: UpdateProductInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractProductRepository = Depends(get_product_repository),
) -> ProductRead:
    return await UpdateProduct(repo).execute(
        current_user.organization_id, _parse_product_id(product_id), inp
    )
