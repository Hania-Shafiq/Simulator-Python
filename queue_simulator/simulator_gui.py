"""
Main GUI for the queue simulator - WITH CHART FIXES
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime

from simulation_engine import QueueSimulator
from queue_analytics import QueueAnalytics
from distributions import get_distribution_params

class QueueSimulatorGUI:
    """Main GUI application for queue simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Queue Simulator - Sapphire Outlet")
        
        # Set window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        self.root.geometry(f"{window_width}x{window_height}+{int((screen_width-window_width)/2)}+{int((screen_height-window_height)/2)}")
        
        # Initialize simulator
        self.simulator = QueueSimulator()
        self.current_df = pd.DataFrame()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        control_frame = ttk.LabelFrame(main_frame, text="Simulation Configuration", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Configure grid for control frame
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # Row 0: Arrival Type
        ttk.Label(control_frame, text="Arrival Type:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.arrival_type = tk.StringVar(value="M")
        ttk.Radiobutton(control_frame, text="M (Markovian)", 
                       variable=self.arrival_type, value="M").grid(
            row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="G (General)", 
                       variable=self.arrival_type, value="G").grid(
            row=0, column=2, sticky=tk.W)
        
        # Row 1: Arrival Distribution
        ttk.Label(control_frame, text="Arrival Distribution:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.arrival_dist = tk.StringVar(value="Exponential")
        self.arrival_dist_combo = ttk.Combobox(control_frame, 
                                              textvariable=self.arrival_dist,
                                              values=["Exponential", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.arrival_dist_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Row 1: Arrival Parameters
        ttk.Label(control_frame, text="Parameters (e.g., rate=0.5):").grid(
            row=1, column=2, sticky=tk.W, padx=5)
        self.arrival_params = ttk.Entry(control_frame, width=20)
        self.arrival_params.grid(row=1, column=3, sticky=tk.W, padx=5)
        self.arrival_params.insert(0, "rate=0.5")
        
        # Row 2: Service Type
        ttk.Label(control_frame, text="Service Type:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.service_type = tk.StringVar(value="M")
        ttk.Radiobutton(control_frame, text="M (Markovian)", 
                       variable=self.service_type, value="M").grid(
            row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="G (General)", 
                       variable=self.service_type, value="G").grid(
            row=2, column=2, sticky=tk.W)
        
        # Row 3: Service Distribution
        ttk.Label(control_frame, text="Service Distribution:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.service_dist = tk.StringVar(value="Exponential")
        self.service_dist_combo = ttk.Combobox(control_frame, 
                                              textvariable=self.service_dist,
                                              values=["Exponential", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.service_dist_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Row 3: Service Parameters
        ttk.Label(control_frame, text="Parameters (e.g., rate=1.0):").grid(
            row=3, column=2, sticky=tk.W, padx=5)
        self.service_params = ttk.Entry(control_frame, width=20)
        self.service_params.grid(row=3, column=3, sticky=tk.W, padx=5)
        self.service_params.insert(0, "rate=1.0")
        
        # Row 4: System Parameters
        ttk.Label(control_frame, text="System Parameters:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Lambda
        ttk.Label(control_frame, text="λ (Arrival Rate):").grid(
            row=5, column=0, sticky=tk.W, padx=5)
        self.lambda_entry = ttk.Entry(control_frame, width=10)
        self.lambda_entry.grid(row=5, column=1, sticky=tk.W, padx=5)
        self.lambda_entry.insert(0, "0.5")
        
        # Mu
        ttk.Label(control_frame, text="μ (Service Rate):").grid(
            row=5, column=2, sticky=tk.W, padx=5)
        self.mu_entry = ttk.Entry(control_frame, width=10)
        self.mu_entry.grid(row=5, column=3, sticky=tk.W, padx=5)
        self.mu_entry.insert(0, "1.0")
        
        # Servers
        ttk.Label(control_frame, text="Servers (c):").grid(
            row=5, column=4, sticky=tk.W, padx=5)
        self.servers_entry = ttk.Entry(control_frame, width=5)
        self.servers_entry.grid(row=5, column=5, sticky=tk.W, padx=5)
        self.servers_entry.insert(0, "1")
        
        # Customers
        ttk.Label(control_frame, text="Number of Customers:").grid(
            row=6, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.customers_entry = ttk.Entry(control_frame, width=10)
        self.customers_entry.grid(row=6, column=1, sticky=tk.W, padx=5, pady=(10, 0))
        self.customers_entry.insert(0, "50")
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=7, column=0, columnspan=6, pady=15)
        
        ttk.Button(button_frame, text="Run Simulation", 
                  command=self.run_simulation, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analytical Results", 
                  command=self.show_analytics, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Results", 
                  command=self.export_results, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_simulation, width=15).pack(side=tk.LEFT, padx=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_data_tab()
        self.create_metrics_tab()
        self.create_charts_tab()
        self.create_gantt_tab()
        self.create_analytics_tab()
        
        # Bind events
        self.arrival_type.trace('w', self.update_distribution_options)
        self.service_type.trace('w', self.update_distribution_options)
        self.update_distribution_options()
    
    def update_distribution_options(self, *args):
        """Update distribution options based on selected type."""
        if self.arrival_type.get() == "M":
            self.arrival_dist_combo.config(values=["Exponential"])
            self.arrival_dist.set("Exponential")
            self.arrival_params.delete(0, tk.END)
            self.arrival_params.insert(0, "rate=0.5")
        else:
            self.arrival_dist_combo.config(values=["Exponential", "Uniform", "Normal", "Gamma"])
            self.arrival_dist.set("Uniform")
            self.arrival_params.delete(0, tk.END)
            self.arrival_params.insert(0, "min=1.0,max=3.0")
            
        if self.service_type.get() == "M":
            self.service_dist_combo.config(values=["Exponential"])
            self.service_dist.set("Exponential")
            self.service_params.delete(0, tk.END)
            self.service_params.insert(0, "rate=1.0")
        else:
            self.service_dist_combo.config(values=["Exponential", "Uniform", "Normal", "Gamma"])
            self.service_dist.set("Uniform")
            self.service_params.delete(0, tk.END)
            self.service_params.insert(0, "min=0.5,max=1.5")
    
    def create_data_tab(self):
        """Create data table tab."""
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Simulation Data")
        
        # Treeview for data
        columns = ("ID", "Arrival", "Service", "Server", "Start", "End", 
                  "Wait", "Turnaround", "Response")
        
        # Create scrollable frame
        container = ttk.Frame(self.data_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
        
        # Configure columns
        col_widths = [50, 80, 80, 60, 80, 80, 80, 100, 80]
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
    
    def create_metrics_tab(self):
        """Create metrics display tab."""
        self.metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.metrics_frame, text="Performance Metrics")
        
        # Create a Text widget with scrollbar
        self.metrics_text = scrolledtext.ScrolledText(
            self.metrics_frame, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial message
        self.metrics_text.insert(tk.END, "Run simulation to see metrics...\n")
        self.metrics_text.config(state=tk.DISABLED)
    
    def create_charts_tab(self):
        """Create charts tab - FIXED VERSION."""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Performance Charts")
        
        # Create a single figure with multiple subplots
        self.charts_fig = Figure(figsize=(12, 8), dpi=100)
        
        # Create subplots (3 rows, 1 column)
        self.chart_ax1 = self.charts_fig.add_subplot(311)  # Wait time
        self.chart_ax2 = self.charts_fig.add_subplot(312)  # Turnaround time
        self.chart_ax3 = self.charts_fig.add_subplot(313)  # Response time
        
        # Create canvas
        self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, self.charts_frame)
        self.charts_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(self.charts_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        toolbar = NavigationToolbar2Tk(self.charts_canvas, toolbar_frame)
        toolbar.update()
    
    def create_gantt_tab(self):
        """Create Gantt chart tab - FIXED VERSION."""
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="Gantt Chart")
        
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
        
        # Initial empty chart
        self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline")
        self.gantt_ax.set_xlabel("Time")
        self.gantt_ax.set_ylabel("Customers")
        self.gantt_canvas.draw()
    
    def create_analytics_tab(self):
        """Create analytical results tab."""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytical Results")
        
        # Create a Text widget with scrollbar
        self.analytics_text = scrolledtext.ScrolledText(
            self.analytics_frame, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25
        )
        self.analytics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial message
        self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate...\n")
        self.analytics_text.config(state=tk.DISABLED)
    
    def run_simulation(self):
        """Run the queue simulation."""
        try:
            # Get parameters
            num_customers = int(self.customers_entry.get())
            num_servers = int(self.servers_entry.get())
            
            # Validate parameters
            if num_customers <= 0:
                messagebox.showerror("Error", "Number of customers must be positive.")
                return
            if num_servers <= 0:
                messagebox.showerror("Error", "Number of servers must be positive.")
                return
            
            # Parse distribution parameters
            arrival_params = self.parse_params(self.arrival_params.get())
            service_params = self.parse_params(self.service_params.get())
            
            # Run simulation
            if num_servers == 1:
                df = self.simulator.simulate_single_server(
                    num_customers,
                    self.arrival_dist.get(),
                    arrival_params,
                    self.service_dist.get(),
                    service_params
                )
            else:
                df = self.simulator.simulate_multi_server(
                    num_customers,
                    self.arrival_dist.get(),
                    arrival_params,
                    self.service_dist.get(),
                    service_params,
                    num_servers
                )
            
            self.current_df = df
            
            # Update UI
            self.update_data_table(df)
            self.update_metrics_display()
            self.update_charts(df)
            self.update_gantt_chart(df, num_servers)
            
            messagebox.showinfo("Success", f"Simulation completed successfully!\nProcessed {len(df)} customers.")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input value: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def parse_params(self, params_str: str) -> dict:
        """Parse parameters string to dictionary."""
        params = {}
        if params_str:
            # Remove whitespace and split by comma
            items = params_str.replace(" ", "").split(",")
            for item in items:
                if "=" in item:
                    key, value = item.split("=")
                    try:
                        params[key.strip()] = float(value.strip())
                    except ValueError:
                        params[key.strip()] = value.strip()
        return params
    
    def update_data_table(self, df: pd.DataFrame):
        """Update the data table with simulation results."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data (limit to 1000 rows for performance)
        display_df = df.head(1000) if len(df) > 1000 else df
        
        for _, row in display_df.iterrows():
            self.tree.insert("", tk.END, values=tuple(row))
    
    def update_metrics_display(self):
        """Update metrics display with simulation statistics."""
        if self.current_df.empty:
            return
        
        stats = self.simulator.get_summary_statistics(self.current_df)
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        
        # Header
        self.metrics_text.insert(tk.END, "=" * 60 + "\n")
        self.metrics_text.insert(tk.END, "SIMULATION PERFORMANCE METRICS\n")
        self.metrics_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Basic metrics
        self.metrics_text.insert(tk.END, "📊 BASIC STATISTICS\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        basic_stats = [
            ("Total Customers", len(self.current_df)),
            ("Simulation Duration", f"{self.current_df['End'].max():.2f}"),
            ("Server Utilization", f"{self.simulator.metrics.get('utilization', 0):.2f}%"),
            ("Throughput", f"{self.simulator.metrics.get('throughput', 0):.4f} cust/time"),
            ("Average Service Time", f"{self.current_df['Service'].mean():.4f}"),
            ("Average Wait Time", f"{self.current_df['Wait'].mean():.4f}"),
            ("Average Turnaround Time", f"{self.current_df['Turnaround'].mean():.4f}"),
            ("Average Response Time", f"{self.current_df['Response'].mean():.4f}")
        ]
        
        for name, value in basic_stats:
            self.metrics_text.insert(tk.END, f"{name:25}: {value}\n")
        
        # Wait time statistics
        self.metrics_text.insert(tk.END, "\n⏱️  WAIT TIME ANALYSIS\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        wait_stats = [
            ("Minimum Wait", f"{self.current_df['Wait'].min():.4f}"),
            ("Maximum Wait", f"{self.current_df['Wait'].max():.4f}"),
            ("Std Deviation", f"{self.current_df['Wait'].std():.4f}"),
            ("Median Wait", f"{self.current_df['Wait'].median():.4f}")
        ]
        
        for name, value in wait_stats:
            self.metrics_text.insert(tk.END, f"{name:25}: {value}\n")
        
        # Percentiles
        if "Wait Time Percentiles" in stats:
            self.metrics_text.insert(tk.END, "\n📈 WAIT TIME PERCENTILES\n")
            self.metrics_text.insert(tk.END, "-" * 40 + "\n")
            for percentile, value in stats["Wait Time Percentiles"].items():
                self.metrics_text.insert(tk.END, f"{percentile:25}: {value:.4f}\n")
        
        # Server utilizations if multi-server
        if "server_utilizations" in self.simulator.metrics:
            self.metrics_text.insert(tk.END, "\n🖥️  SERVER UTILIZATIONS\n")
            self.metrics_text.insert(tk.END, "-" * 40 + "\n")
            for i, util in enumerate(self.simulator.metrics["server_utilizations"]):
                self.metrics_text.insert(tk.END, f"Server {i+1:20}: {util:.2f}%\n")
        
        self.metrics_text.config(state=tk.DISABLED)
    
    def update_charts(self, df: pd.DataFrame):
        """Update performance charts."""
        if df.empty:
            return
        
        # Clear previous plots
        self.chart_ax1.clear()
        self.chart_ax2.clear()
        self.chart_ax3.clear()
        
        # Limit to first 100 customers for clarity
        plot_df = df.head(100)
        
        # Colors
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        # Chart 1: Wait Time
        customer_ids = plot_df['ID'].astype(str).tolist()
        wait_times = plot_df['Wait'].tolist()
        
        bars1 = self.chart_ax1.bar(customer_ids, wait_times, color=colors[0], alpha=0.7)
        self.chart_ax1.set_title('Wait Time per Customer', fontsize=12, fontweight='bold')
        self.chart_ax1.set_xlabel('Customer ID')
        self.chart_ax1.set_ylabel('Wait Time')
        self.chart_ax1.tick_params(axis='x', rotation=45)
        self.chart_ax1.grid(True, alpha=0.3)
        
        # Chart 2: Turnaround Time
        turnaround_times = plot_df['Turnaround'].tolist()
        bars2 = self.chart_ax2.bar(customer_ids, turnaround_times, color=colors[1], alpha=0.7)
        self.chart_ax2.set_title('Turnaround Time per Customer', fontsize=12, fontweight='bold')
        self.chart_ax2.set_xlabel('Customer ID')
        self.chart_ax2.set_ylabel('Turnaround Time')
        self.chart_ax2.tick_params(axis='x', rotation=45)
        self.chart_ax2.grid(True, alpha=0.3)
        
        # Chart 3: Response Time
        response_times = plot_df['Response'].tolist()
        bars3 = self.chart_ax3.bar(customer_ids, response_times, color=colors[2], alpha=0.7)
        self.chart_ax3.set_title('Response Time per Customer', fontsize=12, fontweight='bold')
        self.chart_ax3.set_xlabel('Customer ID')
        self.chart_ax3.set_ylabel('Response Time')
        self.chart_ax3.tick_params(axis='x', rotation=45)
        self.chart_ax3.grid(True, alpha=0.3)
        
        # Adjust layout
        self.charts_fig.tight_layout()
        
        # Update canvas
        self.charts_canvas.draw()
    
    def update_gantt_chart(self, df: pd.DataFrame, num_servers: int):
        """Update Gantt chart visualization - FIXED VERSION."""
        if df.empty:
            return
        
        # Clear previous plot
        self.gantt_ax.clear()
        
        # Get unique servers
        servers = df['Server'].unique()
        server_map = {server: i+1 for i, server in enumerate(sorted(servers))}
        
        # Create color map
        colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
        
        # Plot each customer
        for idx, (_, row) in enumerate(df.head(50).iterrows()):  # Limit to first 50 for clarity
            server_id = server_map[row['Server']]
            start_time = row['Start']
            duration = row['Service']
            
            # Create horizontal bar
            self.gantt_ax.barh(
                server_id,
                duration,
                left=start_time,
                height=0.6,
                color=colors[idx % len(colors)],
                edgecolor='black',
                alpha=0.7
            )
            
            # Add customer ID label
            label_x = start_time + duration / 2
            self.gantt_ax.text(
                label_x,
                server_id,
                f"C{int(row['ID'])}",
                ha='center',
                va='center',
                fontsize=8,
                fontweight='bold',
                color='black'
            )
        
        # Set y-axis labels
        self.gantt_ax.set_yticks(list(server_map.values()))
        self.gantt_ax.set_yticklabels(list(server_map.keys()))
        
        # Set labels and title
        self.gantt_ax.set_xlabel('Time', fontweight='bold')
        self.gantt_ax.set_ylabel('Servers', fontweight='bold')
        self.gantt_ax.set_title('Gantt Chart - Customer Service Timeline', fontsize=14, fontweight='bold')
        
        # Add grid
        self.gantt_ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend for server utilization
        total_time = df['End'].max()
        util_text = ""
        for server in sorted(servers):
            server_df = df[df['Server'] == server]
            busy_time = server_df['Service'].sum()
            utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
            util_text += f"{server}: {utilization:.1f}%\n"
        
        # Add utilization info as text box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.gantt_ax.text(
            0.02, 0.98, 
            f"Server Utilization:\n{util_text}",
            transform=self.gantt_ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=props
        )
        
        # Adjust layout
        self.gantt_fig.tight_layout()
        
        # Update canvas
        self.gantt_canvas.draw()
    
    def show_analytics(self):
        """Calculate and display analytical results."""
        try:
            lambda_val = float(self.lambda_entry.get())
            mu_val = float(self.mu_entry.get())
            c_val = int(self.servers_entry.get())
            
            # Validate inputs
            if lambda_val <= 0 or mu_val <= 0:
                messagebox.showerror("Input Error", "λ and μ must be positive numbers.")
                return
            
            # Calculate analytical results
            if c_val == 1:
                results = QueueAnalytics.mm1(lambda_val, mu_val)
                queue_type = "M/M/1"
            else:
                results = QueueAnalytics.mmc(lambda_val, mu_val, c_val)
                queue_type = f"M/M/{c_val}"
            
            # Display results
            self.analytics_text.config(state=tk.NORMAL)
            self.analytics_text.delete(1.0, tk.END)
            
            self.analytics_text.insert(tk.END, "=" * 60 + "\n")
            self.analytics_text.insert(tk.END, f"ANALYTICAL RESULTS - {queue_type}\n")
            self.analytics_text.insert(tk.END, "=" * 60 + "\n\n")
            self.analytics_text.insert(tk.END, f"Parameters: λ = {lambda_val}, μ = {mu_val}, c = {c_val}\n\n")
            
            if "error" in results:
                self.analytics_text.insert(tk.END, f"❌ ERROR: {results['error']}\n")
            else:
                for key, value in results.items():
                    if callable(value):
                        continue
                    if isinstance(value, float):
                        self.analytics_text.insert(tk.END, f"{key:30}: {value:.6f}\n")
                    else:
                        self.analytics_text.insert(tk.END, f"{key:30}: {value}\n")
            
            # Add comparison if simulation was run
            if not self.current_df.empty:
                self.analytics_text.insert(tk.END, "\n" + "=" * 60 + "\n")
                self.analytics_text.insert(tk.END, "SIMULATION vs ANALYTICAL COMPARISON\n")
                self.analytics_text.insert(tk.END, "=" * 60 + "\n\n")
                
                sim_wait = self.current_df["Wait"].mean()
                sim_turnaround = self.current_df["Turnaround"].mean()
                
                if "Wq (Avg wait in queue)" in results:
                    theo_wait = results["Wq (Avg wait in queue)"]
                    diff_pct = abs(theo_wait - sim_wait) / theo_wait * 100 if theo_wait > 0 else 0
                    self.analytics_text.insert(tk.END, 
                        f"Wait Time (Wq):\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Theoretical: {theo_wait:.6f}\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Simulation:  {sim_wait:.6f}\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Difference:  {abs(theo_wait - sim_wait):.6f} ({diff_pct:.2f}%)\n\n")
                
                if "W (Avg time in system)" in results:
                    theo_turnaround = results["W (Avg time in system)"]
                    diff_pct = abs(theo_turnaround - sim_turnaround) / theo_turnaround * 100 if theo_turnaround > 0 else 0
                    self.analytics_text.insert(tk.END, 
                        f"Turnaround Time (W):\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Theoretical: {theo_turnaround:.6f}\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Simulation:  {sim_turnaround:.6f}\n")
                    self.analytics_text.insert(tk.END, 
                        f"  Difference:  {abs(theo_turnaround - sim_turnaround):.6f} ({diff_pct:.2f}%)\n")
            
            self.analytics_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for λ and μ.")
        except Exception as e:
            messagebox.showerror("Error", f"Analytical calculation failed: {str(e)}")
    
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
                f.write("=" * 60 + "\n")
                f.write("QUEUE SIMULATION RESULTS\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("SIMULATION PARAMETERS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Arrival Type: {self.arrival_type.get()}\n")
                f.write(f"Arrival Distribution: {self.arrival_dist.get()}\n")
                f.write(f"Arrival Parameters: {self.arrival_params.get()}\n")
                f.write(f"Service Type: {self.service_type.get()}\n")
                f.write(f"Service Distribution: {self.service_dist.get()}\n")
                f.write(f"Service Parameters: {self.service_params.get()}\n")
                f.write(f"λ (Arrival Rate): {self.lambda_entry.get()}\n")
                f.write(f"μ (Service Rate): {self.mu_entry.get()}\n")
                f.write(f"Servers (c): {self.servers_entry.get()}\n")
                f.write(f"Number of Customers: {self.customers_entry.get()}\n\n")
                
                f.write("PERFORMANCE METRICS:\n")
                f.write("-" * 40 + "\n")
                stats = self.simulator.get_summary_statistics(self.current_df)
                for key, value in stats.items():
                    if not isinstance(value, dict):
                        if isinstance(value, float):
                            f.write(f"{key}: {value:.4f}\n")
                        else:
                            f.write(f"{key}: {value}\n")
            
            messagebox.showinfo("Export Successful", 
                              f"Results exported successfully!\n\n"
                              f"Data: {data_filename}\n"
                              f"Metrics: {metrics_filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def reset_simulation(self):
        """Reset the simulation."""
        response = messagebox.askyesno("Confirm Reset", 
                                      "Are you sure you want to reset all simulation data?")
        
        if response:
            self.simulator.reset()
            self.current_df = pd.DataFrame()
            
            # Clear tables
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
            
            # Clear charts
            self.chart_ax1.clear()
            self.chart_ax2.clear()
            self.chart_ax3.clear()
            self.chart_ax1.set_title('Wait Time per Customer')
            self.chart_ax1.set_xlabel('Customer ID')
            self.chart_ax1.set_ylabel('Wait Time')
            self.chart_ax2.set_title('Turnaround Time per Customer')
            self.chart_ax2.set_xlabel('Customer ID')
            self.chart_ax2.set_ylabel('Turnaround Time')
            self.chart_ax3.set_title('Response Time per Customer')
            self.chart_ax3.set_xlabel('Customer ID')
            self.chart_ax3.set_ylabel('Response Time')
            self.charts_canvas.draw()
            
            # Clear Gantt chart
            self.gantt_ax.clear()
            self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline")
            self.gantt_ax.set_xlabel("Time")
            self.gantt_ax.set_ylabel("Customers")
            self.gantt_canvas.draw()
            
            messagebox.showinfo("Reset Complete", "Simulation has been reset successfully.")

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = QueueSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()