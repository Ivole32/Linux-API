from collections import defaultdict
import numpy as np
import pickle
from tdigest import TDigest

route_data = defaultdict(list)
status_counts = defaultdict(int)

global_data = {
    "count": 0,
    "total_time": 0,
    "errors": 0,
}

def record(route: str, duration: float, status: int):
    route_data[route].append(duration)
    status_counts[(route, status)] += 1

    global_data["count"] += 1
    global_data["total_time"] += duration
    if status >= 500:
        global_data["errors"] += 1


def summarize():
    summary = {}
    for route, durations in route_data.items():
        arr = np.array(durations)

        # build a t-digest for mergeable percentile sketches
        td = TDigest()
        # TDigest.update accepts iterable of values
        td.update(arr.tolist())
        td_bytes = pickle.dumps(td)

        # percentiles from t-digest (fall back to numpy if not available)
        try:
            p50 = float(td.percentile(50))
            p95 = float(td.percentile(95))
            p99 = float(td.percentile(99))
        except Exception:
            p50 = float(np.percentile(arr, 50))
            p95 = float(np.percentile(arr, 95))
            p99 = float(np.percentile(arr, 99))

        summary[route] = {
            "count": len(arr),
            "avg": float(arr.mean()),
            "min": float(arr.min()),
            "max": float(arr.max()),
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "tdigest": td_bytes,
        }

    global_avg = (
        global_data["total_time"] / global_data["count"]
        if global_data["count"] else 0
    )

    global_summary = {
        "total_requests": global_data["count"],
        "avg_response_time": global_avg,
        "error_rate": (
            global_data["errors"] / global_data["count"]
            if global_data["count"] else 0
        )
    }

    return summary, status_counts.copy(), global_summary


def reset():
    route_data.clear()
    status_counts.clear()
    global_data.update({"count": 0, "total_time": 0, "errors": 0})