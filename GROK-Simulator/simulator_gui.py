# """
# Main GUI for the enhanced queue simulator with all features.
# """
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure
# import pandas as pd
# import numpy as np
# from datetime import datetime
# import seaborn as sns

# from simulation_engine import QueueSimulator
# from queue_analytics import QueueAnalytics
# from distributions import get_distribution_params, get_mean, get_variance

# class QueueSimulatorGUI:
#     """Main GUI application for queue simulator."""
    
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Sapphire Shopping Outlet - Queue Simulator")
        
#         # Set seaborn style for better looking plots
#         sns.set_style("whitegrid")
#         plt.rcParams['figure.figsize'] = [10, 6]
#         plt.rcParams['figure.dpi'] = 100
#         plt.rcParams['font.size'] = 10
        
#         # Initialize simulator
#         self.simulator = QueueSimulator()
#         self.current_df = pd.DataFrame()
#         self.current_params = {}
        
#         # Create main container with scrollbar
#         self.create_main_container()
        
#         # Maximize window
#         self.root.state('zoomed')
    
#     def create_main_container(self):
#         """Create main container with scrollbar for entire application."""
#         # Create main frame
#         main_frame = ttk.Frame(self.root)
#         main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
#         # Create canvas and scrollbar
#         self.canvas = tk.Canvas(main_frame)
#         scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
#         # Create scrollable frame
#         self.scrollable_frame = ttk.Frame(self.canvas)
        
#         # Bind the scrollable frame to the canvas
#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
#         )
        
#         # Create window in canvas
#         self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
#         self.canvas.configure(yscrollcommand=scrollbar.set)
        
#         # Pack canvas and scrollbar
#         self.canvas.pack(side="left", fill="both", expand=True)
#         scrollbar.pack(side="right", fill="y")
        
#         # Bind mouse wheel for scrolling
#         self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
#         self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
#         self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down
        
#         # Create GUI widgets
#         self.create_widgets()
    
#     def _on_mousewheel(self, event):
#         """Handle mouse wheel scrolling."""
#         if event.num == 4 or event.delta > 0:
#             self.canvas.yview_scroll(-1, "units")
#         elif event.num == 5 or event.delta < 0:
#             self.canvas.yview_scroll(1, "units")
    
#     def create_widgets(self):
#         """Create all GUI widgets in the scrollable frame."""
#         # Title
#         title_frame = ttk.Frame(self.scrollable_frame)
#         title_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
#         title_label = ttk.Label(title_frame, 
#                                text="Sapphire Shopping Outlet - Queue Simulator",
#                                font=("Arial", 18, "bold"),
#                                foreground="#2c3e50")
#         title_label.pack()
        
#         subtitle_label = ttk.Label(title_frame,
#                                   text="Advanced Queueing Theory Simulation Tool",
#                                   font=("Arial", 10),
#                                   foreground="#7f8c8d")
#         subtitle_label.pack(pady=(0, 10))
        
#         # Notebook for tabs
#         self.notebook = ttk.Notebook(self.scrollable_frame)
#         self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
#         # Create tabs in order
#         self.create_setup_tab()
#         self.create_simulation_tab()
#         self.create_analytics_tab()
#         self.create_charts_tab()
#         self.create_gantt_tab()
#         self.create_sensitivity_tab()
        
#         # Status bar
#         status_frame = ttk.Frame(self.scrollable_frame)
#         status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
#         self.status_var = tk.StringVar(value="Ready")
#         status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
#                                relief=tk.SUNKEN, anchor=tk.W, padding=5)
#         status_bar.pack(fill=tk.X)
    
#     def create_setup_tab(self):
#         self.setup_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.setup_frame, text="Setup")
        
#         setup_canvas = tk.Canvas(self.setup_frame)
#         setup_scrollbar = ttk.Scrollbar(self.setup_frame, orient="vertical", command=setup_canvas.yview)
#         setup_inner_frame = ttk.Frame(setup_canvas)
        
#         setup_inner_frame.bind("<Configure>", lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all")))
#         setup_canvas.create_window((0, 0), window=setup_inner_frame, anchor="nw")
#         setup_canvas.configure(yscrollcommand=setup_scrollbar.set)
        
#         setup_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
#         setup_scrollbar.pack(side="right", fill="y")

#         # === Simulation Method ===
#         method_frame = ttk.LabelFrame(setup_inner_frame, text="Simulation Method", padding=15)
#         method_frame.pack(fill="x", padx=10, pady=10)

#         self.sim_method = tk.StringVar(value="cp")
#         ttk.Radiobutton(method_frame, text="CP-based (Simulate until CP=0.99999)", 
#                        variable=self.sim_method, value="cp").pack(anchor="w", padx=10, pady=5)
#         ttk.Radiobutton(method_frame, text="Fixed Number of Customers", 
#                        variable=self.sim_method, value="fixed").pack(anchor="w", padx=10, pady=5)

#         self.fixed_frame = ttk.Frame(method_frame)
#         self.fixed_frame.pack(fill="x", padx=30, pady=5)
#         ttk.Label(self.fixed_frame, text="Number of Customers:").pack(side="left")
#         self.customers_entry = ttk.Entry(self.fixed_frame, width=15)
#         self.customers_entry.pack(side="left", padx=5)
#         self.customers_entry.insert(0, "500")
#         self.fixed_frame.pack_forget()

#         self.sim_method.trace('w', self.toggle_sim_method)

#         # === Arrival Configuration ===
#         arrival_frame = ttk.LabelFrame(setup_inner_frame, text="Arrival Process Configuration", padding=15)
#         arrival_frame.pack(fill="x", padx=10, pady=10)

#         ttk.Label(arrival_frame, text="Arrival Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
#         self.arrival_type = tk.StringVar(value="M")
#         type_frame = ttk.Frame(arrival_frame)
#         type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
#         ttk.Radiobutton(type_frame, text="M (Markovian)", variable=self.arrival_type, value="M", command=self.toggle_arrival).pack(side="left", padx=10)
#         ttk.Radiobutton(type_frame, text="G (General)", variable=self.arrival_type, value="G", command=self.toggle_arrival).pack(side="left", padx=10)

#         ttk.Label(arrival_frame, text="Arrival Rate (λ):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
#         self.lambda_entry = ttk.Entry(arrival_frame, width=20)
#         self.lambda_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
#         self.lambda_entry.insert(0, "0.8")
#         ttk.Label(arrival_frame, text="customers/time unit").grid(row=1, column=2, columnspan=2, sticky="w", padx=10)

#         ttk.Label(arrival_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
#         self.arrival_dist = tk.StringVar(value="Exponential")
#         self.arrival_dist_combo = ttk.Combobox(arrival_frame, textvariable=self.arrival_dist,
#                                                values=["Exponential"], state="readonly")
#         self.arrival_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)

#         ttk.Label(arrival_frame, text="Parameters:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
#         self.arrival_params = ttk.Entry(arrival_frame, width=30, state="disabled")
#         self.arrival_params.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=5)
#         self.arrival_params.insert(0, "e.g., 2,5 (Uniform min,max) or 3,1 (Normal mean,std)")

#         # === Service Configuration ===
#         service_frame = ttk.LabelFrame(setup_inner_frame, text="Service Process Configuration", padding=15)
#         service_frame.pack(fill="x", padx=10, pady=10)

#         ttk.Label(service_frame, text="Service Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
#         self.service_type = tk.StringVar(value="M")
#         svc_type_frame = ttk.Frame(service_frame)
#         svc_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
#         ttk.Radiobutton(svc_type_frame, text="M (Markovian)", variable=self.service_type, value="M", command=self.toggle_service).pack(side="left", padx=10)
#         ttk.Radiobutton(svc_type_frame, text="G (General)", variable=self.service_type, value="G", command=self.toggle_service).pack(side="left", padx=10)

