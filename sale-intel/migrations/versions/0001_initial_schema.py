"""initial schema: all 12 tables

Revision ID: 0001
Revises:
Create Date: 2026-07-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts():
    return [
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    ]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('sources',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('base_url', sa.String(512), nullable=False),
        sa.Column('crawl_type', sa.String(64), nullable=False),
        sa.Column('crawl_interval_minutes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        *_ts(),
    )

    op.create_table('raw_snapshots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('url', sa.String(1024), nullable=False),
        sa.Column('content_type', sa.String(128), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('parser_version', sa.String(64), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_raw_snapshots_source_collected', 'raw_snapshots', ['source_id', 'collected_at'])

    op.create_table('products',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('external_product_id', sa.String(128), nullable=True),
        sa.Column('name', sa.String(512), nullable=False),
        sa.Column('brand', sa.String(255), nullable=True),
        sa.Column('category', sa.String(255), nullable=True),
        sa.Column('url', sa.String(1024), nullable=False),
        sa.Column('url_hash', sa.String(64), nullable=False),
        sa.Column('image_url', sa.String(1024), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('stock_status', sa.String(32), nullable=True),
        sa.Column('raw_metadata', JSONB(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        *_ts(),
        sa.UniqueConstraint('source_id', 'url_hash', name='uq_products_source_url'),
    )

    op.create_table('promotions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('title', sa.String(512), nullable=False),
        sa.Column('promotion_type', sa.String(32), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('code', sa.String(64), nullable=True),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('condition_text', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(1024), nullable=True),
        sa.Column('conditions', JSONB(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        *_ts(),
        sa.UniqueConstraint('source_id', 'content_hash', name='uq_promotions_source_hash'),
    )

    op.create_table('product_offers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('promotion_id', UUID(as_uuid=True), sa.ForeignKey('promotions.id'), nullable=True),
        sa.Column('offer_type', sa.String(32), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )
    op.create_index('ix_product_offers_product_id', 'product_offers', ['product_id'])

    op.create_table('price_snapshots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('original_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('current_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('discount_percent', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_price_snapshots_product_collected', 'price_snapshots', ['product_id', 'collected_at'])

    op.create_table('promotion_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('promotion_id', UUID(as_uuid=True), sa.ForeignKey('promotions.id'), nullable=False),
        sa.Column('rule_type', sa.String(64), nullable=False),
        sa.Column('rule_config', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_promotion_rules_promotion_id', 'promotion_rules', ['promotion_id'])

    op.create_table('coupons',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('code', sa.String(64), nullable=True),
        sa.Column('discount_type', sa.String(32), nullable=True),
        sa.Column('discount_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('min_order_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('max_discount_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('condition_text', sa.Text(), nullable=True),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_url', sa.String(1024), nullable=True),
        sa.Column('raw_metadata', JSONB(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        *_ts(),
        sa.UniqueConstraint('source_id', 'content_hash', name='uq_coupons_source_hash'),
    )

    op.create_table('crawl_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('entrypoint', sa.String(64), nullable=False),
        sa.Column('url', sa.String(1024), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('snapshot_id', UUID(as_uuid=True), sa.ForeignKey('raw_snapshots.id'), nullable=True),
        sa.Column('stats', JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_crawl_jobs_source_created', 'crawl_jobs', ['source_id', 'created_at'])

    op.create_table('deal_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', sa.String(64), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('event_type', sa.String(32), nullable=False),
        sa.Column('old_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('new_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('discount_percent', sa.Float(), nullable=True),
        sa.Column('payload', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_deal_events_source_created', 'deal_events', ['source_id', 'created_at'])

    op.create_table('alert_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('rule_type', sa.String(64), nullable=False),
        sa.Column('config', JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        *_ts(),
    )

    op.create_table('alert_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('alert_rule_id', UUID(as_uuid=True), sa.ForeignKey('alert_rules.id'), nullable=False),
        sa.Column('deal_event_id', UUID(as_uuid=True), sa.ForeignKey('deal_events.id'), nullable=False),
        sa.Column('channel', sa.String(32), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    for table in (
        'alert_logs', 'alert_rules', 'deal_events', 'crawl_jobs', 'coupons',
        'promotion_rules', 'price_snapshots', 'product_offers', 'promotions',
        'products', 'raw_snapshots', 'sources',
    ):
        op.drop_table(table)
