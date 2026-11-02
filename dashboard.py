import tkinter as tk
from tkinter import ttk, messagebox

from system_monitor import SystemMonitor
from network_monitor import NetworkMonitor
from process_manager import ProcessManager
from alert_manager import AlertManager

class Dashboard:
    BG = "#20242c"
    CARD_BG = "#303744"
    FG = "#ffffff"
    MUTED = "#9ca3af"
    BLUE = "#3b82f6"
# ------------------------------------ setup --------------------------------------
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.network_monitor = NetworkMonitor()
        self.process_manager = ProcessManager()
        # self.alert_manager = AlertManager(monitor=self.system_monitor)

        # id of the pending window.after() call (so Refresh can't stack timers)
        self.update_job = None
        self.sort_column = "cpu_percent"
        self.sort_reverse = True

        self.window = tk.Tk()
        self.window.title("PC Monitoring Dashboard")
        self.window.geometry("1000x700")
        self.window.minsize(850, 600)
        self.window.config(bg=self.BG)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # variables connected to the process manager controls
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="CPU")

        self.create_metric_widgets()
        self.display_process_frame()
        self.update_monitors()
        
    def create_metric_widgets(self):
        self.title_label = tk.Label(self.window, 
                                    text="Monitoring Dashboard", 
                                    font=("Segoe UI", 18, "bold"),
                                    bg=self.BG,
                                    fg=self.FG)
        self.title_label.pack(pady=(10,5))

        # container for the metric sections
        self.metrics_frame = tk.Frame(self.window, bg=self.BG)
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

        # allow cards to share available width 
        # uniform makes every column the same width no matter how long its text is 
        for col in range(3): # 3 columns 
            self.metrics_frame.grid_columnconfigure(col, weight=1, uniform="cards")
        for row in range(2): # lets stciky='new' make the cards the same height
            self.metrics_frame.grid_rowconfigure(row, weight=1, uniform="rows") 
    
    def create_frame(self, title):
        frame = tk.Frame(self.metrics_frame, bg="#303744")
        tk.Label(frame,
                 text=title,
                 font=("Segoe UI", 12, "bold"),
                 bg="#303744",
                 fg='white').pack(pady=(5,3))
        return frame

    def add_metric_label(self, parent, text, font=("Segoe UI", 10), bg="#303744", fg="#ffffff"):
        label = tk.Label(parent, text=text, font=font, bg=bg, fg=fg, anchor="w")
        label.pack(fill="x", padx=10, pady=2)
        return label

    def close(self):
        if self.update_job is not None:
            self.window.after_cancel(self.update_job)
            self.update_job = None
        self.window.destroy()

