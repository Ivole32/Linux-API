"""performance update

Revision ID: 4fafc0d8ed73
Revises: 9743ea8d3047
Create Date: 2026-02-18 20:16:15.073329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fafc0d8ed73'
down_revision: Union[str, Sequence[str], None] = '9743ea8d3047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create indexes (hypertables do not support CONCURRENTLY)
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_route_metrics_route_time "
            "ON metrics.route_metrics (route, time DESC);"
        )

        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_route_status_codes_route_status_time "
            "ON metrics.route_status_codes (route, status_code, time DESC);"
        )

        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_route_metrics_time_brin "
            "ON metrics.route_metrics USING BRIN (time);"
        )

    # CREATE MATERIALIZED VIEW WITH DATA cannot run inside a transaction block
    # run these statements outside the migration transaction
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS metrics.route_metrics_hourly
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket('1 hour', time) AS bucket,
                route,
                SUM(requests) AS requests,
                (CASE WHEN SUM(requests) = 0 THEN NULL ELSE SUM(avg_response_time * requests) / SUM(requests) END) AS avg_response_time,
                MIN(min_response_time) AS min_response_time,
                MAX(max_response_time) AS max_response_time
            FROM metrics.route_metrics
            GROUP BY bucket, route;
            """
        )

        op.execute(
            """
            SELECT add_continuous_aggregate_policy('metrics.route_metrics_hourly',
                start_offset => INTERVAL '1 day',
                end_offset   => INTERVAL '1 hour',
                schedule_interval => INTERVAL '1 hour');
            """
        )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("SELECT remove_continuous_aggregate_policy('metrics.route_metrics_hourly');")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS metrics.route_metrics_hourly;")

    with op.get_context().autocommit_block():
        op.execute("DROP INDEX IF EXISTS metrics.idx_route_metrics_route_time;")
        op.execute("DROP INDEX IF EXISTS metrics.idx_route_status_codes_route_status_time;")
        op.execute("DROP INDEX IF EXISTS metrics.idx_route_metrics_time_brin;")
        op.execute("DROP INDEX IF EXISTS metrics.idx_route_metrics_hourly_route_bucket;")