#         ttk.Label(service_frame, text="Service Rate (μ):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
#         self.mu_entry = ttk.Entry(service_frame, width=20)
#         self.mu_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
#         self.mu_entry.insert(0, "1.0")
#         ttk.Label(service_frame, text="customers/time unit").grid(row=1, column=2, columnspan=2, sticky="w", padx=10)

#         ttk.Label(service_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
#         self.service_dist = tk.StringVar(value="Exponential")
#         self.service_dist_combo = ttk.Combobox(service_frame, textvariable=self.service_dist,
#                                                values=["Exponential"], state="readonly")
#         self.service_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)

#         ttk.Label(service_frame, text="Parameters:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
#         self.service_params = ttk.Entry(service_frame, width=30, state="disabled")
#         self.service_params.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=5)
#         self.service_params.insert(0, "e.g., 0.5,2.0 (Uniform) or 1.0,0.3 (Normal)")

#         # === System Configuration ===
#         sys_frame = ttk.LabelFrame(setup_inner_frame, text="System Configuration", padding=15)
#         sys_frame.pack(fill="x", padx=10, pady=10)

#         ttk.Label(sys_frame, text="Number of Servers (c):").pack(side="left", padx=10)
#         self.servers_entry = ttk.Entry(sys_frame, width=10)
#         self.servers_entry.pack(side="left", padx=10)
#         self.servers_entry.insert(0, "1")

#         # === Run Button ===
#         run_btn = ttk.Button(setup_inner_frame, text="RUN SIMULATION", command=self.run_simulation, style="Accent.TButton")
#         run_btn.pack(pady=20)

#         # Initial toggle
#         self.toggle_arrival()
#         self.toggle_service()

#     def toggle_sim_method(self, *args):
#         if self.sim_method.get() == "cp":
#             self.fixed_frame.pack_forget()
#         else:
#             self.fixed_frame.pack(fill="x", padx=30, pady=5)

#     def toggle_arrival(self, *args):
#         if self.arrival_type.get() == "M":
#             self.lambda_entry.config(state="normal")
#             self.arrival_params.config(state="disabled")
#             self.arrival_dist_combo["values"] = ["Exponential", "Poisson"]
#             self.arrival_dist_combo.set("Exponential")
#         else:
#             self.lambda_entry.config(state="disabled")
#             self.arrival_params.config(state="normal")
#             self.arrival_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
#             self.arrival_dist_combo.set("Uniform")

#     def toggle_service(self, *args):
#         if self.service_type.get() == "M":
#             self.mu_entry.config(state="normal")
#             self.service_params.config(state="disabled")
#             self.service_dist_combo["values"] = ["Exponential", "Poisson"]
#             self.service_dist_combo.set("Exponential")
#         else:
#             self.mu_entry.config(state="disabled")
#             self.service_params.config(state="normal")
#             self.service_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
#             self.service_dist_combo.set("Uniform")

#     def export_results(self):
#         """Export simulation results to file."""
#         if self.current_df.empty:
#             messagebox.showwarning("Warning", "No simulation data to export!")
#             return
        
#         try:
#             # Create filename with timestamp
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             data_filename = f"queue_simulation_{timestamp}.csv"
#             metrics_filename = f"queue_metrics_{timestamp}.txt"
            
#             # Export data to CSV
#             self.current_df.to_csv(data_filename, index=False)
            
#             # Export metrics to text file
#             with open(metrics_filename, 'w') as f:
#                 f.write("=" * 70 + "\n")
#                 f.write("SAPPHIRE SHOPPING OUTLET - QUEUE SIMULATION RESULTS\n")
#                 f.write("=" * 70 + "\n\n")
                
#                 f.write("SIMULATION PARAMETERS:\n")
#                 f.write("-" * 40 + "\n")
#                 f.write(f"Simulation Method: {'CP-based (until CP=0.99999)' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
#                 f.write(f"Arrival Type: {self.arrival_type.get()}\n")
#                 f.write(f"Arrival Distribution: {self.arrival_dist.get()}\n")
#                 f.write(f"Arrival Parameters: {self.arrival_params.get()}\n")
#                 f.write(f"Arrival Rate (λ): {self.lambda_entry.get()}\n")
#                 f.write(f"Service Type: {self.service_type.get()}\n")
#                 f.write(f"Service Distribution: {self.service_dist.get()}\n")
#                 f.write(f"Service Parameters: {self.service_params.get()}\n")
#                 f.write(f"Service Rate (μ): {self.mu_entry.get()}\n")
#                 f.write(f"Number of Servers (c): {self.servers_entry.get()}\n")
#                 if self.sim_method.get() == "fixed":
#                     f.write(f"Number of Customers: {self.customers_entry.get()}\n")
#                 else:
#                     f.write(f"Max CP: {self.max_cp_entry.get()}\n")
#                 f.write(f"Timestamp: {timestamp}\n\n")
                
#                 f.write("SIMULATION RESULTS:\n")
#                 f.write("-" * 40 + "\n")
#                 f.write(f"Total Customers Simulated: {len(self.current_df)}\n")
#                 f.write(f"Total Simulation Time: {self.current_df['End'].max():.2f}\n")
#                 f.write(f"Server Utilization: {self.simulator.metrics.get('utilization', 0):.2f}%\n")
#                 f.write(f"Throughput: {self.simulator.metrics.get('throughput', 0):.4f} customers/time unit\n")
#                 f.write(f"Maximum CP Achieved: {self.current_df['CP'].max():.5f}\n\n")
                
#                 f.write("PERFORMANCE METRICS:\n")
#                 f.write("-" * 40 + "\n")
#                 stats = self.simulator.get_summary_statistics(self.current_df)
#                 for key, value in stats.items():
#                     f.write(f"{key}: {value}\n")
            
#             messagebox.showinfo("Export Successful", 
#                               f"Results exported successfully!\n\n"
#                               f"Data saved to: {data_filename}\n"
#                               f"Metrics saved to: {metrics_filename}")
            
#         except Exception as e:
#             messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
#     def reset_all(self):
#         """Reset all simulation data and UI."""
#         response = messagebox.askyesno("Confirm Reset", 
#                                       "Are you sure you want to reset all simulation data?")
        
#         if response:
#             # Reset simulator
#             self.simulator.reset()
#             self.current_df = pd.DataFrame()
#             self.current_params = {}
            
#             # Reset UI components
#             # Clear data table
#             for item in self.tree.get_children():
#                 self.tree.delete(item)
            
#             # Clear text areas
#             self.metrics_text.config(state=tk.NORMAL)
#             self.metrics_text.delete(1.0, tk.END)
#             self.metrics_text.insert(tk.END, "Run simulation to see metrics...\n")
#             self.metrics_text.config(state=tk.DISABLED)
            
#             self.analytics_text.config(state=tk.NORMAL)
#             self.analytics_text.delete(1.0, tk.END)
#             self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate...\n")
#             self.analytics_text.config(state=tk.DISABLED)
            
#             # Reset charts
#             self.initialize_charts()
            
#             # Reset Gantt chart
#             self.gantt_ax.clear()
#             self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline", fontsize=14, fontweight='bold')
#             self.gantt_ax.set_xlabel("Time", fontweight='bold')
#             self.gantt_ax.set_ylabel("Customers/Servers", fontweight='bold')
#             self.gantt_ax.grid(True, alpha=0.3)
#             self.gantt_canvas.draw()
            
#             # Reset sensitivity graph
#             self.sens_ax.clear()
#             self.sens_ax.set_title("Sensitivity Analysis", fontsize=14, fontweight='bold')
#             self.sens_ax.set_xlabel("Arrival Rate (λ)", fontweight='bold')
#             self.sens_ax.set_ylabel("Metric Value", fontweight='bold')
#             self.sens_ax.grid(True, alpha=0.3)
#             self.sens_canvas.draw()
            
#             # Reset status
#             self.status_var.set("Ready")
            
#             messagebox.showinfo("Reset Complete", "All simulation data has been reset successfully.")

