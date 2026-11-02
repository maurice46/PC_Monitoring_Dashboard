"""collect system resource usage statistics: CPU, Memory, Disk"""

import psutil
import os

class SystemMonitor:
    def __init__(self, disk_path=None):
        self.disk_path = disk_path or os.path.abspath(os.sep) # default to root of current drive 
        self.gb = 1024 ** 3

        # initialize CPU measurement 
        psutil.cpu_percent(interval=None) 

    def get_cpu_usage(self, interval=None):
        # interval=None doesn't block: it compares against the previous call
        # a blocking interval would freeze the tk window while it waits 
        return psutil.cpu_percent(interval=interval) 

    def get_memory_usage(self):
        memory = psutil.virtual_memory()

        return {
            "total": round(memory.total / self.gb, 2),
            "used": round(memory.used / self.gb, 2),
            "available": round(memory.available / self.gb, 2),
            "percent": memory.percent
        }

    def get_disk_usage(self, path=None):
        disk = psutil.disk_usage(path or self.disk_path)

        return {
            "total": round(disk.total / self.gb, 2),
            "used": round(disk.used / self.gb, 2),
            "free": round(disk.free / self.gb, 2),
            "percent": disk.percent
        }


