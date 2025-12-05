"""
Main GUI for the queue simulator.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns

from simulation_engine import QueueSimulator
from queue_analytics import QueueAnalytics
from distributions import get_distribution_params

class QueueSimulatorGUI:
    """Main GUI application for queue simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Queue Simulator - Sapphire Outlet")
        self.root.geometry("1400x900")
        
        # Set style
        self.setup_styles()
        
        # Initialize simulator
        self.simulator = QueueSimulator()
        self.current_df = pd.DataFrame()
        
        # Create GUI
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.accent_color = "#e74c3c"
        
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Metric.TLabel", font=("Arial", 10, "bold"), foreground=self.primary_color)
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        control_frame = ttk.LabelFrame(main_frame, text="Simulation Configuration", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Arrival configuration
        ttk.Label(control_frame, text="Arrival Process:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Arrival type
        self.arrival_type = tk.StringVar(value="M")
        ttk.Radiobutton(control_frame, text="M (Markovian/Exponential)", 
                       variable=self.arrival_type, value="M").grid(
            row=1, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(control_frame, text="G (General)", 
                       variable=self.arrival_type, value="G").grid(
            row=1, column=1, sticky=tk.W)
        
        # Arrival distribution
        ttk.Label(control_frame, text="Distribution:").grid(
            row=2, column=0, sticky=tk.W, padx=5)
        self.arrival_dist = tk.StringVar(value="Exponential")
        self.arrival_dist_combo = ttk.Combobox(control_frame, 
                                              textvariable=self.arrival_dist,
                                              values=["Exponential", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.arrival_dist_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Arrival parameters
        ttk.Label(control_frame, text="Parameters:").grid(
            row=2, column=2, sticky=tk.W, padx=5)
        self.arrival_params = ttk.Entry(control_frame, width=20)
        self.arrival_params.grid(row=2, column=3, sticky=tk.W, padx=5)
        self.arrival_params.insert(0, "rate=0.5")
        
        # Service configuration
        ttk.Label(control_frame, text="\nService Process:", 
                 font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=(10, 5))
        
        # Service type
        self.service_type = tk.StringVar(value="M")
        ttk.Radiobutton(control_frame, text="M (Markovian/Exponential)", 
                       variable=self.service_type, value="M").grid(
            row=4, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(control_frame, text="G (General)", 
                       variable=self.service_type, value="G").grid(
            row=4, column=1, sticky=tk.W)
        
        # Service distribution
        ttk.Label(control_frame, text="Distribution:").grid(
            row=5, column=0, sticky=tk.W, padx=5)
        self.service_dist = tk.StringVar(value="Exponential")
        self.service_dist_combo = ttk.Combobox(control_frame, 
                                              textvariable=self.service_dist,
                                              values=["Exponential", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=15)
        self.service_dist_combo.grid(row=5, column=1, sticky=tk.W, padx=5)
        
        # Service parameters
        ttk.Label(control_frame, text="Parameters:").grid(
            row=5, column=2, sticky=tk.W, padx=5)
        self.service_params = ttk.Entry(control_frame, width=20)
        self.service_params.grid(row=5, column=3, sticky=tk.W, padx=5)
        self.service_params.insert(0, "rate=1.0")
        
        # System parameters
        ttk.Label(control_frame, text="\nSystem Parameters:", 
                 font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky=tk.W, padx=5, pady=(10, 5))
        
        # Lambda (arrival rate)
        ttk.Label(control_frame, text="λ (Arrival Rate):").grid(
            row=7, column=0, sticky=tk.W, padx=5)
        self.lambda_entry = ttk.Entry(control_frame, width=10)
        self.lambda_entry.grid(row=7, column=1, sticky=tk.W, padx=5)
        self.lambda_entry.insert(0, "0.5")
        
        # Mu (service rate)
        ttk.Label(control_frame, text="μ (Service Rate):").grid(
            row=7, column=2, sticky=tk.W, padx=5)
        self.mu_entry = ttk.Entry(control_frame, width=10)
        self.mu_entry.grid(row=7, column=3, sticky=tk.W, padx=5)
        self.mu_entry.insert(0, "1.0")
        
        # Number of servers
        ttk.Label(control_frame, text="Servers (c):").grid(
            row=7, column=4, sticky=tk.W, padx=5)
        self.servers_entry = ttk.Entry(control_frame, width=5)
        self.servers_entry.grid(row=7, column=5, sticky=tk.W, padx=5)
        self.servers_entry.insert(0, "1")
        
        # Number of customers
        ttk.Label(control_frame, text="Customers:").grid(
            row=8, column=0, sticky=tk.W, padx=5, pady=(5, 0))
        self.customers_entry = ttk.Entry(control_frame, width=10)
        self.customers_entry.grid(row=8, column=1, sticky=tk.W, padx=5)
        self.customers_entry.insert(0, "100")
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=9, column=0, columnspan=6, pady=20)
        
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
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_data_tab()
        self.create_metrics_tab()
        self.create_charts_tab()
        self.create_gantt_tab()
        self.create_analytics_tab()
        
        # Bind events
        self.arrival_type.trace('w', self.update_distribution_options)
        self.service_type.trace('w', self.update_distribution_options)
        
    def create_data_tab(self):
        """Create data table tab."""
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Simulation Data")
        
        # Treeview for data
        columns = ("ID", "Arrival", "Service", "Server", "Start", "End", 
                  "Wait", "Turnaround", "Response")
        
        self.tree = ttk.Treeview(self.data_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.data_frame.grid_rowconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(0, weight=1)
        
    def create_metrics_tab(self):
        """Create metrics display tab."""
        self.metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.metrics_frame, text="Performance Metrics")
        
        # Metrics display area
        self.metrics_text = tk.Text(self.metrics_frame, wrap=tk.WORD, 
                                   font=("Consolas", 10), height=25)
        scrollbar = ttk.Scrollbar(self.metrics_frame, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=scrollbar.set)
        
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial message
        self.metrics_text.insert(tk.END, "Run simulation to see metrics...")
        self.metrics_text.config(state=tk.DISABLED)
        
    def create_charts_tab(self):
        """Create charts tab."""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Charts")
        
        # Canvas for charts
        self.charts_canvas = tk.Canvas(self.charts_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.charts_frame, orient=tk.VERTICAL, 
                                 command=self.charts_canvas.yview)
        
        self.charts_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Inner frame for charts
        self.charts_inner_frame = ttk.Frame(self.charts_canvas)
        
        # Create window in canvas
        self.charts_canvas.create_window((0, 0), window=self.charts_inner_frame, anchor=tk.NW)
        
        # Layout
        self.charts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind configure event to update scrollregion
        self.charts_inner_frame.bind("<Configure>", 
            lambda e: self.charts_canvas.configure(scrollregion=self.charts_canvas.bbox("all")))
        
    def create_gantt_tab(self):
        """Create Gantt chart tab."""
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="Gantt Chart")
        
        # Create figure for Gantt chart
        self.gantt_fig = Figure(figsize=(10, 6), dpi=100)
        self.gantt_ax = self.gantt_fig.add_subplot(111)
        
        # Canvas for Gantt
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, self.gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = NavigationToolbar2Tk(self.gantt_canvas, self.gantt_frame)
        toolbar.update()
        
    def create_analytics_tab(self):
        """Create analytical results tab."""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytical Results")
        
        # Text widget for analytics
        self.analytics_text = tk.Text(self.analytics_frame, wrap=tk.WORD,
                                     font=("Consolas", 10), height=25)
        scrollbar = ttk.Scrollbar(self.analytics_frame, command=self.analytics_text.yview)
        self.analytics_text.configure(yscrollcommand=scrollbar.set)
        
        self.analytics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial message
        self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate...")
        self.analytics_text.config(state=tk.DISABLED)
        
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
    
    def run_simulation(self):
        """Run the queue simulation."""
        try:
            # Get parameters
            num_customers = int(self.customers_entry.get())
            num_servers = int(self.servers_entry.get())
            
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
            self.create_charts(df)
            self.create_gantt_chart(df, num_servers)
            
            messagebox.showinfo("Success", "Simulation completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def parse_params(self, params_str: str) -> dict:
        """Parse parameters string to dictionary."""
        params = {}
        if params_str:
            for item in params_str.split(","):
                if "=" in item:
                    key, value = item.split("=")
                    params[key.strip()] = float(value.strip())
        return params
    
    def update_data_table(self, df: pd.DataFrame):
        """Update the data table with simulation results."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data
        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=tuple(row))
    
    def update_metrics_display(self):
        """Update metrics display with simulation statistics."""
        if self.current_df.empty:
            return
        
        stats = self.simulator.get_summary_statistics(self.current_df)
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        
        # Header
        self.metrics_text.insert(tk.END, "SIMULATION METRICS\n")
        self.metrics_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Basic metrics
        self.metrics_text.insert(tk.END, "Basic Statistics:\n")
        self.metrics_text.insert(tk.END, "-" * 30 + "\n")
        for key, value in stats.items():
            if not isinstance(value, dict):
                self.metrics_text.insert(tk.END, f"{key:<30}: {value:.4f}\n")
        
        # Wait time percentiles
        if "Wait Time Percentiles" in stats:
            self.metrics_text.insert(tk.END, "\nWait Time Percentiles:\n")
            self.metrics_text.insert(tk.END, "-" * 30 + "\n")
            for percentile, value in stats["Wait Time Percentiles"].items():
                self.metrics_text.insert(tk.END, f"{percentile:<25}: {value:.4f}\n")
        
        # Simulation metrics
        self.metrics_text.insert(tk.END, "\nSimulation Metrics:\n")
        self.metrics_text.insert(tk.END, "-" * 30 + "\n")
        for key, value in self.simulator.metrics.items():
            if isinstance(value, list):
                for i, val in enumerate(value):
                    self.metrics_text.insert(tk.END, f"Server {i+1} Utilization: {val:.2f}%\n")
            else:
                self.metrics_text.insert(tk.END, f"{key:<25}: {value:.4f}\n")
        
        self.metrics_text.config(state=tk.DISABLED)
    
    def create_charts(self, df: pd.DataFrame):
        """Create performance charts."""
        # Clear previous charts
        for widget in self.charts_inner_frame.winfo_children():
            widget.destroy()
        
        if df.empty:
            return
        
        # Limit to first 50 customers for clarity
        plot_df = df.head(50)
        
        # Create multiple charts
        charts = [
            ("Wait Time", "Wait", "#ff9999"),
            ("Turnaround Time", "Turnaround", "#66b3ff"),
            ("Service Time", "Service", "#99ff99"),
            ("Response Time", "Response", "#ffcc99")
        ]
        
        for i, (title, column, color) in enumerate(charts):
            fig = Figure(figsize=(8, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            # Create bar chart
            x_positions = np.arange(len(plot_df))
            bars = ax.bar(x_positions, plot_df[column], color=color, width=0.6)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_title(f"{title} per Customer", fontsize=12, fontweight='bold')
            ax.set_xlabel("Customer ID")
            ax.set_ylabel("Time")
            ax.set_xticks(x_positions)
            ax.set_xticklabels([f"{int(id)}" for id in plot_df["ID"]], rotation=45, fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Add to GUI
            canvas = FigureCanvasTkAgg(fig, self.charts_inner_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.X, padx=10, pady=5)
            
            # Add toolbar for each chart
            toolbar_frame = ttk.Frame(self.charts_inner_frame)
            toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
            
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            canvas.get_tk_widget().pack(in_=toolbar_frame, side=tk.LEFT)
    
    def create_gantt_chart(self, df: pd.DataFrame, num_servers: int):
        """Create Gantt chart visualization."""
        self.gantt_ax.clear()
        
        if df.empty:
            return
        
        # Get Gantt data
        gantt_data = self.simulator.get_gantt_data(df, num_servers)
        
        # Prepare data for plotting
        colors = plt.cm.Set3(np.linspace(0, 1, len(gantt_data)))
        
        if num_servers == 1:
            # Single server - horizontal bars
            y_positions = range(len(gantt_data))
            
            for i, task in enumerate(gantt_data):
                duration = task['end'] - task['start']
                self.gantt_ax.barh(y_positions[i], duration, 
                                  left=task['start'], 
                                  color=colors[i], 
                                  edgecolor='black')
                
                # Add task label
                self.gantt_ax.text(task['start'] + duration/2, y_positions[i],
                                 f"C{task['task'].split()[-1]}",
                                 ha='center', va='center', color='black', fontsize=8)
            
            self.gantt_ax.set_yticks(y_positions)
            self.gantt_ax.set_yticklabels([task['task'] for task in gantt_data])
            self.gantt_ax.set_ylabel('Customers')
            
        else:
            # Multiple servers
            server_dict = {}
            for task in gantt_data:
                server = task['server']
                if server not in server_dict:
                    server_dict[server] = []
                server_dict[server].append(task)
            
            # Plot each server
            for i, (server, tasks) in enumerate(server_dict.items()):
                for j, task in enumerate(tasks):
                    duration = task['end'] - task['start']
                    self.gantt_ax.barh(i, duration, 
                                      left=task['start'], 
                                      color=colors[j % len(colors)],
                                      edgecolor='black')
                    
                    # Add task label
                    self.gantt_ax.text(task['start'] + duration/2, i,
                                     f"C{task['task'].split()[-1]}",
                                     ha='center', va='center', color='black', fontsize=8)
            
            self.gantt_ax.set_yticks(range(len(server_dict)))
            self.gantt_ax.set_yticklabels(list(server_dict.keys()))
            self.gantt_ax.set_ylabel('Servers')
        
        self.gantt_ax.set_xlabel('Time')
        self.gantt_ax.set_title('Gantt Chart - Customer Service Timeline')
        self.gantt_ax.grid(True, alpha=0.3)
        
        self.gantt_canvas.draw()
    
    def show_analytics(self):
        """Calculate and display analytical results."""
        try:
            lambda_ = float(self.lambda_entry.get())
            mu = float(self.mu_entry.get())
            c = int(self.servers_entry.get())
            
            # Calculate analytical results
            if c == 1:
                results = QueueAnalytics.mm1(lambda_, mu)
                queue_type = "M/M/1"
            else:
                results = QueueAnalytics.mmc(lambda_, mu, c)
                queue_type = f"M/M/{c}"
            
            # Display results
            self.analytics_text.config(state=tk.NORMAL)
            self.analytics_text.delete(1.0, tk.END)
            
            self.analytics_text.insert(tk.END, f"ANALYTICAL RESULTS - {queue_type}\n")
            self.analytics_text.insert(tk.END, "=" * 50 + "\n")
            self.analytics_text.insert(tk.END, f"λ = {lambda_}, μ = {mu}, c = {c}\n\n")
            
            if "error" in results:
                self.analytics_text.insert(tk.END, f"ERROR: {results['error']}\n")
            else:
                for key, value in results.items():
                    if callable(value):
                        continue
                    self.analytics_text.insert(tk.END, f"{key:<30}: {value:.4f}\n")
            
            # Add comparison if simulation was run
            if not self.current_df.empty:
                self.analytics_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.analytics_text.insert(tk.END, "COMPARISON WITH SIMULATION\n")
                self.analytics_text.insert(tk.END, "-" * 30 + "\n")
                
                sim_wait = self.current_df["Wait"].mean()
                sim_turnaround = self.current_df["Turnaround"].mean()
                
                if "Wq (Avg wait in queue)" in results:
                    theo_wait = results["Wq (Avg wait in queue)"]
                    diff = abs(theo_wait - sim_wait)
                    self.analytics_text.insert(tk.END, 
                        f"Wait Time: Theory={theo_wait:.4f}, Sim={sim_wait:.4f}, Diff={diff:.4f}\n")
                
                if "W (Avg time in system)" in results:
                    theo_turnaround = results["W (Avg time in system)"]
                    diff = abs(theo_turnaround - sim_turnaround)
                    self.analytics_text.insert(tk.END, 
                        f"Turnaround: Theory={theo_turnaround:.4f}, Sim={sim_turnaround:.4f}, Diff={diff:.4f}\n")
            
            self.analytics_text.config(state=tk.DISABLED)
            
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
            filename = f"queue_simulation_{timestamp}.csv"
            
            # Export data
            self.current_df.to_csv(filename, index=False)
            
            # Export metrics
            metrics_filename = f"queue_metrics_{timestamp}.txt"
            with open(metrics_filename, 'w') as f:
                f.write("QUEUE SIMULATION METRICS\n")
                f.write("=" * 50 + "\n\n")
                
                stats = self.simulator.get_summary_statistics(self.current_df)
                for key, value in stats.items():
                    if not isinstance(value, dict):
                        f.write(f"{key}: {value}\n")
                
                f.write("\nSimulation Parameters:\n")
                f.write(f"Arrival Distribution: {self.arrival_dist.get()}\n")
                f.write(f"Service Distribution: {self.service_dist.get()}\n")
                f.write(f"Number of Servers: {self.servers_entry.get()}\n")
                f.write(f"Number of Customers: {self.customers_entry.get()}\n")
            
            messagebox.showinfo("Success", 
                              f"Results exported to:\n{filename}\n{metrics_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.simulator.reset()
        self.current_df = pd.DataFrame()
        
        # Clear tables
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear text areas
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, "Run simulation to see metrics...")
        self.metrics_text.config(state=tk.DISABLED)
        
        self.analytics_text.config(state=tk.NORMAL)
        self.analytics_text.delete(1.0, tk.END)
        self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate...")
        self.analytics_text.config(state=tk.DISABLED)
        
        # Clear charts
        for widget in self.charts_inner_frame.winfo_children():
            widget.destroy()
        
        # Clear Gantt chart
        self.gantt_ax.clear()
        self.gantt_canvas.draw()
        
        messagebox.showinfo("Reset", "Simulation has been reset.")

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = QueueSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()