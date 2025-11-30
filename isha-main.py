import math
import random
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# ---------------- 1. RANDOM NUMBER GENERATORS ---------------- #

def get_interarrival_time(dist_type, lam):
    # Generates arrival times. 
    # M = Exponential
    # G = Uniform (Approximation for simulation context)
    if dist_type == "M":
        return -math.log(1 - random.random()) / lam
    else:
        # Default G arrival: Uniform [0.5/lam, 1.5/lam]
        mean_t = 1/lam
        return random.uniform(mean_t * 0.5, mean_t * 1.5)

def get_service_time(dist_name, mu, params):
    mean_service_time = 1.0 / mu if mu > 0 else 1.0
    try:
        if dist_name == "Exponential":
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
            # Mean = alpha/beta (or k*theta). Using alpha=2 approximation if not provided
            alpha = 2.0
            beta = mean_service_time / alpha
            val = random.gamma(alpha, beta)
            return max(0.01, val)
        else:
            return -math.log(1 - random.random()) / mu
    except:
        return -math.log(1 - random.random()) / mu

# ---------------- 2. ANALYTICAL FORMULAS (STRICTLY FROM IMAGES) ---------------- #

def get_scv(dist_name, mean_val, params):
    """
    Calculates Squared Coefficient of Variation (C^2 = Variance / Mean^2)
    """
    if dist_name == "Exponential" or dist_name == "M":
        return 1.0
    
    variance = 0.0
    if dist_name == "Uniform":
        # Params "a,b". If empty, assumed +/- 50%
        if "," in params:
            a, b = map(float, params.split(","))
            variance = ((b - a)**2) / 12
        else:
            # Default logic used in simulation: 0.5*mean to 1.5*mean
            # width = mean, so variance = mean^2 / 12
            variance = (mean_val**2) / 12
            
    elif dist_name == "Normal":
        sigma = float(params) if params else mean_val * 0.2
        variance = sigma**2
        
    elif dist_name == "Gamma":
        # Using alpha=2 default from simulation logic if specific parsing not added
        # Var(Gamma) = alpha * beta^2. Mean = alpha * beta.
        # beta = mean/alpha. Var = alpha * (mean/alpha)^2 = mean^2 / alpha
        alpha = 2.0
        variance = (mean_val**2) / alpha
        
    return variance / (mean_val**2)

