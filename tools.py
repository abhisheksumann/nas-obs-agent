import os
import requests
from datetime import datetime

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://192.168.1.116:9090")


def query_prometheus(promql: str) -> dict:
    """Execute a PromQL instant query and return the result."""
    try:
        r = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": promql},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_disk_usage() -> str:
    """Return disk usage percentage for all mounted filesystems."""
    result = query_prometheus(
        '100 - ((node_filesystem_avail_bytes{fstype!="tmpfs"} '
        '/ node_filesystem_size_bytes{fstype!="tmpfs"}) * 100)'
    )
    if "error" in result:
        return f"Error: {result['error']}"
    lines = []
    for item in result.get("data", {}).get("result", []):
        mount = item["metric"].get("mountpoint", "unknown")
        pct = float(item["value"][1])
        lines.append(f"{mount}: {pct:.1f}% used")
    return "\n".join(lines) if lines else "No data"


def get_memory_usage() -> str:
    """Return current RAM and swap usage percentages."""
    ram = query_prometheus(
        '100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))'
    )
    swap = query_prometheus(
        '100 * (node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes) '
        '/ node_memory_SwapTotal_bytes'
    )
    ram_pct = float(ram["data"]["result"][0]["value"][1]) \
        if ram.get("data", {}).get("result") else 0
    swap_pct = float(swap["data"]["result"][0]["value"][1]) \
        if swap.get("data", {}).get("result") else 0
    return f"RAM: {ram_pct:.1f}% used\nSwap: {swap_pct:.1f}% used"


def get_cpu_usage() -> str:
    """Return current CPU usage percentage (5 minute average)."""
    result = query_prometheus(
        '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    )
    if result.get("data", {}).get("result"):
        pct = float(result["data"]["result"][0]["value"][1])
        return f"CPU: {pct:.1f}% used (5m avg)"
    return "No CPU data"


def get_disk_health() -> str:
    """Return SMART health status for all monitored disks."""
    result = query_prometheus('smartctl_device_smart_status')
    if "error" in result:
        return f"Error: {result['error']}"
    lines = []
    for item in result.get("data", {}).get("result", []):
        device = item["metric"].get("device", "unknown")
        status = "HEALTHY" if item["value"][1] == "1" else "FAILING"
        lines.append(f"{device}: {status}")
    return "\n".join(lines) if lines else "No SMART data available"


def get_container_status() -> str:
    """Return running/stopped status for all Docker containers."""
    result = query_prometheus('container_last_seen{name!=""}')
    if "error" in result:
        return f"Error: {result['error']}"
    now = datetime.now().timestamp()
    lines = []
    seen = set()
    for item in result.get("data", {}).get("result", []):
        name = item["metric"].get("name", "unknown")
        if name in seen:
            continue
        seen.add(name)
        last_seen = float(item["value"][1])
        age_seconds = now - last_seen
        status = "UP" if age_seconds < 60 else "DOWN"
        lines.append(f"{name}: {status}")
    return "\n".join(sorted(lines)) if lines else "No container data"


def get_alerts() -> str:
    """Return any currently firing Prometheus alerts."""
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=10)
        r.raise_for_status()
        alerts = r.json().get("data", {}).get("alerts", [])
        firing = [a for a in alerts if a.get("state") == "firing"]
        if not firing:
            return "No alerts firing"
        return "\n".join(
            f"{a['labels'].get('alertname', 'unknown')}: "
            f"{a['annotations'].get('summary', '')}"
            for a in firing
        )
    except Exception as e:
        return f"Error: {e}"


def get_full_health_summary() -> str:
    """Aggregate all health checks into one context block for the LLM."""
    return f"""=== NAS Health Summary — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===

[CPU]
{get_cpu_usage()}

[Memory]
{get_memory_usage()}

[Disk usage]
{get_disk_usage()}

[Disk SMART health]
{get_disk_health()}

[Container status]
{get_container_status()}

[Active alerts]
{get_alerts()}
"""
