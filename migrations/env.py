from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables from .env
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Alembic Config object
# -------------------------------------------------
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------
# Load DATABASE_URL from .env (PostgreSQL)
# -------------------------------------------------
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not found in .env")

# Override sqlalchemy.url from alembic.ini
config.set_main_option("sqlalchemy.url", database_url)

# -------------------------------------------------
# Import SQLAlchemy metadata for autogenerate
# -------------------------------------------------
from api.database.models.base import Base
from api.database.models import *
target_metadata = Base.metadata


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
        transaction_per_migration=False
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
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

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()