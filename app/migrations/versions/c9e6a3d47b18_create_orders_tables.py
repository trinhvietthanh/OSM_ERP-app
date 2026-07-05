"""create orders, order_lines and order_receipts tables

Revision ID: c9e6a3d47b18
Revises: b7d2f5a81c43
Create Date: 2026-07-02 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e6a3d47b18'
down_revision: Union[str, Sequence[str], None] = 'b7d2f5a81c43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=True),
    sa.Column('tracking_code', sa.String(length=8), nullable=False),
    sa.Column('status', sa.Enum('pending', 'confirmed', 'purchasing', 'purchased', 'arrived', 'delivered', 'cancelled', name='order_status'), nullable=False),
    sa.Column('is_separate', sa.Boolean(), nullable=False),
    sa.Column('note', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.PrimaryKeyConstraint('id'),
    # Globally unique: the public tracking page resolves a code without a
    # tenant context.
    sa.UniqueConstraint('tracking_code', name='uq_orders_tracking_code')
    )
    op.create_index('ix_orders_org_status', 'orders', ['organization_id', 'status'])
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('ix_orders_trip_id', 'orders', ['trip_id'])

    op.create_table('order_lines',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('product_code', sa.String(length=64), nullable=False),
    sa.Column('product_name', sa.String(length=255), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('unit_deposit', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('purchased_quantity', sa.Integer(), nullable=False),
    sa.Column('actual_unit_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('purchased_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_order_lines_order_id', 'order_lines', ['order_id'])

    op.create_table('order_receipts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('method', sa.Enum('cash', 'bank_transfer', 'other', name='receipt_method'), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('note', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_order_receipts_order_id', 'order_receipts', ['order_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_order_receipts_order_id', table_name='order_receipts')
    op.drop_table('order_receipts')
    op.drop_index('ix_order_lines_order_id', table_name='order_lines')
    op.drop_table('order_lines')
    op.drop_index('ix_orders_trip_id', table_name='orders')
    op.drop_index('ix_orders_customer_id', table_name='orders')
    op.drop_index('ix_orders_org_status', table_name='orders')
    op.drop_table('orders')
    # create_table created the native enum types; drop_table leaves them orphaned.
    sa.Enum('pending', 'confirmed', 'purchasing', 'purchased', 'arrived', 'delivered', 'cancelled', name='order_status').drop(
        op.get_bind(), checkfirst=False
    )
    sa.Enum('cash', 'bank_transfer', 'other', name='receipt_method').drop(
        op.get_bind(), checkfirst=False
    )
