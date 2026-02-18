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
import pickle
from tdigest import TDigest

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
    
    def insert_route_metrics(self, route_rows: list, conn=None):
        """Insert or merge route metrics rows.

        Each row should be: (time, route, requests, avg_response_time, min_response_time,
        max_response_time, p50, p95, p99)

        If `conn` is provided, use that connection (useful when holding advisory lock).
        """
        upsert_sql = f"""
            INSERT INTO {self.schema}.route_metrics
            (time, route, requests, avg_response_time, min_response_time, max_response_time, p50, p95, p99, tdigest)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (time, route) DO UPDATE SET
                requests = route_metrics.requests + EXCLUDED.requests,
                avg_response_time = (
                    COALESCE(route_metrics.avg_response_time, 0.0) * COALESCE(route_metrics.requests, 0)
                    + COALESCE(EXCLUDED.avg_response_time, 0.0) * COALESCE(EXCLUDED.requests, 0)
                ) / NULLIF(COALESCE(route_metrics.requests, 0) + COALESCE(EXCLUDED.requests, 0), 0),
                min_response_time = LEAST(COALESCE(route_metrics.min_response_time, EXCLUDED.min_response_time), EXCLUDED.min_response_time),
                max_response_time = GREATEST(COALESCE(route_metrics.max_response_time, EXCLUDED.max_response_time), EXCLUDED.max_response_time),
                p50 = EXCLUDED.p50,
                p95 = EXCLUDED.p95,
                p99 = EXCLUDED.p99,
                tdigest = EXCLUDED.tdigest
        """

        if conn is not None:
            try:
                with conn.cursor() as cur:
                    for r in route_rows:
                        # expect tdigest as last element (may be None)
                        try:
                            (
                                tstamp,
                                route,
                                requests,
                                avg_rt,
                                min_rt,
                                max_rt,
                                p50,
                                p95,
                                p99,
                                td_bytes,
                            ) = r
                        except Exception:
                            logger.error("Route row has unexpected shape, expected 10 elements")
                            raise

                        # try to fetch existing tdigest (for merge)
                        cur.execute(
                            f"SELECT tdigest, requests, avg_response_time, min_response_time, max_response_time FROM {self.schema}.route_metrics WHERE time = %s AND route = %s",
                            (tstamp, route),
                        )
                        exist = cur.fetchone()

                        if exist and exist["tdigest"] is not None and td_bytes is not None:
                            try:
                                existing_td = pickle.loads(exist["tdigest"])
                                new_td = pickle.loads(td_bytes)
                                # merge best-effort
                                try:
                                    if hasattr(existing_td, "merge"):
                                        existing_td.merge(new_td)
                                    elif hasattr(existing_td, "update") and hasattr(new_td, "centroids"):
                                        # try to update with centroids means
                                        existing_td.update([c.mean for c in new_td.centroids])
                                    else:
                                        # fallback: create a fresh digest and update with both centroids if available
                                        merged_td = TDigest()
                                        try:
                                            merged_td.update([c.mean for c in existing_td.centroids])
                                            merged_td.update([c.mean for c in new_td.centroids])
                                            existing_td = merged_td
                                        except Exception:
                                            existing_td = new_td
                                except Exception:
                                    existing_td = new_td

                                try:
                                    merged_td_bytes = pickle.dumps(existing_td)
                                    # compute merged percentiles if supported
                                    try:
                                        p50_m = float(existing_td.percentile(50))
                                        p95_m = float(existing_td.percentile(95))
                                        p99_m = float(existing_td.percentile(99))
                                    except Exception:
                                        p50_m, p95_m, p99_m = (p50, p95, p99)
                                except Exception:
                                    merged_td_bytes = td_bytes
                                    p50_m, p95_m, p99_m = (p50, p95, p99)
                            except Exception:
                                logger.warning("Failed to merge tdigest blobs; using incoming digest")
                                merged_td_bytes = td_bytes
                                p50_m, p95_m, p99_m = (p50, p95, p99)
                        else:
                            merged_td_bytes = td_bytes
                            p50_m, p95_m, p99_m = (p50, p95, p99)

                        # if existing row exists, perform UPDATE merging numeric metrics
                        if exist:
                            # merge numeric fields: requests, avg (weighted), min/max
                            existing_requests = exist["requests"] or 0
                            existing_avg = exist["avg_response_time"] or 0.0
                            total_requests = existing_requests + (requests or 0)
                            if total_requests:
                                merged_avg = (
                                    (existing_avg * existing_requests) + (avg_rt * (requests or 0))
                                ) / total_requests
                            else:
                                merged_avg = 0.0

                            merged_min = min(filter(lambda x: x is not None, [exist["min_response_time"], min_rt]))
                            merged_max = max(filter(lambda x: x is not None, [exist["max_response_time"], max_rt]))

                            cur.execute(
                                f"UPDATE {self.schema}.route_metrics SET requests=%s, avg_response_time=%s, min_response_time=%s, max_response_time=%s, p50=%s, p95=%s, p99=%s, tdigest=%s WHERE time=%s AND route=%s",
                                (
                                    total_requests,
                                    merged_avg,
                                    merged_min,
                                    merged_max,
                                    p50_m,
                                    p95_m,
                                    p99_m,
                                    merged_td_bytes,
                                    tstamp,
                                    route,
                                ),
                            )
                        else:
                            # insert new
                            cur.execute(
                                f"INSERT INTO {self.schema}.route_metrics (time, route, requests, avg_response_time, min_response_time, max_response_time, p50, p95, p99, tdigest) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (
                                    tstamp,
                                    route,
                                    requests,
                                    avg_rt,
                                    min_rt,
                                    max_rt,
                                    p50_m,
                                    p95_m,
                                    p99_m,
                                    merged_td_bytes,
                                ),
                            )

                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while upserting route metrics (per-row merge): {e}")
                raise
            return

        with postgres_pool.get_connection() as conn_ctx:
            try:
                with conn_ctx.cursor() as cur:
                    cur.executemany(upsert_sql, route_rows)

            except Exception as e:
                conn_ctx.rollback()
                logger.error(f"Unexpected error while upserting route metrics: {e}")
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
                    
    def insert_route_status_code_metrics(self, status_rows: list, conn=None):
        """Insert or increment status code counts.

        Rows are (time, route, status_code, count).
        """
        upsert_sql = f"""
            INSERT INTO {self.schema}.route_status_codes
            (time, route, status_code, count)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (time, route, status_code)
            DO UPDATE SET count = {self.schema}.route_status_codes.count + EXCLUDED.count
        """

        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.executemany(upsert_sql, status_rows)
            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while upserting status code metrics: {e}")
                raise
            return

        with postgres_pool.get_connection() as conn_ctx:
            try:
                with conn_ctx.cursor() as cur:
                    cur.executemany(upsert_sql, status_rows)

            except Exception as e:
                conn_ctx.rollback()
                logger.error(f"Unexpected error while upserting status code metrics: {e}")
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
                time,
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
            query += " AND time >= %s"
            params.append(start_time)

        if end_time:
            query += " AND time <= %s"
            params.append(end_time)

        order = "DESC" if newest_first else "ASC"
        query += f" ORDER BY time {order}"

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

    def insert_global_metrics(self, now, global_summary: dict, conn=None):
        """Insert or merge global metrics for the given timestamp."""
        upsert_sql = f"""
            INSERT INTO {self.schema}.global_metrics
            (time, total_requests, avg_response_time, error_rate)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (time) DO UPDATE SET
                total_requests = {self.schema}.global_metrics.total_requests + EXCLUDED.total_requests,
                avg_response_time = (
                    COALESCE({self.schema}.global_metrics.avg_response_time, 0.0) * COALESCE({self.schema}.global_metrics.total_requests, 0)
                    + COALESCE(EXCLUDED.avg_response_time, 0.0) * COALESCE(EXCLUDED.total_requests, 0)
                ) / NULLIF(COALESCE({self.schema}.global_metrics.total_requests, 0) + COALESCE(EXCLUDED.total_requests,0), 0),
                error_rate = (
                    COALESCE({self.schema}.global_metrics.error_rate, 0.0) * COALESCE({self.schema}.global_metrics.total_requests, 0)
                    + COALESCE(EXCLUDED.error_rate, 0.0) * COALESCE(EXCLUDED.total_requests, 0)
                ) / NULLIF(COALESCE({self.schema}.global_metrics.total_requests, 0) + COALESCE(EXCLUDED.total_requests,0), 0)
        """

        params = (
            now,
            global_summary["total_requests"],
            global_summary["avg_response_time"],
            global_summary["error_rate"],
        )

        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(upsert_sql, params)
            except Exception as e:
                conn.rollback()
                logger.error(f"Unexpected error while upserting global metrics: {e}")
                raise
            return

        with postgres_pool.get_connection() as conn_ctx:
            try:
                with conn_ctx.cursor() as cur:
                    cur.execute(upsert_sql, params)

            except Exception as e:
                conn_ctx.rollback()
                logger.error(f"Unexpected error while upserting global metrics: {e}")
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
                time,
                total_requests,
                avg_response_time,
                error_rate
            FROM {self.schema}.global_metrics
            WHERE 1=1
        """

        params = []

        if start_time:
            query += " AND time >= %s"
            params.append(start_time)

        if end_time:
            query += " AND time <= %s"
            params.append(end_time)

        order = "DESC" if newest_first else "ASC"
        query += f" ORDER BY time {order}"

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