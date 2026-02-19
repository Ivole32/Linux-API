"""fixed error with user child creation in user_auth

Revision ID: f84c0e0cdb7e
Revises: 37abce9a74cb
Create Date: 2026-02-04 20:08:06.573186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f84c0e0cdb7e'
down_revision: Union[str, Sequence[str], None] = '37abce9a74cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Upgarde schema."""
    op.alter_column(
        "user_auth",
        "api_key_hash",
        schema="users",
        existing_type=op.get_bind().dialect.type_descriptor(
            __import__("sqlalchemy").String()
        ),
        nullable=True
    )


def downgrade():
    """Downgrade schema."""
    op.alter_column(
        "user_auth",
        "api_key_hash",
        schema="users",
        existing_type=op.get_bind().dialect.type_descriptor(
            __import__("sqlalchemy").String()
        ),
        nullable=False
    )