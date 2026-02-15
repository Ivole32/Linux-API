"""fix for non immutable user deletion

Revision ID: a2660751bd38
Revises: a0ab061a5bbd
Create Date: 2026-02-15 19:24:24.422600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2660751bd38'
down_revision: Union[str, Sequence[str], None] = 'a0ab061a5bbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION users.prevent_immutable_user_change()
        RETURNS trigger AS $$
        BEGIN
            IF OLD.immutable THEN
                RAISE EXCEPTION 'Immutable user cannot be modified or deleted'
                USING ERRCODE = 'P7501';
            END IF;

            IF TG_OP = 'DELETE' THEN
                RETURN OLD;   -- required for DELETE
            ELSE
                RETURN NEW;   -- required for UPDATE
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Downgrade schema."""
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