#     # def toggle_sim_method(self, *args):
#     #     """Show/hide fixed-customer entry based on simulation method."""
#     #     if self.sim_method.get() == "fixed":
#     #         self.fixed_frame.pack(fill="x", padx=30, pady=5)
#     #     else:
#     #         self.fixed_frame.pack_forget()

#     # def toggle_arrival(self):
#     #     if self.arrival_type.get() == "M":
#     #         self.lambda_entry.config(state="normal")
#     #         self.arrival_params_entry.config(state="disabled")
#     #         self.arrival_dist_combo["values"] = ["Exponential", "Poisson"]
#     #         self.arrival_dist_combo.set("Exponential")
#     #     else:
#     #         self.lambda_entry.config(state="disabled")
#     #         self.arrival_params_entry.config(state="normal")
#     #         self.arrival_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
#     #         self.arrival_dist_combo.set("Uniform")

#     # def toggle_service(self):
#     #     if self.service_type.get() == "M":
#     #         self.mu_entry.config(state="normal")
#     #         self.service_params_entry.config(state="disabled")
#     #         self.service_dist_combo["values"] = ["Exponential", "Poisson"]
#     #     else:
#     #         self.mu_entry.config(state="disabled")
#     #         self.service_params_entry.config(state="normal")
#     #         self.service_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
#     #         self.service_dist_combo.set("Uniform")


#     def create_simulation_tab(self):
#         """Create simulation results tab."""
#         self.sim_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.sim_frame, text="📋 Simulation Results")
        
#         # Create notebook within simulation tab
#         sim_notebook = ttk.Notebook(self.sim_frame)
#         sim_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Data table sub-tab
#         data_frame = ttk.Frame(sim_notebook)
#         sim_notebook.add(data_frame, text="Data Table")
        
#         # Treeview for data
#         columns = ("ID", "Arrival", "Service", "Server", "Start", "End", 
#                   "Wait", "Turnaround", "Response", "CP", "CP_Lookup")
        
#         # Create scrollable frame
#         container = ttk.Frame(data_frame)
#         container.pack(fill=tk.BOTH, expand=True)
        
#         # Treeview
#         self.tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
        
#         # Configure columns
#         col_widths = [50, 80, 80, 60, 80, 80, 80, 100, 80, 80, 90]
#         for i, col in enumerate(columns):
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=col_widths[i], anchor=tk.CENTER)
        
#         # Scrollbars
#         y_scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
#         x_scrollbar = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree.xview)
#         self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
#         # Layout using grid
#         self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
#         y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
#         x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
#         # Configure grid weights
#         container.grid_rowconfigure(0, weight=1)
#         container.grid_columnconfigure(0, weight=1)
        
#         # Metrics sub-tab
#         metrics_frame = ttk.Frame(sim_notebook)
#         sim_notebook.add(metrics_frame, text="Performance Metrics")
        
#         # Create a Text widget with scrollbar
#         self.metrics_text = scrolledtext.ScrolledText(
#             metrics_frame, 
#             wrap=tk.WORD,
#             font=("Consolas", 10),
#             height=25
#         )
#         self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Initial message
#         self.metrics_text.insert(tk.END, "Run simulation to see metrics...\n")
#         self.metrics_text.config(state=tk.DISABLED)
    
#     def update_simulation_tab(self, df: pd.DataFrame):
#         """Update simulation results tab."""
#         # Update data table
#         for item in self.tree.get_children():
#             self.tree.delete(item)
        
#         # Insert new data (limit to 500 rows for performance)
#         display_df = df.head(500)
#         for _, row in display_df.iterrows():
#             self.tree.insert("", tk.END, values=tuple(row))
        
#         # Update metrics text
#         stats = self.simulator.get_summary_statistics(df)
        
#         self.metrics_text.config(state=tk.NORMAL)
#         self.metrics_text.delete(1.0, tk.END)
        
#         # Header
#         self.metrics_text.insert(tk.END, "=" * 70 + "\n")
#         self.metrics_text.insert(tk.END, "SIMULATION PERFORMANCE METRICS\n")
#         self.metrics_text.insert(tk.END, "=" * 70 + "\n\n")
        
#         # Simulation info
#         self.metrics_text.insert(tk.END, "📊 SIMULATION INFO\n")
#         self.metrics_text.insert(tk.END, "-" * 40 + "\n")
#         self.metrics_text.insert(tk.END, f"Simulation Method: {'CP-based (until CP=0.99999)' if self.sim_method.get() == 'cp' else 'Fixed customers'}\n")
#         self.metrics_text.insert(tk.END, f"Total Customers: {len(df)}\n")
#         self.metrics_text.insert(tk.END, f"Arrival Distribution: {self.arrival_dist.get()}\n")
#         self.metrics_text.insert(tk.END, f"Service Distribution: {self.service_dist.get()}\n")
#         self.metrics_text.insert(tk.END, f"Number of Servers: {self.servers_entry.get()}\n")
#         if not df.empty:
#             self.metrics_text.insert(tk.END, f"Max CP Achieved: {df['CP'].max():.5f}\n")
#         self.metrics_text.insert(tk.END, f"Traffic Intensity (ρ): {float(self.lambda_entry.get()) / (int(self.servers_entry.get()) * float(self.mu_entry.get())):.4f}\n\n")
        
#         # Time metrics
#         self.metrics_text.insert(tk.END, "⏱️  TIME METRICS\n")
#         self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
#         if not df.empty:
#             time_metrics = [
#                 ("Average Service Time", df["Service"].mean()),
#                 ("Average Wait Time", df["Wait"].mean()),
#                 ("Average Turnaround Time", df["Turnaround"].mean()),
#                 ("Average Response Time", df["Response"].mean()),
#                 ("Maximum Wait Time", df["Wait"].max()),
#                 ("Minimum Wait Time", df["Wait"].min()),
#                 ("Std Deviation Wait", df["Wait"].std()),
#                 ("Median Wait Time", df["Wait"].median())
#             ]
            
#             for name, value in time_metrics:
#                 self.metrics_text.insert(tk.END, f"{name:25}: {value:.4f}\n")
        
#         # System metrics
#         self.metrics_text.insert(tk.END, "\n⚙️  SYSTEM METRICS\n")
#         self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
#         system_metrics = [
#             ("Server Utilization", f"{self.simulator.metrics.get('utilization', 0):.2f}%"),
#             ("Throughput", f"{self.simulator.metrics.get('throughput', 0):.4f} cust/time"),
#             ("Total Simulation Time", f"{self.simulator.metrics.get('total_time', 0):.2f}")
#         ]
        
#         for name, value in system_metrics:
#             self.metrics_text.insert(tk.END, f"{name:25}: {value}\n")
        
#         # Wait time percentiles
#         self.metrics_text.insert(tk.END, "\n📈 WAIT TIME DISTRIBUTION\n")
#         self.metrics_text.insert(tk.END, "-" * 40 + "\n")
        
#         if not df.empty:
#             percentiles = [25, 50, 75, 90, 95, 99]
#             for p in percentiles:
#                 value = df["Wait"].quantile(p/100)
#                 self.metrics_text.insert(tk.END, f"{p}th Percentile{'':15}: {value:.4f}\n")
        
#         self.metrics_text.config(state=tk.DISABLED)
    
#     def create_analytics_tab(self):
#         """Create analytical results tab."""
#         self.analytics_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.analytics_frame, text="📐 Analytical Results")
        
#         # Create a Text widget with scrollbar
#         self.analytics_text = scrolledtext.ScrolledText(
#             self.analytics_frame, 
#             wrap=tk.WORD,
#             font=("Consolas", 10),
#             height=25
#         )
#         self.analytics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Initial message
#         self.analytics_text.insert(tk.END, "Click 'Analytical Results' to calculate queueing theory formulas...\n")
#         self.analytics_text.config(state=tk.DISABLED)
    
