"""make first admin immutable by default

Revision ID: c37fe0d02922
Revises: e6519d238a1b
Create Date: 2026-02-15 02:15:50.071412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c37fe0d02922'
down_revision: Union[str, Sequence[str], None] = 'e6519d238a1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        UPDATE users."user"
        SET immutable = TRUE
        WHERE username = 'admin';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        UPDATE users."user"
        SET immutable = FALSE
        WHERE username = 'admin';
    """)