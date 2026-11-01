import tkinter as tk
from system_monitor import SystemMonitor
from network_monitor import NetworkMonitor
from process_manager import ProcessManager
from alert_manager import AlertManager

class Dashboard:
# ------------------------------------ setup --------------------------------------
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.network_monitor = NetworkMonitor()
        self.process_manager = ProcessManager()
        # self.alert_manager = AlertManager(monitor=self.system_monitor)

        # id of the pending window.after() call (so Refresh can't stack timers)
        self.update_job = None

        self.window = tk.Tk()
        self.window.title("PC Monitoring Dashboard")
        self.window.geometry("1000x700")
        self.window.config(bg="#20242c")

        self.create_metric_widgets()
        self.update_monitors()
        
    def create_metric_widgets(self):
        self.title_label = tk.Label(self.window, 
                                    text="Monitoring Dashboard", 
                                    font=("Segoe UI", 18, "bold"),
                                    bg="#20242c",
                                    fg='white')
        self.title_label.pack(pady=(10,5))

        # container for the metric sections
        self.metrics_frame = tk.Frame(self.window, bg="#20242c")
        self.metrics_frame.pack(fill='x', padx=10, pady=5)

        # create metric cards 
        self.display_cpu_frame()
        self.display_memory_frame()
        self.display_disk_frame()
        self.display_bytes_frame()
        self.display_network_frame()
        self.display_button_frame()

        # arrange cards in a row
        # only frames that were created with create_frame() go in the grid 
        # the BYTES laybel lives inside network_stats_frame, so the frame is what gets gridded, not the labels
        self.cpu_frame.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.memory_frame.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.disk_frame.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self.network_stats_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        self.network_speed_frame.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        self.metrics_refresh_button_frame.grid(row=1, column=2, padx=8, pady=8, sticky="nsew")
        self.

        # allow cards to share available width 
        # uniform makes every column the same width no matter how long its text is 
        for col in range(3): # 3 columns 
            self.metrics_frame.grid_columnconfigure(col, weight=1, uniform="cards")
        for row in range(3): # lets stciky='new' make the cards the same height
            self.metrics_frame.grid_rowconfigure(row, weight=1, uniform="rows") 

    def display_button_frame(self):
        # create metrics refresh button
        self.metrics_refresh_button_frame = self.create_frame("BUTTON")
        self.metrics_refresh_button_frame.pack(pady=10)
        self.metrics_refresh_button = tk.Button(self.metrics_refresh_button_frame,
                                                text="Refresh",
                                                font=("Segoe UI", 10, "bold"),
                                                bg="#3b82f6",
                                                fg="white",
                                                activebackground="#2563eb",
                                                activeforeground="white",
                                                relief="flat",
                                                command=self.update_monitors) # does the updating 
        self.metrics_refresh_button.pack()
       
        self.metrics_status_label = tk.Label(self.metrics_refresh_button_frame,
                                            text="Monitoring System Resources...",
                                            font=("Segoe UI", 9),
                                            bg="#20242c",
                                            fg='#9ca3af')
        self.metrics_status_label.pack()
    
    def create_frame(self, title):
        frame = tk.Frame(self.metrics_frame, bg="#303744")
        tk.Label(frame,
                 text=title,
                 font=("Segoe UI", 12, "bold"),
                 bg="#303744",
                 fg='white').pack()
        return frame

# ------------------------------ system monitoring ---------------------------------

    def display_cpu_frame(self): 
        self.cpu_frame = self.create_frame("CPU")
        self.cpu_usage = self.system_monitor.get_cpu_usage()
        self.cpu_label = tk.Label(self.cpu_frame, 
                                  text=f"Usage: {self.cpu_usage}%",
                                  font=("Segoe UI", 12, "bold"),
                                  bg="#303744",
                                  fg="#60a5fa")
        self.cpu_label.pack()

    def display_memory_frame(self):
        self.memory_frame = self.create_frame("MEMORY")
        self.memory_usage = self.system_monitor.get_memory_usage()
        self.memory_total = tk.Label(self.memory_frame,
                                     text=f"Total: {self.memory_usage['total']:.2f} GB",
                                     bg="#303744",
                                     fg="white")
        self.memory_total.pack()
        self.memory_used = tk.Label(self.memory_frame,
                                    text=f"Used: {self.memory_usage['used']:.2f} GB",
                                    bg="#303744",
                                    fg="white")
        self.memory_used.pack()
        self.memory_available = tk.Label(self.memory_frame,
                                         text=f"Available: {self.memory_usage['available']:.2f} GB",
                                         bg="#303744",
                                         fg="white")
        self.memory_available.pack()
        self.memory_percent = tk.Label(self.memory_frame,
                                       text=f"Usage: {self.memory_usage['percent']}%",
                                       bg="#303744",
                                       fg="white")
        self.memory_percent.pack()
        
    def display_disk_frame(self):
        self.disk_frame = self.create_frame("DISK")

        self.disk_usage = self.system_monitor.get_disk_usage()

        self.disk_total = tk.Label(self.disk_frame, 
                                   text=f"Total: {self.disk_usage['total']:.2f} GB",
                                   bg="#303744",
                                   fg="white")
        self.disk_total.pack()

        self.disk_used = tk.Label(self.disk_frame, 
                                  text=f"Used: {self.disk_usage['used']:.2f} GB",
                                  bg="#303744",
                                  fg="white")
        self.disk_used.pack()

        self.disk_free = tk.Label(self.disk_frame, 
                                  text=f"Free: {self.disk_usage['free']:.2f} GB",
                                  bg="#303744",
                                  fg="white")
        self.disk_free.pack()

        self.disk_percent = tk.Label(self.disk_frame, 
                                     text=f"Usage: {self.disk_usage['percent']:.1f}%",
                                     bg="#303744",
                                     fg="white")
        self.disk_percent.pack()

