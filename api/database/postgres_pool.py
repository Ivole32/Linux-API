"""PostgreSQL Connection Pool Manager.

This module provides a centralized connection pool for PostgreSQL using psycopg3.
"""

# Time utilities
import time
import threading

# Typing
from typing import Optional

# Psycopg3 rows and connection pool
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Logger
from api.logger.logger import log
from logging import DEBUG, INFO, WARNING, CRITICAL

# PostgreSQL configuration
from api.config.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DATABASE,
    POSTGRES_MIN_CONNECTIONS,
    POSTGRES_MAX_CONNECTIONS,
    POSTGRES_CONNECT_TIMEOUT,
    POSTGRES_RETRIES,
    POSTGRES_RETRY_DELAY,
    POSTGRES_HEALTHCHECK_TIMEOUT,
    POSTGRES_HEALTHCHECK_INTERVALL
)

class PostgresPool:
    """Singleton connection pool for PostgreSQL."""
    
    _instance: Optional['PostgresPool'] = None
    _pool: Optional[ConnectionPool] = None
    
    def __new__(cls):
        """
        Create or return the singleton instance.

        Ensures only a single `PostgresPool` instance exists within the
        process. This implements a minimal singleton pattern used by the
        module-level `postgres_pool` instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the connection pool (only once)."""
        if self._pool is not None:
            return
        log(DEBUG, "PostgresPool instance created (not yet initialized)")
        self._is_ready: bool = False
        self._monitor_thread: Optional["threading.Thread"] = None
        self._monitor_stop = False
        self._lock = threading.Lock()
    
    def init_pool(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        min_size: int = 2,
        max_size: int = 10,
        connect_timeout: float = 5.0,
        retries: int = 1,
        retry_delay: float = 1.0,
        healthcheck_timeout: float | None = None,
        healthcheck_interval: float = 5.0,
    ) -> bool:
        """Initialize the connection pool with database credentials.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            user: Database user
            password: Database password
            database: Database name
            min_size: Minimum pool size
            max_size: Maximum pool size
            connect_timeout: psycopg connection timeout (seconds)
            retries: Number of attempts before giving up
            retry_delay: Delay between retries (seconds)
            healthcheck_timeout: Time to wait for pool warm-up/first connection
            
        Returns:
            True if successful, False otherwise
        """
        if self._pool is not None:
            log(DEBUG, "Connection pool already initialized")
            return True

        last_error: Exception | None = None
        attempts = max(1, int(retries))
        timeout_s = max(1, int(connect_timeout))
        conninfo = (
            f"host={host} port={port} user={user} password={password} "
            f"dbname={database} sslmode=prefer connect_timeout={timeout_s}"
        )

        for attempt in range(1, attempts + 1):
            try:
                self._pool = ConnectionPool(
                    conninfo,
                    min_size=min_size,
                    max_size=max_size,
                    kwargs={"row_factory": dict_row},
                    open=True,
                )

                if healthcheck_timeout:
                    self._pool.wait(timeout=healthcheck_timeout)
                self._run_healthcheck()

                # start background monitor thread that periodically checks readiness
                # if not already started
                if self._monitor_thread is None:
                    self._start_monitor(healthcheck_interval)

                log(
                    INFO,
                    f"PostgreSQL connection pool initialized: {database}@{host}:{port} "
                    f"(pool size: {min_size}-{max_size}, timeout={timeout_s}s)",
                )
                return True

            except Exception as exc:
                last_error = exc
                log(
                    WARNING,
                    f"Pool init attempt {attempt}/{attempts} failed: {exc}",
                )
                self.close(silent=True)
                if attempt < attempts:
                    time.sleep(max(0.1, retry_delay))

        log(CRITICAL, f"Failed to initialize PostgreSQL connection pool after {attempts} attempts: {last_error}")
        return False

    def get_connection(self):
        """Get a connection from the pool.
        
        Returns:
            A context manager for a database connection.
            
        Raises:
            RuntimeError: If pool is not initialized
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call init_pool() first.")
        return self._pool.connection()

    def is_ready(self) -> bool:
        """Return whether the pool currently reports the database as ready."""
        with self._lock:
            return bool(self._is_ready)

    def _start_monitor(self, interval: float = 5.0) -> None:
        """Start a background thread that periodically runs a healthcheck and sets `self._is_ready`."""
        if self._monitor_thread is not None:
            return

        def _monitor_loop():
            while not self._monitor_stop:
                try:
                    self._run_healthcheck()
                    with self._lock:
                        self._is_ready = True
                except Exception:
                    with self._lock:
                        self._is_ready = False
                time.sleep(max(0.5, float(interval)))

        self._monitor_stop = False
        t = threading.Thread(target=_monitor_loop, daemon=True, name="pg-pool-monitor")
        self._monitor_thread = t
        t.start()

    def ensure_ready(self, timeout: float | None = None) -> None:
        """
        Verify the pool can hand out healthy connections.
        Args:
            timeout: Maximum time to wait for a connection (seconds)
        Raises:
            RuntimeError: If pool is not initialized
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call init_pool() first.")
        if timeout:
            self._pool.wait(timeout=timeout)
        self._run_healthcheck()
    
    def close(self, silent: bool = False):
        """
        Close the connection pool.
        Args:
            silent: If True, suppress log messages.
        """
        if self._pool is not None:
            self._pool.close()
            self._pool = None
        # stop monitor thread
        if self._monitor_thread is not None:
            self._monitor_stop = True
            self._monitor_thread = None
            if not silent:
                log(INFO, "PostgreSQL connection pool closed")

    def _run_healthcheck(self) -> None:
        """
        Run a lightweight health check on the pool connection.
        Raises:
            RuntimeError: If pool is not initialized
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call init_pool() first.")

        with self._pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()


# Global singleton instance
postgres_pool = PostgresPool()

# Initialize the pool
postgres_pool.init_pool(host=POSTGRES_HOST,
                        port=POSTGRES_PORT,
                        user=POSTGRES_USER,
                        password=POSTGRES_PASSWORD,
                        database=POSTGRES_DATABASE,
                        min_size=POSTGRES_MIN_CONNECTIONS,
                        max_size=POSTGRES_MAX_CONNECTIONS,
                        connect_timeout=POSTGRES_CONNECT_TIMEOUT,
                        retries=POSTGRES_RETRIES,
                        retry_delay=POSTGRES_RETRY_DELAY,
                        healthcheck_timeout=POSTGRES_HEALTHCHECK_TIMEOUT,
                        healthcheck_interval=POSTGRES_HEALTHCHECK_INTERVALL
                        )