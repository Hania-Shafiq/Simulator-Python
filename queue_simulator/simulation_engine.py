"""
Core simulation engine for queueing systems with CP-based simulation.
"""
import pandas as pd
import random
import math
import numpy as np
from typing import List, Tuple, Dict, Any
from distributions import generate_random, get_distribution_params

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
    
    def generate_arrivals_cp(self, arrival_dist: str, arrival_params: Dict, 
                            lam: float, max_cp: float = 0.99999, max_events: int = 5000) -> Tuple[List, List, List]:
        """
        Generate arrivals until cumulative probability reaches max_cp.
        Based on the original CP simulation method.
        """
        # Seed for reproducibility
        seed = int(round(lam * 1000000)) & 0x7fffffff
        local_rng = random.Random(seed)
        
        arrivals = []
        cp_list = []
        cp_lookup = []
        
        t = 0.0
        prev_cp = 0.0
        
        for i in range(max_events):
            # Generate interarrival time based on distribution
            interarrival = generate_random(arrival_dist, arrival_params)
            t += interarrival
            
            # Calculate cumulative probability based on distribution
            if arrival_dist in ["Exponential", "Poisson"]:
                calculated_cp = 1 - math.exp(-lam * t)
            elif arrival_dist == "Uniform":
                if 'min' in arrival_params and 'max' in arrival_params:
                    a, b = arrival_params['min'], arrival_params['max']
                    if t < a:
                        calculated_cp = 0.0
                    elif t > b:
                        calculated_cp = 1.0
                    else:
                        calculated_cp = (t - a) / (b - a)
                else:
                    # Default uniform approximation
                    calculated_cp = 1 - math.exp(-lam * t)
            elif arrival_dist == "Normal":
                mean = arrival_params.get('mean', 1/lam)
                stddev = arrival_params.get('stddev', mean * 0.2)
                z = (t - mean) / stddev
                calculated_cp = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            elif arrival_dist == "Gamma":
                shape = arrival_params.get('shape', 2.0)
                scale = arrival_params.get('scale', 1/(lam * shape))
                # Approximate Gamma CDF
                x = t / scale
                term = 1.0
                sum_val = 1.0
                for k in range(1, 100):
                    term *= x / (shape + k - 1)
                    sum_val += term
                calculated_cp = 1.0 - (x ** shape) * math.exp(-x) * sum_val / math.gamma(shape + 1)
            else:
                calculated_cp = 1 - math.exp(-lam * t)
            
            if calculated_cp >= max_cp:
                break
            
            arrivals.append(t)
            cp_list.append(round(calculated_cp, 5))
            cp_lookup.append(round(prev_cp, 5))
            prev_cp = calculated_cp
        
        return arrivals, cp_list, cp_lookup
    
    def simulate_single_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                 service_dist: str, service_params: Dict,
                                 lam: float, mu: float) -> pd.DataFrame:
        """Simulate single-server queue using CP-based stopping condition."""
        self.reset()
        self.initialize_servers(1)
        
        # Generate arrivals using CP method
        arrivals, cp_list, cp_lookup = self.generate_arrivals_cp(
            arrival_dist, arrival_params, lam
        )
        
        rows = []
        server_end_time = 0.0
        total_service_time = 0.0
        
        for i, (arrival_time, cp, cp_prev) in enumerate(zip(arrivals, cp_list, cp_lookup)):
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
            # Calculate start and end times
            start_time = max(arrival_time, server_end_time)
            end_time = start_time + service_time
            
            # Calculate metrics
            wait_time = start_time - arrival_time
            turnaround_time = end_time - arrival_time
            response_time = wait_time
            
            # Update server availability
            server_end_time = end_time
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
                round(response_time, 2),
                cp,
                cp_prev
            ])
        
        # Calculate metrics
        utilization = min(1.0, total_service_time / arrivals[-1]) if arrivals else 0
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", "Start", "End", 
            "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
        ])
        
        # Store metrics
        self.metrics = {
            "utilization": utilization * 100,
            "avg_wait": df["Wait"].mean(),
            "avg_turnaround": df["Turnaround"].mean(),
            "avg_response": df["Response"].mean(),
            "throughput": len(df) / arrivals[-1] if len(arrivals) > 0 else 0,
            "total_time": arrivals[-1] if len(arrivals) > 0 else 0,
            "num_customers": len(df)
        }
        
        return df
    
    def simulate_multi_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                lam: float, mu: float, num_servers: int) -> pd.DataFrame:
        """Simulate multi-server queue using CP-based stopping condition."""
        self.reset()
        self.initialize_servers(num_servers)
        
        # Generate arrivals using CP method
        arrivals, cp_list, cp_lookup = self.generate_arrivals_cp(
            arrival_dist, arrival_params, lam
        )
        
        rows = []
        total_service_time = 0.0
        
        for i, (arrival_time, cp, cp_prev) in enumerate(zip(arrivals, cp_list, cp_lookup)):
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
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
                round(response_time, 2),
                cp,
                cp_prev
            ])
        
        # Calculate metrics
        max_end_time = max(self.servers)
        utilization = min(1.0, total_service_time / (num_servers * max_end_time)) if max_end_time > 0 else 0
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", "Start", "End", 
            "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
        ])
        
        # Calculate server-specific utilizations
        server_utilizations = []
        for j in range(num_servers):
            server_rows = df[df["Server"] == f"S{j+1}"]
            busy_time = server_rows["Service"].sum()
            util = (busy_time / max_end_time) * 100 if max_end_time > 0 else 0
            server_utilizations.append(util)
        
        # Store metrics
        self.metrics = {
            "utilization": utilization * 100,
            "avg_wait": df["Wait"].mean(),
            "avg_turnaround": df["Turnaround"].mean(),
            "avg_response": df["Response"].mean(),
            "throughput": len(df) / max_end_time if max_end_time > 0 else 0,
            "total_time": max_end_time,
            "num_customers": len(df),
            "server_utilizations": server_utilizations
        }
        
        return df
    
    # Keep the old fixed-number simulation methods for backward compatibility
    def simulate_single_server_fixed(self, num_customers: int,
                                    arrival_dist: str, arrival_params: Dict,
                                    service_dist: str, service_params: Dict) -> pd.DataFrame:
        """Simulate single-server queue with fixed number of customers."""
        return self.simulate_single_server_cp(
            arrival_dist, arrival_params, service_dist, service_params,
            1.0, 1.0  # Default rates, will be overridden by distributions
        )
    
    def simulate_multi_server_fixed(self, num_customers: int,
                                   arrival_dist: str, arrival_params: Dict,
                                   service_dist: str, service_params: Dict,
                                   num_servers: int) -> pd.DataFrame:
        """Simulate multi-server queue with fixed number of customers."""
        return self.simulate_multi_server_cp(
            arrival_dist, arrival_params, service_dist, service_params,
            1.0, 1.0, num_servers  # Default rates
        )
    
    def get_gantt_data(self, df: pd.DataFrame, num_servers: int = 1) -> List[Dict]:
        """Extract Gantt chart data from simulation results."""
        gantt_data = []
        
        for _, row in df.iterrows():
            gantt_data.append({
                "customer_id": int(row['ID']),
                "start_time": row['Start'],
                "end_time": row['End'],
                "duration": row['Service'],
                "server": row['Server'],
                "wait_time": row['Wait']
            })
        
        return gantt_data
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive summary statistics."""
        if df.empty:
            return {}
        
        stats = {
            "Total Customers": len(df),
            "Simulation Duration": f"{df['End'].max():.2f}",
            "Server Utilization (%)": f"{self.metrics.get('utilization', 0):.2f}",
            "Average Service Time": df["Service"].mean(),
            "Average Wait Time": df["Wait"].mean(),
            "Average Turnaround Time": df["Turnaround"].mean(),
            "Average Response Time": df["Response"].mean(),
            "Maximum Wait Time": df["Wait"].max(),
            "Minimum Wait Time": df["Wait"].min(),
            "Std Wait Time": df["Wait"].std(),
            "Throughput (customers/time unit)": self.metrics.get('throughput', 0)
        }
        
        # Add wait time percentiles
        percentiles = [25, 50, 75, 90, 95]
        for p in percentiles:
            stats[f"Wait Time {p}th Percentile"] = df["Wait"].quantile(p/100)
        
        return stats
    
    def run_sensitivity_analysis(self, arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                mu: float, num_servers: int,
                                lambda_range: List[float] = None) -> pd.DataFrame:
        """Run sensitivity analysis by varying arrival rate."""
        if lambda_range is None:
            # Default range from 0.1 to 0.9 * (num_servers * mu)
            max_lambda = 0.9 * num_servers * mu
            lambda_range = np.linspace(0.1, max_lambda, 20)
        
        results = []
        
        for lam in lambda_range:
            if num_servers == 1:
                df = self.simulate_single_server_cp(
                    arrival_dist, arrival_params, service_dist, service_params,
                    lam, mu
                )
            else:
                df = self.simulate_multi_server_cp(
                    arrival_dist, arrival_params, service_dist, service_params,
                    lam, mu, num_servers
                )
            
            results.append({
                'lambda': lam,
                'rho': lam / (num_servers * mu),
                'avg_wait': df['Wait'].mean(),
                'avg_turnaround': df['Turnaround'].mean(),
                'utilization': self.metrics.get('utilization', 0),
                'throughput': self.metrics.get('throughput', 0),
                'num_customers': len(df)
            })
        
        return pd.DataFrame(results)