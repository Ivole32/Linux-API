from api.config.config import (
    AUTO_MIGRATE_DATABASE_ON_STARTUP,
    BACKUP_DATABASE_BEFORE_MIGRATION,
    BACKUP_DATABASE_AT_STARTUP
)

from api.database.backup import backup_database
from api.database.migrate import migration_needed, run_alembic_upgrade_head

import os
from dotenv import load_dotenv
load_dotenv() # Load .env

database_url = os.getenv("DATABASE_URL")


def startup_database():
    needs_migration = migration_needed()

    # Backup database if database should be backuped at startup or a migration needs to be applied
    if BACKUP_DATABASE_AT_STARTUP or (needs_migration and BACKUP_DATABASE_BEFORE_MIGRATION and AUTO_MIGRATE_DATABASE_ON_STARTUP):
        backup_database(database_url=database_url)

    # migrate if migration is needed AND auto migrate is enabled
    if needs_migration and AUTO_MIGRATE_DATABASE_ON_STARTUP:
        run_alembic_upgrade_head()