# PreOrder OMS

> **An open-source Order Management System built for Pre-order, Cross-border Shopping, and Personal Shopper businesses.**

PreOrder OMS is a modern SaaS-ready Order Management System (OMS) designed specifically for businesses that operate on a **pre-order** model rather than traditional inventory-based retail.

Unlike conventional POS or ERP systems, PreOrder OMS manages the complete lifecycle of a customer order—from request to final delivery—while handling deposits, grouped purchases, international shipping, and profit calculation.

---

## ✨ Why PreOrder OMS?

Most existing ERP and POS solutions are designed for businesses that maintain inventory.

However, thousands of online shops operate differently:

* Customers place orders before products are purchased.
* Products are sourced during flash sales or promotional campaigns.
* Multiple customer orders are consolidated into a single purchase.
* Goods are transported internationally through freight forwarders or personal shoppers.
* Profit depends on exchange rates, shipping costs, service fees, and purchasing efficiency.

PreOrder OMS is purpose-built for this business model.

---

# Core Features

### Order Management

Manage the complete lifecycle of customer orders.

* Customer Orders
* Order Timeline
* Status Tracking
* Order History
* Bulk Operations

---

### Purchase Planning

Group multiple customer orders into purchase batches.

* Purchase Batch
* Flash Sale Planning
* Coupon Management
* Cashback Tracking
* Buyer Assignment

---

### Shipment Tracking

Track products throughout the logistics process.

* Domestic Shipping
* International Shipping
* Freight Tracking
* Delivery Status
* Shipment Timeline

---

### Financial Management

Understand your real business performance.

* Deposit Management
* Remaining Payments
* Cost Allocation
* Shipping Cost
* Profit Calculation
* Exchange Rate Support

---

### Customer Management

Build long-term customer relationships.

* Customer Profiles
* Order History
* Notes
* Contact Information

---

### Reporting

Monitor business performance through dashboards.

* Revenue
* Profit
* Pending Orders
* Purchase Status
* Delivery Performance

---

# Built for

PreOrder OMS is designed for businesses such as:

* Cross-border shopping services
* Personal shopper businesses
* Flash sale agencies
* International order services
* Overseas product sourcing
* Hand-carry (personal luggage) businesses
* Small and medium-sized e-commerce operations

---

# Product Philosophy

We believe managing a pre-order business is fundamentally different from managing inventory.

Instead of focusing on stock, we focus on the lifecycle of an order.

```
Customer Order
        │
        ▼
Deposit Received
        │
        ▼
Purchase Planning
        │
        ▼
Purchase Batch
        │
        ▼
Domestic Shipping
        │
        ▼
International Shipping
        │
        ▼
Delivery
        │
        ▼
Completed
```

Business workflow should drive software design—not database tables.

---

# Architecture

The project follows modern software engineering principles.

* Domain-Driven Design (DDD)
* Clean Architecture
* Modular Monolith
* API First
* Multi-Tenant Ready
* Event-Driven Friendly

Each business capability is implemented as an independent module with clear boundaries.

---

# Planned Modules

## Core

* Identity
* Organization
* Customer
* Catalog
* Order
* Purchase
* Shipment
* Finance
* Notification

## Future

* Deal Management
* Supplier Management
* Pricing Engine
* Trip Management
* CRM
* Analytics
* AI Assistant
* Marketplace Integration

---

# Technology Stack

## Backend

* FastAPI
* SQLAlchemy 2.x
* PostgreSQL
* Redis
* Alembic
* Pydantic

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui

## Infrastructure

* Docker
* Cloudflare R2 / Amazon S3
* GitHub Actions

---

# Design Principles

* Business-first architecture
* Domain-oriented modules
* Minimal dependencies
* API-first development
* Multi-tenant by design
* Developer-friendly
* Scalable and maintainable

---

# Roadmap

### Phase 1

* Order Management
* Purchase Management
* Shipment Tracking
* Customer Management
* Finance Dashboard

### Phase 2

* Deal Management
* Supplier Portal
* Pricing Engine
* Advanced Reporting

### Phase 3

* AI Assistant
* Workflow Automation
* Mobile Application
* Public API
* Marketplace Integration

---

