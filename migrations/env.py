from logging.config import fileConfig
import os

import logging

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.orm import Session
from alembic import context

from datetime import datetime

###################################################
# Load environment variables from .env file
###################################################
load_dotenv()

###################################################
# Alembic Config object
###################################################
config = context.config

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(name)s] %(levelname)s: %(message)s",
)

###################################################
# Configure logging for Alembic
###################################################
alembic_logger = logging.getLogger("uvicorn.logger")
alembic_logger.setLevel(logging.DEBUG)

if not alembic_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[alembic] %(levelname)s: %(message)s")
    )
    alembic_logger.addHandler(handler)

alembic_logger.propagate = False

###################################################
# Load DATABASE_URL from .env (PostgreSQL)
###################################################
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not found in .env")

###################################################
# Override sqlalchemy.url from alembic.ini
###################################################
config.set_main_option("sqlalchemy.url", database_url)

###################################################
# Import SQLAlchemy metadata for autogenerate
###################################################
from api.database.models.base import Base
from api.database.models import *
target_metadata = Base.metadata


def log_migration(connection, revision, direction, status, info):
    session = Session(bind=connection)

    try:
        log_entry = MigrationLog(
            revision=str(revision),
            direction=direction,
            status=status,
            info=info if info else None
        )

        session.add(log_entry)
        session.commit()

    except Exception:
        session.rollback()

    finally:
        session.close()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,  # use .env URL
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
        compare_server_default=True,
        transaction_per_migration=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=False
        )

        try:
            with context.begin_transaction():
                context.run_migrations()

                # Logging: Read revision and direction from Alembic context
                alembic_ctx = context.get_context()
                current_rev = None
                if alembic_ctx:
                    current_rev = alembic_ctx.get_current_revision()
                # Detect migration direction: x-argument > environment variable > sys.argv
                direction = None
                # 1. Alembic x-argument (e.g. --x direction=upgrade)
                x_args = context.get_x_argument()
                for x in x_args:
                    if x.startswith("direction="):
                        direction = x.split("=", 1)[1]
                        break
                # 2. Environment variable
                if not direction:
                    direction = os.getenv("ALEMBIC_DIRECTION")
                # 3. sys.argv fallback
                if not direction:
                    import sys
                    for arg in sys.argv:
                        if "upgrade" in arg:
                            direction = "upgrade"
                        elif "downgrade" in arg:
                            direction = "downgrade"
                if not direction:
                    direction = "unknown"

                log_migration(connection, current_rev, direction, "success", info=None)

        except Exception as e:
            alembic_ctx = context.get_context()
            current_rev = None
            if alembic_ctx:
                current_rev = alembic_ctx.get_current_revision()
            # Detect migration direction: x-argument > environment variable > sys.argv
            direction = None
            x_args = context.get_x_argument()
            for x in x_args:
                if x.startswith("direction="):
                    direction = x.split("=", 1)[1]
                    break
            if not direction:
                direction = os.getenv("ALEMBIC_DIRECTION")
            if not direction:
                import sys
                for arg in sys.argv:
                    if "upgrade" in arg:
                        direction = "upgrade"
                    elif "downgrade" in arg:
                        direction = "downgrade"
            if not direction:
                direction = "unknown"
            log_migration(
                connection,
                current_rev,
                direction,
                "failed",
                info=str(e)
            )
            raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()