# ------------------------------ display metric cards ---------------------------------

    def display_cpu_frame(self): 
        self.cpu_frame = self.create_frame("CPU")
        self.cpu_usage = self.system_monitor.get_cpu_usage()
        self.cpu_label = self.add_metric_label(parent=self.cpu_frame, 
                                               text=f"Usage: {self.cpu_usage}%")

    def display_memory_frame(self):
        self.memory_frame = self.create_frame("MEMORY")
        self.memory_usage = self.system_monitor.get_memory_usage()
        self.memory_total = self.add_metric_label(parent=self.memory_frame, 
                                                  text=f"Total: {self.memory_usage['total']:.2f} GB")
        
        self.memory_used = self.add_metric_label(parent=self.memory_frame,
                                                 text=f"Used: {self.memory_usage['used']:.2f} GB")
 
        self.memory_available = self.add_metric_label(parent=self.memory_frame,
                                                      text=f"Available: {self.memory_usage['available']:.2f} GB")

        self.memory_percent = self.add_metric_label(parent=self.memory_frame,
                                                    text=f"Usage: {self.memory_usage['percent']}%")

    def display_disk_frame(self):
        self.disk_frame = self.create_frame("DISK")
        self.disk_usage = self.system_monitor.get_disk_usage()

        self.disk_total = self.add_metric_label(parent=self.disk_frame, 
                                                text=f"Total: {self.disk_usage['total']:.2f} GB")

        self.disk_used = self.add_metric_label(parent=self.disk_frame, 
                                               text=f"Used: {self.disk_usage['used']:.2f} GB")

        self.disk_free = self.add_metric_label(parent=self.disk_frame, 
                                               text=f"Free: {self.disk_usage['free']:.2f} GB")

        self.disk_percent = self.add_metric_label(parent=self.disk_frame, 
                                                  text=f"Usage: {self.disk_usage['percent']:.1f}%")

    def display_bytes_frame(self):
        self.network_stats_frame = self.create_frame("BYTES")
        self.network_stats = self.network_monitor.get_network_stats()

        self.network_bytes_received = self.add_metric_label(parent=self.network_stats_frame,
                                                            text=f"Bytes Received: {self.network_stats['bytes_received'] / 1024 ** 3:.2f} GB")


        self.network_bytes_sent = self.add_metric_label(parent=self.network_stats_frame,
                                                        text=f"Bytes Sent: {self.network_stats['bytes_sent'] / 1024 ** 3:.2f} GB")

    def display_network_frame(self):
        self.network_speed_frame = self.create_frame("SPEED")
        self.network_speed_stats = self.network_monitor.get_network_speed()

        self.upload_mbps = self.add_metric_label(parent=self.network_speed_frame,
                                                 text=f"Upload (mbps): {self.network_speed_stats['upload_mbps']:.2f}")

        self.download_mbps = self.add_metric_label(parent=self.network_speed_frame,
                                                   text=f"Download (mbps): {self.network_speed_stats['download_mbps']:.2f}")

    def display_button_frame(self):
            self.metrics_refresh_button_frame = self.create_frame("MONITORING")

            self.metrics_refresh_button = tk.Button(self.metrics_refresh_button_frame,
                                                    text="Refresh",
                                                    font=("Segoe UI", 10, "bold"),
                                                    bg="#3b82f6",
                                                    fg="white",
                                                    activebackground="#2563eb",
                                                    activeforeground="white",
                                                    relief="flat",
                                                    command=self.update_monitors,
                                                    cursor="hand2")  
            self.metrics_refresh_button.pack(padx=10, pady=(5,4))
           
            self.metrics_status_label = tk.Label(self.metrics_refresh_button_frame,
                                                text="Monitoring System Resources...",
                                                font=("Segoe UI", 9),
                                                bg="#20242c",
                                                fg='#9ca3af',
                                                wraplength=180)
            self.metrics_status_label.pack(padx=10, pady=(0,5))

    def display_process_frame(self):
        pass

    def display_alert_frame  (self):
        pass


 
# ------------------------------ updating stuff --------------------------

    def update_monitors(self):
        if self.update_job is not None:
            self.window.after_cancel(self.update_job)

        # update cpu stuff 
        self.cpu_usage = self.system_monitor.get_cpu_usage()
        self.cpu_label.config(text=f'Usage: {self.cpu_usage:.1f}%')

        # update memory stuff
        mem = self.system_monitor.get_memory_usage()
        self.memory_total.config(text=f"Total: {mem['total']:.2f} GB")
        self.memory_used.config(text=f"Used: {mem['used']:.2f} GB")
        self.memory_available.config(text=f"Available: {mem['available']:.2f} GB")
        self.memory_percent.config(text=f"Usage: {mem['percent']}%")

        # update disk stuff
        disk = self.system_monitor.get_disk_usage()
        self.disk_total.config(text=f"Total: {disk['total']:.2f} GB")
        self.disk_used.config(text=f"Used: {disk['used']:.2f} GB")
        self.disk_free.config(text=f"Free: {disk['free']:.2f} GB")
        self.disk_percent.config(text=f"Usage: {disk['percent']:.1f}%")

        # update byte stuff
        stats = self.network_monitor.get_network_stats()
        self.network_bytes_received.config(text=f"Bytes Received: {stats['bytes_received'] / 1024 ** 3:.2f} GB")
        self.network_bytes_sent.config(text=f"Bytes Sent: {stats['bytes_sent'] / 1024 ** 3:.2f} GB")

        # update network stuff
        speed = self.network_monitor.get_network_speed()
        self.upload_mbps.config(text=f"Upload (mbps): {speed['upload_mbps']:.2f}")
        self.download_mbps.config(text=f"Download (mbps): {speed['download_mbps']:.2f}")

        self.update_job = self.window.after(2000, self.update_monitors)

    def run(self):
        self.window.mainloop()

a = Dashboard()
a.run()


