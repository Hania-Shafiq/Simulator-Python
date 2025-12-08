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
from distributions import get_distribution_params, get_mean, get_variance

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
              ...(truncated 49869 characters)... 0.5, 'No valid data points\nSystem unstable for all λ values',
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