#     def update_analytics_tab(self):
#         """Update analytical results tab."""
#         try:
#             lam = float(self.lambda_entry.get())
#             mu = float(self.mu_entry.get())
#             c = int(self.servers_entry.get())
            
#             # Calculate analytical results
#             if c == 1:
#                 results = QueueAnalytics.mm1(lam, mu)
#                 queue_type = "M/M/1"
#             else:
#                 results = QueueAnalytics.mmc(lam, mu, c)
#                 queue_type = f"M/M/{c}"
            
#             # Display results
#             self.analytics_text.config(state=tk.NORMAL)
#             self.analytics_text.delete(1.0, tk.END)
            
#             self.analytics_text.insert(tk.END, "=" * 70 + "\n")
#             self.analytics_text.insert(tk.END, f"ANALYTICAL RESULTS - {queue_type}\n")
#             self.analytics_text.insert(tk.END, "=" * 70 + "\n\n")
#             self.analytics_text.insert(tk.END, f"Parameters: λ = {lam}, μ = {mu}, c = {c}\n\n")
            
#             if "error" in results:
#                 self.analytics_text.insert(tk.END, f"❌ {results['error']}\n")
#             else:
#                 for key, value in results.items():
#                     if callable(value):
#                         continue
#                     if isinstance(value, float):
#                         self.analytics_text.insert(tk.END, f"{key:35}: {value:.6f}\n")
#                     else:
#                         self.analytics_text.insert(tk.END, f"{key:35}: {value}\n")
            
#             # Add comparison with simulation if available
#             if not self.current_df.empty:
#                 self.analytics_text.insert(tk.END, "\n" + "=" * 70 + "\n")
#                 self.analytics_text.insert(tk.END, "SIMULATION vs ANALYTICAL COMPARISON\n")
#                 self.analytics_text.insert(tk.END, "=" * 70 + "\n\n")
                
#                 sim_metrics = {
#                     "Avg Wait (Wq)": self.current_df["Wait"].mean(),
#                     "Avg Turnaround (W)": self.current_df["Turnaround"].mean(),
#                     "System Customers (L)": self.current_df["Wait"].mean() * float(self.lambda_entry.get())
#                 }
                
#                 theo_metrics = {
#                     "Avg Wait (Wq)": results.get("Wq (Avg wait in queue)", 0),
#                     "Avg Turnaround (W)": results.get("W (Avg time in system)", 0),
#                     "System Customers (L)": results.get("L (Avg in system)", 0)
#                 }
                
#                 for metric in ["Avg Wait (Wq)", "Avg Turnaround (W)"]:
#                     if metric in sim_metrics and metric in theo_metrics:
#                         sim_val = sim_metrics[metric]
#                         theo_val = theo_metrics[metric]
#                         diff = abs(theo_val - sim_val)
#                         diff_pct = (diff / theo_val * 100) if theo_val != 0 else 0
                        
#                         self.analytics_text.insert(tk.END, f"{metric}:\n")
#                         self.analytics_text.insert(tk.END, f"  Theoretical: {theo_val:.6f}\n")
#                         self.analytics_text.insert(tk.END, f"  Simulation:  {sim_val:.6f}\n")
#                         self.analytics_text.insert(tk.END, f"  Difference:  {diff:.6f} ({diff_pct:.2f}%)\n\n")
            
#             self.analytics_text.config(state=tk.DISABLED)
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Analytical calculation failed: {str(e)}")
    
#     def show_analytics(self):
#         """Calculate and show analytical results."""
#         self.update_analytics_tab()
#         self.notebook.select(2)  # Analytics tab
    
#     def create_charts_tab(self):
#         """Create performance charts tab."""
#         self.charts_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.charts_frame, text="📊 Performance Charts")
        
#         # Create canvas for charts with scrollbar
#         charts_canvas = tk.Canvas(self.charts_frame)
#         charts_scrollbar = ttk.Scrollbar(self.charts_frame, orient="vertical", command=charts_canvas.yview)
#         charts_inner_frame = ttk.Frame(charts_canvas)
        
#         charts_inner_frame.bind(
#             "<Configure>",
#             lambda e: charts_canvas.configure(scrollregion=charts_canvas.bbox("all"))
#         )
        
#         charts_canvas.create_window((0, 0), window=charts_inner_frame, anchor="nw")
#         charts_canvas.configure(yscrollcommand=charts_scrollbar.set)
        
#         charts_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
#         charts_scrollbar.pack(side="right", fill="y")
        
#         # Create figure with multiple subplots
#         self.charts_fig = Figure(figsize=(10, 12), dpi=100)
        
#         # Create subplots
#         self.chart_ax1 = self.charts_fig.add_subplot(311)  # Wait time
#         self.chart_ax2 = self.charts_fig.add_subplot(312)  # Turnaround time
#         self.chart_ax3 = self.charts_fig.add_subplot(313)  # Service time
        
#         # Create canvas
#         self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, charts_inner_frame)
#         self.charts_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
#         # Add toolbar
#         toolbar_frame = ttk.Frame(charts_inner_frame)
#         toolbar_frame.pack(fill=tk.X, pady=(10, 0))
        
#         toolbar = NavigationToolbar2Tk(self.charts_canvas, toolbar_frame)
#         toolbar.update()
        
#         # Initialize empty charts
#         self.initialize_charts()
    
#     def initialize_charts(self):
#         """Initialize empty charts."""
#         for ax in [self.chart_ax1, self.chart_ax2, self.chart_ax3]:
#             ax.clear()
#             ax.set_xlabel("")
#             ax.set_ylabel("")
#             ax.set_title("")
#             ax.grid(True, alpha=0.3)
        
#         self.chart_ax1.set_title("Wait Time per Customer", fontsize=12, fontweight='bold')
#         self.chart_ax2.set_title("Turnaround Time per Customer", fontsize=12, fontweight='bold')
#         self.chart_ax3.set_title("Service Time per Customer", fontsize=12, fontweight='bold')
        
#         self.charts_fig.tight_layout(pad=3.0)
#         self.charts_canvas.draw()
    
#     def update_charts_tab(self, df: pd.DataFrame):
#         """Update performance charts."""
#         if df.empty:
#             return
        
#         # Clear previous plots
#         for ax in [self.chart_ax1, self.chart_ax2, self.chart_ax3]:
#             ax.clear()
        
#         # Limit to first 100 customers for clarity
#         plot_df = df.head(100)
        
#         # Colors
#         colors = ['#3498db', '#e74c3c', '#2ecc71']
        
#         # Chart 1: Wait Time (Bar chart)
#         customer_ids = plot_df['ID'].astype(str).tolist()
#         wait_times = plot_df['Wait'].tolist()
        
#         bars1 = self.chart_ax1.bar(customer_ids, wait_times, color=colors[0], alpha=0.7, edgecolor='white')
#         self.chart_ax1.set_title('Wait Time per Customer', fontsize=12, fontweight='bold')
#         self.chart_ax1.set_xlabel('Customer ID', fontweight='bold')
#         self.chart_ax1.set_ylabel('Wait Time', fontweight='bold')
#         self.chart_ax1.tick_params(axis='x', rotation=45)
#         self.chart_ax1.grid(True, alpha=0.3)
        
#         # Add average line
#         avg_wait = plot_df['Wait'].mean()
#         self.chart_ax1.axhline(y=avg_wait, color='red', linestyle='--', linewidth=2, 
#                               label=f'Average: {avg_wait:.2f}')
#         self.chart_ax1.legend()
        
#         # Chart 2: Turnaround Time (Line chart)
#         turnaround_times = plot_df['Turnaround'].tolist()
        
