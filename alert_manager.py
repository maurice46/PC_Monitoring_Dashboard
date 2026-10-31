from system_monitor import SystemMonitor

class AlertManager:
    def __init__(self, cpu_threshold=85, memory_threshold=85, disk_threshold=90, monitor=None):
        # Store thresholds
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        # allow an existing SystemMonitor to be supplied
        self.monitor = monitor or SystemMonitor()
        self.active_alerts = {}

    def check_cpu(self, cpu_usage):
        if cpu_usage > self.cpu_threshold:
            self.active_alerts['cpu'] = (f"High CPU usage: {cpu_usage}%")
        else:
            self.active_alerts.pop('cpu', None)

    def check_memory(self, memory_usage):
        if memory_usage > self.memory_threshold:
            self.active_alerts['memory'] = (f"High memory usage: {memory_usage}%")
        else:
            self.active_alerts.pop('memory', None)

    def check_disk(self, disk_usage):
        if disk_usage > self.disk_threshold:
            self.active_alerts['disk'] = (f"High disk usage: {disk_usage}%")
        else:
            self.active_alerts.pop('disk', None)

    def check_all(self):
        # collect the latest system readings 
        cpu = self.monitor.get_cpu_usage()
        memory = self.monitor.get_memory_usage()
        disk = self.monitor.get_disk_usage()

        self.check_cpu(cpu)
        self.check_memory(memory['percent'])
        self.check_disk(disk['percent'])

        return self.get_active_alerts()

    def get_active_alerts(self):
        return list(self.active_alerts.values())

    def clear_alerts(self):
        self.active_alerts.clear()

