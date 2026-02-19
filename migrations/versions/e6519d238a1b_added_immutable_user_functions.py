"""added immutable user functions

Revision ID: e6519d238a1b
Revises: 29d2e30dee1b
Create Date: 2026-02-15 02:08:52.785903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6519d238a1b'
down_revision: Union[str, Sequence[str], None] = '29d2e30dee1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION users.prevent_immutable_user_change()
        RETURNS trigger AS $$
        DECLARE
            is_immutable BOOLEAN;
        BEGIN
            -- Check if user is immutable
            SELECT immutable INTO is_immutable
            FROM users.user
            WHERE user_id = COALESCE(OLD.user_id, NEW.user_id);

            IF is_immutable THEN
                RAISE EXCEPTION 'Immutable user cannot be modified or deleted'
                USING ERRCODE = 'P7501';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER prevent_immutable_user_update
        BEFORE UPDATE OR DELETE ON users.user
        FOR EACH ROW
        EXECUTE FUNCTION users.prevent_immutable_user_change();
    """)

    op.execute("""
        CREATE TRIGGER prevent_immutable_user_auth_update
        BEFORE UPDATE OR DELETE ON users.user_auth
        FOR EACH ROW
        EXECUTE FUNCTION users.prevent_immutable_user_change();
    """)

    op.execute("""
        CREATE TRIGGER prevent_immutable_user_perm_update
        BEFORE UPDATE OR DELETE ON users.user_perm
        FOR EACH ROW
        EXECUTE FUNCTION users.prevent_immutable_user_change();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS prevent_immutable_user_perm_update ON users.user_perm;")
    op.execute("DROP TRIGGER IF EXISTS prevent_immutable_user_auth_update ON users.user_auth;")
    op.execute("DROP TRIGGER IF EXISTS prevent_immutable_user_update ON users.user;")
    op.execute("DROP FUNCTION IF EXISTS users.prevent_immutable_user_change;")
