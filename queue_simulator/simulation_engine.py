"""
Core simulation engine for queueing systems.
"""
import pandas as pd
import random
import math
from typing import List, Tuple, Dict, Any
from distributions import generate_random, get_distribution_params

class Customer:
    """Represents a customer in the queueing system."""
    
    def __init__(self, customer_id: int):
        self.id = customer_id
        self.arrival_time = 0.0
        self.service_time = 0.0
        self.start_time = 0.0
        self.end_time = 0.0
        self.server_id = None
        self.wait_time = 0.0
        self.turnaround_time = 0.0
        self.response_time = 0.0
        self.status = "Arrived"  # Arrived, Waiting, In Service, Completed

class QueueSimulator:
    """Main simulation engine for queueing systems."""
    
    def __init__(self):
        self.customers = []
        self.servers = []
        self.simulation_time = 0.0
        self.metrics = {}
        
    def reset(self):
        """Reset the simulator state."""
        self.customers = []
        self.servers = []
        self.simulation_time = 0.0
        self.metrics = {}
    
    def initialize_servers(self, num_servers: int):
        """Initialize servers with their availability times."""
        self.servers = [0.0] * num_servers  # Server availability times
    
    def simulate_single_server(self, num_customers: int,
                               arrival_dist: str, arrival_params: Dict,
                               service_dist: str, service_params: Dict) -> pd.DataFrame:
        """Simulate single-server queue (G/G/1)."""
        self.reset()
        self.initialize_servers(1)
        
        rows = []
        current_time = 0.0
        last_departure = 0.0
        total_service_time = 0.0
        
        for i in range(num_customers):
            # Generate interarrival time
            interarrival = generate_random(arrival_dist, arrival_params)
            interarrival = max(0.01, interarrival)  # Ensure positive
            
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
            # Update arrival time
            arrival_time = current_time + interarrival
            current_time = arrival_time
            
            # Calculate start and end times
            start_time = max(arrival_time, last_departure)
            end_time = start_time + service_time
            
            # Calculate metrics
            wait_time = start_time - arrival_time
            turnaround_time = end_time - arrival_time
            response_time = wait_time  # For single server
            
            # Update last departure
            last_departure = end_time
            total_service_time += service_time
            
            # Store customer data
            rows.append([
                i + 1,
                round(arrival_time, 2),
                round(service_time, 2),
                "S1",
                round(start_time, 2),
                round(end_time, 2),
                round(wait_time, 2),
                round(turnaround_time, 2),
                round(response_time, 2)
            ])
        
        # Calculate utilization
        utilization = min(1.0, total_service_time / current_time)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", 
            "Start", "End", "Wait", "Turnaround", "Response"
        ])
        
        # Store metrics
        self.metrics = {
            "utilization": utilization * 100,
            "avg_wait": df["Wait"].mean(),
            "avg_turnaround": df["Turnaround"].mean(),
            "avg_response": df["Response"].mean(),
            "throughput": num_customers / last_departure if last_departure > 0 else 0,
            "total_time": last_departure
        }
        
        return df
    
    def simulate_multi_server(self, num_customers: int,
                              arrival_dist: str, arrival_params: Dict,
                              service_dist: str, service_params: Dict,
                              num_servers: int) -> pd.DataFrame:
        """Simulate multi-server queue (G/G/c)."""
        self.reset()
        self.initialize_servers(num_servers)
        
        rows = []
        current_time = 0.0
        total_service_time = 0.0
        
        for i in range(num_customers):
            # Generate interarrival time
            interarrival = generate_random(arrival_dist, arrival_params)
            interarrival = max(0.01, interarrival)
            
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
            # Update arrival time
            arrival_time = current_time + interarrival
            current_time = arrival_time
            
            # Find available server
            available_server = min(range(num_servers), key=lambda x: self.servers[x])
            server_available_time = self.servers[available_server]
            
            # Calculate start and end times
            start_time = max(arrival_time, server_available_time)
            end_time = start_time + service_time
            
            # Update server availability
            self.servers[available_server] = end_time
            
            # Calculate metrics
            wait_time = start_time - arrival_time
            turnaround_time = end_time - arrival_time
            response_time = wait_time
            
            total_service_time += service_time
            
            # Store customer data
            rows.append([
                i + 1,
                round(arrival_time, 2),
                round(service_time, 2),
                f"S{available_server + 1}",
                round(start_time, 2),
                round(end_time, 2),
                round(wait_time, 2),
                round(turnaround_time, 2),
                round(response_time, 2)
            ])
        
        # Calculate metrics
        max_end_time = max(self.servers)
        utilization = min(1.0, total_service_time / (num_servers * max_end_time))
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", 
            "Start", "End", "Wait", "Turnaround", "Response"
        ])
        
        # Store metrics
        self.metrics = {
            "utilization": utilization * 100,
            "avg_wait": df["Wait"].mean(),
            "avg_turnaround": df["Turnaround"].mean(),
            "avg_response": df["Response"].mean(),
            "throughput": num_customers / max_end_time if max_end_time > 0 else 0,
            "total_time": max_end_time,
            "server_utilizations": [
                (max_end_time - sum(1 for r in rows if r[3] == f"S{j+1}")) / max_end_time * 100
                if max_end_time > 0 else 0
                for j in range(num_servers)
            ]
        }
        
        return df
    
    def get_gantt_data(self, df: pd.DataFrame, num_servers: int = 1) -> Dict:
        """Extract Gantt chart data from simulation results."""
        gantt_data = []
        
        if num_servers == 1:
            # Single server Gantt
            for _, row in df.iterrows():
                gantt_data.append({
                    "task": f"Customer {int(row['ID'])}",
                    "start": row['Start'],
                    "end": row['End'],
                    "server": "S1",
                    "wait": row['Wait']
                })
        else:
            # Multi-server Gantt
            for _, row in df.iterrows():
                gantt_data.append({
                    "task": f"Customer {int(row['ID'])}",
                    "start": row['Start'],
                    "end": row['End'],
                    "server": row['Server'],
                    "wait": row['Wait']
                })
        
        return gantt_data
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive summary statistics."""
        if df.empty:
            return {}
        
        stats = {
            "Total Customers": len(df),
            "Avg Wait Time": df["Wait"].mean(),
            "Std Wait Time": df["Wait"].std(),
            "Max Wait Time": df["Wait"].max(),
            "Min Wait Time": df["Wait"].min(),
            "Avg Turnaround Time": df["Turnaround"].mean(),
            "Avg Service Time": df["Service"].mean(),
            "Throughput (customers/time unit)": len(df) / df["End"].max() if df["End"].max() > 0 else 0,
            "Server Utilization (%)": self.metrics.get("utilization", 0),
            "Wait Time Percentiles": {
                "25th": df["Wait"].quantile(0.25),
                "50th (Median)": df["Wait"].median(),
                "75th": df["Wait"].quantile(0.75),
                "90th": df["Wait"].quantile(0.90),
                "95th": df["Wait"].quantile(0.95)
            }
        }
        
        # Add queue length statistics if we have arrival rate
        if "throughput" in self.metrics:
            stats["Avg Queue Length (Little's Law)"] = (
                self.metrics["avg_wait"] * (len(df) / df["End"].max()) 
                if df["End"].max() > 0 else 0
            )
        
        return stats