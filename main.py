"""
Queue Simulation GUI with Proper Server Utilization and Separate Gantt Charts
Supports: MM1, MMC, MG1, MGC, GG1, GGC

Fixes applied:
- Stopping criteria uses max_cp=0.99999
- Correct CP lookup alignment (previous CP) for each arrival
- Server busy intervals store customer id so labels show correct customer numbers
- Server utilization percentage placed inside plot limits (xlim adjusted)
- Defensive parsing for number of servers input
- Minor robustness and UI improvements

"""

import math
import random
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- SIMULATION FUNCTIONS ---------------- #

# GENERATE EXPONENTIAL RANDOM VARIABLE
def exponential(rate):
    return -math.log(1 - random.random()) / rate

# GENERATE UNIFORM RANDOM VARIABLE
def uniform(a, b):
    return random.uniform(a, b)

# GENERATE ARRIVALS UNTIL CUMULATIVE PROBABILITY REACHES max_cp
def generate_arrivals(distribution, lam=1, max_cp=0.99999, max_events=5000):
    arrivals = []
    cp_list = []          # cumulative probability at each arrival time
    cp_lookup = []        # previous cumulative probability (for lookup)
    t = 0.0
    cp = 0.0
    events = 0
    # we guard with max_events to avoid infinite loops in degenerate cases
    while cp < max_cp and events < max_events:
        if distribution == "M":
            interarrival = exponential(lam)
            # For exponential interarrival, CDF at time t is 1 - exp(-lam*t)
        else:
            # For G-type (uniform service), arrival process assumed here as a generic renewal
            # Using a simple proxy CDF: 1 - exp(-0.2*t) (keeps behaviour similar to original code)
            # Note: user can change this mapping if they have a specific G arrival distribution.
            interarrival = uniform(1, 5)
        t += interarrival
        arrivals.append(t)
        events += 1
        if distribution == "M":
            cp = 1 - math.exp(-lam * t)
        else:
            cp = 1 - math.exp(-0.2 * t)
        if cp > max_cp:
            cp = max_cp
        # append current cp and the previous cp (0 for first)
        cp_list.append(round(cp, 5))
        prev_cp = round(cp_list[-2], 5) if len(cp_list) > 1 else 0.0
        cp_lookup.append(prev_cp)
    return arrivals, cp_list, cp_lookup

# SIMULATE QUEUE (SUPPORTS MULTIPLE SERVER VARIANTS)
def simulate_queue(queue_type, lam, mu, servers=1):
    distribution = "M" if queue_type in ["MM1","MMC"] else "G"
    num_servers = servers if queue_type in ["MMC","MGC","GGC"] else 1
    arrivals, cp_list, cp_lookup = generate_arrivals(distribution, lam)

    server_end_times = [0.0] * num_servers
    # store tuples (start, duration, customer_id) for clearer labeling
    server_busy_times = [[] for _ in range(num_servers)]
    rows = []

    for i, arrival in enumerate(arrivals, start=1):
        # service time depends on M or G service discipline
        service_time = exponential(mu) if ("M" in queue_type) else uniform(1, 5)
        # pick the next free server (shortest end time)
        next_free = server_end_times.index(min(server_end_times))
        start_time = max(arrival, server_end_times[next_free])
        end_time = start_time + service_time
        wait = start_time - arrival
        turnaround = end_time - arrival
        response = turnaround  # same as turnaround here

        server_end_times[next_free] = end_time
        server_busy_times[next_free].append((start_time, service_time, i))

        # ensure CP lists align with rows; use safe indexing
        cp_val = cp_list[i-1] if i-1 < len(cp_list) else round(min(1.0, 1 - math.exp(-lam * arrival)), 5)
        cp_prev = cp_lookup[i-1] if i-1 < len(cp_lookup) else (cp_list[i-2] if i-2 >= 0 and i-2 < len(cp_list) else 0.0)

        rows.append([
            i,
            round(arrival, 2),
            round(service_time, 2),
            f"S{next_free+1}",
            round(start_time, 2),
            round(end_time, 2),
            round(wait, 2),
            round(turnaround, 2),
            round(response, 2),
            cp_val,
            cp_prev
        ])

    df = pd.DataFrame(rows, columns=["ID","Arrival","Service","Server","Start","End","Wait","Turnaround","Response","CP","CP_Lookup"])
    return df, server_busy_times

# ---------------- GUI FUNCTIONS ---------------- #

def update_input_fields(*args):
    queue_type = queue_var.get()
    if queue_type in ["MMC", "MGC", "GGC"]:
        servers_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        servers_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    else:
        servers_label.grid_remove()
        servers_entry.grid_remove()


def run_simulation():
    try:
        lam = float(entry_lambda.get())
        mu = float(entry_mu.get())
        # defensive parsing: if servers entry empty or invalid, fallback to 1
        if queue_var.get() in ["MMC","MGC","GGC"]:
            try:
                servers = int(servers_entry.get())
                if servers < 1:
                    raise ValueError
            except Exception:
                servers = 1
        else:
            servers = 1

        df, server_busy_times = simulate_queue(queue_var.get(), lam, mu, servers)
        display_table(df)
        display_charts(df)
        display_server_gantt(server_busy_times)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def display_table(df):
    for widget in table_frame.winfo_children():
        widget.destroy()
    table_canvas = tk.Canvas(table_frame, bg="#f5f5f5")
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=table_canvas.yview)
    scrollable_frame = tk.Frame(table_canvas, bg="#f5f5f5")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all"))
    )

    table_canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
    table_canvas.configure(yscrollcommand=scrollbar.set)
    table_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    headers = list(df.columns)
    for j, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, relief="ridge", bg="#4e79a7", fg="white",
                 font=("Segoe UI", 10, "bold"), width=12).grid(row=0,column=j)
    for i, row in df.iterrows():
        bg_color = "#e6f2ff" if i%2==0 else "#ffffff"
        for j, val in enumerate(row):
            tk.Label(scrollable_frame, text=val, relief="ridge", bg=bg_color,
                     font=("Segoe UI", 10), width=12).grid(row=i+1,column=j)


