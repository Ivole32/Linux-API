"""
The main module for metric database operations.
"""

# Import PostgreSQL connection pool
from api.database.postgres_pool import postgres_pool

from api.database.migrate import migration_needed

# Import psycopg DictCursor
from psycopg.rows import dict_row

# Import logger
from api.logger.logger import logger

from datetime import datetime
from typing import Optional

class MetricDatabase:
    """Class to handle metric database operations"""

    def __init__(self):
        """Initialize the metric database connection."""
        self._ready = False
        self.schema = "metrics"

    def init_db(self) -> bool:
        """
        Initialize the readiness state for the user database.

        This checks whether a migration is needed and sets the internal
        `_ready` flag accordingly.

        Returns:
            bool: True if the database is up-to-date (no migration needed),
            False otherwise.
        """
        self._ready = not migration_needed()
        return self._ready
    
    def insert_route_metrics(self, route_rows: list):
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(f"""
                        INSERT INTO {self.schema}.route_metrics
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, route_rows)

            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while insertign route metrics: {e}")
                raise

    def get_route_metrics(
        self,
        route: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
        cursor: Optional[datetime] = None,
    ):
        """
        Fetch route metrics with optional filters.

        Args:
            route: filter by route
            start: start time (inclusive)
            end: end time (inclusive)
            cursor: pagination cursor (bucket timestamp)
            limit: max rows to return

        Returns:
            list[dict]
        """

        query = f"""
            SELECT *
            FROM {self.schema}.route_metrics
            WHERE 1=1
        """

        params = []

        if route:
            query += " AND route = %s"
            params.append(route)

        if start:
            query += " AND time >= %s"
            params.append(start)

        if end:
            query += " AND time <= %s"
            params.append(end)

        # cursor pagination (older entries)
        if cursor:
            query += " AND time < %s"
            params.append(cursor)

        query += """
            ORDER BY time DESC
            LIMIT %s
        """
        params.append(limit)

        with postgres_pool.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

        return rows
                    
    def insert_route_status_code_metrics(self, status_rows: list):
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(f"""
                        INSERT INTO {self.schema}.route_status_codes
                        VALUES (%s,%s,%s,%s)
                    """, status_rows)

            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while insertign status code metrics: {e}")
                raise

    def get_route_status_code_metrics(
        self,
        route: Optional[str] = None,
        status_code: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        newest_first: bool = True,
    ):
        """
        Fetch route status code metrics with filtering and pagination.
        """

        query = f"""
            SELECT
                time_bucket,
                route,
                status_code,
                count
            FROM {self.schema}.route_status_codes
            WHERE 1=1
        """

        params = []

        if route:
            query += " AND route = %s"
            params.append(route)

        if status_code:
            query += " AND status_code = %s"
            params.append(status_code)

        if start_time:
            query += " AND time_bucket >= %s"
            params.append(start_time)

        if end_time:
            query += " AND time_bucket <= %s"
            params.append(end_time)

        order = "DESC" if newest_first else "ASC"
        query += f" ORDER BY time_bucket {order}"

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()

            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Failed fetching route status code metrics | "
                    f"Route: {route} | Status: {status_code} | Error: {e}"
                )
                raise

    def insert_global_metrics(self, now, global_summary: dict):
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        INSERT INTO {self.schema}.global_metrics
                        VALUES (%s,%s,%s,%s)
                    """, (
                        now,
                        global_summary["total_requests"],
                        global_summary["avg_response_time"],
                        global_summary["error_rate"],
                    ))

            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while insertign status code metrics: {e}")
                raise

    def get_global_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        newest_first: bool = True,
    ):
        """
        Fetch global metrics with optional time filtering and pagination.

        Args:
            start_time: filter metrics after this timestamp
            end_time: filter metrics before this timestamp
            limit: number of rows to return
            offset: pagination offset
            newest_first: sort order

        Returns:
            List[dict]
        """

        query = f"""
            SELECT
                time_bucket,
                total_requests,
                avg_response_time,
                error_rate
            FROM {self.schema}.global_metrics
            WHERE 1=1
        """

        params = []

        if start_time:
            query += " AND time_bucket >= %s"
            params.append(start_time)

        if end_time:
            query += " AND time_bucket <= %s"
            params.append(end_time)

        order = "DESC" if newest_first else "ASC"
        query += f" ORDER BY time_bucket {order}"

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()

            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while fetching global metrics: {e}")
                raise

    def is_ready(self) -> bool:
        """
        Check if the user database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready and postgres_pool.is_ready()
    
# Global singleton instance
metric_database = MetricDatabase()