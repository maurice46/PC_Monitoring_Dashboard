"""retrieve and manage information about running processes"""

import psutil

class ProcessManager:
    # PIDs that should never be terminated from the dashboard
    PROTECTED_PIDS = {0, 1, 4}
    
    def __init__(self): 
        self.stored_processes = {}
        self.mb = 1024 ** 2
        self.cpu_count = psutil.cpu_count() or 1

        # the first cpu_percent reading for a process is always 0.0 (nothing to compare against)
        # so take one throwaway reading now, the first real refresh will then have a baseline
        for process in psutil.process_iter(['cpu_percent']):
            pass

    def get_running_processes(self): # get process information (attributes)
        processes = {}
        attributes = ['pid', 'name', 'cpu_percent', 'memory_info', 'memory_percent', 'status', 'username', 'create_time', 'exe']
        
        for process in psutil.process_iter(attrs=attributes):
            try:
                info = process.info
                pid = info['pid']
                memory_info = info['memory_info']

                # normalize cpu usage to a max of approxamialtey 100^%
                cpu_percent = ((info['cpu_percent'] or 0.0) / self.cpu_count)

                memory_rss = (memory_info.rss if memory_info is not None else 0)

                processes[pid] = {
                    "pid": pid,
                    "name": info['name'] or "Unknown",
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_rss": memory_rss,
                    "memory_mb": round(memory_rss / self.mb, 2),
                    "memory_percent": info['memory_percent'] or 0.0,
                    "status": info['status'] or "Unknown",
                    "username": info['username'] or "Unknown",
                    "create_time": info['create_time'],
                    "exe": info["exe"] or "Unavailable"
                }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # the process may exit or deny access during collection
                continue

        self.stored_processes = processes
        return self.stored_processes


