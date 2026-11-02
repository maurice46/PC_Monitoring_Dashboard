"""retrieve and manage information about running processes"""

import psutil
import os

class ProcessManager:
    # PIDs that should never be terminated from the dashboard
    PROTECTED_PIDS = {0, 1, 4}
    
    def __init__(self): 
        self.stored_processes = {}
        self.mb = 1024 ** 2
        self.cpu_count = psutil.cpu_count() or 1

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
    
    def sort_processes_by_cpu(self, processes=None): # sort processes by CPU utilization
        processes = (self.stored_processes if processes is None else processes)
        return sorted(
            processes.items(),
            key=lambda item: item[1]['cpu_percent'],
            reverse=True
        )
    
    def sort_processes_by_memory(self, processes=None): # sort processes by memory utilization
        processes = (self.stored_processes if processes is None else processes)
        return sorted(
            processes.items(),
            key=lambda item: item[1]['memory_percent'],
            reverse=True
        )
    
    def sort_processes_by_name(self, processes=None):
        processes = (self.stored_processes if processes is None else processes)
        return sorted(
            processes.items(),
            key=lambda item: item[1]['name'].casefold()
        )
    
    def search_processes(self, query, processes=None):
        processes = (self.stored_processes if processes is None else processes)

        query = str(query).strip().casefold()

        if not query:
            return dict(processes)

        return {
            pid: details 
            for pid, details in processes.items() 
            if (query in details['name'].casefold()) or (query in str(pid))
        }
    
    def get_process_details(self, process_id): # retrieve details for a specific PID
        try:
            process_id = int(process_id)
        except (TypeError, ValueError):
            return None

        details = self.stored_processes.get(process_id)

        if details is None:
            return None

        try:
            proc = psutil.Process(process_id)
            details = {**details, "useranme": proc.username(), "exe":proc.exe() or "Unavailable"}
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
        return details
    
    def terminate_process(self, process_id, timeout=3):
        try:
            process_id = int(process_id)
        except (TypeError, ValueError):
            return False
        
        # never terminate the dashboard itself or critical system PIDs
        if (process_id <= 0 or process_id == os.getpid() or process_id in self.PROTECTED_PIDS):
            return False

        # verify the process still matches the entry collected
        stored_details = self.stored_processes.get(process_id)
        
        try:
            process = psutil.Process(process_id)

            if stored_details is not None:
                stored_create_time = stored_details["create_time"]

                if (stored_create_time is not None and process.create_time() != stored_create_time):
                    # the PID may now belond to a different process
                    self.stored_processes.pop(process_id, None)
                    return False

            process.terminate()

            try:
                process.wait(timeout=timeout)
            except psutil.TimeoutExpired: # ignored the polite request, force it
                process.kill()
                process.wait(timeout=timeout)

            self.stored_processes.pop(process_id, None)
            return True
        
        # ZombieProcess is a subclass of NoSuchProcess
        except (psutil.ZombieProcess, psutil.NoSuchProcess):
            self.stored_processes.pop(process_id, None)
            return False
        
        except (psutil.AccessDenied, psutil.TimeoutExpired):
            return False



