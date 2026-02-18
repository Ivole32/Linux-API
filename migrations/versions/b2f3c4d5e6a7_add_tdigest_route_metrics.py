"""add tdigest column to route_metrics

Revision ID: b2f3c4d5e6a7
Revises: cc082cfc30f5
Create Date: 2026-02-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f3c4d5e6a7'
down_revision: Union[str, Sequence[str], None] = 'cc082cfc30f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('route_metrics', sa.Column('tdigest', sa.LargeBinary(), nullable=True), schema='metrics')


def downgrade() -> None:
    op.drop_column('route_metrics', 'tdigest', schema='metrics')
