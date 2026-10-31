"""Collect network statistics."""

import psutil
import time

class NetworkMonitor:
    def __init__(self):
        self.previous_stats = psutil.net_io_counters()
        self.previous_time = time.monotonic()

    def get_network_stats(self):
        stats = psutil.net_io_counters()

        return {
            "bytes_sent": stats.bytes_sent,
            "bytes_received": stats.bytes_recv
        }
    
    def get_network_speed(self):
        current_stats = psutil.net_io_counters()
        current_time = time.monotonic()

        previous_stats = self.previous_stats
        elapsed_time = current_time - self.previous_time

        # always advance the baseline
        self.previous_stats = current_stats
        self.previous_time = current_time

        upload = 0.0
        download = 0.0

        if elapsed_time > 0:
            upload_delta = current_stats.bytes_sent - previous_stats.bytes_sent
            download_delta = current_stats.bytes_recv - previous_stats.bytes_recv
            upload = max(0.0, upload_delta / elapsed_time)
            download = max(0.0, download_delta / elapsed_time)

        result = {
            "upload": upload,                         # bytes per second
            "download": download,                     # bytes per second
            "upload_mbps": upload * 8 / 1_000_000,
            "download_mbps": download * 8 / 1_000_000
        }

        return result
