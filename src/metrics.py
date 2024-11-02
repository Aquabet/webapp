from statsd import StatsClient
import time

statsd_client = StatsClient(host="localhost", port=8125, prefix="WebAppMetrics")


def log_api_call_count(api_name):
    statsd_client.incr(f"{api_name}.count")


def log_api_call_duration(api_name, duration_ms):
    statsd_client.timing(f"{api_name}.duration", duration_ms)