#         self.chart_ax2.plot(customer_ids, turnaround_times, color=colors[1], 
#                            marker='o', linewidth=2, markersize=4)
#         self.chart_ax2.fill_between(customer_ids, turnaround_times, alpha=0.3, color=colors[1])
#         self.chart_ax2.set_title('Turnaround Time per Customer', fontsize=12, fontweight='bold')
#         self.chart_ax2.set_xlabel('Customer ID', fontweight='bold')
#         self.chart_ax2.set_ylabel('Turnaround Time', fontweight='bold')
#         self.chart_ax2.tick_params(axis='x', rotation=45)
#         self.chart_ax2.grid(True, alpha=0.3)
        
#         # Chart 3: Service Time (Stacked bar with wait time)
#         service_times = plot_df['Service'].tolist()
#         wait_for_service = plot_df['Wait'].tolist()
        
#         x = np.arange(len(customer_ids))
#         width = 0.6
        
#         self.chart_ax3.bar(x, service_times, width, label='Service Time', color=colors[2], alpha=0.7)
#         self.chart_ax3.bar(x, wait_for_service, width, bottom=service_times, 
#                           label='Wait Time', color=colors[0], alpha=0.7)
        
#         self.chart_ax3.set_title('Service Time vs Wait Time', fontsize=12, fontweight='bold')
#         self.chart_ax3.set_xlabel('Customer ID', fontweight='bold')
#         self.chart_ax3.set_ylabel('Time', fontweight='bold')
#         self.chart_ax3.set_xticks(x)
#         self.chart_ax3.set_xticklabels(customer_ids, rotation=45)
#         self.chart_ax3.legend()
#         self.chart_ax3.grid(True, alpha=0.3, axis='y')
        
#         # Adjust layout with more padding
#         self.charts_fig.tight_layout(pad=3.0, h_pad=2.0)
        
#         # Update canvas
#         self.charts_canvas.draw()
    
#     def create_gantt_tab(self):
#         """Create Gantt chart tab."""
#         self.gantt_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.gantt_frame, text="📅 Gantt Chart")
        
#         # Create figure for Gantt chart
#         self.gantt_fig = Figure(figsize=(12, 6), dpi=100)
#         self.gantt_ax = self.gantt_fig.add_subplot(111)
        
#         # Create canvas
#         self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, self.gantt_frame)
#         self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Add toolbar
#         toolbar_frame = ttk.Frame(self.gantt_frame)
#         toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
#         toolbar = NavigationToolbar2Tk(self.gantt_canvas, toolbar_frame)
#         toolbar.update()
        
#         # Initialize empty chart
#         self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline", fontsize=14, fontweight='bold')
#         self.gantt_ax.set_xlabel("Time", fontweight='bold')
#         self.gantt_ax.set_ylabel("Customers/Servers", fontweight='bold')
#         self.gantt_ax.grid(True, alpha=0.3)
#         self.gantt_canvas.draw()
    
#     def update_gantt_tab(self, df: pd.DataFrame, num_servers: int):
#         """Update Gantt chart."""
#         if df.empty:
#             return
        
#         # Clear previous plot
#         self.gantt_ax.clear()
        
#         # Limit to first 50 customers for clarity
#         plot_df = df.head(50).copy()
        
#         # Sort by start time
#         plot_df = plot_df.sort_values('Start')
        
#         # Get unique servers
#         servers = sorted(plot_df['Server'].unique())
#         server_map = {server: i for i, server in enumerate(servers)}
        
#         # Color palette
#         colors = plt.cm.tab20(np.linspace(0, 1, len(plot_df)))
        
#         # Plot each customer as a horizontal bar
#         for idx, (_, row) in enumerate(plot_df.iterrows()):
#             server_idx = server_map[row['Server']]
#             start_time = row['Start']
#             duration = row['Service']
            
#             # Create bar for the service time
#             self.gantt_ax.barh(
#                 server_idx,
#                 duration,
#                 left=start_time,
#                 height=0.6,
#                 color=colors[idx % len(colors)],
#                 edgecolor='black',
#                 alpha=0.8,
#                 linewidth=1
#             )
            
#             # Add customer ID label
#             if duration > 0.1:  # Only add label if duration is significant
#                 self.gantt_ax.text(
#                     start_time + duration / 2,
#                     server_idx,
#                     f"C{int(row['ID'])}",
#                     ha='center',
#                     va='center',
#                     fontsize=8,
#                     fontweight='bold',
#                     color='white'
#                 )
        
#         # Set y-axis labels
#         self.gantt_ax.set_yticks(range(len(servers)))
#         self.gantt_ax.set_yticklabels(servers)
#         self.gantt_ax.set_ylabel('Servers', fontweight='bold')
        
#         # Set x-axis
#         self.gantt_ax.set_xlabel('Time', fontweight='bold')
        
#         # Calculate server utilizations
#         total_time = plot_df['End'].max()
#         util_text = "Server Utilization:\n"
#         for server in servers:
#             server_data = plot_df[plot_df['Server'] == server]
#             busy_time = server_data['Service'].sum()
#             utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
#             util_text += f"{server}: {utilization:.1f}%\n"
        
#         # Add utilization text box
#         props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
#         self.gantt_ax.text(
#             0.02, 0.98,
#             util_text,
#             transform=self.gantt_ax.transAxes,
#             fontsize=10,
#             verticalalignment='top',
#             bbox=props
#         )
        
#         # Add title
#         title = f"Gantt Chart - {len(plot_df)} Customers on {len(servers)} Server(s)"
#         self.gantt_ax.set_title(title, fontsize=14, fontweight='bold')
        
#         # Add grid
#         self.gantt_ax.grid(True, alpha=0.3, linestyle='--')
        
#         # Adjust layout
#         self.gantt_fig.tight_layout(pad=3.0)
        
#         # Update canvas
#         self.gantt_canvas.draw()
    
#     def create_sensitivity_tab(self):
#         """Create sensitivity analysis tab."""
#         self.sens_frame = ttk.Frame(self.notebook)
#         self.notebook.add(self.sens_frame, text="📈 Sensitivity Analysis")
        
#         # Control frame for sensitivity analysis
#         sens_control_frame = ttk.LabelFrame(self.sens_frame, text="Sensitivity Analysis Parameters", padding=15)
#         sens_control_frame.pack(fill="x", padx=10, pady=10)
        
#         sens_control_frame.columnconfigure(0, weight=1)
#         sens_control_frame.columnconfigure(1, weight=2)
#         sens_control_frame.columnconfigure(2, weight=1)
#         sens_control_frame.columnconfigure(3, weight=2)
        
#         # Lambda range
#         ttk.Label(sens_control_frame, text="λ Range (min,max,steps):").grid(
#             row=0, column=0, sticky="w", padx=10, pady=10)
#         self.lambda_range_entry = ttk.Entry(sens_control_frame, width=25)
#         self.lambda_range_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
#         self.lambda_range_entry.insert(0, "0.1,2.0,20")
        
#         # Metric to analyze
#         ttk.Label(sens_control_frame, text="Metric to Analyze:").grid(
#             row=0, column=2, sticky="w", padx=10, pady=10)
#         self.sens_metric = tk.StringVar(value="avg_wait")
#         ttk.Combobox(sens_control_frame, textvariable=self.sens_metric,
#                     values=["avg_wait", "avg_turnaround", "utilization", "throughput", "queue_length"],
#                     state="readonly", width=20).grid(row=0, column=3, sticky="w", padx=10, pady=10)
        
#         # Run button
#         ttk.Button(sens_control_frame, text="Run Sensitivity Analysis", 
#                   command=self.run_sensitivity, width=20).grid(row=1, column=0, columnspan=4, pady=10)
        
#         # Create figure for sensitivity graph
#         self.sens_fig = Figure(figsize=(10, 6), dpi=100)
#         self.sens_ax = self.sens_fig.add_subplot(111)
        
#         # Create canvas
#         self.sens_canvas = FigureCanvasTkAgg(self.sens_fig, self.sens_frame)
#         self.sens_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         # Add toolbar
#         toolbar_frame = ttk.Frame(self.sens_frame)
#         toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
#         toolbar = NavigationToolbar2Tk(self.sens_canvas, toolbar_frame)
#         toolbar.update()
        
