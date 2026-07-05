from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.presentation.dependencies import get_current_user
from src.modules.campaign.application.commands.create_campaign_product import (
    CreateCampaignProduct,
)
from src.modules.campaign.application.commands.create_sale_round import (
    CreateSaleRound,
)
from src.modules.campaign.application.commands.update_campaign_product import (
    UpdateCampaignProduct,
)
from src.modules.campaign.application.commands.update_sale_round import (
    UpdateSaleRound,
)
from src.modules.campaign.application.dto.campaign_product import (
    CampaignProductRead,
    CreateCampaignProductInput,
    UpdateCampaignProductInput,
)
from src.modules.campaign.application.dto.sale_round import (
    CreateSaleRoundInput,
    SaleRoundRead,
    UpdateSaleRoundInput,
)
from src.modules.campaign.application.queries.get_campaign_product import (
    GetCampaignProduct,
)
from src.modules.campaign.application.queries.get_sale_round import GetSaleRound
from src.modules.campaign.application.queries.list_campaign_products import (
    ListCampaignProducts,
)
from src.modules.campaign.application.queries.list_sale_rounds import (
    ListSaleRounds,
)
from src.modules.campaign.domain.repository import (
    AbstractCampaignProductRepository,
    AbstractSaleRoundRepository,
)
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
)
from src.modules.campaign.domain.value_objects.sale_round import SaleRoundId
from src.modules.campaign.presentation.dependencies import (
    get_campaign_product_repository,
    get_sale_round_repository,
)
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.presentation.dependencies import get_product_repository
from src.shared.domain.base import DomainError

router = APIRouter(prefix="/campaign", tags=["campaign"])


def _parse_round_id(round_id: str) -> SaleRoundId:
    """Parse a path round id, mapping bad input to 404."""
    try:
        return SaleRoundId.from_string(round_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _parse_campaign_product_id(campaign_product_id: str) -> CampaignProductId:
    """Parse a path campaign-product id, mapping bad input to 404."""
    try:
        return CampaignProductId.from_string(campaign_product_id)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------- Sale rounds ----------------


@router.post("/rounds", response_model=SaleRoundRead, status_code=201)
async def create_round(
    inp: CreateSaleRoundInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractSaleRoundRepository = Depends(get_sale_round_repository),
) -> SaleRoundRead:
    return await CreateSaleRound(repo).execute(current_user.organization_id, inp)


@router.get("/rounds", response_model=list[SaleRoundRead])
async def list_rounds(
    current_user: User = Depends(get_current_user),
    repo: AbstractSaleRoundRepository = Depends(get_sale_round_repository),
) -> list[SaleRoundRead]:
    return await ListSaleRounds(repo).execute(current_user.organization_id)


@router.get("/rounds/{round_id}", response_model=SaleRoundRead)
async def get_round(
    round_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractSaleRoundRepository = Depends(get_sale_round_repository),
) -> SaleRoundRead:
    read = await GetSaleRound(repo).execute(
        current_user.organization_id, _parse_round_id(round_id)
    )
    if read is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sale round not found."
        )
    return read


@router.patch("/rounds/{round_id}", response_model=SaleRoundRead)
async def update_round(
    round_id: str,
    inp: UpdateSaleRoundInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractSaleRoundRepository = Depends(get_sale_round_repository),
) -> SaleRoundRead:
    return await UpdateSaleRound(repo).execute(
        current_user.organization_id, _parse_round_id(round_id), inp
    )


# ---------------- Campaign products (offerings in a round) ----------------


@router.post(
    "/rounds/{round_id}/products",
    response_model=CampaignProductRead,
    status_code=201,
)
async def create_campaign_product(
    round_id: str,
    inp: CreateCampaignProductInput,
    current_user: User = Depends(get_current_user),
    campaign_products: AbstractCampaignProductRepository = Depends(
        get_campaign_product_repository
    ),
    sale_rounds: AbstractSaleRoundRepository = Depends(get_sale_round_repository),
    products: AbstractProductRepository = Depends(get_product_repository),
) -> CampaignProductRead:
    return await CreateCampaignProduct(
        campaign_products, sale_rounds, products
    ).execute(current_user.organization_id, _parse_round_id(round_id), inp)


@router.get(
    "/rounds/{round_id}/products", response_model=list[CampaignProductRead]
)
async def list_campaign_products(
    round_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractCampaignProductRepository = Depends(
        get_campaign_product_repository
    ),
) -> list[CampaignProductRead]:
    return await ListCampaignProducts(repo).execute(
        current_user.organization_id, _parse_round_id(round_id)
    )


@router.get(
    "/rounds/{round_id}/products/{campaign_product_id}",
    response_model=CampaignProductRead,
)
async def get_campaign_product(
    round_id: str,
    campaign_product_id: str,
    current_user: User = Depends(get_current_user),
    repo: AbstractCampaignProductRepository = Depends(
        get_campaign_product_repository
    ),
) -> CampaignProductRead:
    rid = _parse_round_id(round_id)
    read = await GetCampaignProduct(repo).execute(
        current_user.organization_id, _parse_campaign_product_id(campaign_product_id)
    )
    if read is None or read.sale_round_id != rid.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign product not found.",
        )
    return read


@router.patch(
    "/rounds/{round_id}/products/{campaign_product_id}",
    response_model=CampaignProductRead,
)
async def update_campaign_product(
    round_id: str,
    campaign_product_id: str,
    inp: UpdateCampaignProductInput,
    current_user: User = Depends(get_current_user),
    repo: AbstractCampaignProductRepository = Depends(
        get_campaign_product_repository
    ),
) -> CampaignProductRead:
    rid = _parse_round_id(round_id)
    cp_id = _parse_campaign_product_id(campaign_product_id)
    existing = await GetCampaignProduct(repo).execute(
        current_user.organization_id, cp_id
    )
    if existing is None or existing.sale_round_id != rid.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign product not found.",
        )
    return await UpdateCampaignProduct(repo).execute(
        current_user.organization_id, cp_id, inp
    )
