import os
import subprocess
from datetime import datetime
from sqlalchemy.engine import make_url

from api.config.config import DATABASE_BACKUP_DIR

def backup_database(database_url: str):
    """
    Create a PostgreSQL database backup using pg_dump.
    Supports SQLAlchemy URLs (postgresql+psycopg2://).
    """

    os.makedirs(DATABASE_BACKUP_DIR, exist_ok=True)

    url = make_url(database_url)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(
        DATABASE_BACKUP_DIR,
        f"backup_{timestamp}.sql"
    )

    cmd = [
        "pg_dump",
        "-h", url.host,
        "-p", str(url.port or 5432),
        "-U", url.username,
        "-d", url.database,
        "-f", backup_file,
    ]

    env = os.environ.copy()
    if url.password:
        env["PGPASSWORD"] = url.password

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Backup failed:\n{result.stderr}"
        )

    print(f"Backup successful: {backup_file}")
    return backup_file