#         # Initialize empty graph
#         self.sens_ax.set_title("Sensitivity Analysis", fontsize=14, fontweight='bold')
#         self.sens_ax.set_xlabel("Arrival Rate (λ)", fontweight='bold')
#         self.sens_ax.set_ylabel("Metric Value", fontweight='bold')
#         self.sens_ax.grid(True, alpha=0.3)
#         self.sens_canvas.draw()
    
#     def run_sensitivity(self):
#         """Run sensitivity analysis using ANALYTICAL formulas."""
#         try:
#             # Get parameters
#             lam = float(self.lambda_entry.get())
#             mu = float(self.mu_entry.get())
#             num_servers = int(self.servers_entry.get())
            
#             # Parse lambda range
#             range_str = self.lambda_range_entry.get()
#             if "," in range_str:
#                 min_lam, max_lam, steps = map(float, range_str.split(","))
#                 lambda_range = np.linspace(min_lam, max_lam, int(steps))
#             else:
#                 # Default range around current lambda
#                 min_lam = max(0.1, lam * 0.5)
#                 max_lam = min(lam * 2, mu * num_servers * 0.95)  # Keep below capacity
#                 lambda_range = np.linspace(min_lam, max_lam, 20)
            
#             # Parse distribution parameters
#             arrival_params = self.parse_params(self.arrival_params.get())
#             service_params = self.parse_params(self.service_params.get())
            
#             self.status_var.set("Running sensitivity analysis using analytical formulas...")
#             self.root.update()
            
#             # Run sensitivity analysis using ANALYTICAL formulas
#             results = self.simulator.run_sensitivity_analysis(
#                 self.arrival_dist.get(), arrival_params,
#                 self.service_dist.get(), service_params,
#                 mu, num_servers, lambda_range
#             )
            
#             # Update sensitivity graph
#             self.update_sensitivity_graph(results)
            
#             # Switch to sensitivity tab
#             self.notebook.select(5)  # Sensitivity tab
            
#             self.status_var.set(f"Sensitivity analysis completed with {len(results)} points")
#             messagebox.showinfo("Sensitivity Analysis", 
#                               f"Sensitivity analysis completed!\n"
#                               f"Analyzed λ from {lambda_range[0]:.2f} to {lambda_range[-1]:.2f}\n"
#                               f"System capacity: {num_servers * mu:.2f}")
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Sensitivity analysis failed: {str(e)}")
#             self.status_var.set("Sensitivity analysis failed")
    
#     def update_sensitivity_graph(self, results: pd.DataFrame):
#         """Update sensitivity graph with results."""
#         self.sens_ax.clear()
        
#         if results.empty:
#             return
        
#         # Get metric to plot
#         metric = self.sens_metric.get()
#         metric_names = {
#             'avg_wait': 'Average Wait Time (Wq)',
#             'avg_turnaround': 'Average Turnaround Time (W)',
#             'utilization': 'Server Utilization (%)',
#             'throughput': 'Throughput (customers/time)',
#             'queue_length': 'Average Queue Length (Lq)'
#         }
        
#         # Filter out infinite values
#         valid_results = results[results[metric] != float('inf')]
        
#         if len(valid_results) == 0:
#             self.sens_ax.text(0.5, 0.5, 'No valid data points\nSystem unstable for all λ values',
#                              ha='center', va='center', transform=self.sens_ax.transAxes,
#                              fontsize=12, color='red')
#         else:
#             # Plot the metric vs lambda
#             self.sens_ax.plot(valid_results['lambda'], valid_results[metric], 
#                              'b-', linewidth=2, marker='o', markersize=4, label='Analytical')
            
#             # Fill under the curve
#             self.sens_ax.fill_between(valid_results['lambda'], valid_results[metric], 
#                                      alpha=0.3, color='blue')
            
#             # Add stability line (rho = 1)
#             if 'rho' in valid_results.columns:
#                 # Find where system becomes unstable (rho >= 0.95)
#                 unstable_mask = valid_results['rho'] >= 0.95
#                 if unstable_mask.any():
#                     first_unstable = valid_results[unstable_mask].iloc[0]
#                     self.sens_ax.axvline(x=first_unstable['lambda'], color='red', 
#                                        linestyle='--', linewidth=2, 
#                                        label=f'Stability limit (λ={first_unstable["lambda"]:.2f})')
            
#             # Add current lambda marker if available
#             if 'lam' in self.current_params:
#                 current_lam = self.current_params['lam']
#                 # Find closest lambda in results
#                 closest_idx = (valid_results['lambda'] - current_lam).abs().idxmin()
#                 current_point = valid_results.loc[closest_idx]
#                 self.sens_ax.plot(current_lam, current_point[metric], 'ro', 
#                                 markersize=8, label=f'Current (λ={current_lam:.2f})')
                
#                 # Add annotation
#                 self.sens_ax.annotate(f'Current: λ={current_lam:.2f}\n{metric_names.get(metric, metric)}={current_point[metric]:.2f}',
#                                     xy=(current_lam, current_point[metric]),
#                                     xytext=(10, 10), textcoords='offset points',
#                                     bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.5))
        
#         # Set labels and title
#         self.sens_ax.set_xlabel('Arrival Rate (λ)', fontweight='bold')
#         self.sens_ax.set_ylabel(metric_names.get(metric, metric), fontweight='bold')
        
#         title = f"Sensitivity Analysis: {metric_names.get(metric, metric)} vs Arrival Rate"
#         subtitle = f"Using Analytical Formulas ({self.arrival_dist.get()}/{self.service_dist.get()}/{self.servers_entry.get()})"
#         self.sens_ax.set_title(f"{title}\n{subtitle}", fontsize=12, fontweight='bold')
        
#         # Add grid and legend
#         self.sens_ax.grid(True, alpha=0.3, linestyle='--')
#         if len(valid_results) > 0:
#             self.sens_ax.legend(loc='best')
        
#         # Adjust layout
#         self.sens_fig.tight_layout(pad=3.0)
        
#         # Update canvas
#         self.sens_canvas.draw()

#     def run_simulation(self):
#         try:
#             # Get number of customers
#             if self.sim_method.get() == "cp":
#                 num_customers = 10000  # Large number for CP convergence
#             else:
#                 num_customers = int(self.customers_entry.get())
#                 if num_customers < 10:
#                     raise ValueError("Minimum 10 customers")

#             # === Arrival Parameters ===
#             arrival_dist = self.arrival_dist.get()
#             if self.arrival_type.get() == "M":
#                 lam = float(self.lambda_entry.get())
#                 arrival_params = {"rate": lam}
#             else:
#                 params_str = self.arrival_params.get().strip()
#                 if not params_str:
#                     raise ValueError("Enter parameters for General arrival (e.g., 2,5)")
#                 arrival_params = {}
#                 if arrival_dist == "Uniform":
#                     a, b = map(float, params_str.split(","))
#                     arrival_params = {"min": a, "max": b}
#                 elif arrival_dist == "Normal":
#                     m, s = map(float, params_str.split(","))
#                     arrival_params = {"mean": m, "stddev": s}
#                 elif arrival_dist == "Gamma":
#                     shape, scale = map(float, params_str.split(","))
#                     arrival_params = {"shape": shape, "scale": scale}

#             # === Service Parameters ===
#             service_dist = self.service_dist.get()
#             if self.service_type.get() == "M":
#                 mu = float(self.mu_entry.get())
#                 service_params = {"rate": mu}
#             else:
#                 params_str = self.service_params.get().strip()
#                 if not params_str:
#                     raise ValueError("Enter parameters for General service")
#                 service_params = {}
#                 if service_dist == "Uniform":
#                     a, b = map(float, params_str.split(","))
#                     service_params = {"min": a, "max": b}
#                 elif service_dist == "Normal":
#                     m, s = map(float, params_str.split(","))
#                     service_params = {"mean": m, "stddev": s}
#                 elif service_dist == "Gamma":
#                     shape, scale = map(float, params_str.split(","))
#                     service_params = {"shape": shape, "scale": scale}

