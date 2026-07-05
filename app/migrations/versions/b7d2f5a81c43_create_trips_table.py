"""create trips table

Revision ID: b7d2f5a81c43
Revises: a1c4e7b93f02
Create Date: 2026-07-02 17:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d2f5a81c43'
down_revision: Union[str, Sequence[str], None] = 'a1c4e7b93f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('trips',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('planning', 'buying', 'shipping', 'arrived', 'completed', 'cancelled', name='trip_status'), nullable=False),
    sa.Column('shopper_name', sa.String(length=255), nullable=False),
    sa.Column('departure_date', sa.Date(), nullable=True),
    sa.Column('arrival_date', sa.Date(), nullable=True),
    sa.Column('note', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'code', name='uq_trips_org_code')
    )
    op.create_index('ix_trips_org_status', 'trips', ['organization_id', 'status'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_trips_org_status', table_name='trips')
    op.drop_table('trips')
    # create_table created the native enum type; drop_table leaves it orphaned.
    sa.Enum('planning', 'buying', 'shipping', 'arrived', 'completed', 'cancelled', name='trip_status').drop(
        op.get_bind(), checkfirst=False
    )
