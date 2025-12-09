"""
Core simulation engine for queueing systems with CP-based simulation.
"""
import pandas as pd
import random
import math
import numpy as np
from typing import List, Tuple, Dict, Any
from distributions import generate_random, get_distribution_params
from scipy.stats import norm 

def parse_arrival_params(param_str):
    """Convert GUI string like 'min=1.0,max=3.0' to dictionary."""
    params = {}
    for item in param_str.split(","):
        key, value = item.split("=")
        params[key.strip()] = float(value.strip())
    return params
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
    


    
    def generate_arrivals_cp(self, arrival_dist: str, arrival_params: dict,
                             lam: float, max_cp: float = 0.99999,
                             max_events: int = 10000, step: float = 0.1):
        arrivals = []
        cp_list = []
        cp_lookup = []
    
        prev_cp = 0.0
    
        # Determine t values
        if arrival_dist == "Poisson":
            t_values = list(range(max_events))  # Poisson is discrete
        else:
            t_values = [i * step for i in range(max_events)]  # continuous
    
        for t in t_values:
    
            if arrival_dist == "Poisson":
                # For Poisson distribution (discrete time)
                k = int(t)
                
                # Calculate Poisson CDF: P(X ≤ k) where X ~ Poisson(λ)
                if k < 0:
                    calculated_cp = 0.0
                else:
                    # Use iterative calculation for numerical stability
                    # P(X = 0) = e^(-λ)
                    prob = math.exp(-lam)
                    cumulative = prob
                    
                    for j in range(1, k + 1):
                        # P(X = j) = P(X = j-1) * λ / j
                        prob = prob * lam / j
                        cumulative += prob
                    
                    calculated_cp = cumulative
    
            elif arrival_dist == "Exponential":
                calculated_cp = 1 - math.exp(-lam * t)
    
            elif arrival_dist == "Uniform":
                a = arrival_params.get("min", 0)
                b = arrival_params.get("max", 1)
                if t < a:
                    calculated_cp = 0.0
                elif t > b:
                    calculated_cp = 1.0
                else:
                    calculated_cp = (t - a) / (b - a)
    
            elif arrival_dist == "Normal":
                mean = arrival_params.get("mean", arrival_params.get("mu", 0))
                stddev = arrival_params.get("stddev", arrival_params.get("std", 1))
                calculated_cp = norm.cdf(t, loc=mean, scale=stddev)
                calculated_cp = max(0, min(1, calculated_cp))
    
            elif arrival_dist == "Gamma":
                shape = arrival_params.get("shape", 2.0)
                scale = arrival_params.get("scale", 0.5)
                calculated_cp = self.gamma_cdf(t, shape, scale)
    
            else:
                # Default to Exponential
                print(f"Warning: Unknown distribution '{arrival_dist}', defaulting to Exponential")
                calculated_cp = 1 - math.exp(-lam * t)
    
            # Stop if max_cp reached
            if calculated_cp >= max_cp:
                arrivals.append(t)
                cp_list.append(round(calculated_cp, 5))
                cp_lookup.append(round(prev_cp, 5))
                break
    
            arrivals.append(t)
            cp_list.append(round(calculated_cp, 5))
            cp_lookup.append(round(prev_cp, 5))
            prev_cp = calculated_cp
    
        return arrivals, cp_list, cp_lookup

    def gamma_cdf(self, x: float, shape: float, scale: float) -> float:
        """Approximate Gamma CDF using incomplete gamma function."""
        if x <= 0:
            return 0.0
        
        # Use series expansion for incomplete gamma function
        a = shape
        term = 1.0
        sum_val = 1.0
        x_scaled = x / scale
        
        for k in range(1, 50):  # Increased iterations for accuracy
            term *= x_scaled / (a + k - 1)
            sum_val += term
        
        # Gamma CDF = 1 - (x^a * e^-x * sum) / Γ(a+1)
        try:
            cdf = 1.0 - (x_scaled ** a) * math.exp(-x_scaled) * sum_val / math.gamma(a + 1)
        except (OverflowError, ValueError):
            # If calculation fails, use approximation
            if x_scaled > a * scale:
                cdf = 1.0
            else:
                cdf = 0.5
        
        return max(0, min(1, cdf))



    def simulate_single_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                 service_dist: str, service_params: Dict,
                                 lam: float, mu: float) -> pd.DataFrame:
        """Simulate single-server queue using CP-based stopping condition (CP=0.99999)."""
        self.reset()
        self.initialize_servers(1)
        
        # Generate arrivals using CP method (until CP=0.99999)
        arrivals, cp_list, cp_lookup = self.generate_arrivals_cp(
            arrival_dist, arrival_params, lam, max_cp=0.99999
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
                round(service_time, 0), ###
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
        if arrivals:
            utilization = min(1.0, total_service_time / arrivals[-1]) if arrivals[-1] > 0 else 0
        else:
            utilization = 0
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", "Start", "End", 
            "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
        ])
        
        # Store metrics
        self.metrics = {
            "utilization": utilization * 100,
            "avg_wait": df["Wait"].mean() if not df.empty else 0,
            "avg_turnaround": df["Turnaround"].mean() if not df.empty else 0,
            "avg_response": df["Response"].mean() if not df.empty else 0,
            "throughput": len(df) / arrivals[-1] if arrivals and arrivals[-1] > 0 else 0,
            "total_time": arrivals[-1] if arrivals else 0,
            "num_customers": len(df)
        }
        
        return df
    
    def simulate_multi_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                lam: float, mu: float, num_servers: int) -> pd.DataFrame:
        """Simulate multi-server queue using CP-based stopping condition (CP=0.99999)."""
        self.reset()
        self.initialize_servers(num_servers)
        
        # Generate arrivals using CP method (until CP=0.99999)
        arrivals, cp_list, cp_lookup = self.generate_arrivals_cp(
            arrival_dist, arrival_params, lam, max_cp=0.99999
        )
        
        rows = []
        total_service_time = 0.0
        
        for i, (arrival_time, cp, cp_prev) in enumerate(zip(arrivals, cp_list, cp_lookup)):
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
            # Find available server (earliest available)
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
        max_end_time = max(self.servers) if self.servers else 0
        if max_end_time > 0:
            utilization = min(1.0, total_service_time / (num_servers * max_end_time))
        else:
            utilization = 0
        
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
            "avg_wait": df["Wait"].mean() if not df.empty else 0,
            "avg_turnaround": df["Turnaround"].mean() if not df.empty else 0,
            "avg_response": df["Response"].mean() if not df.empty else 0,
            "throughput": len(df) / max_end_time if max_end_time > 0 else 0,
            "total_time": max_end_time,
            "num_customers": len(df),
            "server_utilizations": server_utilizations
        }
        
        return df
    
    # Fixed number simulation methods (for backward compatibility)
    def simulate_single_server_fixed(self, num_customers: int,
                                    arrival_dist: str, arrival_params: Dict,
                                    service_dist: str, service_params: Dict) -> pd.DataFrame:
        """Simulate single-server queue with fixed number of customers."""
        self.reset()
        self.initialize_servers(1)
        
        rows = []
        current_time = 0.0
        server_end_time = 0.0
        total_service_time = 0.0
        
        for i in range(num_customers):
            # Generate interarrival time
            interarrival = generate_random(arrival_dist, arrival_params)
            interarrival = max(0.01, interarrival)
            
            # Generate service time
            service_time = generate_random(service_dist, service_params)
            service_time = max(0.01, service_time)
            
            arrival_time = current_time + interarrival
            current_time = arrival_time
            
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
            
            # Calculate CP (for consistency with CP-based simulation)
            # For fixed number simulation, we don't have real CP, so we'll use index-based
            cp = min(0.99999, (i + 1) / num_customers * 0.99999)
            cp_prev = min(0.99999, i / num_customers * 0.99999)
            
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
                round(cp, 5),
                round(cp_prev, 5)
            ])
        
        # Calculate metrics
        utilization = min(1.0, total_service_time / current_time) if current_time > 0 else 0
        
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
            "throughput": num_customers / server_end_time if server_end_time > 0 else 0,
            "total_time": server_end_time,
            "num_customers": num_customers
        }
        
        return df
    
    def simulate_multi_server_fixed(self, num_customers: int,
                                   arrival_dist: str, arrival_params: Dict,
                                   service_dist: str, service_params: Dict,
                                   num_servers: int) -> pd.DataFrame:
        """Simulate multi-server queue with fixed number of customers."""
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
            
            # Calculate CP (for consistency)
            cp = min(0.99999, (i + 1) / num_customers * 0.99999)
            cp_prev = min(0.99999, i / num_customers * 0.99999)
            
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
                round(cp, 5),
                round(cp_prev, 5)
            ])
        
        # Calculate metrics
        max_end_time = max(self.servers) if self.servers else 0
        if max_end_time > 0:
            utilization = min(1.0, total_service_time / (num_servers * max_end_time))
        else:
            utilization = 0
        
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
            "throughput": num_customers / max_end_time if max_end_time > 0 else 0,
            "total_time": max_end_time,
            "num_customers": num_customers,
            "server_utilizations": server_utilizations
        }
        
        return df
    
    def get_gantt_data(self, df: pd.DataFrame) -> List[Dict]:
        """Extract Gantt chart data from simulation results."""
        gantt_data = []
        
        for _, row in df.iterrows():
            gantt_data.append({
                "customer_id": int(row['ID']),
                "arrival_time": row['Arrival'],
                "start_time": row['Start'],
                "end_time": row['End'],
                "service_time": row['Service'],
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
            "Average Service Time": f"{df['Service'].mean():.4f}",
            "Average Wait Time": f"{df['Wait'].mean():.4f}",
            "Average Turnaround Time": f"{df['Turnaround'].mean():.4f}",
            "Average Response Time": f"{df['Response'].mean():.4f}",
            "Maximum Wait Time": f"{df['Wait'].max():.4f}",
            "Minimum Wait Time": f"{df['Wait'].min():.4f}",
            "Std Deviation Wait": f"{df['Wait'].std():.4f}",
            "Throughput (customers/time)": f"{self.metrics.get('throughput', 0):.4f}"
        }
        
        # Add wait time percentiles
        if not df.empty:
            percentiles = [25, 50, 75, 90, 95]
            for p in percentiles:
                stats[f"Wait Time {p}th Percentile"] = f"{df['Wait'].quantile(p/100):.4f}"
        
        return stats
    
    def run_sensitivity_analysis(self, arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                mu: float, num_servers: int,
                                lambda_range: List[float] = None) -> pd.DataFrame:
        """Run sensitivity analysis by varying arrival rate using ANALYTICAL formulas."""
        if lambda_range is None:
            # Default range from 0.1 to 0.95 * capacity
            max_lambda = 0.95 * num_servers * mu
            lambda_range = np.linspace(0.1, max_lambda, 20)
        
        results = []
        
        for lam in lambda_range:
            # Calculate traffic intensity
            rho = lam / (num_servers * mu)
            
            if rho >= 1:
                # System is unstable
                results.append({
                    'lambda': lam,
                    'rho': rho,
                    'avg_wait': float('inf'),
                    'avg_turnaround': float('inf'),
                    'utilization': 100.0,
                    'throughput': lam,
                    'queue_length': float('inf'),
                    'status': 'Unstable'
                })
                continue
            
            # Use analytical formulas based on queue type
            if arrival_dist in ["Exponential", "Poisson"] and service_dist in ["Exponential", "Poisson"]:
                # M/M/c queue
                if num_servers == 1:
                    # M/M/1 formulas
                    wq = rho / (mu * (1 - rho))
                    w = wq + 1/mu
                    lq = lam * wq
                    l = lam * w
                else:
                    # M/M/c formulas
                    r = lam / mu
                    sum_part = sum([(r**k) / math.factorial(k) for k in range(num_servers)])
                    last_term = (r**num_servers) / (math.factorial(num_servers) * (1 - rho))
                    p0 = 1.0 / (sum_part + last_term)
                    
                    lq = (p0 * (r**num_servers) * rho) / (math.factorial(num_servers) * ((1 - rho)**2))
                    wq = lq / lam
                    w = wq + 1/mu
                    l = lq + r
            else:
                # G/G/c approximation (Allen-Cunneen approximation)
                # For simplicity, we'll use M/M/c as baseline and adjust
                # In a real implementation, you'd use Allen-Cunneen formula
                if num_servers == 1:
                    wq_base = rho / (mu * (1 - rho))
                else:
                    r = lam / mu
                    sum_part = sum([(r**k) / math.factorial(k) for k in range(num_servers)])
                    last_term = (r**num_servers) / (math.factorial(num_servers) * (1 - rho))
                    p0 = 1.0 / (sum_part + last_term)
                    lq_base = (p0 * (r**num_servers) * rho) / (math.factorial(num_servers) * ((1 - rho)**2))
                    wq_base = lq_base / lam
                
                # Simple adjustment factor for non-exponential distributions
                adjustment = 1.2  # Conservative estimate for general distributions
                wq = wq_base * adjustment
            
                w = wq + 1/mu
                l = lam * w
                lq = lam * wq
            
            results.append({
                'lambda': lam,
                'rho': rho,
                'avg_wait': wq,
                'avg_turnaround': w,
                'utilization': rho * 100,
                'throughput': lam,
                'queue_length': lq,
                'status': 'Stable'
            })
        
        return pd.DataFrame(results)
