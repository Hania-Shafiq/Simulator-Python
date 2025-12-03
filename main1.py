# Sapphire Shopping Outlet - Queue Simulator
import math
import random
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ---------------- 1. RANDOM NUMBER GENERATORS ---------------- #
def get_interarrival_time(dist_type, lam):
    if dist_type == "Poisson" or dist_type == "Exponential":
        return -math.log(1 - random.random()) / lam
    else:  # General
        mean_t = 1/lam
        return random.uniform(mean_t * 0.5, mean_t * 1.5)

def get_service_time(dist_name, mu, params):
    mean_service_time = 1.0 / mu if mu > 0 else 1.0
    try:
        if dist_name == "Exponential" or dist_name == "Poisson":
            return -math.log(1 - random.random()) / mu
        elif dist_name == "Uniform":
            if "," in params:
                a, b = map(float, params.split(","))
                return random.uniform(a, b)
            else:
                return random.uniform(mean_service_time * 0.5, mean_service_time * 1.5)
        elif dist_name == "Normal":
            sigma = float(params) if params else mean_service_time * 0.2
            val = random.normalvariate(mean_service_time, sigma)
            return max(0.01, val)
        elif dist_name == "Gamma":
            alpha = 2.0
            beta = mean_service_time / alpha
            val = random.gammavariate(alpha, beta)
            return max(0.01, val)
        else:
            return -math.log(1 - random.random()) / mu
    except:
        return -math.log(1 - random.random()) / mu

# ---------------- 2. ANALYTICAL FORMULAS ---------------- #
def get_scv(dist_name, mean_val, params):
    if dist_name in ["Exponential", "Poisson", "M"]:
        return 1.0
    variance = 0.0
    if dist_name == "Uniform":
        if "," in params:
            a, b = map(float, params.split(","))
            variance = ((b - a)**2) / 12
        else:
            variance = (mean_val**2) / 12
    elif dist_name == "Normal":
        sigma = float(params) if params else mean_val * 0.2
        variance = sigma**2
    elif dist_name == "Gamma":
        alpha = 2.0
        variance = (mean_val**2) / alpha
    return variance / (mean_val**2)

