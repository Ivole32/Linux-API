"""user auto child trigger

Revision ID: 37abce9a74cb
Revises: f71c56d56452
Create Date: 2026-02-04 19:59:00.909178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37abce9a74cb'
down_revision: Union[str, Sequence[str], None] = 'f71c56d56452'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.execute("""
    CREATE OR REPLACE FUNCTION users.create_user_children()
    RETURNS trigger AS $$
    BEGIN
        INSERT INTO users.user_perm (user_id)
        VALUES (NEW.user_id);

        INSERT INTO users.user_auth (user_id)
        VALUES (NEW.user_id);

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trg_create_user_children
    AFTER INSERT ON users.user
    FOR EACH ROW
    EXECUTE FUNCTION users.create_user_children();
    """)


def downgrade():

    op.execute("""
    DROP TRIGGER IF EXISTS trg_create_user_children ON users.user;
    """)

    op.execute("""
    DROP FUNCTION IF EXISTS users.create_user_children;
    """)