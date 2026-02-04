"""
The main module for managing user database operations.
"""

# Import psycopg errors
import psycopg.errors

# Import psycopg DictCursor
from psycopg.rows import dict_row

# Import regular expressions and other utilities
import os
import re
import secrets
import hashlib
import hmac

# Import configuration constants
from api.config.config import API_KEY_SECRET

from api.logger.logger import logger

# Import PostgreSQL connection pool
from api.database.postgres_pool import postgres_pool

from api.database.migrate import migration_needed

from api.exeptions.exeptions import *

class UserDatabase:
    """Class to handle user database operations."""

    def __init__(self):
        """Initialize the user database connection."""
        self._ready = False
        self.schema = "users"

        from dotenv import load_dotenv
        load_dotenv() # Load .env

        self.database_url = os.getenv("DATABASE_URL")

    def init_db(self) -> bool:
        # Set ready value if migration is not needed and database is up to date
        self._ready = not migration_needed()

    def _generate_api_key(self) -> str:
        """
        Generate a secure random API key.
        Returns:
            str: The generated API key.
        """
        return secrets.token_urlsafe(32)
    
    def _hash_api_key(self, api_key: str) -> str:
        """
        Create a HMAC-SHA256 hash of an API key using configured secret.
        
        Args:
            api_key: The plain API key string to hash
        
        Returns:
            A hexadecimal string representation of the HMAC-SHA256 digest.
        """
        return hmac.new(
            API_KEY_SECRET.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        """
        verify an API key against a previously stored HMAC-SHA256 hash.

        Args:
            api_key: The plain API key provided by the cient
            stored_hash: The stored hexadecimal HMAC hash to verify against.

        Returns:
            True if the API key matches the stored hash, otherwise False.
        """
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

    def _delete_user_record(self, user_id: str) -> bool:
        """
        Delete a user record from the users table by user_id

        Args:
            user_id: The unique identifier of the user to delete
        
        Returns:
            True if the user record was successfully deleted
        
        Raises:
            NoUserdeleted:
                If no database row was affected (user_id not found).

            UserDeletionError:
                If an unexpected database error occurs during deletion.
        """
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        DELETE FROM {self.schema}.users WHERE user_id = %s
                        """,
                        (user_id,)
                    )

                    if cur.rowcount == 0:
                        raise NoUserDeleted("Requested user not found: No rows affected")
                    
                    else:
                        return True

            except Exception as e:
                logger.error(f"Error deleting account: {e}")
                conn.rollback()
                raise UserDeletionError("Unexpected error while deleting user.")

    def _create_user_record(self, username: str) -> str:
        """
        Create a new user record in the database and return its generated user_id

        Args:
            username: The username to store for the new user record.
        
        Returns:
            The generated user_id of the newly created user.

        Raises:
            NoDatabaseReturnError:
                If no user_id is returned after the insert operation.
            UserRecordCreationError:     
                If an unexpected dtabase error occuers.
        """
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        f"""
                        INSERT INTO {self.schema}.users (username)
                        VALUES (%s)
                        RETURNING user_id;
                        """,
                        (username,)
                    )

                    user_id = cur.fetchone()["user_id"]
                    conn.commit()
            
                if user_id:
                    return user_id
                else:
                    raise

            except Exception as e:
                logger.error(f"Error creating account: {e}")
                conn.rollback()
                raise UserRecordCreationError("Unexpected error while creating user record")
            
    def _get_user_record(self, user_id: str) -> dict:
        """
        Load a single user record from the database by user_id.

        Args:
            user_id: The unique identifier of the user to load

        Returns:
            A dictionary containing the full user record columns and values.

        Raises:
            UserNotFoundError:
                If no user record exists for the given user_id.
            UserrecordReadError:
                If a database or query error occurs while reading the record.
        """

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        f"""
                        SELECT * FROM users.user WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    
                    user = cur.fetchone()
                    if user:
                        return user
                    else:
                        raise UserNotFoundError(f"User record for user_id {user_id} could not be loaded")

            except Exception as e:
                logger.error(f"Error getting user record: {e}")
                raise UserRecordReadError(f"User record for user_id {user_id} could not be read")

    def _get_user_perm_record(self, user_id: str) -> dict:
        """
        Load the perm record for a user from the database.

        Args:
            user_id: The unique identifier of the user whose perm record shuld be loaded.

        Returns:
            A dictionary containing the user perminission filds and values.

        Raises:
            UserNotFoundError:
                If no perm record exists for the given user_id.
            UserPermReadError:
                If an unexpected database error occurs while reading user perm.
        """
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        f"""
                        SELECT * FROM users.user_perm WHERE user_id = %s
                        """,
                        (user_id,)
                    )

                user_perm = cur.fetchone()
                if user_perm:
                    return user_perm
                else:
                    raise UserNotFoundError(f"User perm record for user_id {user_id} could not be loaded")

            except Exception as e:
                logger.error(f"Error getting user perm record: {e}")
                raise UserPermReadError(f"User perm for user_id {user_id} could not be read")

    def _get_admin_count(self) -> int:
        """
        Count the number of active admin users in the database.

        Returns:
            The number of users who are both marked as admin and activated.
            Returns 0 if the query fails due to an unexpected error.

        """
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM users.user_perm
                        WHERE is_admin = TRUE
                            AND activated = TRUE 
                        """
                    )

                    return cur.fetchone()[0]
            
            except Exception as e:
                logger.error(f"Error counting active admins: {e}")
                return 0

    def _create_user_auth_record(self, user_id: str) -> str:
        """
        Create the authentication record for a user and return a new API key.

        Args:
            user_id: The unique identifier of the user whose auth record shuld be created.

        Returns:
            The newly generated plain API key.

        Raises:
            NoUserAuthCreatedError:
                If the update affects zero rows (no auth record found for user_id)
            UserAuthCreationError:
                If an unexpected database error occurs during the operation.
        """
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
                        raise NoUserAuthCreatedError("Error creating user auth record: No rows affected")
                    
                    conn.commit()
                    return api_key
                
            except Exception as e:
                logger.error(f"Error creating creating auth record: {e}")
                conn.rollback()
                raise UserAuthCreationError("Error while creating user auth table.")

    def _set_user_perm_record(self, user_id: str, is_admin: bool, activate: bool) -> bool:
        """
        Update the perminissin flags for a user in the user_perm table.
        Note: Can currently only be used for account creation as updating is based on default values.

        Args:
            user_id: The unique identifier of the user whose permissions should be updated.
            is_admin: Whether the user should have admin privileges.
            activate: Whether the user account shouldbe marked as activated.

        Returns:
            True if the perminissions are already at default values or were updated successfully in the database.

        Raises:
            NoRowsAffected:
                If the update query did not modify any row (user_id not found)
            UserPermEditError:
                If an unexpected database error occurs during the update.
        """
        if activate == False and is_admin == False:
            # Since activate is set to false and user is no admin, which are default values there is nothing to do here
            # // TODO: Update to support changes back to default values -> Only if needed in future features
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
                            raise NoUserPermEditedError("Error setting user perm record: No rows affected")
                        
                        conn.commit()
                        return True
                
                except Exception as e:
                    logger.error(f"Error setting perm record: {e}")
                    conn.rollback()
                    raise UserPermEditError("Unexpected error setting user perm record.")

    def create_user(self, username: str, is_admin: bool, activate: bool) -> tuple:
        """
        Create a complete user including base record, auth data and perminissions.

        Args:
            username: The requested username (will be sanitized before storage).
            is_admin: Whether the new user should have admin privileges.
            activate: Whether the new user should be marked as activated.

        Returns:
            A tuple of (sanitized_username, user_id, api_key)

        Raises:
            UserRecordCreatinError:
                If no user_id is returned in user record creation.
            UserAuthCreationError:
                If no api_key is returned in user auth creation.
            UserPermEditError:
                If no success return after setting user perm values.
        """
        sanitized_username = self._sanitize_username(username=username)

        user_id = self._create_user_record(username=sanitized_username)
        if not user_id:
            raise UserRecordCreationError("No user_id returned in self._create_user_record")
        
        api_key = self._create_user_auth_record(user_id=user_id)
        if not api_key:
            raise UserAuthCreationError("No api_key returned in self._set_user_perm_record")
        
        perm_record_set = self._set_user_perm_record(user_id=user_id, is_admin=is_admin, activate=activate)
        if not perm_record_set:
            raise UserPermEditError("No success return from self._set_user_perm_record")

        return sanitized_username, user_id, api_key

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user after validating existence and admin safety constraints.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            True if the user was successfully deleted.

        Raises:
            UserNotFoundError:
                If no user or perm record exists for the given user_id
            LastAdminError:
                If the user is an admin and is the last active admin account.
        """
        user = self._get_user_record(user_id=user_id)
        if user:
            user_perm = self._get_user_perm_record(user_id=user_id)
            if user_perm:
                if user_perm["is_admin"]:
                    if self._get_admin_count() <= 1:
                        raise LastAdminError("Last active admin can not be deleted.")
                else:
                    return self._delete_user_record(user_id=user_id)

        else:
            raise UserNotFoundError("Requested user not found")

    def flush_database(self) -> None:
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""TRUNCATE TABLE {self.schema}.user CASCADE;"""
                    )

                if cur.rowcount == 0:
                    raise NoRowsAffected("Error flushing database: No rows affected.")
            
                logger.log("Database Flushed...")
                conn.commit()

            except Exception as e:
                logger.error(f"Error flushing database: {e}")
                conn.rollback()
                raise DatabaseFlushError("Unexpected error flushing database.")


    def is_ready(self) -> bool:
        """
        Check if the user database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready
    
# Global singleton instance
user_database = UserDatabase()