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

    def init_db(self, schema: str = "users") -> bool:
        try:
            self.schema = schema
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")
                    conn.commit()
            self._create_tables()

            self._ready = True

            return True

        except psycopg.Error as e:
            from api.logger.logger import logger
            logger.error(f"Database error: {e}")
            return False
        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Unexpected error: {e}")
            return False
        
    def _create_tables(self) -> None:
        """Create necessary tables in the user database."""
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Create user table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.users (
                        user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        username TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMPTZ
                    );
                    """
                )

                # Create user_auth table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.user_auth (
                        user_id UUID PRIMARY KEY NOT NULL,
                        api_key_hash TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES {self.schema}.users(user_id) ON DELETE CASCADE
                    );
                    """
                )

                # Create user_perm table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.user_perm (
                        user_id UUID PRIMARY KEY NOT NULL,
                        is_admin BOOL DEFAULT false,
                        activated BOOL DEFAUL false,
                        FOREIGN KEY (user_id) REFERENCES {self.schema}.users(user_id) ON DELETE CASCADE
                    );
                    """
                )
                conn.commit()

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