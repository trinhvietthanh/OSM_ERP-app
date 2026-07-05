# Campaign (sale rounds & per-round pricing)

The **Campaign** module implements the pre-order **pricing model**. Because this
is a group-buy / pre-order system (gộp đơn / chia đơn), **a product has no fixed
price** — its price and deposit depend on the **sale round** (đợt sale) it is
offered in. The same product can be offered in multiple rounds at different
prices.

> Price lives **here**, on a `CampaignProduct` — never on a `Product`
> (see [Catalog](catalog.md)).

Module location: `src/modules/campaign/`

---

## 1. Concepts

| Concept | Meaning |
|---|---|
| **SaleRound** ("đợt sale") | A pre-order campaign that groups the products offered together for a period. Belongs to a tenant. |
| **CampaignProduct** | A product *offered in a specific round*, with that round's **price** and **deposit**. This is where money lives. |
| **Per-round pricing** | One product × N rounds = N `CampaignProduct` rows, each with its own price/deposit. |
| **Money** | A non-negative `Decimal` value object; used for both `price` and `deposit`. Currency is an org-level concern (out of scope). |

Depends on: [`authenticate`](#) (`get_current_user`), `organization` (tenant), and [`catalog`](catalog.md) (`Product`, `ProductId`).

---

## 2. Domain model

### SaleRound (`domain/entities/sale_round.py`)
```
SaleRound
  id              SaleRoundId    (UUID, immutable)
  organization_id OrganizationId (tenant, immutable)
  code            RoundCode      (immutable)   e.g. "T6-2026"
  name            RoundName      (mutable)
  status          RoundStatus    (mutable)     draft | open | closed  (default draft)
  opens_at        datetime?      (mutable)
  closes_at       datetime?      (mutable)
  created_at / updated_at        (DB-managed)
```
Methods: `rename`, `change_status`, `set_opens_at`, `set_closes_at`.

### CampaignProduct (`domain/entities/campaign_product.py`)
```
CampaignProduct
  id              CampaignProductId (UUID, immutable)
  organization_id OrganizationId    (tenant, denormalized — immutable)
  sale_round_id   SaleRoundId       (immutable)
  product_id      ProductId         (immutable)
  price           Money             (mutable)
  deposit         Money             (mutable)
  created_at / updated_at           (DB-managed)
```
Methods: `change_price`, `change_deposit`.

### Value objects
`SaleRoundId`, `RoundCode` (`^[A-Za-z0-9._/-]+$`, 1–64), `RoundName` (1–255),
`RoundStatus` (enum), `CampaignProductId`, `Money` (`Decimal`, `>= 0`). All raise
`DomainError` → HTTP 400 on violation.

---

## 3. Architecture

Two aggregates in one bounded context, same DDD layering.

| Layer | File | Contains |
|---|---|---|
| Domain | `domain/value_objects/{sale_round,campaign_product}.py` | VOs + `RoundStatus` + `Money` |
| Domain | `domain/entities/{sale_round,campaign_product}.py` | aggregates |
| Domain | `domain/repository.py` | `AbstractSaleRoundRepository`, `AbstractCampaignProductRepository` (both tenant-scoped) |
| Application | `application/exceptions.py` | `SaleRoundNotFoundError`, `SaleRoundCodeAlreadyExistsError`, `CampaignProductNotFoundError`, `CampaignProductAlreadyExistsError` |
| Application | `application/dto/{sale_round,campaign_product}.py` | inputs + read models |
| Application | `application/commands/*` · `application/queries/*` | use cases (create/update/get/list ×2) |
| Infrastructure | `infrastructure/models.py` · `mappers.py` · `repository.py` | `SaleRoundModel`, `CampaignProductModel`, mappers, two `SqlAlchemy` repos |
| Presentation | `presentation/dependencies.py` · `routes.py` | DI + routes |

**Request flow:** `get_current_user` → tenant → repos (request `AsyncSession`) →
use case → repos (`flush` only); `get_session` commits. `CreateCampaignProduct`
injects **three** repos (campaign_products, sale_rounds, products) to verify the
round and product both belong to the caller's tenant before creating the offering.

---

## 4. API reference

**Base path:** `/campaign` · **Auth:** bearer token required everywhere.

### Sale rounds
| Method | Path | Notes |
|---|---|---|
| `POST` | `/rounds` | `{code, name}` → `201` `SaleRoundRead` (status starts `draft`). |
| `GET` | `/rounds` | List the tenant's rounds, newest first. |
| `GET` | `/rounds/{round_id}` | → `200` / `404`. |
| `PATCH` | `/rounds/{round_id}` | Partial: `{name?, status?, opens_at?, closes_at?}`. `status` ∈ `draft|open|closed`. |

### Campaign products (offerings in a round)
| Method | Path | Notes |
|---|---|---|
| `POST` | `/rounds/{round_id}/products` | `{product_id, price, deposit}` → `201`. Verifies round+product are in the tenant; rejects duplicates. |
| `GET` | `/rounds/{round_id}/products` | List the round's offerings. |
| `GET` | `/rounds/{round_id}/products/{id}` | → `200` / `404` (must belong to the path round). |
| `PATCH` | `/rounds/{round_id}/products/{id}` | Partial: `{price?, deposit?}`. |

`price`/`deposit` are sent and returned as **strings** (e.g. `"150.00"`) to
preserve decimal precision.

### Example: same product, two rounds, two prices
```bash
PID=$(curl -s -XPOST localhost:8000/catalog/products -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d '{"code":"AO-01","name":"Áo thun"}' | jq -r .id)

R6=$(curl -s -XPOST localhost:8000/campaign/rounds -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d '{"code":"T6-2026","name":"Đợt 6"}' | jq -r .id)
R7=$(curl -s -XPOST localhost:8000/campaign/rounds -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d '{"code":"T7-2026","name":"Đợt 7"}' | jq -r .id)

# same product, different price per round
curl -s -XPOST localhost:8000/campaign/rounds/$R6/products -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d "{\"product_id\":\"$PID\",\"price\":\"150.00\",\"deposit\":\"50.00\"}"
curl -s -XPOST localhost:8000/campaign/rounds/$R7/products -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d "{\"product_id\":\"$PID\",\"price\":\"140.00\",\"deposit\":\"40.00\"}"
```

### Error reference
| Status | When |
|---|---|
| `400` | Domain rule violation (negative price/deposit, bad code, invalid status). |
| `401` | Missing/invalid token. |
| `404` | Round / campaign product / product not found in the caller's tenant, or bad path id. |
| `409` | Duplicate round code, or product already offered in the round. |
| `422` | Body schema validation failure. |

---

## 5. Data model (migration `d3a1f9c20b57`)

**`sale_rounds`**: `id` UUID PK, `organization_id` FK→organizations, `code` varchar(64), `name` varchar(255), `status` enum `round_status` (`draft|open|closed`), `opens_at`/`closes_at` timestamptz nullable, timestamps. Unique `uq_sale_rounds_org_code (organization_id, code)`.

**`campaign_products`**: `id` UUID PK, `organization_id` FK→organizations (**denormalized**), `sale_round_id` FK→sale_rounds, `product_id` FK→products, `price` numeric(12,2), `deposit` numeric(12,2), timestamps. Unique `uq_campaign_products_round_product (sale_round_id, product_id)`.

`organization_id` is denormalized onto `campaign_products` so offerings can be
scoped by tenant without a join (it always equals the round's and product's
tenant).

---

## 6. Tenant isolation

Both repositories scope by `organization_id` (on the round directly; denormalized
on each offering). A tenant cannot see or mutate another tenant's rounds or
offerings; cross-tenant access by guessed id returns `404`. The tenant always
comes from the JWT.

---

## 7. Design decisions

- **Price on CampaignProduct, not Product.** The whole point — price varies by round.
- **Denormalized `organization_id`** on offerings for direct, join-free tenant scoping.
- **One product per round** (`unique(sale_round_id, product_id)`); the same product may appear in many rounds.
- **MVP `RoundStatus`: `draft | open | closed`.** Richer lifecycle (ordered / arrived / distributing) deferred until the order/fulfillment modules exist.
- **`Money` VO** shared by price and deposit; no currency (org-level concern).

---

## 8. Roadmap (not built yet)

- **PreOrder** — a customer's reservation in a round (references `CampaignProduct`). **gộp đơn**: aggregating a round's pre-orders into a bulk purchase order to the supplier.
- **Allocation** — **chia đơn**: splitting arrived stock back to pre-orders for fulfillment.
- **Price tiers** — volume pricing resolved at round close from aggregated quantity.
- **Deposits on orders** — deposit policy per round/product applied to pre-orders.