#             num_servers = int(self.servers_entry.get())

#             self.status_var.set("Running simulation...")
#             self.root.update()

#             # Run simulation
#             if num_servers == 1:
#                 if self.sim_method.get() == "cp":
#                     self.current_df = self.simulator.simulate_single_server_cp(
#                         arrival_dist, arrival_params, service_dist, service_params,
#                         lam if self.arrival_type.get() == "M" else 1/get_mean(arrival_dist, arrival_params),
#                         mu if self.service_type.get() == "M" else 1/get_mean(service_dist, service_params)
#                     )
#                 else:
#                     self.current_df = self.simulator.simulate_single_server_fixed(
#                         num_customers, arrival_dist, arrival_params, service_dist, service_params
#                     )
#             else:
#                 if self.sim_method.get() == "cp":
#                     self.current_df = self.simulator.simulate_multi_server_cp(
#                         arrival_dist, arrival_params, service_dist, service_params,
#                         lam if self.arrival_type.get() == "M" else 1/get_mean(arrival_dist, arrival_params),
#                         mu if self.service_type.get() == "M" else 1/get_mean(service_dist, service_params),
#                         num_servers
#                     )
#                 else:
#                     self.current_df = self.simulator.simulate_multi_server_fixed(
#                         num_customers, arrival_dist, arrival_params, service_dist, service_params, num_servers
#                     )

#             self.current_params = {
#                 "lam": lam if self.arrival_type.get() == "M" else 1/get_mean(arrival_dist, arrival_params),
#                 "mu": mu if self.service_type.get() == "M" else 1/get_mean(service_dist, service_params),
#                 "c": num_servers
#             }

#             self.status_var.set(f"Complete! {len(self.current_df)} customers simulated.")
#             messagebox.showinfo("Success", "Simulation completed successfully!")

#         except Exception as e:
#             messagebox.showerror("Error", f"Simulation failed:\n{str(e)}")
#             self.status_var.set("Error")

# def main():
#     """Main function to run the application."""
#     root = tk.Tk()
#     app = QueueSimulatorGUI(root)
#     root.mainloop()

# if __name__ == "__main__":
#     main()


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
from distributions import get_mean, get_variance