# ------------------------------ network monitoring ---------------------------------

    def display_bytes_frame(self):
        self.network_stats_frame = self.create_frame("BYTES")

        self.network_stats = self.network_monitor.get_network_stats()

        self.network_bytes_received = tk.Label(self.network_stats_frame,
                                               text=f"Bytes Received: {self.network_stats['bytes_received'] / 1024 ** 3:.2f} GB",
                                               bg="#303744",
                                               fg="white")
        self.network_bytes_received.pack()

        self.network_bytes_sent = tk.Label(self.network_stats_frame,
                                           text=f"Bytes Sent: {self.network_stats['bytes_sent'] / 1024 ** 3:.2f} GB",
                                           bg="#303744",
                                           fg="white")
        self.network_bytes_sent.pack()

    def display_network_frame(self):
        self.network_speed_frame = self.create_frame("SPEED")

        self.network_speed_stats = self.network_monitor.get_network_speed()

        self.upload_mbps = tk.Label(self.network_speed_frame,
                                    text=f"Upload (mbps): {self.network_speed_stats['upload_mbps']:.2f}",
                                    bg="#303744",
                                    fg="white")
        self.upload_mbps.pack()

        self.download_mbps = tk.Label(self.network_speed_frame,
                                      text=f"Download (mbps): {self.network_speed_stats['download_mbps']:.2f}",
                                      bg="#303744",
                                      fg="white")
        self.download_mbps.pack()

# ------------------------------ process manager ---------------------------------
    def display_process_frame(self):
        self.process_frame = self.create_frame("PROCESS")

        self.process_information = self.process_manager.get_running_processes()

        for pid, process in self.process_information.items():
            tk.Label(self.process_frame,
                     text=f"Process {process['pid']}: {process['name']} | \
                     Memory Usage (%): {process['memory_percent']} | Status: \
                     {process['status']} | Created At: {process['create_time']}").pack()


# -----------------------------------------------------------------------------------

    def update_monitors(self):
        # cancel the timer that is already waiting, so clicking Refresh restarts the 4.5s
        # countdown instead of starting a second, overlapping update loop
        if self.update_job is not None:
            self.window.after_cancel(self.update_job)
            self.update_job = None

        try:
            # system monitoring stuff 
            self.cpu_usage = self.system_monitor.get_cpu_usage(interval=None)
            self.memory_usage = self.system_monitor.get_memory_usage()
            self.disk_usage = self.system_monitor.get_disk_usage()

            # update CPU
            self.cpu_label.config(text=f'Usage: {self.cpu_usage:.1f}%')

            # update memory
            self.memory_used.config(text=f"Used: {self.memory_usage['used']:.1f} GB")
            self.memory_available.config(text=f"Available: {self.memory_usage['available']:.1f} GB")
            self.memory_percent.config(text=f"Usage: {self.memory_usage['percent']:.1f}%")

            # update disk
            self.disk_used.config(text=f"Used: {self.disk_usage['used']:.1f} GB")
            self.disk_free.config(text=f"Free: {self.disk_usage['free']:.1f} GB")
            self.disk_percent.config(text=f"Usage: {self.disk_usage['percent']:.1f}%")

            # network monitoring stuff
            self.network_stats = self.network_monitor.get_network_stats()
            self.network_speed_stats = self.network_monitor.get_network_speed()

            # update bytes received
            self.network_bytes_received.config(text=f"Bytes Received: {self.network_stats['bytes_received'] / 1024 ** 3:.2f} GB")

            # update bytes sent 
            self.network_bytes_sent.config(text=f"Bytes Sent: {self.network_stats['bytes_sent'] / 1024 ** 3:.2f} GB")

            # update upload speed
            self.upload_mbps.config(text=f"Upload (mbps): {self.network_speed_stats['upload_mbps']:.2f}")

            # update download speed
            self.download_mbps.config(text=f"Download (mbps): {self.network_speed_stats['download_mbps']:.2f}")

            # clear any earlier error message
            self.metrics_status_label.config(text="Monitoring System Resources...")

        except Exception as error:
            self.title_label.config(text=f"Monitoring Error: {error}")

        finally:
            # schedule another update roughly every 4.5 seconds
            self.window.after(4500, self.update_monitors)

    def run(self):
        self.window.mainloop()

dashboard = Dashboard()
dashboard.run()


