"""
Main GUI for the enhanced queue simulator with all features.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
from matplotlib.patches import Rectangle

from simulation_engine import QueueSimulator
from queue_analytics import QueueAnalytics
from distributions import get_distribution_params

class QueueSimulatorGUI:
    """Main GUI application for queue simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sapphire Shopping Outlet - Enhanced Queue Simulator")
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
        
        # Initialize simulator
        self.simulator = QueueSimulator()
        self.current_df = pd.DataFrame()
        self.current_params = {}
        
        # Create GUI
        self.create_widgets()
        
        # Maximize window
        self.root.state('zoomed')
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Sapphire Shopping Outlet Queue Simulator", 
                               font=("Arial", 16, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs in order
        self.create_setup_tab()
        self.create_simulation_tab()
        self.create_analytics_tab()
        self.create_charts_tab()
        self.create_gantt_tab()
        self.create_sensitivity_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_setup_tab(self):
        """Create setup/configuration tab."""
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="⚙️ Setup")
        
        # Main container with scroll
        setup_canvas = tk.Canvas(self.setup_frame)
        scrollbar = ttk.Scrollbar(self.setup_frame, orient="vertical", command=setup_canvas.yview)
        self.setup_scroll_frame = ttk.Frame(setup_canvas)
        
        self.setup_scroll_frame.bind(
            "<Configure>",
            lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all"))
        )
        
        setup_canvas.create_window((0, 0), window=self.setup_scroll_frame, anchor="nw")
        setup_canvas.configure(yscrollcommand=scrollbar.set)
        
        setup_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Simulation Method Selection
        method_frame = ttk.LabelFrame(self.setup_scroll_frame, text="Simulation Method", padding="10")
        method_frame.pack(fill="x", padx=10, pady=10)
        
        self.sim_method = tk.StringVar(value="cp")
        ttk.Radiobutton(method_frame, text="CP-based (Simulate until CP=0.99999)", 
                       variable=self.sim_method, value="cp").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Fixed Number of Customers", 
                       variable=self.sim_method, value="fixed").pack(anchor="w", padx=10, pady=5)
        
        # Fixed customers entry (hidden by default)
        self.fixed_frame = ttk.Frame(method_frame)
        self.fixed_frame.pack(fill="x", padx=30, pady=5)
        ttk.Label(self.fixed_frame, text="Number of Customers:").pack(side="left", padx=(0, 10))
        self.customers_entry = ttk.Entry(self.fixed_frame, width=10)
        self.customers_entry.pack(side="left")
        self.customers_entry.insert(0, "100")
        self.fixed_frame.pack_forget()  # Hide initially
        
        # Bind method change
        self.sim_method.trace('w', self.toggle_sim_method)
        
        # Arrival Configuration
        arrival_frame = ttk.LabelFrame(self.setup_scroll_frame, text="Arrival Process Configuration", padding="10")
        arrival_frame.pack(fill="x", padx=10, pady=10)
        
        # Arrival Type
        ttk.Label(arrival_frame, text="Arrival Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.arrival_type = tk.StringVar(value="M")
        arrival_type_frame = ttk.Frame(arrival_frame)
        arrival_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=5)
        
        ttk.Radiobutton(arrival_type_frame, text="M (Markovian)", 
                       variable=self.arrival_type, value="M").pack(side="left", padx=5)
        ttk.Radiobutton(arrival_type_frame, text="G (General)", 
                       variable=self.arrival_type, value="G").pack(side="left", padx=5)
        
        # Arrival Rate
        ttk.Label(arrival_frame, text="Arrival Rate (λ):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lambda_entry = ttk.Entry(arrival_frame, width=15)
        self.lambda_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.lambda_entry.insert(0, "0.5")
        
        # Arrival Distribution
        ttk.Label(arrival_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.arrival_dist = tk.StringVar(value="Exponential")
        self.arrival_dist_combo = ttk.Combobox(arrival_frame, textvariable=self.arrival_dist,
                                              values=["Exponential", "Poisson", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.arrival_dist_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Arrival Parameters
        ttk.Label(arrival_frame, text="Parameters:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.arrival_params = ttk.Entry(arrival_frame, width=20)
        self.arrival_params.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.arrival_params.insert(0, "rate=0.5")
        ttk.Label(arrival_frame, text="e.g., rate=0.5, min=1,max=3, mean=2,std=0.5", 
                 font=("Arial", 8), foreground="gray").grid(row=3, column=1, columnspan=3, sticky="w", padx=5)
        
        # Service Configuration
        service_frame = ttk.LabelFrame(self.setup_scroll_frame, text="Service Process Configuration", padding="10")
        service_frame.pack(fill="x", padx=10, pady=10)
        
        # Service Type
        ttk.Label(service_frame, text="Service Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.service_type = tk.StringVar(value="M")
        service_type_frame = ttk.Frame(service_frame)
        service_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=5)
        
        ttk.Radiobutton(service_type_frame, text="M (Markovian)", 
                       variable=self.service_type, value="M").pack(side="left", padx=5)
        ttk.Radiobutton(service_type_frame, text="G (General)", 
                       variable=self.service_type, value="G").pack(side="left", padx=5)
        
        # Service Rate
        ttk.Label(service_frame, text="Service Rate (μ):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mu_entry = ttk.Entry(service_frame, width=15)
        self.mu_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.mu_entry.insert(0, "1.0")
        
        # Service Distribution
        ttk.Label(service_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.service_dist = tk.StringVar(value="Exponential")
        self.service_dist_combo = ttk.Combobox(service_frame, textvariable=self.service_dist,
                                              values=["Exponential", "Poisson", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.service_dist_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Service Parameters
        ttk.Label(service_frame, text="Parameters:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.service_params = ttk.Entry(service_frame, width=20)
        self.service_params.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.service_params.insert(0, "rate=1.0")
        
        # System Configuration
        system_frame = ttk.LabelFrame(self.setup_scroll_frame, text="System Configuration", padding="10")
        system_frame.pack(fill="x", padx=10, pady=10)
        
        # Number of Servers
        ttk.Label(system_frame, text="Number of Servers (c):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.servers_entry = ttk.Entry(system_frame, width=10)
        self.servers_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.servers_entry.insert(0, "1")
        
        # Max CP for simulation
        ttk.Label(system_frame, text="Max CP (for CP-based):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.max_cp_entry = ttk.Entry(system_frame, width=10)
        self.max_cp_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.max_cp_entry.insert(0, "0.99999")
        
        # Control Buttons
        button_frame = ttk.Frame(self.setup_scroll_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Button(button_frame, text="🚀 Run Simulation", 
                  command=self.run_simulation, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📊 Analytical Results", 
                  command=self.show_analytics, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📈 Sensitivity Analysis", 
                  command=self.run_sensitivity, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔄 Reset All", 
                  command=self.reset_all, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="💾 Export Results", 
                  command=self.export_results, width=20).pack(side="left", padx=5)
        
        # Bind events
        self.arrival_type.trace('w', self.update_distribution_options)
        self.service_type.trace('w', self.update_distribution_options)
        self.update_distribution_options()
    
    def toggle_sim_method(self, *args):
        """Toggle between CP-based and fixed number simulation."""
        if self.sim_method.get() == "fixed":
            self.fixed_frame.pack(fill="x", padx=30, pady=5)
        else:
            self.fixed_frame.pack_forget()
    
    def update_distribution_options(self, *args):
        """Update distribution options based on selected type."""
        if self.arrival_type.get() == "M":
            self.arrival_dist_combo.config(values=["Exponential", "Poisson"])
            self.arrival_dist.set("Exponential")
            self.arrival_params.delete(0, tk.END)
            self.arrival_params.insert(0, "rate=0.5")
        else:
            self.arrival_dist_combo.config(values=["Uniform", "Normal", "Gamma"])
            self.arrival_dist.set("Uniform")
            self.arrival_params.delete(0, tk.END)
            self.arrival_params.insert(0, "min=1.0,max=3.0")
            
        if self.service_type.get() == "M":
            self.service_dist_combo.config(values=["Exponential", "Poisson"])
            self.service_dist.set("Exponential")
            self.service_params.delete(0, tk.END)
            self.service_params.insert(0, "rate=1.0")
        else:
            self.service_dist_combo.config(values=["Uniform", "Normal", "Gamma"])
            self.service_dist.set("Uniform")
            self.service_params.delete(0, tk.END)
            self.service_params.insert(0, "min=0.5,max=1.5")
    
    def parse_params(self, params_str: str) -> dict:
        """Parse parameters string to dictionary."""
        params = {}
        if params_str:
            items = params_str.replace(" ", "").split(",")
            for item in items:
                if "=" in item:
                    key, value = item.split("=")
                    try:
                        params[key.strip()] = float(value.strip())
                    except ValueError:
                        params[key.strip()] = value.strip()
        return params
    
    def run_simulation(self):
        """Run the queue simulation."""
        try:
            # Get parameters
            lam = float(self.lambda_entry.get())
            mu = float(self.mu_entry.get())
            num_servers = int(self.servers_entry.get())
            
            # Validate parameters
            if lam <= 0 or mu <= 0:
                messagebox.showerror("Error", "λ and μ must be positive numbers.")
                return
            
            if num_servers <= 0:
                messagebox.showerror("Error", "Number of servers must be positive.")
                return
            
            # Parse distribution parameters
            arrival_params = self.parse_params(self.arrival_params.get())
            service_params = self.parse_params(self.service_params.get())
            
            self.status_var.set("Running simulation...")
            self.root.update()
            
            # Run simulation based on selected method
            if self.sim_method.get() == "cp":
                max_cp = float(self.max_cp_entry.get())
                if num_servers == 1:
                    df = self.simulator.simulate_single_server_cp(
                        self.arrival_dist.get(), arrival_params,
                        self.service_dist.get(), service_params,
                        lam, mu
                    )
                else:
                    df = self.simulator.simulate_multi_server_cp(
                        self.arrival_dist.get(), arrival_params,
                        self.service_dist.get(), service_params,
                        lam, mu, num_servers
                    )
            else:  # Fixed number
                num_customers = int(self.customers_entry.get())
                if num_customers <= 0:
                    messagebox.showerror("Error", "Number of customers must be positive.")
                    return
                
                if num_servers == 1:
                    df = self.simulator.simulate_single_server_fixed(
                        num_customers,
                        self.arrival_dist.get(), arrival_params,
                        self.service_dist.get(), service_params
                    )
                else:
                    df = self.simulator.simulate_multi_server_fixed(
                        num_customers,
                        self.arrival_dist.get(), arrival_params,
                        self.service_dist.get(), service_params,
                        num_servers
                    )
            
            self.current_df = df
            
            # Store current parameters
            self.current_params = {
                'lam': lam,
                'mu': mu,
                'servers': num_servers,
                'arrival_dist': self.arrival_dist.get(),
                'service_dist': self.service_dist.get(),
                'arrival_params': arrival_params,
                'service_params': service_params,
                'method': self.sim_method.get()
            }
            
            # Update all tabs
            self.update_simulation_tab(df)
            self.update_analytics_tab()
            self.update_charts_tab(df)
            self.update_gantt_tab(df, num_servers)
            
            # Switch to simulation tab
            self.notebook.select(1)  # Simulation tab
            
            self.status_var.set(f"Simulation completed: {len(df)} customers processed")
            messagebox.showinfo("Success", 
                              f"Simulation completed successfully!\n"
                              f"Processed {len(df)} customers\n"
                              f"Total time: {df['End'].max():.2f}\n"
                              f"Avg wait time: {df['Wait'].mean():.2f}")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input value: {str(e)}")
            self.status_var.set("Error in input")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
            self.status_var.set("Simulation failed")
    
    def create_simulation_tab(self):
        """Create simulation results tab."""
        self.sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sim_frame, text="📋 Simulation Results")
        
        # Create notebook within simulation tab
        sim_notebook = ttk.Notebook(self.sim_frame)
        sim_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data table sub-tab
        data_frame = ttk.Frame(sim_notebook)
        sim_notebook.add(data_frame, text="Data Table")
        
        # Treeview for data
        columns = ("ID", "Arrival", "Service", "Server", "Start", "End", 
                  "Wait", "Turnaround", "Response", "CP", "CP_Lookup")
        
        # Create scrollable frame
        container = ttk.Frame(data_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=25)
        
        # Configure columns
        col_widths = [50, 80, 80, 60, 80, 80, 80, 100, 80, 80, 80]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[i], anchor=tk.CENTER)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Layout using grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Metrics sub-tab
        metrics_frame = ttk.Frame(sim_notebook)
        sim_notebook.add(metrics_frame, text="Performance Metrics")
        
        # Create a Text widget with scrollbar
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial message
        self.metrics_text.insert(tk.END, "Run simulation to see metrics...\n")
        self.metrics_text.config(state=tk.DISABLED)
    
    def update_simulation_tab(self, df: pd.DataFrame):
        """Update simulation results tab."""
        # Update data table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data (limit to 500 rows for performance)
        display_df = df.head(500)
        for _, row in display_df.iterrows():
            self.tree.insert("", tk.END, values=tuple(row))
        
        # Update metrics text
        stats = self.simulator.get_summary_statistics(df)
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        
        # Header
        self.metrics_text.insert(tk.END, "=" * 70 + "\n")
        self.metrics_text.insert(tk.END, "SIMULATION PERFORMANCE METRICS\n")
        self.metrics_text.insert(tk.END, "=" * 70 + "\n\n")
        
        # Simulation info
        self.metrics_text.insert(tk.END, "📊 SIMULATION INFO\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        self.metrics_text.insert(tk.END, f"Simulation Method: {'CP-based' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
        self.metrics_text.insert(tk.END, f"Total Customers: {len(df)}\n")
        self.metrics_text.insert(tk.END, f"Arrival Distribution: {self.arrival_dist.get()}\n")
        self.metrics_text.insert(tk.END, f"Service Distribution: {self.service_dist.get()}\n")
        self.metrics_text.insert(tk.END, f"Number of Servers: {self.servers_entry.get()}\n\n")
        
        # Basic metrics
        self.metrics_text.insert(tk.END, "⏱️  TIME METRICS\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        time_metrics = [
            ("Average Service Time", df["Service"].mean()),
            ("Average Wait Time", df["Wait"].mean()),
            ("Average Turnaround Time", df["Turnaround"].mean()),
            ("Average Response Time", df["Response"].mean()),
            ("Maximum Wait Time", df["Wait"].max()),
            ("Minimum Wait Time", df["Wait"].min()),
            ("Std Deviation Wait", df["Wait"].std()),
            ("Median Wait Time", df["Wait"].median())
        ]
        
        for name, value in time_metrics:
            self.metrics_text.insert(tk.END, f"{name:25}: {value:.4f}\n")
        
        # System metrics
        self.metrics_text.insert(tk.END, "\n⚙️  SYSTEM METRICS\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        system_metrics = [
            ("Server Utilization", f"{self.simulator.metrics.get('utilization', 0):.2f}%"),
            ("Throughput", f"{self.simulator.metrics.get('throughput', 0):.4f} cust/time"),
            ("Total Simulation Time", f"{self.simulator.metrics.get('total_time', 0):.2f}"),
            ("Traffic Intensity (ρ)", f"{float(self.lambda_entry.get()) / (int(self.servers_entry.get()) * float(self.mu_entry.get())):.4f}")
        ]
        
        for name, value in system_metrics:
            self.metrics_text.insert(tk.END, f"{name:25}: {value}\n")
        
        # Wait time percentiles
        self.metrics_text.insert(tk.END, "\n📈 WAIT TIME DISTRIBUTION\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        percentiles = [25, 50, 75, 90, 95, 99]
        for p in percentiles:
            value = df["Wait"].quantile(p/100)
            self.metrics_text.insert(tk.END, f"{p}th Percentile{'':15}: {value:.4f}\n")
        
        self.metrics_text.config(state=tk.DISABLED)
    
    def create_analytics_tab(self):
        """Create analytical results tab."""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📐 Analytical Results")
        
        # Create a Text widget with scrollbar
        self.analytics_text = scrolledtext.ScrolledText(
            self.analytics_frame, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25
        )
        self.analytics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial message
        self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate queueing theory formulas...\n")
        self.analytics_text.config(state=tk.DISABLED)
    
    def update_analytics_tab(self):
        """Update analytical results tab."""
        try:
            lam = float(self.lambda_entry.get())
            mu = float(self.mu_entry.get())
            c = int(self.servers_entry.get())
            
            # Calculate analytical results
            if c == 1:
                results = QueueAnalytics.mm1(lam, mu)
                queue_type = "M/M/1"
            else:
                results = QueueAnalytics.mmc(lam, mu, c)
                queue_type = f"M/M/{c}"
            
            # Display results
            self.analytics_text.config(state=tk.NORMAL)
            self.analytics_text.delete(1.0, tk.END)
            
            self.analytics_text.insert(tk.END, "=" * 70 + "\n")
            self.analytics_text.insert(tk.END, f"ANALYTICAL RESULTS - {queue_type}\n")
            self.analytics_text.insert(tk.END, "=" * 70 + "\n\n")
            self.analytics_text.insert(tk.END, f"Parameters: λ = {lam}, μ = {mu}, c = {c}\n\n")
            
            if "error" in results:
                self.analytics_text.insert(tk.END, f"❌ {results['error']}\n")
            else:
                for key, value in results.items():
                    if callable(value):
                        continue
                    if isinstance(value, float):
                        self.analytics_text.insert(tk.END, f"{key:35}: {value:.6f}\n")
                    else:
                        self.analytics_text.insert(tk.END, f"{key:35}: {value}\n")
            
            # Add comparison with simulation if available
            if not self.current_df.empty:
                self.analytics_text.insert(tk.END, "\n" + "=" * 70 + "\n")
                self.analytics_text.insert(tk.END, "SIMULATION vs ANALYTICAL COMPARISON\n")
                self.analytics_text.insert(tk.END, "=" * 70 + "\n\n")
                
                sim_metrics = {
                    "Avg Wait (Wq)": self.current_df["Wait"].mean(),
                    "Avg Turnaround (W)": self.current_df["Turnaround"].mean(),
                    "System Customers (L)": len(self.current_df) / self.current_df["End"].max() * self.current_df["Turnaround"].mean() if self.current_df["End"].max() > 0 else 0
                }
                
                theo_metrics = {
                    "Avg Wait (Wq)": results.get("Wq (Avg wait in queue)", 0),
                    "Avg Turnaround (W)": results.get("W (Avg time in system)", 0),
                    "System Customers (L)": results.get("L (Avg in system)", 0)
                }
                
                for metric in ["Avg Wait (Wq)", "Avg Turnaround (W)"]:
                    if metric in sim_metrics and metric in theo_metrics:
                        sim_val = sim_metrics[metric]
                        theo_val = theo_metrics[metric]
                        diff = abs(theo_val - sim_val)
                        diff_pct = (diff / theo_val * 100) if theo_val != 0 else 0
                        
                        self.analytics_text.insert(tk.END, f"{metric}:\n")
                        self.analytics_text.insert(tk.END, f"  Theoretical: {theo_val:.6f}\n")
                        self.analytics_text.insert(tk.END, f"  Simulation:  {sim_val:.6f}\n")
                        self.analytics_text.insert(tk.END, f"  Difference:  {diff:.6f} ({diff_pct:.2f}%)\n\n")
            
            self.analytics_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analytical calculation failed: {str(e)}")
    
    def show_analytics(self):
        """Calculate and show analytical results."""
        self.update_analytics_tab()
        self.notebook.select(2)  # Analytics tab
    
    def create_charts_tab(self):
        """Create performance charts tab."""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="📊 Performance Charts")
        
        # Create figure with multiple subplots
        self.charts_fig = Figure(figsize=(12, 8), dpi=100)
        
        # Create subplots (3 rows, 1 column)
        self.chart_ax1 = self.charts_fig.add_subplot(311)  # Wait time
        self.chart_ax2 = self.charts_fig.add_subplot(312)  # Turnaround time
        self.chart_ax3 = self.charts_fig.add_subplot(313)  # Service time
        
        # Create canvas
        self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, self.charts_frame)
        self.charts_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(self.charts_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        toolbar = NavigationToolbar2Tk(self.charts_canvas, toolbar_frame)
        toolbar.update()
        
        # Initialize empty charts
        self.initialize_charts()
    
    def initialize_charts(self):
        """Initialize empty charts."""
        for ax in [self.chart_ax1, self.chart_ax2, self.chart_ax3]:
            ax.clear()
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_title("")
            ax.grid(True, alpha=0.3)
        
        self.chart_ax1.set_title("Wait Time per Customer", fontsize=12, fontweight='bold')
        self.chart_ax2.set_title("Turnaround Time per Customer", fontsize=12, fontweight='bold')
        self.chart_ax3.set_title("Service Time per Customer", fontsize=12, fontweight='bold')
        
        self.charts_fig.tight_layout()
        self.charts_canvas.draw()
    
    def update_charts_tab(self, df: pd.DataFrame):
        """Update performance charts."""
        if df.empty:
            return
        
        # Clear previous plots
        for ax in [self.chart_ax1, self.chart_ax2, self.chart_ax3]:
            ax.clear()
        
        # Limit to first 100 customers for clarity
        plot_df = df.head(100)
        
        # Colors
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        # Chart 1: Wait Time (Bar chart)
        customer_ids = plot_df['ID'].astype(str).tolist()
        wait_times = plot_df['Wait'].tolist()
        
        bars1 = self.chart_ax1.bar(customer_ids, wait_times, color=colors[0], alpha=0.7, edgecolor='white')
        self.chart_ax1.set_title('Wait Time per Customer', fontsize=12, fontweight='bold')
        self.chart_ax1.set_xlabel('Customer ID', fontweight='bold')
        self.chart_ax1.set_ylabel('Wait Time', fontweight='bold')
        self.chart_ax1.tick_params(axis='x', rotation=45)
        self.chart_ax1.grid(True, alpha=0.3)
        
        # Add average line
        avg_wait = plot_df['Wait'].mean()
        self.chart_ax1.axhline(y=avg_wait, color='red', linestyle='--', linewidth=2, 
                              label=f'Average: {avg_wait:.2f}')
        self.chart_ax1.legend()
        
        # Chart 2: Turnaround Time (Line chart)
        turnaround_times = plot_df['Turnaround'].tolist()
        
        self.chart_ax2.plot(customer_ids, turnaround_times, color=colors[1], 
                           marker='o', linewidth=2, markersize=4)
        self.chart_ax2.fill_between(customer_ids, turnaround_times, alpha=0.3, color=colors[1])
        self.chart_ax2.set_title('Turnaround Time per Customer', fontsize=12, fontweight='bold')
        self.chart_ax2.set_xlabel('Customer ID', fontweight='bold')
        self.chart_ax2.set_ylabel('Turnaround Time', fontweight='bold')
        self.chart_ax2.tick_params(axis='x', rotation=45)
        self.chart_ax2.grid(True, alpha=0.3)
        
        # Chart 3: Service Time (Stacked bar with wait time)
        service_times = plot_df['Service'].tolist()
        wait_for_service = plot_df['Wait'].tolist()
        
        x = np.arange(len(customer_ids))
        width = 0.6
        
        self.chart_ax3.bar(x, service_times, width, label='Service Time', color=colors[2], alpha=0.7)
        self.chart_ax3.bar(x, wait_for_service, width, bottom=service_times, 
                          label='Wait Time', color=colors[0], alpha=0.7)
        
        self.chart_ax3.set_title('Service Time vs Wait Time', fontsize=12, fontweight='bold')
        self.chart_ax3.set_xlabel('Customer ID', fontweight='bold')
        self.chart_ax3.set_ylabel('Time', fontweight='bold')
        self.chart_ax3.set_xticks(x)
        self.chart_ax3.set_xticklabels(customer_ids, rotation=45)
        self.chart_ax3.legend()
        self.chart_ax3.grid(True, alpha=0.3, axis='y')
        
        # Adjust layout
        self.charts_fig.tight_layout()
        
        # Update canvas
        self.charts_canvas.draw()
    
    def create_gantt_tab(self):
        """Create Gantt chart tab."""
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="📅 Gantt Chart")
        
        # Create figure for Gantt chart
        self.gantt_fig = Figure(figsize=(12, 6), dpi=100)
        self.gantt_ax = self.gantt_fig.add_subplot(111)
        
        # Create canvas
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, self.gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(self.gantt_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        toolbar = NavigationToolbar2Tk(self.gantt_canvas, toolbar_frame)
        toolbar.update()
        
        # Initialize empty chart
        self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline", fontsize=14, fontweight='bold')
        self.gantt_ax.set_xlabel("Time", fontweight='bold')
        self.gantt_ax.set_ylabel("Customers/Servers", fontweight='bold')
        self.gantt_ax.grid(True, alpha=0.3)
        self.gantt_canvas.draw()
    
    def update_gantt_tab(self, df: pd.DataFrame, num_servers: int):
        """Update Gantt chart."""
        if df.empty:
            return
        
        # Clear previous plot
        self.gantt_ax.clear()
        
        # Limit to first 50 customers for clarity
        plot_df = df.head(50).copy()
        
        # Sort by start time
        plot_df = plot_df.sort_values('Start')
        
        # Get unique servers
        servers = sorted(plot_df['Server'].unique())
        server_map = {server: i for i, server in enumerate(servers)}
        
        # Color palette
        colors = plt.cm.tab20(np.linspace(0, 1, len(plot_df)))
        
        # Plot each customer as a horizontal bar
        for idx, (_, row) in enumerate(plot_df.iterrows()):
            server_idx = server_map[row['Server']]
            start_time = row['Start']
            duration = row['Service']
            
            # Create rectangle for the service time
            rect = Rectangle(
                (start_time, server_idx - 0.3),
                duration,
                0.6,
                facecolor=colors[idx % len(colors)],
                edgecolor='black',
                alpha=0.8,
                linewidth=1
            )
            self.gantt_ax.add_patch(rect)
            
            # Add customer ID label
            if duration > 0.1:  # Only add label if duration is significant
                self.gantt_ax.text(
                    start_time + duration / 2,
                    server_idx,
                    f"C{int(row['ID'])}",
                    ha='center',
                    va='center',
                    fontsize=8,
                    fontweight='bold',
                    color='white'
                )
            
            # Add wait time indicator (if any)
            wait_time = row['Wait']
            if wait_time > 0.01:
                # Draw a dashed line for wait time
                self.gantt_ax.plot(
                    [row['Arrival'], start_time],
                    [server_idx, server_idx],
                    'k--',
                    linewidth=1,
                    alpha=0.5
                )
                # Add wait time marker
                self.gantt_ax.plot(
                    row['Arrival'],
                    server_idx,
                    'ro',
                    markersize=4,
                    alpha=0.7
                )
        
        # Set y-axis labels
        self.gantt_ax.set_yticks(range(len(servers)))
        self.gantt_ax.set_yticklabels(servers)
        self.gantt_ax.set_ylabel('Servers', fontweight='bold')
        
        # Set x-axis
        self.gantt_ax.set_xlabel('Time', fontweight='bold')
        
        # Calculate server utilizations
        total_time = plot_df['End'].max()
        util_text = "Server Utilization:\n"
        for server in servers:
            server_data = plot_df[plot_df['Server'] == server]
            busy_time = server_data['Service'].sum()
            utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
            util_text += f"{server}: {utilization:.1f}%\n"
        
        # Add utilization text box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        self.gantt_ax.text(
            0.02, 0.98,
            util_text,
            transform=self.gantt_ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=props
        )
        
        # Add legend for colors
        self.gantt_ax.text(
            0.02, 0.02,
            "Colors represent different customers",
            transform=self.gantt_ax.transAxes,
            fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5)
        )
        
        # Set title
        title = f"Gantt Chart - {len(plot_df)} Customers on {len(servers)} Server(s)"
        self.gantt_ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        self.gantt_ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust layout
        self.gantt_fig.tight_layout()
        
        # Update canvas
        self.gantt_canvas.draw()
    
    def create_sensitivity_tab(self):
        """Create sensitivity analysis tab."""
        self.sens_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sens_frame, text="📈 Sensitivity Analysis")
        
        # Control frame for sensitivity analysis
        sens_control_frame = ttk.LabelFrame(self.sens_frame, text="Sensitivity Analysis Parameters", padding="10")
        sens_control_frame.pack(fill="x", padx=10, pady=10)
        
        # Lambda range
        ttk.Label(sens_control_frame, text="λ Range (min,max,steps):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lambda_range_entry = ttk.Entry(sens_control_frame, width=20)
        self.lambda_range_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.lambda_range_entry.insert(0, "0.1,2.0,20")
        
        # Metric to analyze
        ttk.Label(sens_control_frame, text="Metric to Analyze:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.sens_metric = tk.StringVar(value="avg_wait")
        ttk.Combobox(sens_control_frame, textvariable=self.sens_metric,
                    values=["avg_wait", "avg_turnaround", "utilization", "throughput"],
                    state="readonly", width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Run button
        ttk.Button(sens_control_frame, text="Run Sensitivity Analysis", 
                  command=self.run_sensitivity).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Create figure for sensitivity graph
        self.sens_fig = Figure(figsize=(10, 6), dpi=100)
        self.sens_ax = self.sens_fig.add_subplot(111)
        
        # Create canvas
        self.sens_canvas = FigureCanvasTkAgg(self.sens_fig, self.sens_frame)
        self.sens_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(self.sens_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        toolbar = NavigationToolbar2Tk(self.sens_canvas, toolbar_frame)
        toolbar.update()
        
        # Initialize empty graph
        self.sens_ax.set_title("Sensitivity Analysis", fontsize=14, fontweight='bold')
        self.sens_ax.set_xlabel("Arrival Rate (λ)", fontweight='bold')
        self.sens_ax.set_ylabel("Metric Value", fontweight='bold')
        self.sens_ax.grid(True, alpha=0.3)
        self.sens_canvas.draw()
    
    def run_sensitivity(self):
        """Run sensitivity analysis."""
        try:
            # Get parameters
            lam = float(self.lambda_entry.get())
            mu = float(self.mu_entry.get())
            num_servers = int(self.servers_entry.get())
            
            # Parse lambda range
            range_str = self.lambda_range_entry.get()
            if "," in range_str:
                min_lam, max_lam, steps = map(float, range_str.split(","))
                lambda_range = np.linspace(min_lam, max_lam, int(steps))
            else:
                # Default range around current lambda
                min_lam = max(0.1, lam * 0.5)
                max_lam = min(lam * 2, mu * num_servers * 0.95)  # Keep below capacity
                lambda_range = np.linspace(min_lam, max_lam, 20)
            
            # Parse distribution parameters
            arrival_params = self.parse_params(self.arrival_params.get())
            service_params = self.parse_params(self.service_params.get())
            
            self.status_var.set("Running sensitivity analysis...")
            self.root.update()
            
            # Run sensitivity analysis
            results = self.simulator.run_sensitivity_analysis(
                self.arrival_dist.get(), arrival_params,
                self.service_dist.get(), service_params,
                mu, num_servers, lambda_range
            )
            
            # Update sensitivity graph
            self.update_sensitivity_graph(results)
            
            # Switch to sensitivity tab
            self.notebook.select(5)  # Sensitivity tab
            
            self.status_var.set(f"Sensitivity analysis completed with {len(results)} points")
            
        except Exception as e:
            messagebox.showerror("Error", f"Sensitivity analysis failed: {str(e)}")
            self.status_var.set("Sensitivity analysis failed")
    
    def update_sensitivity_graph(self, results: pd.DataFrame):
        """Update sensitivity graph with results."""
        self.sens_ax.clear()
        
        if results.empty:
            return
        
        # Get metric to plot
        metric = self.sens_metric.get()
        metric_names = {
            'avg_wait': 'Average Wait Time',
            'avg_turnaround': 'Average Turnaround Time',
            'utilization': 'Server Utilization (%)',
            'throughput': 'Throughput (customers/time)'
        }
        
        # Plot the metric vs lambda
        self.sens_ax.plot(results['lambda'], results[metric], 
                         'b-', linewidth=2, marker='o', markersize=4)
        
        # Fill under the curve
        self.sens_ax.fill_between(results['lambda'], results[metric], 
                                 alpha=0.3, color='blue')
        
        # Add theoretical stability line (rho = 1)
        if 'rho' in results.columns:
            stability_idx = np.argmax(results['rho'] >= 0.95)
            if stability_idx > 0:
                stable_lam = results['lambda'].iloc[stability_idx]
                self.sens_ax.axvline(x=stable_lam, color='red', linestyle='--', 
                                   linewidth=2, label=f'Stability limit (λ={stable_lam:.2f})')
        
        # Add current lambda marker if available
        if 'lam' in self.current_params:
            current_lam = self.current_params['lam']
            current_metric = results[results['lambda'].sub(current_lam).abs().idxmin()][metric]
            self.sens_ax.plot(current_lam, current_metric, 'ro', markersize=8, 
                            label=f'Current (λ={current_lam:.2f})')
        
        # Set labels and title
        self.sens_ax.set_xlabel('Arrival Rate (λ)', fontweight='bold')
        self.sens_ax.set_ylabel(metric_names.get(metric, metric), fontweight='bold')
        
        title = f"Sensitivity Analysis: {metric_names.get(metric, metric)} vs Arrival Rate"
        self.sens_ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid and legend
        self.sens_ax.grid(True, alpha=0.3, linestyle='--')
        self.sens_ax.legend()
        
        # Adjust layout
        self.sens_fig.tight_layout()
        
        # Update canvas
        self.sens_canvas.draw()
    
    def export_results(self):
        """Export simulation results to file."""
        if self.current_df.empty:
            messagebox.showwarning("Warning", "No simulation data to export!")
            return
        
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_filename = f"queue_simulation_{timestamp}.csv"
            metrics_filename = f"queue_metrics_{timestamp}.txt"
            
            # Export data to CSV
            self.current_df.to_csv(data_filename, index=False)
            
            # Export metrics to text file
            with open(metrics_filename, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("SAPPHIRE SHOPPING OUTLET - QUEUE SIMULATION RESULTS\n")
                f.write("=" * 70 + "\n\n")
                
                f.write("SIMULATION PARAMETERS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Simulation Method: {'CP-based' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
                f.write(f"Arrival Type: {self.arrival_type.get()}\n")
                f.write(f"Arrival Distribution: {self.arrival_dist.get()}\n")
                f.write(f"Arrival Parameters: {self.arrival_params.get()}\n")
                f.write(f"Arrival Rate (λ): {self.lambda_entry.get()}\n")
                f.write(f"Service Type: {self.service_type.get()}\n")
                f.write(f"Service Distribution: {self.service_dist.get()}\n")
                f.write(f"Service Parameters: {self.service_params.get()}\n")
                f.write(f"Service Rate (μ): {self.mu_entry.get()}\n")
                f.write(f"Number of Servers (c): {self.servers_entry.get()}\n")
                if self.sim_method.get() == "fixed":
                    f.write(f"Number of Customers: {self.customers_entry.get()}\n")
                else:
                    f.write(f"Max CP: {self.max_cp_entry.get()}\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                
                f.write("SIMULATION RESULTS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Customers Simulated: {len(self.current_df)}\n")
                f.write(f"Total Simulation Time: {self.current_df['End'].max():.2f}\n")
                f.write(f"Server Utilization: {self.simulator.metrics.get('utilization', 0):.2f}%\n")
                f.write(f"Throughput: {self.simulator.metrics.get('throughput', 0):.4f} customers/time unit\n\n")
                
                f.write("PERFORMANCE METRICS:\n")
                f.write("-" * 40 + "\n")
                stats = self.simulator.get_summary_statistics(self.current_df)
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
            
            messagebox.showinfo("Export Successful", 
                              f"Results exported successfully!\n\n"
                              f"Data saved to: {data_filename}\n"
                              f"Metrics saved to: {metrics_filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def reset_all(self):
        """Reset all simulation data and UI."""
        response = messagebox.askyesno("Confirm Reset", 
                                      "Are you sure you want to reset all simulation data?")
        
        if response:
            # Reset simulator
            self.simulator.reset()
            self.current_df = pd.DataFrame()
            self.current_params = {}
            
            # Reset UI components
            # Clear data table
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear text areas
            self.metrics_text.config(state=tk.NORMAL)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, "Run simulation to see metrics...\n")
            self.metrics_text.config(state=tk.DISABLED)
            
            self.analytics_text.config(state=tk.NORMAL)
            self.analytics_text.delete(1.0, tk.END)
            self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate...\n")
            self.analytics_text.config(state=tk.DISABLED)
            
            # Reset charts
            self.initialize_charts()
            
            # Reset Gantt chart
            self.gantt_ax.clear()
            self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline", fontsize=14, fontweight='bold')
            self.gantt_ax.set_xlabel("Time", fontweight='bold')
            self.gantt_ax.set_ylabel("Customers/Servers", fontweight='bold')
            self.gantt_ax.grid(True, alpha=0.3)
            self.gantt_canvas.draw()
            
            # Reset sensitivity graph
            self.sens_ax.clear()
            self.sens_ax.set_title("Sensitivity Analysis", fontsize=14, fontweight='bold')
            self.sens_ax.set_xlabel("Arrival Rate (λ)", fontweight='bold')
            self.sens_ax.set_ylabel("Metric Value", fontweight='bold')
            self.sens_ax.grid(True, alpha=0.3)
            self.sens_canvas.draw()
            
            # Reset status
            self.status_var.set("Ready")
            
            messagebox.showinfo("Reset Complete", "All simulation data has been reset successfully.")

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = QueueSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()