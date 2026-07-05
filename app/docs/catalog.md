# Catalog

The **Catalog** module manages a tenant's **product master data** — the items an
organization can offer. It is **JWT-authenticated**, **tenant-scoped**, and uses
**soft-delete**.

> **Pricing is not here.** In this pre-order system a product has **no fixed
> price** — price depends on the sale round. Pricing lives in the
> [Campaign](campaign.md) module, on a `CampaignProduct`. A `Product` only
> describes *what* the item is.

Module location: `src/modules/catalog/`

---

## 1. Concepts

| Concept | Meaning |
|---|---|
| **Tenant** | An organization. Every product belongs to exactly one tenant (`organization_id`), taken from the authenticated user's JWT. |
| **Product** | An item: a tenant-unique `code`, `name`, `description`, and an `active` flag. No price. |
| **Code** | A short, tenant-unique product identifier (e.g. `AO-01`). Not called "SKU" — this isn't inventory. |
| **Soft-delete** | Deactivating a product (`active = false`). Deactivated products are hidden from the default list but remain and can be reactivated. Never hard-deleted. |

Depends on: [`authenticate`](#) (`get_current_user`, `User`/`OrganizationId`) and `organization` (the tenant).

---

## 2. Domain model

### Product aggregate (`domain/entities/product.py`)

```
Product
  id              ProductId        (UUID, immutable)
  organization_id OrganizationId   (tenant, immutable)
  code            ProductCode      (immutable)
  name            ProductName      (mutable)
  description     Description      (mutable)
  active          bool             (mutable; default true)
  created_at      datetime         (DB-managed)
  updated_at      datetime         (DB-managed)
```

Mutation methods (idempotent, refresh `updated_at`): `rename`,
`change_description`, `activate`, `deactivate`. `id`, `organization_id`, `code`
are immutable.

### Value objects (`domain/value_objects/product.py`)

| Value object | Type | Constraints |
|---|---|---|
| `ProductId` | `uuid.UUID` | UUID; `generate()` / `from_string()`. |
| `ProductCode` | `str` | 1–64 chars, `^[A-Za-z0-9_-]+$`; whitespace stripped. |
| `ProductName` | `str` | 1–255 chars. |
| `Description` | `str` | 0–1000 chars (may be empty). |

All validate in `__post_init__` and raise `DomainError` (→ HTTP 400).

---

## 3. Architecture (DDD layers)

Same layering as the other modules (presentation → application → domain; infrastructure implements domain ports).

| Layer | File | Responsibility |
|---|---|---|
| Domain | `domain/value_objects/product.py` | `ProductId`, `ProductCode`, `ProductName`, `Description` |
| Domain | `domain/entities/product.py` | `Product` aggregate |
| Domain | `domain/repository.py` | `AbstractProductRepository` — persistence port (tenant-aware) |
| Application | `application/exceptions.py` | `ProductNotFoundError`, `ProductCodeAlreadyExistsError` |
| Application | `application/dto/product.py` | `CreateProductInput`, `UpdateProductInput`, `ProductRead` |
| Application | `application/commands/{create,update}_product.py` | use cases |
| Application | `application/queries/{get,list}_product{s}.py` | queries |
| Infrastructure | `infrastructure/models.py` | `ProductModel` (table `products`) |
| Infrastructure | `infrastructure/mappers.py` | entity ↔ model |
| Infrastructure | `infrastructure/repository.py` | `SqlAlchemyProductRepository` |
| Presentation | `presentation/dependencies.py` · `routes.py` | DI + routes |

**Request flow:** `get_current_user` → tenant (`organization_id`) →
`get_product_repository` (request `AsyncSession`) → use case → repository
(`flush` only). `get_session` is the single commit boundary (unit-of-work per
request). The repository qualifies every read/write by `organization_id`.

---

## 4. API reference

**Base path:** `/catalog` · **Auth:** `Authorization: Bearer <token>` on every endpoint.

### Create a product — `POST /catalog/products` → `201`
```json
{ "code": "AO-01", "name": "Áo thun", "description": "Cotton tee" }
```
- `code` *(required)* tenant-unique · `name` *(required)* · `description` *(optional, default `""`)*.

### List products — `GET /catalog/products?include_inactive=false` → `200`
Returns `ProductRead[]` (sorted by name). `include_inactive=true` includes deactivated products.

### Get a product — `GET /catalog/products/{id}` → `200` / `404`

### Update a product — `PATCH /catalog/products/{id}` → `200` / `404`
All fields optional: `name`, `description`, `active` (`false` = soft-delete, `true` = reactivate). `code` is immutable.

### `ProductRead`
`id, organization_id, code, name, description, active, created_at, updated_at` (no `price`).

### Error reference

| Status | When |
|---|---|
| `400` | Domain rule violation (bad code format, name/description length). |
| `401` | Missing/invalid bearer token. |
| `404` | Product id not found in the caller's tenant (or not a UUID). |
| `409` | `code` already used in the tenant on create. |
| `422` | Body schema validation failure. |

---

## 5. Data model

Table `products` (migration `b8f2a1c04e91`): `id` UUID PK, `organization_id` UUID FK→`organizations.id`, `code` varchar(64), `name` varchar(255), `description` varchar(1000) default `''`, `active` boolean default true, `created_at`/`updated_at` timestamptz. Unique index `uq_products_org_code` on `(organization_id, code)` — **code is unique per tenant**, so the same code may exist in different organizations.

---

## 6. Tenant isolation

Enforced at the repository: every `AbstractProductRepository` method takes `OrganizationId`. A tenant never sees another tenant's products; `GET`/`PATCH` of another tenant's product id returns `404` (IDOR-safe). The tenant always comes from the JWT, never the request body.

---

## 7. Setup & running

```bash
uv run alembic upgrade head
uv run python scripts/seed_user.py    # Default org / admin@example.com / admin12345
uv run uvicorn src.main:app --reload
```
Interactive docs at `http://localhost:8000/docs`.

---

## 8. Design decisions

- **No price on Product.** Price varies by sale round → lives on `CampaignProduct` (see [Campaign](campaign.md)).
- **`code`, not `SKU`.** Pre-order is not inventory; "Stock-Keeping Unit" is the wrong term, but a stable per-tenant code is still needed (one product spans many rounds).
- **Soft-delete only** (no `DELETE`); `active` is the lifecycle flag.
- **Per-tenant code uniqueness** (not global).
- **Validation in the domain** (value objects), surfaced as HTTP 400.
