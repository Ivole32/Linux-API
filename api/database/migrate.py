import os
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

from api.config.config import ALEMBIC_INI_FILE

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


def migration_needed():
    """
    Check if database migration is needed.
    Returns:
        True: if migration is needed
        False: if migration is not needed
    """
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")
    
    # Alembic config
    alembic_cfg = Config(ALEMBIC_INI_FILE)
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    # Load script directory (migration files)
    script = ScriptDirectory.from_config(alembic_cfg)
    head_revision = script.get_current_head()

    # Connect to DB and get current revision
    engine = create_engine(database_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_revision = context.get_current_revision()

    # Id DB is not  at head -> migration needed
    return current_revision != head_revision

def run_alembic_upgrade_head():
    """
    Apply all pending Alembic migrations (upgrade to head)
    """
    load_dotenv()

    # Check if alembic.ini exists
    if not os.path.exists(ALEMBIC_INI_FILE):
        raise FileNotFoundError(
            f"Alembic ini file not found: {ALEMBIC_INI_FILE}"
        )

    alembic_cfg = Config(ALEMBIC_INI_FILE)

    # Load database URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    # Migrate/Upgrade
    command.upgrade(alembic_cfg, "head")