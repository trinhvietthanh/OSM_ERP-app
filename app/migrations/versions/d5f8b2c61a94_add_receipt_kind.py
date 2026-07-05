"""add kind (collection/refund) to order_receipts

Revision ID: d5f8b2c61a94
Revises: c9e6a3d47b18
Create Date: 2026-07-02 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f8b2c61a94'
down_revision: Union[str, Sequence[str], None] = 'c9e6a3d47b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

receipt_kind = sa.Enum('collection', 'refund', name='receipt_kind')


def upgrade() -> None:
    """Upgrade schema."""
    receipt_kind.create(op.get_bind(), checkfirst=False)
    op.add_column(
        'order_receipts',
        sa.Column(
            'kind',
            receipt_kind,
            nullable=False,
            server_default='collection',
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('order_receipts', 'kind')
    receipt_kind.drop(op.get_bind(), checkfirst=False)