def display_charts(df):
    fig.clear()
    colors = ["#4e79a7","#f28e2b","#e15759"]
    titles = ["Wait Time","Turnaround","Response"]
    metrics = ["Wait","Turnaround","Response"]

    for i, metric in enumerate(metrics):
        ax = fig.add_subplot(1,3,i+1)
        ax.bar(df["ID"][:20], df[metric][:20], color=colors[i])
        ax.set_title(titles[i], fontsize=10, fontweight="bold")
        ax.set_xlabel("ID", fontsize=9)
        ax.set_ylabel("Time", fontsize=9)
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    canvas.draw()


def display_server_gantt(server_busy_times):
    # Clear previous charts
    for widget in gantt_frame.winfo_children():
        widget.destroy()

    canvas_scroll = tk.Canvas(gantt_frame, bg="#f0f4f8", height=400)
    scrollbar = tk.Scrollbar(gantt_frame, orient="vertical", command=canvas_scroll.yview)
    scrollable_frame = tk.Frame(canvas_scroll, bg="#f0f4f8")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
    )

    canvas_scroll.create_window((0,0), window=scrollable_frame, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    canvas_scroll.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    colors = plt.cm.tab20.colors
    for i, times in enumerate(server_busy_times):
        fig_server = plt.Figure(figsize=(12,2.5), dpi=100)
        ax = fig_server.add_subplot(111)
        # prepare bars as (start, duration)
        bars = [(start, duration) for start, duration, cid in times]
        ax.broken_barh(bars, (0, 5), facecolors=[colors[i % len(colors)]]*len(bars), edgecolor='black')

        # Add customer numbers inside bars using stored customer ids
        for start, duration, cid in times:
            ax.text(start + duration/2, 2.5, str(cid), ha='center', va='center', fontsize=8, color='black')

        # Server utilization %
        if times:
            total_busy = sum(duration for start, duration, cid in times)
            total_time = max((start + duration) for start, duration, cid in times)
            utilization = (total_busy / total_time) * 100 if total_time > 0 else 0.0
            # expand x-limits a bit so utilization label is visible
            ax.set_xlim(0, total_time * 1.08)
            ax.text(total_time * 0.98, 4.2, f"Util: {utilization:.1f}%", fontsize=9, color='red', ha='right')
        else:
            ax.set_xlim(0, 1)

        ax.set_yticks([])
        ax.set_ylabel(f"Server {i+1}", fontsize=9)
        ax.set_xlabel("Time", fontsize=9)
        ax.set_title(f"Server {i+1} Gantt Chart")
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)

        canvas_server = FigureCanvasTkAgg(fig_server, master=scrollable_frame)
        canvas_server.get_tk_widget().pack(padx=5, pady=5, fill="both")
        canvas_server.draw()

# ---------------- GUI SETUP ---------------- #
root = tk.Tk()
root.title("Queue Simulation & Server Utilization")
root.geometry("1250x1000")
root.configure(bg="#f0f4f8")

# Input Frame
input_frame = tk.Frame(root, bg="#f0f4f8", bd=2, relief="groove")
input_frame.pack(padx=10, pady=10, fill="x")

tk.Label(input_frame, text="Queue Type:", bg="#f0f4f8", font=("Segoe UI",11)).grid(row=0,column=0,sticky="w")
queue_var = tk.StringVar(value="MM1")
queue_menu = ttk.Combobox(input_frame, textvariable=queue_var, values=["MM1","MMC","MG1","MGC","GG1","GGC"], width=12)
queue_menu.grid(row=0,column=1,padx=5,pady=5)
queue_var.trace("w", update_input_fields)

tk.Label(input_frame, text="Arrival Rate λ:", bg="#f0f4f8", font=("Segoe UI",11)).grid(row=1,column=0,sticky="w")
entry_lambda = tk.Entry(input_frame, width=12, font=("Segoe UI",11))
entry_lambda.grid(row=1,column=1,padx=5,pady=5)

tk.Label(input_frame, text="Service Rate μ:", bg="#f0f4f8", font=("Segoe UI",11)).grid(row=1,column=2,sticky="w")
entry_mu = tk.Entry(input_frame, width=12, font=("Segoe UI",11))
entry_mu.grid(row=1,column=3,padx=5,pady=5)

servers_label = tk.Label(input_frame, text="Number of Servers:", bg="#f0f4f8", font=("Segoe UI",11))
servers_entry = tk.Entry(input_frame, width=12, font=("Segoe UI",11))

tk.Button(input_frame, text="Run Simulation", bg="#4e79a7", fg="white",
          font=("Segoe UI",11,"bold"), command=run_simulation, relief="raised", bd=3).grid(row=0,column=4,rowspan=2,padx=10,pady=5)

# Table Frame
table_frame = tk.Frame(root, bg="#f5f5f5", bd=2, relief="groove")
table_frame.pack(padx=10, pady=5, fill="both", expand=True)

# Charts Frame (Wait/Turnaround/Response)
fig = plt.Figure(figsize=(12,3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(padx=10,pady=5, fill="both", expand=False)

# Gantt Charts Frame (per server)
gantt_frame = tk.Frame(root, bg="#f0f4f8")
gantt_frame.pack(padx=10, pady=5, fill="both", expand=False)

root.mainloop()
