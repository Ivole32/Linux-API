import asyncio
from datetime import datetime, timezone
from api.metrics.aggregator import summarize, reset

from api.database.metric_database.metric_database import metric_database

from api.metrics.health import flush_health


# Import logger
from api.logger.logger import logger


FLUSH_INTERVAL = 60

async def flush_loop():
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)

        flush_health.record_attempt()

        try:
            summary, status_counts, global_summary = summarize()
            now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

            # Route metrics
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
                )
                for route, data in summary.items()
            ]
            metric_database.insert_route_metrics(route_rows=route_rows)

            # Status codes
            status_rows = [
                (now, route, status, count)
                for (route, status), count in status_counts.items()
            ]
            metric_database.insert_route_status_code_metrics(status_rows=status_rows)

            # Global metrics
            metric_database.insert_global_metrics(now=now, global_summary=global_summary)

            reset()


            flush_health.record_success()

        except Exception as e:
            flush_health.record_error(e)
            logger.error(f"Flush worker failed: {e}")