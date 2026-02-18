import asyncio
from datetime import datetime, timezone
from api.metrics.aggregator import summarize, reset

from api.database.metric_database.metric_database import metric_database
from api.database.postgres_pool import postgres_pool

from api.metrics.health import flush_health


# Import logger
from api.logger.logger import logger


FLUSH_INTERVAL = 60
_ADVISORY_LOCK_KEY = 987654321098765432

async def flush_loop():
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)

        flush_health.record_attempt()

        try:
            # Acquire advisory lock so only one worker flushes at a time
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_try_advisory_lock(%s)", (_ADVISORY_LOCK_KEY,))
                    got_lock = cur.fetchone()[0]

                if not got_lock:
                    logger.debug("Flush skipped: another worker holds advisory lock")
                    flush_health.record_skipped()
                    continue

                try:
                    summary, status_counts, global_summary = summarize()
                    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

                    route_rows = [
                        (
                            now,
                            route,
                            data["count"],
                            data["avg"],
                            data["min"],
                            data["max"],
                            data["p50"],
                            data["p95"],
                            data["p99"],
                            data.get("tdigest"),
                        )
                        for route, data in summary.items()
                    ]

                    status_rows = [
                        (now, route, status, count)
                        for (route, status), count in status_counts.items()
                    ]

                    # perform upserts using the same connection (lock-holder)
                    if route_rows:
                        metric_database.insert_route_metrics(route_rows=route_rows, conn=conn)

                    if status_rows:
                        metric_database.insert_route_status_code_metrics(status_rows=status_rows, conn=conn)

                    metric_database.insert_global_metrics(now=now, global_summary=global_summary, conn=conn)

                    # reset aggregator after successful writes
                    reset()
                    flush_health.record_success()

                finally:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("SELECT pg_advisory_unlock(%s)", (_ADVISORY_LOCK_KEY,))
                    except Exception:
                        logger.warning("Failed to release advisory lock (ignored)")

        except Exception as e:
            flush_health.record_error(e)
            logger.error(f"Flush worker failed: {e}")