def calculate_analytical(queue_type, lam, mu, c, dist_name="Exponential", dist_params=""):
    rho = lam / (c * mu)
    
    if rho >= 1:
        return {"Error": "System Unstable (ρ ≥ 1). Arrival rate > Service capacity."}, None

    Lq, Wq, L, W = 0, 0, 0, 0

    # --- 1. M/M/1 (Image 1) ---
    if queue_type == "MM1":
        # Image 1 Formulas:
        # Lq = rho^2 / (1-rho)  (Equivalent to formulas in image derived from L)
        Lq = (rho**2) / (1 - rho)
        Wq = Lq / lam
        W = Wq + (1/mu)
        L = lam * W

    # --- 2. M/M/c (Image 2) ---
    elif queue_type == "MMC":
        r = lam / mu
        
        # Helper for Summation part of P0
        sum_part = sum([(r**m)/math.factorial(m) for m in range(c)])
        last_term = (r**c) / (math.factorial(c) * (1 - rho))
        
        P0 = 1.0 / (sum_part + last_term)
        
        # Eq (6) from Image 2
        Lq = (P0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
        Wq = Lq / lam
        W = Wq + (1 / mu)
        L = Lq + r  # L = Lq + lambda/mu

    # --- 3. G/G/1 (Image 3 - Marchal's Approximation) ---
    elif queue_type == "GG1" or queue_type == "MG1":
        # Calculate Ca^2 (Arrival) and Cs^2 (Service)
        # If model starts with M, Ca^2 = 1. If G, we approximate based on the simulation's Uniform generator
        Ca2 = 1.0
        if queue_type.startswith("G"):
            # Simulation uses Uniform arrival for G
            Ca2 = get_scv("Uniform", 1/lam, "") 
            
        Cs2 = get_scv(dist_name, 1/mu, dist_params)
        
        if queue_type == "MG1":
            # Pollaczek-Khinchine (Standard for M/G/1)
            # Lq = (lam^2 * var_s + rho^2) / 2(1-rho)
            var_s = Cs2 * (1/mu)**2
            numerator = (lam**2)*var_s + rho**2
            Lq = numerator / (2*(1-rho))
        else:
            # G/G/1 -> Marchal's Approximation (Image 3)
            # Lq = [rho^2 (1+Cs^2)(Ca^2 + rho^2 Cs^2)] / [2(1-rho)(1 + rho^2 Cs^2)]
            term1 = (rho**2) / (2 * (1 - rho))
            term2 = (1 + Cs2)
            term3 = (Ca2 + (rho**2)*Cs2)
            term4 = (1 + (rho**2)*Cs2)
            
            Lq = term1 * term2 * (term3 / term4)

        Wq = Lq / lam
        W = Wq + (1 / mu)
        L = lam * W

    # --- 4. G/G/c (Image 2 & 4 - Whitt's Approximation) ---
    else: # MGC or GGC
        # 1. Calculate Exact M/M/c Lq first
        r = lam / mu
        sum_part = sum([(r**m)/math.factorial(m) for m in range(c)])
        last_term = (r**c) / (math.factorial(c) * (1 - rho))
        P0 = 1.0 / (sum_part + last_term)
        Lq_mmc = (P0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
        Wq_mmc = Lq_mmc / lam
        
        # 2. Variability Factors
        Ca2 = 1.0
        if queue_type.startswith("G"):
             Ca2 = get_scv("Uniform", 1/lam, "")
             
        Cs2 = get_scv(dist_name, 1/mu, dist_params)
        
        # 3. Apply Whitt's Approximation (Eq 8 in Image 2)
        # Wq_ggc = Wq_mmc * (Ca^2 + Cs^2)/2
        Wq = Wq_mmc * ((Ca2 + Cs2) / 2)
        Lq = Wq * lam
        W = Wq + (1/mu)
        L = lam * W

    results = {
        "Traffic Intensity (ρ)": round(rho, 4),
        "Lq (Queue Length)": round(Lq, 4),
        "Wq (Wait in Queue)": round(Wq, 4),
        "W (Total System Time)": round(W, 4),
        "L (Total Customers)": round(L, 4)
    }
    return results, rho

# ---------------- 3. SIMULATION LOGIC ---------------- #

def generate_arrivals_strict(lam, max_cp=0.99999):
    arrivals = []
    cp_list = []
    cp_lookup = []
    t = 0.0
    current_cp = 0.0
    prev_cp = 0.0
    
    # Generate until CP reaches 0.99999
    while current_cp < max_cp:
        interarrival = -math.log(1 - random.random()) / lam
        t += interarrival
        calculated_cp = 1 - math.exp(-lam * t)
        
        if calculated_cp >= max_cp:
            break

        arrivals.append(t)
        cp_list.append(round(calculated_cp, 5))
        cp_lookup.append(round(prev_cp, 5))
        prev_cp = calculated_cp
        current_cp = calculated_cp
        if len(arrivals) > 5000: break # Safety Cap
        
    return arrivals, cp_list, cp_lookup

def simulate_queue_engine(queue_type, lam, mu, servers, service_dist, service_params):
    arrivals, cp_list, cp_lookup = generate_arrivals_strict(lam)
    num_servers = servers
    server_end_times = [0.0] * num_servers
    server_busy_log = [[] for _ in range(num_servers)]
    rows = []
    
    for i in range(len(arrivals)):
        arrival_t = arrivals[i]
        cust_id = i + 1
        
        # Determine service time
        if queue_type in ["MM1", "MMC"]:
            srv_time = get_service_time("Exponential", mu, "")
        else:
            srv_time = get_service_time(service_dist, mu, service_params)
            
        next_free_server_idx = server_end_times.index(min(server_end_times))
        
        start_t = max(arrival_t, server_end_times[next_free_server_idx])
        end_t = start_t + srv_time
        
        wait_t = start_t - arrival_t
        turnaround_t = end_t - arrival_t
        
        server_end_times[next_free_server_idx] = end_t
        server_busy_log[next_free_server_idx].append((start_t, srv_time, cust_id))
        
        rows.append([
            cust_id, round(arrival_t, 2), round(srv_time, 2), f"S{next_free_server_idx+1}",
            round(start_t, 2), round(end_t, 2), round(wait_t, 2), round(turnaround_t, 2),
            round(turnaround_t, 2), cp_list[i], cp_lookup[i]
        ])
        
    df = pd.DataFrame(rows, columns=["ID","Arrival","Service","Server","Start","End","Wait","Turnaround","Response","CP","CP_Lookup"])
    return df, server_busy_log

# ---------------- 4. GUI IMPLEMENTATION ---------------- #

class QueueSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Queue Simulator & Analyzer")
        # Start Maximized
        try:
            self.root.state('zoomed') 
        except:
            self.root.geometry("1400x900")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Input Section ---
        input_frame = ttk.LabelFrame(root, text="Configuration", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Model:").grid(row=0, column=0, padx=5)
        self.queue_var = tk.StringVar(value="MM1")
        self.cb_queue = ttk.Combobox(input_frame, textvariable=self.queue_var, 
                                     values=["MM1","MMC","MG1","MGC","GG1","GGC"], state="readonly", width=8)
        self.cb_queue.grid(row=0, column=1, padx=5)
        self.cb_queue.bind("<<ComboboxSelected>>", self.toggle_inputs)

        ttk.Label(input_frame, text="λ (Arr Rate):").grid(row=0, column=2, padx=5)
        self.entry_lambda = ttk.Entry(input_frame, width=8)
        self.entry_lambda.insert(0, "4")
        self.entry_lambda.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="μ (Svc Rate):").grid(row=0, column=4, padx=5)
        self.entry_mu = ttk.Entry(input_frame, width=8)
        self.entry_mu.insert(0, "5")
        self.entry_mu.grid(row=0, column=5, padx=5)
        
        self.lbl_servers = ttk.Label(input_frame, text="Servers (c):")
        self.entry_servers = ttk.Entry(input_frame, width=5)
        self.entry_servers.insert(0, "1")
        
        self.lbl_dist = ttk.Label(input_frame, text="Service Dist:")
        self.dist_var = tk.StringVar(value="Uniform")
        self.cb_dist = ttk.Combobox(input_frame, textvariable=self.dist_var, 
                                    values=["Uniform", "Normal", "Gamma"], state="readonly", width=10)
        
        self.lbl_params = ttk.Label(input_frame, text="Params (a,b or σ):")
        self.entry_params = ttk.Entry(input_frame, width=8)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=0, column=10, rowspan=1, padx=20)
        ttk.Button(btn_frame, text="Run Simulation", command=self.run_sim).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Analytics", command=self.run_analytics).pack(side="left", padx=5)

        self.toggle_inputs()

        # --- TABS ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 1. Table Tab
        self.tab_data = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text="Data Table")
        self.setup_table_tab()
        
        # 2. Time Charts Tab
        self.tab_charts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_charts, text="Time Charts (Wait/Turn/Resp)")
        self.setup_chart_tab()

        # 3. Gantt Chart Tab
        self.tab_gantt = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gantt, text="Gantt Chart (Utilization)")
        self.setup_gantt_tab()

        # 4. Metrics Tab
        self.tab_metrics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_metrics, text="Analytic Metrics")
        self.lbl_metrics_result = tk.Label(self.tab_metrics, text="Run Analytics to see results...", 
                                           font=("Consolas", 14), bg="white", relief="sunken", anchor="nw", justify="left")
        self.lbl_metrics_result.pack(fill="both", expand=True, padx=10, pady=10)

        # 5. Sensitivity Graph Tab
        self.tab_sens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sens, text="Sensitivity Graph")
        self.fig_sens = plt.Figure(figsize=(8,5), dpi=100)
        self.canvas_sens = FigureCanvasTkAgg(self.fig_sens, master=self.tab_sens)
        self.canvas_sens.get_tk_widget().pack(fill="both", expand=True)

    def toggle_inputs(self, event=None):
        q_type = self.queue_var.get()
        # Show/Hide Servers input
        if "C" in q_type:
            self.lbl_servers.grid(row=0, column=6, padx=5)
            self.entry_servers.grid(row=0, column=7, padx=5)
        else:
            self.lbl_servers.grid_forget()
            self.entry_servers.grid_forget()
            
        # Show/Hide Distribution input
        if "G" in q_type:
            self.lbl_dist.grid(row=0, column=8, padx=5)
            self.cb_dist.grid(row=0, column=9, padx=5)
            self.lbl_params.grid(row=1, column=8, padx=5)
            self.entry_params.grid(row=1, column=9, padx=5)
        else:
            self.lbl_dist.grid_forget()
            self.cb_dist.grid_forget()
            self.lbl_params.grid_forget()
            self.entry_params.grid_forget()

    def setup_table_tab(self):
        self.tree = ttk.Treeview(self.tab_data, columns=("ID","Arr","Svc","Svr","Start","End","Wait","Turn","Resp","CP","PrevCP"), show='headings')
        cols = ["ID","Arr","Svc","Svr","Start","End","Wait","Turn","Resp","CP","PrevCP"]
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=60, anchor="center")
        ysb = ttk.Scrollbar(self.tab_data, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

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
            q_type = self.queue_var.get()
            servers = int(self.entry_servers.get()) if "C" in q_type else 1
            dist = self.dist_var.get()
            params = self.entry_params.get()
            
            df, server_log = simulate_queue_engine(q_type, lam, mu, servers, dist, params)
            
            # 1. Update Table
            for item in self.tree.get_children(): self.tree.delete(item)
            for _, row in df.iterrows(): self.tree.insert("", "end", values=list(row))
            
            # 2. Update Charts
            self.draw_time_charts(df)
            self.draw_gantt(server_log, df["End"].max())
            
            self.notebook.select(self.tab_data)
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))

    def draw_time_charts(self, df):
        for widget in self.chart_frame.winfo_children(): widget.destroy()
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), dpi=100)
        plot_df = df.head(50) # Just show first 50 to avoid clutter
        ids = plot_df["ID"]
        
        ax1.bar(ids, plot_df["Wait"], color='#ff9999')
        ax1.set_title("Wait Time (First 50 Customers)")
        ax1.set_ylabel("Minutes")
        
        ax2.bar(ids, plot_df["Turnaround"], color='#66b3ff')
        ax2.set_title("Turnaround Time")
        ax2.set_ylabel("Minutes")
        
        ax3.bar(ids, plot_df["Response"], color='#99ff99')
        ax3.set_title("Response Time")
        ax3.set_xlabel("Customer ID")
        ax3.set_ylabel("Minutes")
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_gantt(self, server_logs, max_sim_time):
        for widget in self.gantt_frame_inner.winfo_children(): widget.destroy()
        
        # Determine width based on duration to allow scrolling
        fig_width = max(12, max_sim_time / 4)
        fig_height = 2 + len(server_logs) * 1.5
        
        fig = plt.Figure(figsize=(fig_width, fig_height), dpi=100)
        ax = fig.add_subplot(111)
        
        # Colors for different customers
        cmap = plt.cm.get_cmap('tab20')
        
        y_ticks = []
        y_labels = []
        
        for i, logs in enumerate(server_logs):
            y_pos = (i + 1) * 10
            y_ticks.append(y_pos)
            y_labels.append(f"Server {i+1}")
            
            bars = []
            colors = []
            total_busy = 0
            
            for start, duration, cid in logs:
                bars.append((start, duration))
                colors.append(cmap(cid % 20))
                # Add Customer ID text
                ax.text(start + duration/2, y_pos, str(cid), ha='center', va='center', color='black', fontsize=8, fontweight='bold')
                total_busy += duration
            
            if bars:
                ax.broken_barh(bars, (y_pos - 4, 8), facecolors=colors, edgecolor='black', linewidth=0.5)
            
            # Utilization Calc: Busy Time / Total Simulation Time
            util = (total_busy / max_sim_time) * 100 if max_sim_time > 0 else 0
            # Place text at the end of the timeline
            ax.text(max_sim_time * 1.01, y_pos, f"Util: {util:.2f}%", va='center', color='red', fontweight='bold', fontsize=10)

        ax.set_ylim(0, (len(server_logs) + 1) * 10 + 5)
        ax.set_xlim(0, max_sim_time * 1.1) # Add 10% padding for text
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel("Time (Minutes)")
        ax.set_title("Server Utilization Gantt Chart")
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame_inner)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def run_analytics(self):
        try:
            lam = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            q_type = self.queue_var.get()
            servers = int(self.entry_servers.get()) if "C" in q_type else 1
            dist = self.dist_var.get()
            params = self.entry_params.get()
            
            metrics, rho = calculate_analytical(q_type, lam, mu, servers, dist, params)
            
            if metrics:
                res_text = f"ANALYTICAL RESULTS: {q_type}\n"
                res_text += f"Inputs: λ={lam}, μ={mu}, c={servers}, Dist={dist}\n"
                res_text += "="*50 + "\n"
                for k, v in metrics.items():
                    res_text += f"{k:<30}: {v}\n"
            else:
                res_text = "Calculation Failed."
                
            self.lbl_metrics_result.config(text=res_text)
            self.draw_sensitivity_chart(q_type, mu, servers, dist, params)
            self.notebook.select(self.tab_metrics)
        except Exception as e:
            messagebox.showerror("Analytics Error", str(e))

    def draw_sensitivity_chart(self, q_type, mu, servers, dist, params):
        self.fig_sens.clear()
        ax = self.fig_sens.add_subplot(111)
        rhos = np.linspace(0.1, 0.95, 20)
        lqs, wqs = [], []
        
        for r in rhos:
            lam_temp = r * servers * mu
            m, _ = calculate_analytical(q_type, lam_temp, mu, servers, dist, params)
            if m and "Lq (Queue Length)" in m:
                lqs.append(m["Lq (Queue Length)"])
                wqs.append(m["Wq (Wait in Queue)"])
            else:
                lqs.append(0); wqs.append(0)
                
        ax.plot(rhos, lqs, marker='o', label='Lq (Queue Length)', color='blue')
        ax.plot(rhos, wqs, marker='s', label='Wq (Wait Time)', color='orange')
        ax.set_xlabel("Traffic Intensity (ρ)")
        ax.set_ylabel("Value")
        ax.set_title(f"Sensitivity Analysis: {q_type}")
        ax.legend()
        ax.grid(True)
        self.canvas_sens.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueSimulatorApp(root)
    root.mainloop()