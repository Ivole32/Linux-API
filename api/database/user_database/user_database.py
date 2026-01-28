"""
The main module for managing user database operations.
"""

# Import psycopg errors
import psycopg.errors

# Import regular expressions and other utilities
import re
import secrets
import hashlib
import hmac

# Import alembic stuff
from alembic.config import Config
from alembic import command
import os
import subprocess
from datetime import datetime

# Import configuration constants
from api.config.config import API_KEY_SECRET

from api.logger.logger import logger

# Import PostgreSQL connection pool
from api.database.postgres_pool import postgres_pool

class UserDatabase:
    """Class to handle user database operations."""

    def __init__(self):
        """Initialize the user database connection."""
        self._ready = False
        self.schema = "users"

        from dotenv import load_dotenv
        load_dotenv() # Load .env

        self.database_url = os.getenv("DATABASE_URL")

    def _run_alembic_upgrade_head(self, alembic_ini_path: str = "../alembic.ini"):
        """
        Apply all pending Alembic migrations (upgrade to head)
        """
        if not os.path.exists(alembic_ini_path):
            raise FileNotFoundError(f"{alembic_ini_path} not found")
        
        alembic_cfg = Config(alembic_ini_path)

        if self.database_url:
            alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)

        # Run upgrade
        command.upgrade(alembic_cfg, "head")

    def _dump_database(self, database_url: str, backup_dir: str = "./backups"):
        """
        Create a backup of the PostgreSQL database using pg_dump.
        """
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

        # pg_dump expects: postgres://user:password@host:port/db
        database_url = "postgres" + database_url.split("//", 1)[1]

        result = subprocess.run(
            ["pg_dump", database_url, "-f", backup_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Backup failed: {result.stderr}")
        
        print(f"Backup successful: {backup_file}")
        return backup_file

    def init_db(self) -> bool:
        # Backup the db
        success = self._dump_database(database_url=self.database_url) # //TODO add actual URL

        # Perform database migrations if backup is successful
        if success:
            self._run_alembic_upgrade_head()

    def _generate_api_key(self) -> str:
        """
        Generate a secure random API key.
        Returns:
            str: The generated API key.
        """
        return secrets.token_urlsafe(32)
    
    def _hash_api_key(self, api_key: str) -> str:
        return hmac.new(
            API_KEY_SECRET.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        return hmac.compare_digest(
            self._hash_api_key(api_key),
            stored_hash
        )

    def _sanitize_username(self, username: str) -> str:
            """
            Sanitize the username by stripping whitespace and removing invalid characters.
            Args:
                username: The username to sanitize.
            Returns:
                The sanitized username. (str)
            """
            cleaned = re.sub(r"[^A-Za-z0-9_]", "", username) # Only allow alphanumeric characters and underscores
            return cleaned.lower() # Convert to lowercase for consistency

    def _delete_user_record(self, user_id: str):
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    pass
                    #cur.execute(
                    #    f"""

                    #    """
                    #)

            except Exception as e:
                logger.error(f"Error creating account: {e}")
                conn.rollback()
                return None

    def _create_user_record(self, username: str) -> str | None:
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO {self.schema}.users (username)
                        VALUES (%s)
                        RETURNING user_id;
                        """,
                        (username,)
                    )

                    user_id = cur.fetchone()[0]
                    conn.commit()
            
                return user_id

            except Exception as e:
                logger.error(f"Error creating account: {e}")
                conn.rollback()
                return None
            
    def _create_user_auth_record(self, user_id: str):
        api_key = self._generate_api_key()
        hashed_api_key = self._hash_api_key(api_key=api_key)

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        UPDATE {self.schema}.user_auth
                        SET api_key_hash = %s
                        WHERE user_id = %s;
                        """,
                        (hashed_api_key, user_id)
                    )

                    if cur.rowcount == 0:
                        return None
                    
                    conn.commit()
                    return api_key
                
            except Exception as e:
                logger.error(f"Error creating creating auth record: {e}")
                conn.rollback()
                return False

    def _set_user_perm_record(self, user_id: str, is_admin: bool, activate: bool):
        if activate == False and is_admin == False:
            # Since activate is set to false and user is no admin, which are default values there is nothing to do here
            return True
        
        else:
            with postgres_pool.get_connection() as conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            UPDATE {self.schema}.user_perm
                            SET 
                                activated = %s, 
                                is_admin = %s
                            WHERE user_id = %s;
                            """,
                            (activate, is_admin, user_id)
                        )

                        if cur.rowcount == 0:
                            return None
                        
                        conn.commit()
                        return True
                
                except Exception as e:
                    logger.error(f"Error creating creating perm record: {e}")
                    conn.rollback()
                    return False

    def create_user(self, username: str, is_admin: bool, activate: bool) -> tuple:
        sanitized_username = self._sanitize_username(username=username)

        user_id = self._create_user_record(username=sanitized_username)
        if not user_id:
            return
        
        api_key = self._create_user_auth_record(user_id=user_id)
        if not api_key:
            return
        
        perm_record_set = self._set_user_perm_record(user_id=user_id, is_admin=is_admin, activate=activate)
        if not perm_record_set:
            return

        return sanitized_username, user_id, api_key

    def delete_user(self, user_id: str) -> bool:
        pass

    def is_ready(self) -> bool:
        """
        Check if the user database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready
    
# Global singleton instance
user_database = UserDatabase()

# Initialize the database instance
user_database.init_db()