def calculate_analytical(queue_type, lam, mu, c, dist_name="Exponential", dist_params=""):
    rho = lam / (c * mu)
    if rho >= 1:
        return {"Error": "System Unstable (ρ ≥ 1). Arrival rate > Service capacity."}, None
    Lq, Wq, L, W = 0, 0, 0, 0

    if queue_type == "MM1":
        Lq = (rho**2) / (1 - rho)
        Wq = Lq / lam
        W = Wq + (1/mu)
        L = lam * W
    elif queue_type == "MMC":
        r = lam / mu
        sum_part = sum([(r**m)/math.factorial(m) for m in range(c)])
        last_term = (r**c) / (math.factorial(c) * (1 - rho))
        P0 = 1.0 / (sum_part + last_term)
        Lq = (P0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
        Wq = Lq / lam
        W = Wq + (1 / mu)
        L = Lq + r
    elif queue_type in ["GG1", "MG1"]:
        Ca2 = 1.0
        if queue_type.startswith("G"):
            Ca2 = get_scv("Uniform", 1/lam, "")
        Cs2 = get_scv(dist_name, 1/mu, dist_params)
        if queue_type == "MG1":
            var_s = Cs2 * (1/mu)**2
            numerator = (lam**2)*var_s + rho**2
            Lq = numerator / (2*(1-rho))
        else:
            term1 = (rho**2) / (2 * (1 - rho))
            term2 = (1 + Cs2)
            term3 = (Ca2 + (rho**2)*Cs2)
            term4 = (1 + (rho**2)*Cs2)
            Lq = term1 * term2 * (term3 / term4)
        Wq = Lq / lam
        W = Wq + (1 / mu)
        L = lam * W
    else:
        r = lam / mu
        sum_part = sum([(r**m)/math.factorial(m) for m in range(c)])
        last_term = (r**c) / (math.factorial(c) * (1 - rho))
        P0 = 1.0 / (sum_part + last_term)
        Lq_mmc = (P0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
        Wq_mmc = Lq_mmc / lam
        Ca2 = 1.0
        if queue_type.startswith("G"):
             Ca2 = get_scv("Uniform", 1/lam, "")
        Cs2 = get_scv(dist_name, 1/mu, dist_params)
        Wq = Wq_mmc * ((Ca2 + Cs2) / 2)
        Lq = Wq * lam
        W = Wq + (1/mu)

    results = {
        "Traffic Intensity (ρ)": round(rho, 4),
        "Lq (Queue Length)": round(Lq, 4),
        "Wq (Wait in Queue)": round(Wq, 4),
        "W (Total System Time)": round(W, 4),
        "L (Total Customers)": round(L, 4)
    }
    return results, rho


# ---------------- 3. TIME FORMATTING HELPER ---------------- #
def format_time(minutes):
    """Convert minutes to HH:MM format"""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

# ---------------- 4. SIMULATION LOGIC (SAPPHIRE - SEQUENTIAL IDs!) ---------------- #

# ---------------- 3. SIMULATION LOGIC ---------------- #

def generate_arrivals_strict(lam, max_cp=0.99999, max_events=5000):
    """
    Deterministic arrivals for a given lambda (lam).
    Uses a local RNG seeded from lam so that same lam -> same arrivals & CPs,
    while leaving the global RNG untouched (so service randomness remains).
    """
    # Create a local RNG seeded deterministically from lam
    # Multiply lam by a constant and convert to int to avoid float hashing issues.
    seed = int(round(lam * 1000000)) & 0x7fffffff
    local_rng = random.Random(seed)

    arrivals = []
    cp_list = []
    cp_lookup = []

    t = 0.0
    prev_cp = 0.0

    # generate interarrivals using the local RNG (exponential)
    while True:
        # generate exponential interarrival using the local RNG
        u = local_rng.random()
        interarrival = -math.log(1 - u) / lam
        t += interarrival

        calculated_cp = 1 - math.exp(-lam * t)
        if calculated_cp >= max_cp:
            break

        # don't scale/round to integers — keep float times (rounded only for display)
        arrivals.append(t)
        cp_list.append(round(calculated_cp, 5))
        cp_lookup.append(round(prev_cp, 5))

        prev_cp = calculated_cp
        if len(arrivals) >= max_events:
            break

    return arrivals, cp_list, cp_lookup

def simulate_queue_engine(arrival_type, arrival_dist, service_type, service_dist, lam, mu, servers, service_params=""):
    # generate arrivals (deterministic for given lam)
    arrivals, cp_list, cp_lookup = generate_arrivals_strict(lam)
    num_servers = servers
    server_end_times = [0.0] * num_servers
    server_busy_log = [[] for _ in range(num_servers)]
    rows = []
    max_end_time = 0

    for i in range(len(arrivals)):
        arrival_t = arrivals[i]     # float, deterministic for given lam
        cust_id = i + 1

        # DO NOT call get_interarrival_time() here — it consumes global RNG and ruins reproducibility of arrivals
        srv_time = get_service_time(service_dist, mu, service_params)  # keep global RNG for service randomness
        queue_join_time = arrival_t

        next_free_server_idx = server_end_times.index(min(server_end_times))
        start_t = max(arrival_t, server_end_times[next_free_server_idx])
        end_t = start_t + srv_time
        wait_t = start_t - queue_join_time
        turnaround_t = end_t - arrival_t

        server_end_times[next_free_server_idx] = end_t
        server_busy_log[next_free_server_idx].append((start_t, srv_time, cust_id))
        max_end_time = max(max_end_time, end_t)

        rows.append([
            cust_id,
            format_time(arrival_t),           # display conversion remains
            round(srv_time, 2),
            f"S{next_free_server_idx+1}",
            format_time(start_t),
            format_time(end_t),
            round(wait_t, 2),
            round(turnaround_t, 2),
            round(turnaround_t, 2),
            cp_list[i],
            cp_lookup[i]
        ])

    df = pd.DataFrame(rows, columns=["ID","Arrival","Service","Server","Start","End","Wait","Turnaround","Response","CP","CP_Lookup"])
    return df, server_busy_log, max_end_time


# ---------------- 5. GUI ---------------- #
class QueueSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sapphire Shopping Outlet - Queue Simulator")
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1400x900")


        style = ttk.Style()
        style.theme_use('clam')

        input_frame = ttk.LabelFrame(root, text="Configuration", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Arrival:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.arrival_type = tk.StringVar(value="M")
        ttk.Radiobutton(input_frame, text="M (Poisson/Exp)", variable=self.arrival_type, value="M").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(input_frame, text="G (General)", variable=self.arrival_type, value="G").grid(row=0, column=2, sticky="w")

        self.arrival_dist = tk.StringVar(value="Poisson")
        self.cb_arrival_dist = ttk.Combobox(input_frame, textvariable=self.arrival_dist, state="readonly", width=12)
        self.cb_arrival_dist.grid(row=1, column=1, columnspan=2, pady=2)

        self.lbl_arr_params = ttk.Label(input_frame, text="Arrival Params:")
        self.entry_arr_params = ttk.Entry(input_frame, width=15)

        ttk.Label(input_frame, text="Service:").grid(row=0, column=3, padx=20, pady=5, sticky="e")
        self.service_type = tk.StringVar(value="M")
        ttk.Radiobutton(input_frame, text="M (Exp/Poisson)", variable=self.service_type, value="M").grid(row=0, column=4, sticky="w")
        ttk.Radiobutton(input_frame, text="G (General)", variable=self.service_type, value="G").grid(row=0, column=5, sticky="w")

        self.service_dist = tk.StringVar(value="Exponential")
        self.cb_service_dist = ttk.Combobox(input_frame, textvariable=self.service_dist, state="readonly", width=12)
        self.cb_service_dist.grid(row=1, column=4, columnspan=2, pady=2)

        self.lbl_svc_params = ttk.Label(input_frame, text="Service Params (a,b or σ):")
        self.entry_svc_params = ttk.Entry(input_frame, width=15)

        ttk.Label(input_frame, text="λ (Arr Rate):").grid(row=0, column=6, padx=5)
        self.entry_lambda = ttk.Entry(input_frame, width=8); self.entry_lambda.insert(0, "8"); self.entry_lambda.grid(row=0, column=7, padx=5)
        ttk.Label(input_frame, text="μ (Svc Rate):").grid(row=0, column=8, padx=5)
        self.entry_mu = ttk.Entry(input_frame, width=8); self.entry_mu.insert(0, "5"); self.entry_mu.grid(row=0, column=9, padx=5)
        ttk.Label(input_frame, text="Servers (c):").grid(row=0, column=10, padx=5)
        self.entry_servers = ttk.Entry(input_frame, width=5); self.entry_servers.insert(0, "1"); self.entry_servers.grid(row=0, column=11, padx=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=0, column=12, padx=30)
        ttk.Button(btn_frame, text="Run Simulation", command=self.run_sim).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Queueing Theory Calculator", command=self.run_analytics).pack(side="left", padx=5)

        self.arrival_type.trace("w", self.update_dist_options)
        self.service_type.trace("w", self.update_dist_options)
        self.update_dist_options()

        # Tabs

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_data = ttk.Frame(self.notebook); self.notebook.add(self.tab_data, text="Data Table"); self.setup_table_tab()
        self.tab_charts = ttk.Frame(self.notebook); self.notebook.add(self.tab_charts, text="Time Charts (Wait/Turn/Resp)"); self.setup_chart_tab()
        self.tab_gantt = ttk.Frame(self.notebook); self.notebook.add(self.tab_gantt, text="Gantt Chart (Utilization)"); self.setup_gantt_tab()
        self.tab_metrics = ttk.Frame(self.notebook); self.notebook.add(self.tab_metrics, text="Analytic Metrics")
        self.lbl_metrics_result = tk.Label(self.tab_metrics, text="Run Queueing Theory Calculator...", font=("Consolas", 14), bg="white", relief="sunken", anchor="nw", justify="left")
        self.lbl_metrics_result.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_sens = ttk.Frame(self.notebook); self.notebook.add(self.tab_sens, text="Sensitivity Graph")
        self.fig_sens = plt.Figure(figsize=(8,5), dpi=100)
        self.canvas_sens = FigureCanvasTkAgg(self.fig_sens, self.tab_sens)
        self.canvas_sens.get_tk_widget().pack(fill="both", expand=True)

    def update_dist_options(self, *args):
     if self.arrival_type.get() == "M":
        self.cb_arrival_dist.config(values=["Poisson", "Exponential"])
        self.arrival_dist.set("Poisson")
        self.lbl_arr_params.grid_forget()
        self.entry_arr_params.grid_forget()
     else:
        self.cb_arrival_dist.config(values=["Uniform", "Normal", "Gamma"])
        self.arrival_dist.set("Uniform")
        self.lbl_arr_params.grid(row=2, column=0, columnspan=2, sticky="e")
        self.entry_arr_params.grid(row=2, column=2, pady=2)

     if self.service_type.get() == "M":
        self.cb_service_dist.config(values=["Exponential", "Poisson"])
        self.service_dist.set("Exponential")
        self.lbl_svc_params.grid_forget()
        self.entry_svc_params.grid_forget()
     else:
        self.cb_service_dist.config(values=["Uniform", "Normal", "Gamma"])
        self.service_dist.set("Uniform")
        self.lbl_svc_params.grid(row=2, column=3, columnspan=2, sticky="e")
        self.entry_svc_params.grid(row=2, column=5, pady=2)


    # ---------------- GUI Tabs ---------------- #
    def setup_table_tab(self):
        cols = ("ID","Arr","Svc","Svr","Start","End","Wait","Turn","Resp","CP","PrevCP")
        self.tree = ttk.Treeview(self.tab_data, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=60, anchor="center")
        sb = ttk.Scrollbar(self.tab_data, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def setup_chart_tab(self):
        self.chart_canvas = tk.Canvas(self.tab_charts)
        self.chart_scroll = ttk.Scrollbar(self.tab_charts, orient="vertical", command=self.chart_canvas.yview)
        self.chart_frame = ttk.Frame(self.chart_canvas)
        self.chart_frame.bind("<Configure>", lambda e: self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all")))
        self.chart_canvas.create_window((0, 0), window=self.chart_frame, anchor="nw")
        self.chart_canvas.configure(yscrollcommand=self.chart_scroll.set)
        self.chart_canvas.pack(side="left", fill="both", expand=True)
        self.chart_scroll.pack(side="right", fill="y")

    def setup_gantt_tab(self):
        self.gantt_canvas = tk.Canvas(self.tab_gantt, bg="white")
        self.gantt_h_scroll = ttk.Scrollbar(self.tab_gantt, orient="horizontal", command=self.gantt_canvas.xview)
        self.gantt_v_scroll = ttk.Scrollbar(self.tab_gantt, orient="vertical", command=self.gantt_canvas.yview)
        self.gantt_frame_inner = tk.Frame(self.gantt_canvas, bg="white")
        self.gantt_frame_inner.bind("<Configure>", lambda e: self.gantt_canvas.configure(scrollregion=self.gantt_canvas.bbox("all")))
        self.gantt_canvas.create_window((0, 0), window=self.gantt_frame_inner, anchor="nw")
        self.gantt_canvas.configure(xscrollcommand=self.gantt_h_scroll.set, yscrollcommand=self.gantt_v_scroll.set)
        self.gantt_h_scroll.pack(side="bottom", fill="x")
        self.gantt_v_scroll.pack(side="right", fill="y")
        self.gantt_canvas.pack(side="left", fill="both", expand=True)

    def run_sim(self):
        try:
            lam = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            servers = int(self.entry_servers.get())

            # --- VALIDATION ---
            if lam <= 0:
                messagebox.showerror("Input Error", "Arrival rate λ must be a positive number.")
                return
            if mu <= 0:
                messagebox.showerror("Input Error", "Service rate μ must be a positive number.")
                return
            if servers <= 0:
                messagebox.showerror("Input Error", "Number of servers must be at least 1.")
                return

            df, server_log, max_end_time = simulate_queue_engine(
                self.arrival_type.get(),
                self.arrival_dist.get(),
                self.service_type.get(),
                self.service_dist.get(),
                lam, mu, servers,
                self.entry_svc_params.get() if self.service_type.get() == "G" else ""
            )

            # Clear old data and insert new
            for i in self.tree.get_children(): 
                self.tree.delete(i)
            for _, r in df.iterrows(): 
                self.tree.insert("", "end", values=r.tolist())

            self.draw_time_charts(df)
            self.draw_sensitivity_graph()
            self.draw_gantt(server_log, max_end_time)
            self.notebook.select(self.tab_data)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def draw_time_charts(self, df):
        # Clear previous charts
        for w in self.chart_frame.winfo_children():
            w.destroy()
        
        # Create subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        d = df.head(50)
        
        # Plot Wait Time
        ax1.bar(d["ID"], d["Wait"], color='#ff9999')
        ax1.set_title("Wait Time at Billing Counter")
        
        # Plot Turnaround Time
        ax2.bar(d["ID"], d["Turnaround"], color='#66b3ff')
        ax2.set_title("Total Time in Outlet")
        
        # Plot Response Time
        ax3.bar(d["ID"], d["Response"], color='#99ff99')
        ax3.set_title("Response Time")
        
        # Adjust layout
        plt.tight_layout()
        
        # Draw on Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
           

    def draw_gantt(self, logs, max_t):
        # Clear previous Gantt chart
        for w in self.gantt_frame_inner.winfo_children():
            w.destroy()
        
        # Create figure
        fig = plt.Figure(figsize=(max(12, max_t / 4), 2 + len(logs) * 1.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get colormap
        try:
            cmap = plt.colormaps['tab20']  # For Matplotlib 3.7+
        except AttributeError:
            cmap = plt.cm.get_cmap('tab20')  # Fallback for older versions
        
        # Plot each server's logs
        for i, log in enumerate(logs):
            y = i + 1
            total = sum(d for _, d, _ in log)
            
            for s, d, cid in log:
                ax.broken_barh([(s, d)], (y - 0.4, 0.8), facecolors=cmap(cid % 20))
                ax.text(s + d / 2, y, str(cid), ha='center', va='center', color='white', fontsize=8, weight='bold')
            
            # Utilization text on the right
            ax.text(max_t * 1.01, y, f"Util: {total / max_t * 100:.1f}%", va='center', color='red', weight='bold')
        
        # Set y-axis labels
        ax.set_yticks(range(1, len(logs) + 1))
        ax.set_yticklabels([f"Server {i}" for i in range(1, len(logs) + 1)])
        ax.set_title("Gantt Chart - Billing Counter Utilization")
        
        # Draw on Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, self.gantt_frame_inner)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    def draw_sensitivity_graph(self):
        # Clear previous graph
        for w in self.tab_sens.winfo_children():
            w.destroy()

        try:
            mu = float(self.entry_mu.get())
            servers = int(self.entry_servers.get())
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        # Generate a range of λ values around the current λ
        try:
            base_lam = float(self.entry_lambda.get())
        except:
            base_lam = 5  # default if invalid

        lam_values = [max(0.1, base_lam + i) for i in range(-5, 6)]  # λ-5 to λ+5
        avg_waits = []

        for lam in lam_values:
            # Simulate the queue for each λ
            df, _, _ = simulate_queue_engine(
                self.arrival_type.get(),
                self.arrival_dist.get(),
                self.service_type.get(),
                self.service_dist.get(),
                lam, mu, servers,
                self.entry_svc_params.get() if self.service_type.get() == "G" else ""
            )
            avg_waits.append(df["Wait"].mean())  # average wait time

        # Plotting
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(lam_values, avg_waits, marker='o', linestyle='-', color='purple')
        ax.set_xlabel("Arrival Rate λ")
        ax.set_ylabel("Average Wait Time")
        ax.set_title("Sensitivity Graph: Wait Time vs Arrival Rate")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, self.tab_sens)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


       

    def run_analytics(self):
        try:
            lam = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            c = int(self.entry_servers.get())

            # --- VALIDATION ---
            if lam <= 0:
                messagebox.showerror("Input Error", "Arrival rate λ must be a positive number.")
                return
            if mu <= 0:
                messagebox.showerror("Input Error", "Service rate μ must be a positive number.")
                return
            if c <= 0:
                messagebox.showerror("Input Error", "Number of servers must be at least 1.")
                return

            q_type = self.arrival_type.get() + self.service_type.get() + ("C" if c>1 else "1")
            dist = self.service_dist.get()
            params = self.entry_svc_params.get() if self.service_type.get() == "G" else ""

            res, _ = calculate_analytical(q_type, lam, mu, c, dist, params)
            text = f"ANALYTICAL RESULTS: {q_type}\nλ={lam}, μ={mu}, c={c}\n"
            text += "="*50 + "\n"
            for k, v in res.items():
                text += f"{k:<30}: {v}\n"
            self.lbl_metrics_result.config(text=text)
            self.notebook.select(self.tab_metrics)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = QueueSimulatorApp(root)
    root.mainloop()

