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

from simulation_engine import QueueSimulator
from queue_analytics import QueueAnalytics
from distributions import get_distribution_params

class QueueSimulatorGUI:
    """Main GUI application for queue simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sapphire Shopping Outlet - Queue Simulator")
        
        # Set seaborn style for better looking plots
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['font.size'] = 10
        
        # Initialize simulator
        self.simulator = QueueSimulator()
        self.current_df = pd.DataFrame()
        self.current_params = {}
        
        # Create main container with scrollbar
        self.create_main_container()
        
        # Maximize window
        self.root.state('zoomed')
    
    def create_main_container(self):
        """Create main container with scrollbar for entire application."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Bind the scrollable frame to the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down
        
        # Create GUI widgets
        self.create_widgets()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def create_widgets(self):
        """Create all GUI widgets in the scrollable frame."""
        # Title
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        title_label = ttk.Label(title_frame, 
                               text="Sapphire Shopping Outlet - Queue Simulator",
                               font=("Arial", 18, "bold"),
                               foreground="#2c3e50")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                  text="Advanced Queueing Theory Simulation Tool",
                                  font=("Arial", 10),
                                  foreground="#7f8c8d")
        subtitle_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create tabs in order
        self.create_setup_tab()
        self.create_simulation_tab()
        self.create_analytics_tab()
        self.create_charts_tab()
        self.create_gantt_tab()
        self.create_sensitivity_tab()
        
        # Status bar
        status_frame = ttk.Frame(self.scrollable_frame)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(fill=tk.X)
    
    def create_setup_tab(self):
        """Create setup/configuration tab with better layout."""
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="⚙️ Setup")
        
        # Create a canvas for the setup tab as well
        setup_canvas = tk.Canvas(self.setup_frame)
        setup_scrollbar = ttk.Scrollbar(self.setup_frame, orient="vertical", command=setup_canvas.yview)
        setup_inner_frame = ttk.Frame(setup_canvas)
        
        setup_inner_frame.bind(
            "<Configure>",
            lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all"))
        )
        
        setup_canvas.create_window((0, 0), window=setup_inner_frame, anchor="nw")
        setup_canvas.configure(yscrollcommand=setup_scrollbar.set)
        
        setup_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        setup_scrollbar.pack(side="right", fill="y")
        
        # Simulation Method Selection
        method_frame = ttk.LabelFrame(setup_inner_frame, text="Simulation Method", padding=15)
        method_frame.pack(fill="x", padx=10, pady=10)
        
        self.sim_method = tk.StringVar(value="cp")
        ttk.Radiobutton(method_frame, text="CP-based (Simulate until CP=0.99999)", 
                       variable=self.sim_method, value="cp").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Fixed Number of Customers", 
                       variable=self.sim_method, value="fixed").pack(anchor="w", padx=10, pady=5)
        
        # Fixed customers entry (initially hidden)
        self.fixed_frame = ttk.Frame(method_frame)
        self.fixed_frame.pack(fill="x", padx=30, pady=5)
        ttk.Label(self.fixed_frame, text="Number of Customers:").pack(side="left", padx=(0, 10))
        self.customers_entry = ttk.Entry(self.fixed_frame, width=15)
        self.customers_entry.pack(side="left")
        self.customers_entry.insert(0, "100")
        self.fixed_frame.pack_forget()  # Hide initially
        
        # Bind method change
        self.sim_method.trace('w', self.toggle_sim_method)
        
        # Arrival Configuration
        arrival_frame = ttk.LabelFrame(setup_inner_frame, text="Arrival Process Configuration", padding=15)
        arrival_frame.pack(fill="x", padx=10, pady=10)
        
        # Use grid for better alignment
        arrival_frame.columnconfigure(0, weight=1)
        arrival_frame.columnconfigure(1, weight=2)
        arrival_frame.columnconfigure(2, weight=1)
        arrival_frame.columnconfigure(3, weight=2)
        
        # Row 0: Arrival Type
        ttk.Label(arrival_frame, text="Arrival Type:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.arrival_type = tk.StringVar(value="M")
        arrival_type_frame = ttk.Frame(arrival_frame)
        arrival_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
        
        ttk.Radiobutton(arrival_type_frame, text="M (Markovian)", 
                       variable=self.arrival_type, value="M").pack(side="left", padx=10)
        ttk.Radiobutton(arrival_type_frame, text="G (General)", 
                       variable=self.arrival_type, value="G").pack(side="left", padx=10)
        
        # Row 1: Arrival Rate
        ttk.Label(arrival_frame, text="Arrival Rate (λ):").grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        self.lambda_entry = ttk.Entry(arrival_frame, width=20)
        self.lambda_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.lambda_entry.insert(0, "0.5")
        ttk.Label(arrival_frame, text="customers per time unit").grid(
            row=1, column=2, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Row 2: Arrival Distribution
        ttk.Label(arrival_frame, text="Distribution:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        self.arrival_dist = tk.StringVar(value="Exponential")
        self.arrival_dist_combo = ttk.Combobox(arrival_frame, textvariable=self.arrival_dist,
                                              values=["Exponential", "Poisson", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=20)
        self.arrival_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Row 2: Arrival Parameters
        ttk.Label(arrival_frame, text="Parameters:").grid(
            row=2, column=2, sticky="w", padx=10, pady=5)
        self.arrival_params = ttk.Entry(arrival_frame, width=25)
        self.arrival_params.grid(row=2, column=3, sticky="w", padx=10, pady=5)
        self.arrival_params.insert(0, "rate=0.5")
        
        # Parameter help
        param_help = ttk.Label(arrival_frame, 
                              text="Examples: rate=0.5, min=1,max=3, mean=2,std=0.5, shape=2,scale=0.5",
                              font=("Arial", 8), foreground="#7f8c8d")
        param_help.grid(row=3, column=1, columnspan=3, sticky="w", padx=10, pady=(0, 10))
        
        # Service Configuration
        service_frame = ttk.LabelFrame(setup_inner_frame, text="Service Process Configuration", padding=15)
        service_frame.pack(fill="x", padx=10, pady=10)
        
        service_frame.columnconfigure(0, weight=1)
        service_frame.columnconfigure(1, weight=2)
        service_frame.columnconfigure(2, weight=1)
        service_frame.columnconfigure(3, weight=2)
        
        # Row 0: Service Type
        ttk.Label(service_frame, text="Service Type:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.service_type = tk.StringVar(value="M")
        service_type_frame = ttk.Frame(service_frame)
        service_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
        
        ttk.Radiobutton(service_type_frame, text="M (Markovian)", 
                       variable=self.service_type, value="M").pack(side="left", padx=10)
        ttk.Radiobutton(service_type_frame, text="G (General)", 
                       variable=self.service_type, value="G").pack(side="left", padx=10)
        
        # Row 1: Service Rate
        ttk.Label(service_frame, text="Service Rate (μ):").grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        self.mu_entry = ttk.Entry(service_frame, width=20)
        self.mu_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.mu_entry.insert(0, "1.0")
        ttk.Label(service_frame, text="customers per time unit").grid(
            row=1, column=2, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Row 2: Service Distribution
        ttk.Label(service_frame, text="Distribution:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        self.service_dist = tk.StringVar(value="Exponential")
        self.service_dist_combo = ttk.Combobox(service_frame, textvariable=self.service_dist,
                                              values=["Exponential", "Poisson", "Uniform", "Normal", "Gamma"],
                                              state="readonly", width=20)
        self.service_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Row 2: Service Parameters
        ttk.Label(service_frame, text="Parameters:").grid(
            row=2, column=2, sticky="w", padx=10, pady=5)
        self.service_params = ttk.Entry(service_frame, width=25)
        self.service_params.grid(row=2, column=3, sticky="w", padx=10, pady=5)
        self.service_params.insert(0, "rate=1.0")
        
        # System Configuration
        system_frame = ttk.LabelFrame(setup_inner_frame, text="System Configuration", padding=15)
        system_frame.pack(fill="x", padx=10, pady=10)
        
        system_frame.columnconfigure(0, weight=1)
        system_frame.columnconfigure(1, weight=2)
        system_frame.columnconfigure(2, weight=1)
        system_frame.columnconfigure(3, weight=2)
        
        # Row 0: Number of Servers
        ttk.Label(system_frame, text="Number of Servers (c):").grid(
            row=0, column=0, sticky="w", padx=10, pady=10)
        self.servers_entry = ttk.Entry(system_frame, width=20)
        self.servers_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        self.servers_entry.insert(0, "1")
        
        # Row 0: Max CP for simulation
        ttk.Label(system_frame, text="Max CP (for CP-based):").grid(
            row=0, column=2, sticky="w", padx=10, pady=10)
        self.max_cp_entry = ttk.Entry(system_frame, width=20)
        self.max_cp_entry.grid(row=0, column=3, sticky="w", padx=10, pady=10)
        self.max_cp_entry.insert(0, "0.99999")
        
        # Control Buttons
        button_frame = ttk.Frame(setup_inner_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        ttk.Button(button_frame, text="🚀 Run Simulation", 
                  command=self.run_simulation, width=18).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="📊 Analytical Results", 
                  command=self.show_analytics, width=18).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="📈 Sensitivity Analysis", 
                  command=self.run_sensitivity, width=18).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="🔄 Reset All", 
                  command=self.reset_all, width=18).grid(row=0, column=3, padx=5, pady=5)
        
        # Export and Help buttons in second row
        ttk.Button(button_frame, text="💾 Export Results", 
                  command=self.export_results, width=18).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="ℹ️ Help", 
                  command=self.show_help, width=18).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="📊 View All Charts", 
                  command=self.show_all_charts, width=18).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="🔍 Quick Stats", 
                  command=self.show_quick_stats, width=18).grid(row=1, column=3, padx=5, pady=5)
        
        # Bind events
        self.arrival_type.trace('w', self.update_distribution_options)
        self.service_type.trace('w', self.update_distribution_options)
        self.arrival_dist.trace('w', self.update_distribution_options)  # ADD THIS LINE
        self.service_dist.trace('w', self.update_distribution_options)  # ADD THIS LINE
        self.update_distribution_options()
                
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
        🎯 Sapphire Shopping Outlet Queue Simulator Help
        
        📋 SIMULATION METHODS:
        • CP-based: Simulates until cumulative probability reaches 0.99999
        • Fixed Customers: Simulates specified number of customers
        
        📊 DISTRIBUTIONS:
        • Markovian (M): Exponential or Poisson distributions
        • General (G): Uniform, Normal, or Gamma distributions
        
        ⚙️ PARAMETERS:
        • Exponential/Poisson: rate=λ (e.g., rate=0.5)
        • Uniform: min=a,max=b (e.g., min=1,max=3)
        • Normal: mean=μ,std=σ (e.g., mean=2,std=0.5)
        • Gamma: shape=k,scale=θ (e.g., shape=2,scale=0.5)
        
        📈 OUTPUT COLUMNS:
        • CP: Cumulative Probability (0 to 0.99999)
        • CP_Lookup: Previous CP value
        
        💡 TIPS:
        1. Start with λ < c×μ for stable system
        2. Use Sensitivity Analysis to find optimal parameters
        3. Check Analytical Results for theoretical values
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Queue Simulator")
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                               font=("Consolas", 10), height=25)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_all_charts(self):
        """Show all charts in a separate window."""
        if self.current_df.empty:
            messagebox.showinfo("No Data", "Run simulation first to see charts.")
            return
        
        charts_window = tk.Toplevel(self.root)
        charts_window.title("All Charts - Queue Simulator")
        charts_window.geometry("1200x800")
        
        # Create notebook for charts
        charts_notebook = ttk.Notebook(charts_window)
        charts_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Performance Charts
        perf_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(perf_frame, text="Performance Charts")
        self.create_performance_charts(perf_frame)
        
        # Distribution Charts
        dist_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(dist_frame, text="Distribution Analysis")
        self.create_distribution_charts(dist_frame)
        
        # CP Analysis
        cp_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(cp_frame, text="CP Analysis")
        self.create_cp_charts(cp_frame)
    
    def create_performance_charts(self, parent):
        """Create performance charts."""
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Subplot 1: Wait Time
        ax1 = fig.add_subplot(221)
        ax1.plot(self.current_df['ID'], self.current_df['Wait'], 'b-', linewidth=2)
        ax1.set_title('Wait Time Progression')
        ax1.set_xlabel('Customer ID')
        ax1.set_ylabel('Wait Time')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Service Time
        ax2 = fig.add_subplot(222)
        ax2.plot(self.current_df['ID'], self.current_df['Service'], 'g-', linewidth=2)
        ax2.set_title('Service Time Distribution')
        ax2.set_xlabel('Customer ID')
        ax2.set_ylabel('Service Time')
        ax2.grid(True, alpha=0.3)
        
        # Subplot 3: Turnaround Time
        ax3 = fig.add_subplot(223)
        ax3.plot(self.current_df['ID'], self.current_df['Turnaround'], 'r-', linewidth=2)
        ax3.set_title('Turnaround Time Progression')
        ax3.set_xlabel('Customer ID')
        ax3.set_ylabel('Turnaround Time')
        ax3.grid(True, alpha=0.3)
        
        # Subplot 4: CP vs Time
        ax4 = fig.add_subplot(224)
        ax4.plot(self.current_df['Arrival'], self.current_df['CP'], 'm-', linewidth=2)
        ax4.set_title('CP vs Arrival Time')
        ax4.set_xlabel('Arrival Time')
        ax4.set_ylabel('Cumulative Probability (CP)')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout(pad=3.0)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_distribution_charts(self, parent):
        """Create distribution analysis charts."""
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Subplot 1: Histogram of Wait Times
        ax1 = fig.add_subplot(221)
        ax1.hist(self.current_df['Wait'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_title('Wait Time Distribution')
        ax1.set_xlabel('Wait Time')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Box plot of all times
        ax2 = fig.add_subplot(222)
        data_to_plot = [self.current_df['Wait'], 
                       self.current_df['Service'], 
                       self.current_df['Turnaround']]
        ax2.boxplot(data_to_plot, labels=['Wait', 'Service', 'Turnaround'])
        ax2.set_title('Time Distribution Comparison')
        ax2.set_ylabel('Time')
        ax2.grid(True, alpha=0.3)
        
        # Subplot 3: Scatter plot: Service vs Wait
        ax3 = fig.add_subplot(223)
        ax3.scatter(self.current_df['Service'], self.current_df['Wait'], 
                   alpha=0.5, c='blue', s=20)
        ax3.set_title('Service Time vs Wait Time')
        ax3.set_xlabel('Service Time')
        ax3.set_ylabel('Wait Time')
        ax3.grid(True, alpha=0.3)
        
        # Subplot 4: CDF of Wait Times
        ax4 = fig.add_subplot(224)
        sorted_wait = np.sort(self.current_df['Wait'])
        cdf = np.arange(1, len(sorted_wait) + 1) / len(sorted_wait)
        ax4.plot(sorted_wait, cdf, 'r-', linewidth=2)
        ax4.set_title('CDF of Wait Times')
        ax4.set_xlabel('Wait Time')
        ax4.set_ylabel('Cumulative Probability')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout(pad=3.0)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_cp_charts(self, parent):
        """Create CP analysis charts."""
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Subplot 1: CP vs Customer ID
        ax1 = fig.add_subplot(221)
        ax1.plot(self.current_df['ID'], self.current_df['CP'], 'b-', linewidth=2)
        ax1.axhline(y=0.99999, color='r', linestyle='--', alpha=0.5, label='Target CP=0.99999')
        ax1.set_title('CP Progression')
        ax1.set_xlabel('Customer ID')
        ax1.set_ylabel('Cumulative Probability')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Arrival Time vs CP
        ax2 = fig.add_subplot(222)
        ax2.plot(self.current_df['Arrival'], self.current_df['CP'], 'g-', linewidth=2)
        ax2.set_title('CP vs Arrival Time')
        ax2.set_xlabel('Arrival Time')
        ax2.set_ylabel('CP')
        ax2.grid(True, alpha=0.3)
        
        # Subplot 3: CP difference
        ax3 = fig.add_subplot(223)
        cp_diff = self.current_df['CP'] - self.current_df['CP_Lookup']
        ax3.plot(self.current_df['ID'], cp_diff, 'r-', linewidth=2)
        ax3.set_title('CP Increment per Customer')
        ax3.set_xlabel('Customer ID')
        ax3.set_ylabel('ΔCP')
        ax3.grid(True, alpha=0.3)
        
        # Subplot 4: Histogram of CP increments
        ax4 = fig.add_subplot(224)
        ax4.hist(cp_diff, bins=20, color='purple', edgecolor='black', alpha=0.7)
        ax4.set_title('Distribution of CP Increments')
        ax4.set_xlabel('ΔCP')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout(pad=3.0)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_quick_stats(self):
        """Show quick statistics in a dialog."""
        if self.current_df.empty:
            messagebox.showinfo("No Data", "Run simulation first to see statistics.")
            return
        
        stats = self.simulator.get_summary_statistics(self.current_df)
        
        stats_text = "📊 QUICK STATISTICS\n"
        stats_text += "=" * 50 + "\n\n"
        
        for key, value in stats.items():
            stats_text += f"{key:25}: {value}\n"
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Quick Statistics")
        stats_window.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, 
                                               font=("Consolas", 10), height=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
    
    def toggle_sim_method(self, *args):
        """Toggle between CP-based and fixed number simulation."""
        if self.sim_method.get() == "fixed":
            self.fixed_frame.pack(fill="x", padx=30, pady=5)
        else:
            self.fixed_frame.pack_forget()
    
    def update_distribution_options(self, *args):
        """Update distribution options and parameters based on selections."""
        
        # Track which variable triggered the update
        # (This is a simplified approach - for a more robust solution, 
        # you might want separate functions for type vs distribution changes)
        
        # ----------------- Update Available Distributions -----------------
        # Only update combobox values when type changes, NOT when distribution changes
        
        # For Arrival
        if self.arrival_type.get() == "M":
            # Only update combobox if values are different
            current_values = list(self.arrival_dist_combo['values'])
            if current_values != ["Exponential", "Poisson"]:
                self.arrival_dist_combo.config(values=["Exponential", "Poisson"])
                # Only set default if current value is not in new list
                if self.arrival_dist.get() not in ["Exponential", "Poisson"]:
                    self.arrival_dist.set("Exponential")
        else:
            current_values = list(self.arrival_dist_combo['values'])
            if current_values != ["Uniform", "Normal", "Gamma"]:
                self.arrival_dist_combo.config(values=["Uniform", "Normal", "Gamma"])
                # Only set default if current value is not in new list
                if self.arrival_dist.get() not in ["Uniform", "Normal", "Gamma"]:
                    self.arrival_dist.set("Uniform")
        
        # For Service
        if self.service_type.get() == "M":
            current_values = list(self.service_dist_combo['values'])
            if current_values != ["Exponential", "Poisson"]:
                self.service_dist_combo.config(values=["Exponential", "Poisson"])
                if self.service_dist.get() not in ["Exponential", "Poisson"]:
                    self.service_dist.set("Exponential")
        else:
            current_values = list(self.service_dist_combo['values'])
            if current_values != ["Uniform", "Normal", "Gamma"]:
                self.service_dist_combo.config(values=["Uniform", "Normal", "Gamma"])
                if self.service_dist.get() not in ["Uniform", "Normal", "Gamma"]:
                    self.service_dist.set("Uniform")
        
        # ----------------- Update Parameters -----------------
        # ALWAYS update parameters based on current selection
        arrival_selected = self.arrival_dist.get()
        service_selected = self.service_dist.get()
        
        # Update arrival parameters
        self.arrival_params.delete(0, tk.END)
        if arrival_selected in ["Exponential", "Poisson"]:
            self.arrival_params.insert(0, "rate=0.5")
        elif arrival_selected == "Uniform":
            self.arrival_params.insert(0, "min=1.0,max=3.0")
        elif arrival_selected == "Normal":
            self.arrival_params.insert(0, "mean=2.0,std=0.5")
        elif arrival_selected == "Gamma":
            self.arrival_params.insert(0, "shape=2.0,scale=0.5")
        
        # Update service parameters
        self.service_params.delete(0, tk.END)
        if service_selected in ["Exponential", "Poisson"]:
            self.service_params.insert(0, "rate=1.0")
        elif service_selected == "Uniform":
            self.service_params.insert(0, "min=1.0,max=3.0")
        elif service_selected == "Normal":
            self.service_params.insert(0, "mean=2.0,std=0.5")
        elif service_selected == "Gamma":
            self.service_params.insert(0, "shape=2.0,scale=0.5")
    
    def parse_params(self, params_str: str) -> dict:
        """Parse parameters string to dictionary."""
        params = {}
        if params_str:
            # Remove spaces and split by comma
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
            
            # Check CP value
            if not df.empty:
                max_cp = df['CP'].max()
                self.status_var.set(f"Simulation completed: {len(df)} customers, Max CP={max_cp:.5f}")
                
                if self.sim_method.get() == "cp" and max_cp < 0.99999:
                    messagebox.showwarning("CP Not Reached", 
                                         f"Maximum CP reached: {max_cp:.5f}\n"
                                         f"Consider increasing max events in code.")
                else:
                    messagebox.showinfo("Success", 
                                      f"Simulation completed successfully!\n"
                                      f"Processed {len(df)} customers\n"
                                      f"Total time: {df['End'].max():.2f}\n"
                                      f"Avg wait time: {df['Wait'].mean():.2f}")
            else:
                self.status_var.set("Simulation completed with no data")
                messagebox.showwarning("No Data", "Simulation produced no data. Check parameters.")
            
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
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
        
        # Configure columns
        col_widths = [50, 80, 80, 60, 80, 80, 80, 100, 80, 80, 90]
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
        self.metrics_text.insert(tk.END, f"Simulation Method: {'CP-based (until CP=0.99999)' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
        self.metrics_text.insert(tk.END, f"Total Customers: {len(df)}\n")
        self.metrics_text.insert(tk.END, f"Arrival Distribution: {self.arrival_dist.get()}\n")
        self.metrics_text.insert(tk.END, f"Service Distribution: {self.service_dist.get()}\n")
        self.metrics_text.insert(tk.END, f"Number of Servers: {self.servers_entry.get()}\n")
        if not df.empty:
            self.metrics_text.insert(tk.END, f"Max CP Achieved: {df['CP'].max():.5f}\n")
        self.metrics_text.insert(tk.END, f"Traffic Intensity (ρ): {float(self.lambda_entry.get()) / (int(self.servers_entry.get()) * float(self.mu_entry.get())):.4f}\n\n")
        
        # Time metrics
        self.metrics_text.insert(tk.END, "⏱️  TIME METRICS\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        if not df.empty:
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
            ("Total Simulation Time", f"{self.simulator.metrics.get('total_time', 0):.2f}")
        ]
        
        for name, value in system_metrics:
            self.metrics_text.insert(tk.END, f"{name:25}: {value}\n")
        
        # Wait time percentiles
        self.metrics_text.insert(tk.END, "\n📈 WAIT TIME DISTRIBUTION\n")
        self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
        if not df.empty:
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
                    "System Customers (L)": self.current_df["Wait"].mean() * float(self.lambda_entry.get())
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
        
        # Create canvas for charts with scrollbar
        charts_canvas = tk.Canvas(self.charts_frame)
        charts_scrollbar = ttk.Scrollbar(self.charts_frame, orient="vertical", command=charts_canvas.yview)
        charts_inner_frame = ttk.Frame(charts_canvas)
        
        charts_inner_frame.bind(
            "<Configure>",
            lambda e: charts_canvas.configure(scrollregion=charts_canvas.bbox("all"))
        )
        
        charts_canvas.create_window((0, 0), window=charts_inner_frame, anchor="nw")
        charts_canvas.configure(yscrollcommand=charts_scrollbar.set)
        
        charts_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        charts_scrollbar.pack(side="right", fill="y")
        
        # Create figure with multiple subplots
        self.charts_fig = Figure(figsize=(10, 12), dpi=100)
        
        # Create subplots
        self.chart_ax1 = self.charts_fig.add_subplot(311)  # Wait time
        self.chart_ax2 = self.charts_fig.add_subplot(312)  # Turnaround time
        self.chart_ax3 = self.charts_fig.add_subplot(313)  # Service time
        
        # Create canvas
        self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, charts_inner_frame)
        self.charts_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(charts_inner_frame)
        toolbar_frame.pack(fill=tk.X, pady=(10, 0))
        
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
        
        self.charts_fig.tight_layout(pad=3.0)
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
        
        # Adjust layout with more padding
        self.charts_fig.tight_layout(pad=3.0, h_pad=2.0)
        
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
            
            # Create bar for the service time
            self.gantt_ax.barh(
                server_idx,
                duration,
                left=start_time,
                height=0.6,
                color=colors[idx % len(colors)],
                edgecolor='black',
                alpha=0.8,
                linewidth=1
            )
            
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
        
        # Add title
        title = f"Gantt Chart - {len(plot_df)} Customers on {len(servers)} Server(s)"
        self.gantt_ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        self.gantt_ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust layout
        self.gantt_fig.tight_layout(pad=3.0)
        
        # Update canvas
        self.gantt_canvas.draw()
    
    def create_sensitivity_tab(self):
        """Create sensitivity analysis tab."""
        self.sens_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sens_frame, text="📈 Sensitivity Analysis")
        
        # Control frame for sensitivity analysis
        sens_control_frame = ttk.LabelFrame(self.sens_frame, text="Sensitivity Analysis Parameters", padding=15)
        sens_control_frame.pack(fill="x", padx=10, pady=10)
        
        sens_control_frame.columnconfigure(0, weight=1)
        sens_control_frame.columnconfigure(1, weight=2)
        sens_control_frame.columnconfigure(2, weight=1)
        sens_control_frame.columnconfigure(3, weight=2)
        
        # Lambda range
        ttk.Label(sens_control_frame, text="λ Range (min,max,steps):").grid(
            row=0, column=0, sticky="w", padx=10, pady=10)
        self.lambda_range_entry = ttk.Entry(sens_control_frame, width=25)
        self.lambda_range_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        self.lambda_range_entry.insert(0, "0.1,2.0,20")
        
        # Metric to analyze
        ttk.Label(sens_control_frame, text="Metric to Analyze:").grid(
            row=0, column=2, sticky="w", padx=10, pady=10)
        self.sens_metric = tk.StringVar(value="avg_wait")
        ttk.Combobox(sens_control_frame, textvariable=self.sens_metric,
                    values=["avg_wait", "avg_turnaround", "utilization", "throughput", "queue_length"],
                    state="readonly", width=20).grid(row=0, column=3, sticky="w", padx=10, pady=10)
        
        # Run button
        ttk.Button(sens_control_frame, text="Run Sensitivity Analysis", 
                  command=self.run_sensitivity, width=20).grid(row=1, column=0, columnspan=4, pady=10)
        
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
        """Run sensitivity analysis using ANALYTICAL formulas."""
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
            
            self.status_var.set("Running sensitivity analysis using analytical formulas...")
            self.root.update()
            
            # Run sensitivity analysis using ANALYTICAL formulas
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
            messagebox.showinfo("Sensitivity Analysis", 
                              f"Sensitivity analysis completed!\n"
                              f"Analyzed λ from {lambda_range[0]:.2f} to {lambda_range[-1]:.2f}\n"
                              f"System capacity: {num_servers * mu:.2f}")
            
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
            'avg_wait': 'Average Wait Time (Wq)',
            'avg_turnaround': 'Average Turnaround Time (W)',
            'utilization': 'Server Utilization (%)',
            'throughput': 'Throughput (customers/time)',
            'queue_length': 'Average Queue Length (Lq)'
        }
        
        # Filter out infinite values
        valid_results = results[results[metric] != float('inf')]
        
        if len(valid_results) == 0:
            self.sens_ax.text(0.5, 0.5, 'No valid data points\nSystem unstable for all λ values',
                             ha='center', va='center', transform=self.sens_ax.transAxes,
                             fontsize=12, color='red')
        else:
            # Plot the metric vs lambda
            self.sens_ax.plot(valid_results['lambda'], valid_results[metric], 
                             'b-', linewidth=2, marker='o', markersize=4, label='Analytical')
            
            # Fill under the curve
            self.sens_ax.fill_between(valid_results['lambda'], valid_results[metric], 
                                     alpha=0.3, color='blue')
            
            # Add stability line (rho = 1)
            if 'rho' in valid_results.columns:
                # Find where system becomes unstable (rho >= 0.95)
                unstable_mask = valid_results['rho'] >= 0.95
                if unstable_mask.any():
                    first_unstable = valid_results[unstable_mask].iloc[0]
                    self.sens_ax.axvline(x=first_unstable['lambda'], color='red', 
                                       linestyle='--', linewidth=2, 
                                       label=f'Stability limit (λ={first_unstable["lambda"]:.2f})')
            
            # Add current lambda marker if available
            if 'lam' in self.current_params:
                current_lam = self.current_params['lam']
                # Find closest lambda in results
                closest_idx = (valid_results['lambda'] - current_lam).abs().idxmin()
                current_point = valid_results.loc[closest_idx]
                self.sens_ax.plot(current_lam, current_point[metric], 'ro', 
                                markersize=8, label=f'Current (λ={current_lam:.2f})')
                
                # Add annotation
                self.sens_ax.annotate(f'Current: λ={current_lam:.2f}\n{metric_names.get(metric, metric)}={current_point[metric]:.2f}',
                                    xy=(current_lam, current_point[metric]),
                                    xytext=(10, 10), textcoords='offset points',
                                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.5))
        
        # Set labels and title
        self.sens_ax.set_xlabel('Arrival Rate (λ)', fontweight='bold')
        self.sens_ax.set_ylabel(metric_names.get(metric, metric), fontweight='bold')
        
        title = f"Sensitivity Analysis: {metric_names.get(metric, metric)} vs Arrival Rate"
        subtitle = f"Using Analytical Formulas ({self.arrival_dist.get()}/{self.service_dist.get()}/{self.servers_entry.get()})"
        self.sens_ax.set_title(f"{title}\n{subtitle}", fontsize=12, fontweight='bold')
        
        # Add grid and legend
        self.sens_ax.grid(True, alpha=0.3, linestyle='--')
        if len(valid_results) > 0:
            self.sens_ax.legend(loc='best')
        
        # Adjust layout
        self.sens_fig.tight_layout(pad=3.0)
        
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
                f.write(f"Simulation Method: {'CP-based (until CP=0.99999)' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
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
                f.write(f"Throughput: {self.simulator.metrics.get('throughput', 0):.4f} customers/time unit\n")
                f.write(f"Maximum CP Achieved: {self.current_df['CP'].max():.5f}\n\n")
                
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


