"""fix for database error when loading immutable values

Revision ID: 5441ed5a5756
Revises: a2660751bd38
Create Date: 2026-02-15 19:29:11.399939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5441ed5a5756'
down_revision: Union[str, Sequence[str], None] = 'a2660751bd38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION users.prevent_immutable_user_change()
        RETURNS trigger AS $$
        BEGIN
            -- Only check if trigger runs on users.user
            IF TG_TABLE_NAME = 'user' THEN
                IF OLD.immutable THEN
                    RAISE EXCEPTION 'Immutable user cannot be modified or deleted'
                    USING ERRCODE = 'P7501';
                END IF;
            END IF;

            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Downgrade schema."""
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