class QueueSimulatorGUI:
    """Main GUI application for queue simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sapphire Shopping Outlet - Queue Simulator")
        
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['font.size'] = 10
        
        self.simulator = QueueSimulator()
        self.current_df = pd.DataFrame()
        self.current_params = {}
        
        self.create_main_container()
        self.root.state('zoomed')
    
    def create_main_container(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        self.create_widgets()
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def create_widgets(self):
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        ttk.Label(title_frame, text="Sapphire Shopping Outlet - Queue Simulator",
                  font=("Arial", 18, "bold"), foreground="#2c3e50").pack()
        ttk.Label(title_frame, text="Advanced Queueing Theory Simulation Tool",
                  font=("Arial", 10), foreground="#7f8c8d").pack(pady=(0, 10))
        
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.create_setup_tab()
        self.create_simulation_tab()
        self.create_analytics_tab()
        self.create_charts_tab()
        self.create_gantt_tab()
        self.create_sensitivity_tab()
        
        status_frame = ttk.Frame(self.scrollable_frame)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5).pack(fill=tk.X)

    def create_setup_tab(self):
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="Setup")
        
        setup_canvas = tk.Canvas(self.setup_frame)
        setup_scrollbar = ttk.Scrollbar(self.setup_frame, orient="vertical", command=setup_canvas.yview)
        setup_inner_frame = ttk.Frame(setup_canvas)
        
        setup_inner_frame.bind("<Configure>", lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all")))
        setup_canvas.create_window((0, 0), window=setup_inner_frame, anchor="nw")
        setup_canvas.configure(yscrollcommand=setup_scrollbar.set)
        
        setup_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        setup_scrollbar.pack(side="right", fill="y")

        # === Simulation Method ===
        method_frame = ttk.LabelFrame(setup_inner_frame, text="Simulation Method", padding=15)
        method_frame.pack(fill="x", padx=10, pady=10)

        self.sim_method = tk.StringVar(value="cp")
        ttk.Radiobutton(method_frame, text="CP-based (Simulate until CP=0.99999)", 
                       variable=self.sim_method, value="cp").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Fixed Number of Customers", 
                       variable=self.sim_method, value="fixed").pack(anchor="w", padx=10, pady=5)

        self.fixed_frame = ttk.Frame(method_frame)
        self.fixed_frame.pack(fill="x", padx=30, pady=5)
        ttk.Label(self.fixed_frame, text="Number of Customers:").pack(side="left")
        self.customers_entry = ttk.Entry(self.fixed_frame, width=15)
        self.customers_entry.pack(side="left", padx=5)
        self.customers_entry.insert(0, "500")
        self.fixed_frame.pack_forget()

        self.sim_method.trace('w', self.toggle_sim_method)

        # === Arrival Configuration ===
        arrival_frame = ttk.LabelFrame(setup_inner_frame, text="Arrival Process Configuration", padding=15)
        arrival_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(arrival_frame, text="Arrival Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.arrival_type = tk.StringVar(value="M")
        type_frame = ttk.Frame(arrival_frame)
        type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
        ttk.Radiobutton(type_frame, text="M (Markovian)", variable=self.arrival_type, value="M", command=self.toggle_arrival).pack(side="left", padx=10)
        ttk.Radiobutton(type_frame, text="G (General)", variable=self.arrival_type, value="G", command=self.toggle_arrival).pack(side="left", padx=10)

        ttk.Label(arrival_frame, text="Arrival Rate (λ):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.lambda_entry = ttk.Entry(arrival_frame, width=20)
        self.lambda_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.lambda_entry.insert(0, "0.8")

        ttk.Label(arrival_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.arrival_dist = tk.StringVar(value="Exponential")
        self.arrival_dist_combo = ttk.Combobox(arrival_frame, textvariable=self.arrival_dist,
                                               values=["Exponential"], state="readonly")
        self.arrival_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(arrival_frame, text="Parameters:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.arrival_params = ttk.Entry(arrival_frame, width=30, state="disabled")
        self.arrival_params.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=5)
        self.arrival_params.insert(0, "e.g., 2,5 (Uniform min,max)")

        # === Service Configuration ===
        service_frame = ttk.LabelFrame(setup_inner_frame, text="Service Process Configuration", padding=15)
        service_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(service_frame, text="Service Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.service_type = tk.StringVar(value="M")
        svc_type_frame = ttk.Frame(service_frame)
        svc_type_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=10)
        ttk.Radiobutton(svc_type_frame, text="M (Markovian)", variable=self.service_type, value="M", command=self.toggle_service).pack(side="left", padx=10)
        ttk.Radiobutton(svc_type_frame, text="G (General)", variable=self.service_type, value="G", command=self.toggle_service).pack(side="left", padx=10)

        ttk.Label(service_frame, text="Service Rate (μ):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.mu_entry = ttk.Entry(service_frame, width=20)
        self.mu_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.mu_entry.insert(0, "1.0")

        ttk.Label(service_frame, text="Distribution:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.service_dist = tk.StringVar(value="Exponential")
        self.service_dist_combo = ttk.Combobox(service_frame, textvariable=self.service_dist,
                                               values=["Exponential"], state="readonly")
        self.service_dist_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(service_frame, text="Parameters:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.service_params = ttk.Entry(service_frame, width=30, state="disabled")
        self.service_params.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=5)
        self.service_params.insert(0, "e.g., 0.5,2.0 (Uniform)")

        # === System Configuration ===
        sys_frame = ttk.LabelFrame(setup_inner_frame, text="System Configuration", padding=15)
        sys_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(sys_frame, text="Number of Servers (c):").pack(side="left", padx=10)
        self.servers_entry = ttk.Entry(sys_frame, width=10)
        self.servers_entry.pack(side="left", padx=10)
        self.servers_entry.insert(0, "1")

        # === Run Button ===
        run_btn = ttk.Button(setup_inner_frame, text="RUN SIMULATION", command=self.run_simulation)
        run_btn.pack(pady=20)

        self.toggle_arrival()
        self.toggle_service()

    def toggle_sim_method(self, *args):
        if self.sim_method.get() == "cp":
            self.fixed_frame.pack_forget()
        else:
            self.fixed_frame.pack(fill="x", padx=30, pady=5)

    def toggle_arrival(self, *args):
        if self.arrival_type.get() == "M":
            self.lambda_entry.config(state="normal")
            self.arrival_params.config(state="disabled")
            self.arrival_dist_combo["values"] = ["Exponential", "Poisson"]
            self.arrival_dist_combo.set("Exponential")
        else:
            self.lambda_entry.config(state="disabled")
            self.arrival_params.config(state="normal")
            self.arrival_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
            self.arrival_dist_combo.set("Uniform")

    def toggle_service(self, *args):
        if self.service_type.get() == "M":
            self.mu_entry.config(state="normal")
            self.service_params.config(state="disabled")
            self.service_dist_combo["values"] = ["Exponential", "Poisson"]
            self.service_dist_combo.set("Exponential")
        else:
            self.mu_entry.config(state="disabled")
            self.service_params.config(state="normal")
            self.service_dist_combo["values"] = ["Uniform", "Normal", "Gamma"]
            self.service_dist_combo.set("Uniform")

    def run_simulation(self):
        try:
            lambda_rate = float(self.lambda_entry.get())
            mu_rate = float(self.mu_entry.get())

            self.status_var.set("Calculating CP using Poisson formula...")
            self.root.update()

            if self.sim_method.get() == "cp":
                df = self.simulator.simulate_mm1_cp_exact(lambda_rate, mu_rate, target_cp=0.99999)
            else:
                n = int(self.customers_entry.get())
                df = self.simulator.simulate_mm1_fixed(n, lambda_rate, mu_rate)

            self.current_df = df
            self.update_simulation_tab(df)
            self.update_gantt_tab(df, 1)

            final_cp = df["CP"].iloc[-1] if not df.empty else 0
            self.status_var.set(f"Done! {len(df)} customers | Final CP = {final_cp:.5f}")

            messagebox.showinfo("Success",
                                f"CP-based simulation completed!\n"
                                f"Customers simulated: {len(df)}\n"
                                f"Final CP: {final_cp:.5f} (1 - e^(-λt))\n"
                                f"All values are discrete integers\n"
                                f"Same result structure every time!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
    def create_simulation_tab(self):
        self.sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sim_frame, text="Simulation Results")
        
        sim_notebook = ttk.Notebook(self.sim_frame)
        sim_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data Table
        data_frame = ttk.Frame(sim_notebook)
        sim_notebook.add(data_frame, text="Data Table")
        self.tree = ttk.Treeview(data_frame, columns=("ID","Arrival","Service","Server","Start","End","Wait","Turnaround","Response","CP","CP_Lookup"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Metrics
        metrics_frame = ttk.Frame(sim_notebook)
        sim_notebook.add(metrics_frame, text="Metrics")
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.metrics_text.insert(tk.END, "Run simulation to see results...\n")
        self.metrics_text.config(state=tk.DISABLED)

    def update_simulation_tab(self, df):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in df.head(200).iterrows():
            self.tree.insert("", "end", values=tuple(round(v, 4) if isinstance(v, float) else v for v in row))

        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        stats = self.simulator.get_summary_statistics(df)
        for k, v in stats.items():
            self.metrics_text.insert(tk.END, f"{k:35}: {v}\n")
        self.metrics_text.config(state=tk.DISABLED)

    def create_analytics_tab(self):
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytical Results")
        self.analytics_text = scrolledtext.ScrolledText(self.analytics_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.analytics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.analytics_text.insert(tk.END, "Run simulation first, then view analytical results...\n")
        self.analytics_text.config(state=tk.DISABLED)

    def update_analytics_tab(self):
        if self.current_df.empty:
            return
        lam = self.current_params.get("lam", 0.8)
        mu = self.current_params.get("mu", 1.0)
        c = self.current_params.get("c", 1)

        self.analytics_text.config(state=tk.NORMAL)
        self.analytics_text.delete(1.0, tk.END)
        self.analytics_text.insert(tk.END, QueueAnalytics.generate_queue_summary(lam, mu, c))
        self.analytics_text.config(state=tk.DISABLED)

    def create_charts_tab(self):
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Performance Charts")
        self.charts_fig = Figure(figsize=(12, 8))
        self.chart_ax1 = self.charts_fig.add_subplot(221)
        self.chart_ax2 = self.charts_fig.add_subplot(222)
        self.chart_ax3 = self.charts_fig.add_subplot(223)
        self.chart_ax4 = self.charts_fig.add_subplot(224)
        self.charts_canvas = FigureCanvasTkAgg(self.charts_fig, self.charts_frame)
        self.charts_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.charts_canvas, self.charts_frame).pack(fill=tk.X)

    def update_charts_tab(self, df):
        if df.empty: return
        for ax in [self.chart_ax1, self.chart_ax2, self.chart_ax3, self.chart_ax4]:
            ax.clear()
        x = df['ID'].head(100)
        self.chart_ax1.plot(x, df['Wait'].head(100), 'b-o', label="Wait")
        self.chart_ax1.set_title("Wait Time")
        self.chart_ax2.plot(x, df['Turnaround'].head(100), 'g-o')
        self.chart_ax2.set_title("Turnaround Time")
        self.chart_ax3.plot(x, df['Service'].head(100), 'r-o')
        self.chart_ax3.set_title("Service Time")
        self.chart_ax4.hist(df['Wait'].head(1000), bins=30, color='skyblue', edgecolor='black')
        self.chart_ax4.set_title("Wait Time Distribution")
        self.charts_fig.tight_layout()
        self.charts_canvas.draw()

    def create_gantt_tab(self):
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="Gantt Chart")
        self.gantt_fig = Figure(figsize=(12, 6))
        self.gantt_ax = self.gantt_fig.add_subplot(111)
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, self.gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.gantt_canvas, self.gantt_frame).pack(fill=tk.X)

    def update_gantt_tab(self, df, num_servers):
        if df.empty: return
        self.gantt_ax.clear()
        df_plot = df.head(50)
        colors = plt.cm.tab10(np.linspace(0, 1, num_servers))
        for _, row in df_plot.iterrows():
            server_idx = int(row['Server'][1:]) - 1
            self.gantt_ax.barh(server_idx, row['Service'], left=row['Start'], color=colors[server_idx % num_servers], edgecolor='black')
            self.gantt_ax.text(row['Start'] + row['Service']/2, server_idx, f"C{int(row['ID'])}", ha='center', va='center', color='white', fontweight='bold')
        self.gantt_ax.set_yticks(range(num_servers))
        self.gantt_ax.set_yticklabels([f"Server {i+1}" for i in range(num_servers)])
        self.gantt_ax.set_title("Gantt Chart - Customer Service Timeline")
        self.gantt_ax.set_xlabel("Time")
        self.gantt_ax.grid(True, alpha=0.3)
        self.gantt_fig.tight_layout()
        self.gantt_canvas.draw()

    def create_sensitivity_tab(self):
        self.sens_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sens_frame, text="Sensitivity Analysis")
        # Add controls and chart here if needed
        ttk.Label(self.sens_frame, text="Sensitivity analysis will be added in next version", font=("Arial", 12)).pack(pady=50)

def main():
    root = tk.Tk()
    app = QueueSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()