"""revert add tdigest column to route_metrics

Revision ID: 9743ea8d3047
Revises: b2f3c4d5e6a7
Create Date: 2026-02-18 19:33:42.255616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9743ea8d3047'
down_revision: Union[str, Sequence[str], None] = 'b2f3c4d5e6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('route_metrics', 'tdigest', schema='metrics')


def downgrade() -> None:
    op.add_column('route_metrics', sa.Column('tdigest', sa.LargeBinary(), nullable=True), schema='metrics')
