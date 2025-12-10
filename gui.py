import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading


try:
    from bb84 import run_bb84_simulation
    from e91 import run_e91_simulation
except ImportError as e:
    print(f"CRITICAL ERROR: {e}.")

class QKDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QKD Simulator (BB84 & E91)")
        self.root.geometry("1100x750")

        self.history_x = []
        self.history_y = []
        self.trial_counter = 0

        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.paned_window, padding="15")
        self.visual_frame = ttk.Frame(self.paned_window, padding="15")
        self.paned_window.add(self.control_frame, weight=1)
        self.paned_window.add(self.visual_frame, weight=4)

        self._init_controls()
        self._init_visuals()


    def _init_controls(self):
        lbl_title = ttk.Label(self.control_frame, text="Control Panel", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=(0, 20), anchor="w")

        # 1. Protocol Selection
        lbl_proto = ttk.Label(self.control_frame, text="Select Protocol:")
        lbl_proto.pack(pady=5, anchor="w")
        self.protocol_var = tk.StringVar(value="BB84")
        self.combo_proto = ttk.Combobox(self.control_frame, textvariable=self.protocol_var, state="readonly")
        self.combo_proto['values'] = ('BB84', 'E91')
        self.combo_proto.current(0)
        self.combo_proto.pack(fill="x", pady=5)
        self.combo_proto.bind("<<ComboboxSelected>>", self._reset_graphs)

        # 2. Key Size
        lbl_size = ttk.Label(self.control_frame, text="Number of Bits / Pairs:")
        lbl_size.pack(pady=(15, 5), anchor="w")
        self.size_var = tk.IntVar(value=50)
        self.spin_size = ttk.Spinbox(self.control_frame, from_=10, to=1000, textvariable=self.size_var)
        self.spin_size.pack(fill="x")

        # 3. Eve Checkbox
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=20)
        lbl_sec = ttk.Label(self.control_frame, text="Adversary (Eve)", font=("Helvetica", 11, "bold"))
        lbl_sec.pack(anchor="w")
        self.eve_var = tk.BooleanVar()
        self.chk_eve = ttk.Checkbutton(self.control_frame, text="Enable Intercept Attack", variable=self.eve_var)
        self.chk_eve.pack(pady=5, anchor="w")

        # 4. Noise Slider
        lbl_noise = ttk.Label(self.control_frame, text="Fiber Optic Noise (%):")
        lbl_noise.pack(pady=(15, 5), anchor="w")
        self.noise_val = tk.DoubleVar()
        self.slider_noise = ttk.Scale(self.control_frame, from_=0, to=50, variable=self.noise_val, orient='horizontal')
        self.slider_noise.pack(fill='x')
        self.lbl_noise_display = ttk.Label(self.control_frame, text="0.0%")
        self.lbl_noise_display.pack(anchor="e")
        self.slider_noise.configure(command=lambda v: self.lbl_noise_display.configure(text=f"{float(v):.1f}%"))
        
        # 5. Run Button
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=20)
        self.btn_run = ttk.Button(self.control_frame, text="RUN SIMULATION", command=self.run_simulation_thread)
        self.btn_run.pack(fill="x", ipady=10)
        
        self.progress = ttk.Progressbar(self.control_frame, mode='indeterminate')

        # 6. Status
        self.lbl_result_title = ttk.Label(self.control_frame, text="Current Status:", font=("Arial", 12, "bold"))
        self.lbl_result_title.pack(pady=(30, 5), anchor="w")
        self.lbl_metric = ttk.Label(self.control_frame, text="Metric: --", font=("Courier", 12))
        self.lbl_metric.pack(anchor="w")
        self.lbl_secure = ttk.Label(self.control_frame, text="Waiting...", foreground="gray")
        self.lbl_secure.pack(anchor="w")


    def _init_visuals(self):
        self.tabs = ttk.Notebook(self.visual_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.tab_logs = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_logs, text="Transmission Log")
        self.log_text = tk.Text(self.tab_logs, height=15, width=60, font=("Consolas", 10))
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tab_graphs = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_graphs, text="Analysis Charts")
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab_graphs)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._reset_graphs()


    def _reset_graphs(self, event=None):
        self.history_x = []
        self.history_y = []
        self.trial_counter = 0
        self.ax.clear()
        
        protocol = self.protocol_var.get()
        if protocol == "BB84":
            self.ax.set_title("BB84: QBER vs Trials")
            self.ax.set_ylabel("Error Rate (QBER)")
            self.ax.axhline(y=0.11, color='r', linestyle='--', label='Secure Limit (0.11)')
            self.ax.set_ylim(0, 0.55)
        else:
            self.ax.set_title("E91: CHSH S-Value")
            self.ax.set_ylabel("Bell Parameter S")
            self.ax.axhline(y=2.0, color='r', linestyle='--', label='Classical Limit (2.0)')
            self.ax.set_ylim(1.0, 3.0)
            
        self.ax.legend()
        self.ax.grid(True, alpha=0.5)
        self.canvas.draw()


    def run_simulation_thread(self):
        self.btn_run.config(state="disabled")
        self.progress.pack(fill='x', pady=5)
        self.progress.start()
        thread = threading.Thread(target=self.run_logic)
        thread.start()


    def run_logic(self):
        protocol = self.protocol_var.get()
        try:
            num_trials = int(self.size_var.get())
        except ValueError:
            num_trials = 50

        has_eve = self.eve_var.get()
        noise_level = self.noise_val.get() / 100.0
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Running {protocol} | Size: {num_trials} | Eve: {has_eve} | Noise: {noise_level:.2f}\n")
        self.log_text.insert(tk.END, "-"*60 + "\n")

        if protocol == "BB84":
            results = run_bb84_simulation(num_trials, noise_level, has_eve)
            self.root.after(0, lambda: self.update_gui_bb84(results))
        elif protocol == "E91":
            results = run_e91_simulation(num_trials, noise_level, has_eve)
            self.root.after(0, lambda: self.update_gui_e91(results))


    def update_gui_bb84(self, results):
        qber = results['qber']
        is_secure = qber < 0.11
        
        self.lbl_metric.config(text=f"QBER: {qber:.2%}")
        self._update_status(is_secure)
        
        self.log_text.insert(tk.END, f"Sifted Key Length: {results['sifted_size']}\n")
        self.log_text.insert(tk.END, f"Error Rate (QBER): {qber:.4f}\n")
        self.log_text.insert(tk.END, f"Alice Key: {results['alice_key'][:40]}...\n")
        
        self._update_graph(qber)
        self._finish_run()


    def update_gui_e91(self, results):
        s_value = results['s_value']
        is_secure = results['is_secure']
        
        self.lbl_metric.config(text=f"S-Value: {s_value:.3f}")
        self._update_status(is_secure)
        
        self.log_text.insert(tk.END, f"Total Bell Pairs: {results['total_pairs']}\n")
        self.log_text.insert(tk.END, f"Calculated S: {s_value:.4f}\n")
        if is_secure:
            self.log_text.insert(tk.END, "Result: VIOLATION (Quantum Entanglement)\n")
        else:
            self.log_text.insert(tk.END, "Result: NO VIOLATION (Classical/Eve)\n")
            
        self._update_graph(s_value)
        self._finish_run()


    def _update_status(self, is_secure):
        if is_secure:
            self.lbl_secure.config(text="Status: SECURE", foreground="green")
        else:
            self.lbl_secure.config(text="Status: INSECURE", foreground="red")


    def _update_graph(self, y_value):
        self.trial_counter += 1
        self.history_x.append(self.trial_counter)
        self.history_y.append(y_value)
        self.ax.plot(self.history_x, self.history_y, marker='o', linestyle='-', color='b')
        self.canvas.draw()


    def _finish_run(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_run.config(state="normal")