"""
Clothing Store Queue Simulation (M/M/c) with Cumulative Probability (CP)
-----------------------------------------------------------------------
Purpose:
    - Simulates arrivals & service times using exponential distribution.
    - Stops arrival generation when CP ≥ 0.9999.
    - Works for both M/M/1 (single counter) and M/M/c (multiple counters).
    - Tracks waiting, response, turnaround times, and server utilization.
    - Saves detailed log to 'simulation_results.csv'.

Dependencies:
    pip install tabulate pandas numpy
"""

import math
import random
import pandas as pd
from tabulate import tabulate


# ---------------- USER INPUTS ---------------- #
LAMBDA = float(input("Enter Arrival Rate (λ customers/min): "))
MU = float(input("Enter Service Rate (μ customers/min per counter): "))
SERVERS = int(input("Enter number of counters (c): "))


# ---------------- INITIAL SETUP ---------------- #
headers = [
    "ID", "Arrival", "Service", "Assigned Server",
    "Start", "End", "Wait", "Turnaround", "Response",
    "CP", "CP Lookup"
]

rows = []

# Track when each server becomes free
server_end_times = [0.0 for _ in range(SERVERS)]

arrival_times = []
cumulative_probabilities = []
cp_lookup = [0.0]  # first lookup value is zero

current_time = 0.0
cumulative_prob = 0.0


# ---------------- ARRIVAL GENERATION (CP STOPPING) ---------------- #
while cumulative_prob < 0.9999:

    # exponential inter-arrival time
    interarrival = -math.log(1 - random.random()) / LAMBDA
    current_time += interarrival
    arrival_times.append(current_time)

    # CP for exponential distribution
    cumulative_prob = 1 - math.exp(-LAMBDA * current_time)

    if cumulative_prob > 0.9999:
        cumulative_prob = 0.9999

    cumulative_probabilities.append(round(cumulative_prob, 5))

    # Append previous CP in cp_lookup
    if len(cumulative_probabilities) > 1:
        cp_lookup.append(cumulative_probabilities[-2])
    else:
        cp_lookup.append(0.0)


NUM_CUSTOMERS = len(arrival_times)


# ---------------- SIMULATION ---------------- #
for i, arrival in enumerate(arrival_times, start=1):

    # exponential service time
    service_time = -math.log(1 - random.random()) / MU

    # server that becomes free first
    next_free_server = server_end_times.index(min(server_end_times))

    start_time = max(arrival, server_end_times[next_free_server])
    end_time = start_time + service_time

    wait_time = start_time - arrival
    turnaround = end_time - arrival
    response = wait_time + service_time

    # update server availability
    server_end_times[next_free_server] = end_time

    rows.append([
        i,
        arrival,
        service_time,
        f"S{next_free_server + 1}",
        start_time,
        end_time,
        wait_time,
        turnaround,
        response,
        cumulative_probabilities[i - 1],
        cp_lookup[i]
    ])


# ---------------- OUTPUT (CONSOLE) ---------------- #
print("\n" + "=" * 110)
print(f" Simulation Results for M/M/{SERVERS} Queue (Stopped at CP ≥ 0.9999) ")
print("=" * 110)

formatted_rows = [
    [
        r[0],
        f"{r[1]:.2f}",
        f"{r[2]:.2f}",
        r[3],
        f"{r[4]:.2f}",
        f"{r[5]:.2f}",
        f"{r[6]:.2f}",
        f"{r[7]:.2f}",
        f"{r[8]:.2f}",
        f"{r[9]:.5f}",
        f"{r[10]:.5f}"
    ]
    for r in rows
]

print(tabulate(
    formatted_rows,
    headers,
    tablefmt="fancy_grid",
    numalign="right",
    stralign="center"
))

print("=" * 110)


# ---------------- SAVE TO CSV ---------------- #
df = pd.DataFrame(rows, columns=headers)
df.to_csv("simulation_results.csv", index=False)


# ---------------- PERFORMANCE METRICS ---------------- #
avg_wait = df["Wait"].mean()
avg_turnaround = df["Turnaround"].mean()
avg_response = df["Response"].mean()

total_service_time = df["Service"].sum()
sim_time = df["End"].max()
utilization = total_service_time / (sim_time * SERVERS)


# ---------------- SUMMARY OUTPUT ---------------- #
print(f"\n✅ Simulation complete for {NUM_CUSTOMERS} customers.")
print(f"📄 Results saved to 'simulation_results.csv'\n")
print(f"📊 Averages → Wait: {avg_wait:.2f} | Turnaround: {avg_turnaround:.2f} | Response: {avg_response:.2f}")
print(f"🧮 Server Utilization: {utilization:.2%}")
print(f"⏳ Simulation stopped when cumulative probability (CP) reached ≈ {cumulative_probabilities[-1]:.5f}")
