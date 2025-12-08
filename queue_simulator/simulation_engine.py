# # 


# """
# Core simulation engine for queueing systems with CP-based simulation.
# FIXED VERSION with correct CP calculation.
# """
# import pandas as pd
# import random
# import math
# import numpy as np
# from typing import List, Tuple, Dict, Any
# from distributions import generate_random, get_distribution_params

# class QueueSimulator:
#     """Main simulation engine for queueing systems."""
    
#     def __init__(self):
#         self.customers = []
#         self.servers = []
#         self.simulation_time = 0.0
#         self.metrics = {}
#         self.step_size = 1.0  # Discrete time step
    
#     def reset(self):
#         """Reset the simulator state."""
#         self.customers = []
#         self.servers = []
#         self.simulation_time = 0.0
#         self.metrics = {}
    
#     def initialize_servers(self, num_servers: int):
#         """Initialize servers with their availability times."""
#         self.servers = [0.0] * num_servers
    
#     def generate_arrivals_cp(self, arrival_dist: str, arrival_params: Dict,
#                              lam: float, max_cp: float = 0.99999,
#                              max_events: int = 1000) -> tuple[list, list, list]:
#         """
#         Generate arrivals until CP reaches max_cp.
#         For ARRIVAL PROCESS, CP is the probability that next arrival occurs by time t.
#         """
#         arrivals = []
#         cp_list = []
#         cp_lookup = []
        
#         t = 0.0
#         cp_prev = 0.0
        
#         while t < max_events:
#             # Calculate CP(t) = P(interarrival time ≤ t)
#             # This is the CDF of the INTERARRIVAL time distribution
            
#             if arrival_dist == "Poisson":
#                 # For Poisson process, interarrival times are Exponential(λ)
#                 cp = 1 - math.exp(-lam * t) if lam > 0 else 0.0
                
#             elif arrival_dist == "Exponential":
#                 # Direct exponential distribution for interarrivals
#                 cp = 1 - math.exp(-lam * t) if lam > 0 else 0.0
                
#             elif arrival_dist == "Uniform":
#                 a = arrival_params.get("min", 0)
#                 b = arrival_params.get("max", 1)
#                 if b <= a:
#                     b = a + 1
#                 if t < a:
#                     cp = 0.0
#                 elif t > b:
#                     cp = 1.0
#                 else:
#                     cp = (t - a) / (b - a)
                    
#             elif arrival_dist == "Normal":
#                 mean = arrival_params.get("mean", 1/lam if lam > 0 else 1)
#                 stddev = arrival_params.get("stddev", mean * 0.3)
#                 if stddev <= 0:
#                     stddev = 0.1
#                 z = (t - mean) / stddev
#                 cp = 0.5 * (1 + math.erf(z / math.sqrt(2)))
#                 cp = max(0.0, min(1.0, cp))
                
#             elif arrival_dist == "Gamma":
#                 shape = arrival_params.get("shape", 2.0)
#                 scale = arrival_params.get("scale", 1/(lam * shape) if lam > 0 else 0.5)
#                 cp = self.gamma_cdf(t, shape, scale)
                
#             else:
#                 # Default to exponential
#                 cp = 1 - math.exp(-lam * t) if lam > 0 else 0.0
            
#             # Round CP for stability
#             cp = round(cp, 5)
            
#             # Store values (generate an arrival at this time)
#             arrivals.append(t)
#             cp_list.append(cp)
#             cp_lookup.append(cp_prev)
            
#             # Update for next iteration
#             cp_prev = cp
            
#             # Check if we've reached max CP
#             if cp >= max_cp:
#                 break
            
#             # Increment time for next CP calculation
#             # For arrival process, we need to check CP at increasing times
#             t += self.step_size
        
#         return arrivals, cp_list, cp_lookup
    
#     def gamma_cdf(self, x: float, shape: float, scale: float) -> float:
#         """Calculate Gamma CDF using the regularized lower incomplete gamma function."""
#         if x <= 0:
#             return 0.0
        
#         # Use the regularized lower incomplete gamma function
#         # P = γ(k, x/θ) / Γ(k)
#         from scipy.special import gammainc
#         try:
#             cp = gammainc(shape, x / scale)
#         except:
#             # Fallback approximation
#             if x / scale < shape:
#                 cp = 0.5 * (1 + math.erf((math.sqrt(x/scale) - math.sqrt(shape))/math.sqrt(2)))
#             else:
#                 cp = 0.5 * (1 + math.erf((math.sqrt(x/scale) - math.sqrt(shape))/math.sqrt(2)))
        
#         return max(0.0, min(1.0, cp))
    
#     def simulate_cp_based(self, arrival_dist: str, arrival_params: Dict,
#                          service_dist: str, service_params: Dict,
#                          lam: float, mu: float,
#                          num_servers: int = 1) -> pd.DataFrame:
#         """
#         Simulate using CP-based stopping (CP >= 0.99999).
#         Each customer's arrival time is determined by CP threshold.
#         """
#         self.reset()
#         self.initialize_servers(num_servers)
        
#         # Generate arrivals based on CP
#         arrivals, cp_list, cp_lookup = self.generate_arrivals_cp(
#             arrival_dist, arrival_params, lam, max_cp=0.99999
#         )
        
#         rows = []
        
#         for i, (arrival_time, cp, cp_prev) in enumerate(zip(arrivals, cp_list, cp_lookup)):
#             # Generate service time (DISCRETE integer)
#            # In your simulate_fixed_customers method, change:
#             service_time = max(1, int(service_time))  # Force integer

# # And in simulate_cp_based:
#             service_time = max(1, int(service_time))
            
#             # Find available server
#             if num_servers == 1:
#                 server_available_time = self.servers[0]
#                 start_time = max(arrival_time, server_available_time)
#                 end_time = start_time + service_time
#                 self.servers[0] = end_time
#                 server_name = "S1"
#             else:
#                 available_server = min(range(num_servers), key=lambda x: self.servers[x])
#                 server_available_time = self.servers[available_server]
#                 start_time = max(arrival_time, server_available_time)
#                 end_time = start_time + service_time
#                 self.servers[available_server] = end_time
#                 server_name = f"S{available_server + 1}"
            
#             # Calculate metrics
#             wait_time = start_time - arrival_time
#             turnaround_time = end_time - arrival_time
#             response_time = wait_time
            
#             # Store data
#             rows.append([
#                 i + 1,
#                 round(arrival_time, 2),
#                 round(service_time, 2),
#                 server_name,
#                 round(start_time, 2),
#                 round(end_time, 2),
#                 round(wait_time, 2),
#                 round(turnaround_time, 2),
#                 round(response_time, 2),
#                 cp,
#                 cp_prev
#             ])
        
#         # Create DataFrame
#         df = pd.DataFrame(rows, columns=[
#             "ID", "Arrival", "Service", "Server", "Start", "End", 
#             "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
#         ])
        
#         # Calculate metrics
#         max_end_time = max(self.servers) if self.servers else 0
#         total_service_time = df["Service"].sum()
        
#         if num_servers == 1:
#             utilization = (total_service_time / max_end_time) * 100 if max_end_time > 0 else 0
#         else:
#             utilization = (total_service_time / (num_servers * max_end_time)) * 100 if max_end_time > 0 else 0
        
#         self.metrics = {
#             "utilization": utilization,
#             "avg_wait": df["Wait"].mean(),
#             "avg_turnaround": df["Turnaround"].mean(),
#             "avg_response": df["Response"].mean(),
#             "throughput": len(df) / max_end_time if max_end_time > 0 else 0,
#             "total_time": max_end_time,
#             "num_customers": len(df)
#         }
        
#         return df
    
#     def simulate_fixed_customers(self, num_customers: int,
#                                 arrival_dist: str, arrival_params: Dict,
#                                 service_dist: str, service_params: Dict,
#                                 num_servers: int = 1) -> pd.DataFrame:
#         """
#         Simulate with FIXED number of customers using CP method for timing.
#         CP values represent the probability distribution of arrival times.
#         """
#         self.reset()
#         self.initialize_servers(num_servers)
        
#         rows = []
#         current_time = 0.0
        
#         # For fixed number, generate interarrival times
#         interarrivals = []
#         for _ in range(num_customers):
#             interarrival = generate_random(arrival_dist, arrival_params)
#             interarrival = max(0.01, interarrival)
#             interarrivals.append(interarrival)
        
#         # Calculate CP for each arrival
#         cumulative_time = 0.0
#         for i in range(num_customers):
#             # Calculate arrival time
#             arrival_time = cumulative_time + interarrivals[i]
#             cumulative_time = arrival_time
            
#             # Calculate CP for this arrival time
#             # CP = P(interarrival time ≤ arrival_time)
#             lam = arrival_params.get('rate', 0.5)
            
#             if arrival_dist == "Poisson" or arrival_dist == "Exponential":
#                 cp = 1 - math.exp(-lam * arrival_time)
#             elif arrival_dist == "Uniform":
#                 a = arrival_params.get("min", 0)
#                 b = arrival_params.get("max", 1)
#                 if b <= a:
#                     b = a + 1
#                 if arrival_time < a:
#                     cp = 0.0
#                 elif arrival_time > b:
#                     cp = 1.0
#                 else:
#                     cp = (arrival_time - a) / (b - a)
#             elif arrival_dist == "Normal":
#                 mean = arrival_params.get("mean", 1/lam if lam > 0 else 1)
#                 stddev = arrival_params.get("stddev", mean * 0.3)
#                 if stddev <= 0:
#                     stddev = 0.1
#                 z = (arrival_time - mean) / stddev
#                 cp = 0.5 * (1 + math.erf(z / math.sqrt(2)))
#                 cp = max(0.0, min(1.0, cp))
#             else:
#                 cp = 1 - math.exp(-lam * arrival_time)
            
#             cp_prev = cp * (i / (i + 1)) if i > 0 else 0.0
            
#             # Generate service time
#             service_time = generate_random(service_dist, service_params)
#             service_time = max(1, round(service_time))
            
#             # Find available server
#             if num_servers == 1:
#                 server_available_time = self.servers[0]
#                 start_time = max(arrival_time, server_available_time)
#                 end_time = start_time + service_time
#                 self.servers[0] = end_time
#                 server_name = "S1"
#             else:
#                 available_server = min(range(num_servers), key=lambda x: self.servers[x])
#                 server_available_time = self.servers[available_server]
#                 start_time = max(arrival_time, server_available_time)
#                 end_time = start_time + service_time
#                 self.servers[available_server] = end_time
#                 server_name = f"S{available_server + 1}"
            
#             # Calculate metrics
#             wait_time = start_time - arrival_time
#             turnaround_time = end_time - arrival_time
#             response_time = wait_time
            
#             # Store data
#             rows.append([
#                 i + 1,
#                 round(arrival_time, 2),
#                 round(service_time, 2),
#                 server_name,
#                 round(start_time, 2),
#                 round(end_time, 2),
#                 round(wait_time, 2),
#                 round(turnaround_time, 2),
#                 round(response_time, 2),
#                 round(cp, 5),
#                 round(cp_prev, 5)
#             ])
        
#         # Create DataFrame
#         df = pd.DataFrame(rows, columns=[
#             "ID", "Arrival", "Service", "Server", "Start", "End", 
#             "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
#         ])
        
#         # Calculate metrics
#         max_end_time = max(self.servers) if self.servers else 0
#         total_service_time = df["Service"].sum()
        
#         if num_servers == 1:
#             utilization = (total_service_time / max_end_time) * 100 if max_end_time > 0 else 0
#         else:
#             utilization = (total_service_time / (num_servers * max_end_time)) * 100 if max_end_time > 0 else 0
        
#         self.metrics = {
#             "utilization": utilization,
#             "avg_wait": df["Wait"].mean(),
#             "avg_turnaround": df["Turnaround"].mean(),
#             "avg_response": df["Response"].mean(),
#             "throughput": num_customers / max_end_time if max_end_time > 0 else 0,
#             "total_time": max_end_time,
#             "num_customers": num_customers
#         }
        
#         return df
    
#     # Backward compatibility methods
#     def simulate_single_server_cp(self, arrival_dist: str, arrival_params: Dict,
#                                  service_dist: str, service_params: Dict,
#                                  lam: float, mu: float) -> pd.DataFrame:
#         return self.simulate_cp_based(arrival_dist, arrival_params, 
#                                      service_dist, service_params, 
#                                      lam, mu, num_servers=1)
    
#     def simulate_multi_server_cp(self, arrival_dist: str, arrival_params: Dict,
#                                 service_dist: str, service_params: Dict,
#                                 lam: float, mu: float, num_servers: int) -> pd.DataFrame:
#         return self.simulate_cp_based(arrival_dist, arrival_params,
#                                      service_dist, service_params,
#                                      lam, mu, num_servers)
    
#     def simulate_single_server_fixed(self, num_customers: int,
#                                     arrival_dist: str, arrival_params: Dict,
#                                     service_dist: str, service_params: Dict) -> pd.DataFrame:
#         return self.simulate_fixed_customers(num_customers, arrival_dist, arrival_params,
#                                             service_dist, service_params, num_servers=1)
    
#     def simulate_multi_server_fixed(self, num_customers: int,
#                                    arrival_dist: str, arrival_params: Dict,
#                                    service_dist: str, service_params: Dict,
#                                    num_servers: int) -> pd.DataFrame:
#         return self.simulate_fixed_customers(num_customers, arrival_dist, arrival_params,
#                                             service_dist, service_params, num_servers)
    
#     # Keep other methods as they are...
#     def get_gantt_data(self, df: pd.DataFrame) -> List[Dict]:
#         """Extract Gantt chart data from simulation results."""
#         gantt_data = []
        
#         for _, row in df.iterrows():
#             gantt_data.append({
#                 "customer_id": int(row['ID']),
#                 "arrival_time": row['Arrival'],
#                 "start_time": row['Start'],
#                 "end_time": row['End'],
#                 "service_time": row['Service'],
#                 "server": row['Server'],
#                 "wait_time": row['Wait']
#             })
        
#         return gantt_data
    
#     def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
#         """Calculate comprehensive summary statistics."""
#         if df.empty:
#             return {}
        
#         stats = {
#             "Total Customers": len(df),
#             "Simulation Duration": f"{df['End'].max():.2f}",
#             "Server Utilization (%)": f"{self.metrics.get('utilization', 0):.2f}",
#             "Average Service Time": f"{df['Service'].mean():.2f}",
#             "Average Wait Time": f"{df['Wait'].mean():.2f}",
#             "Average Turnaround Time": f"{df['Turnaround'].mean():.2f}",
#             "Average Response Time": f"{df['Response'].mean():.2f}",
#             "Maximum Wait Time": f"{df['Wait'].max():.2f}",
#             "Minimum Wait Time": f"{df['Wait'].min():.2f}",
#             "Std Deviation Wait": f"{df['Wait'].std():.2f}",
#             "Throughput (customers/time)": f"{self.metrics.get('throughput', 0):.4f}"
#         }
        
#         # Add wait time percentiles
#         if not df.empty:
#             percentiles = [25, 50, 75, 90, 95]
#             for p in percentiles:
#                 stats[f"Wait Time {p}th Percentile"] = f"{df['Wait'].quantile(p/100):.2f}"
        
#         return stats


"""
Core simulation engine for queueing systems with CP-based simulation.
CORRECTED VERSION - Distribution ke sahi formulas se CP calculate karo.
"""
import pandas as pd
import random
import math
import numpy as np
from typing import List, Tuple, Dict, Any
from scipy import stats
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
        self.servers = [0.0] * num_servers
    
    def calculate_cdf(self, t: float, dist_name: str, params: Dict, lam: float = None) -> float:
        """
        Calculate CDF for different distributions at time t.
        CP = F(t) = P(X ≤ t) where X is interarrival time.
        """
        if dist_name == "Poisson":
            # IMPORTANT: For Poisson ARRIVAL PROCESS, interarrival times are Exponential!
            # CP for next arrival by time t = 1 - e^(-λt)
            rate = params.get('rate', lam if lam else 0.5)
            return 1 - math.exp(-rate * t)
            
        elif dist_name == "Exponential":
            rate = params.get('rate', lam if lam else 0.5)
            return 1 - math.exp(-rate * t)
            
        elif dist_name == "Uniform":
            a = params.get("min", 0)
            b = params.get("max", 10)
            if b <= a:
                b = a + 1
            if t < a:
                return 0.0
            elif t > b:
                return 1.0
            else:
                return (t - a) / (b - a)
                
        elif dist_name == "Normal":
            mean = params.get("mean", 5)
            std = params.get("stddev", 1)
            if std <= 0:
                std = 0.1
            # Use scipy for accurate normal CDF
            try:
                return stats.norm.cdf(t, loc=mean, scale=std)
            except:
                # Fallback to error function
                z = (t - mean) / std
                return 0.5 * (1 + math.erf(z / math.sqrt(2)))
                
        elif dist_name == "Gamma":
            shape = params.get("shape", 2)
            scale = params.get("scale", 1)
            try:
                return stats.gamma.cdf(t, a=shape, scale=scale)
            except:
                # Approximation
                if t <= 0:
                    return 0.0
                # Use regularized incomplete gamma
                from scipy.special import gammainc
                return gammainc(shape, t / scale)
                
        else:
            # Default to exponential
            rate = lam if lam else 0.5
            return 1 - math.exp(-rate * t)
    
    def generate_arrivals_cp(self, arrival_dist: str, arrival_params: Dict,
                             lam: float, max_cp: float = 0.99999,
                             max_customers: int = 100) -> tuple[list, list, list]:
        """
        CORRECT VERSION: Generate arrivals using ACTUAL CDF formulas.
        Returns: (arrival_times, cp_values, cp_lookup_values)
        """
        arrivals = []
        cp_values = []
        cp_lookup = []
        
        # For CP-based simulation, we need to find times when CP reaches certain values
        # We'll generate discrete time points and calculate CP at each
        
        # Step 1: Generate time points (discrete)
        time_points = []
        max_time = 50  # Reasonable max simulation time
        
        # Generate more dense time points at beginning, sparse at end
        for i in range(max_customers):
            # Time increases gradually
            t = i * 0.5  # Start with 0.5 increments
            time_points.append(t)
        
        # Step 2: Calculate CP at each time point
        prev_cp = 0.0
        
        for i, t in enumerate(time_points):
            # Calculate CP using correct CDF formula
            cp = self.calculate_cdf(t, arrival_dist, arrival_params, lam)
            
            # Ensure CP is between 0 and 1
            cp = max(0.0, min(1.0, cp))
            
            # Only add if CP increased (or it's the first point)
            if cp > prev_cp or i == 0:
                arrivals.append(t)
                cp_values.append(cp)
                cp_lookup.append(prev_cp)
                prev_cp = cp
            
            # Stop if we reached max CP
            if cp >= max_cp:
                break
        
        # If we didn't get enough points, add more
        if len(arrivals) < 10:
            # Add more time points with larger steps
            additional_times = np.linspace(time_points[-1] if time_points else 0, 
                                          max_time * 2, 50)
            for t in additional_times:
                cp = self.calculate_cdf(t, arrival_dist, arrival_params, lam)
                cp = max(0.0, min(1.0, cp))
                
                if cp > prev_cp:
                    arrivals.append(t)
                    cp_values.append(cp)
                    cp_lookup.append(prev_cp)
                    prev_cp = cp
                
                if cp >= max_cp or len(arrivals) >= max_customers:
                    break
        
        # Round values
        arrivals = [round(t, 2) for t in arrivals]
        cp_values = [round(cp, 5) for cp in cp_values]
        cp_lookup = [round(cp, 5) for cp in cp_lookup]
        
        return arrivals, cp_values, cp_lookup
    
    def simulate_cp_based(self, arrival_dist: str, arrival_params: Dict,
                         service_dist: str, service_params: Dict,
                         lam: float, mu: float,
                         num_servers: int = 1) -> pd.DataFrame:
        """
        Simulate until CP reaches 0.99999 using CORRECT CDF formulas.
        """
        self.reset()
        self.initialize_servers(num_servers)
        
        # Generate arrivals using correct CP calculation
        arrivals, cp_values, cp_lookup = self.generate_arrivals_cp(
            arrival_dist, arrival_params, lam, max_cp=0.99999
        )
        
        rows = []
        
        for i, (arrival_time, cp, cp_prev) in enumerate(zip(arrivals, cp_values, cp_lookup)):
            # Generate service time based on service distribution
            service_time = self.generate_service_time(service_dist, service_params, mu)
            
            # Find available server
            if num_servers == 1:
                server_available_time = self.servers[0]
                start_time = max(arrival_time, server_available_time)
                end_time = start_time + service_time
                self.servers[0] = end_time
                server_name = "S1"
            else:
                available_server = min(range(num_servers), key=lambda x: self.servers[x])
                server_available_time = self.servers[available_server]
                start_time = max(arrival_time, server_available_time)
                end_time = start_time + service_time
                self.servers[available_server] = end_time
                server_name = f"S{available_server + 1}"
            
            # Calculate metrics
            wait_time = start_time - arrival_time
            turnaround_time = end_time - arrival_time
            response_time = wait_time
            
            # Store as discrete integers
            rows.append([
                i + 1,
                int(round(arrival_time)),    # DISCRETE
                int(round(service_time)),    # DISCRETE  
                server_name,
                int(round(start_time)),      # DISCRETE
                int(round(end_time)),        # DISCRETE
                int(round(wait_time)),       # DISCRETE
                int(round(turnaround_time)), # DISCRETE
                int(round(response_time)),   # DISCRETE
                cp,                          # CP (float)
                cp_prev                      # CP_Lookup (float)
            ])
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", "Start", "End", 
            "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
        ])
        
        # Calculate metrics
        self.calculate_metrics(df, num_servers)
        
        return df
    
    def generate_service_time(self, dist_name: str, params: Dict, mu: float = 1.0) -> float:
        """Generate service time from distribution."""
        if dist_name == "Exponential":
            rate = params.get('rate', mu)
            return max(1, np.random.exponential(1/rate))
        elif dist_name == "Uniform":
            a = params.get("min", 1)
            b = params.get("max", 5)
            return max(1, random.uniform(a, b))
        elif dist_name == "Normal":
            mean = params.get("mean", 3)
            std = params.get("stddev", 1)
            service = random.normalvariate(mean, std)
            return max(1, service)
        elif dist_name == "Gamma":
            shape = params.get("shape", 2)
            scale = params.get("scale", 1)
            service = random.gammavariate(shape, scale)
            return max(1, service)
        else:
            # Default exponential
            return max(1, np.random.exponential(1/mu))
    
    def calculate_metrics(self, df: pd.DataFrame, num_servers: int):
        """Calculate performance metrics."""
        if df.empty:
            self.metrics = {}
            return
        
        max_end_time = df['End'].max()
        total_service_time = df['Service'].sum()
        
        if num_servers == 1:
            utilization = (total_service_time / max_end_time) * 100 if max_end_time > 0 else 0
        else:
            utilization = (total_service_time / (num_servers * max_end_time)) * 100 if max_end_time > 0 else 0
        
        self.metrics = {
            "utilization": utilization,
            "avg_wait": df["Wait"].mean(),
            "avg_turnaround": df["Turnaround"].mean(),
            "avg_response": df["Response"].mean(),
            "throughput": len(df) / max_end_time if max_end_time > 0 else 0,
            "total_time": max_end_time,
            "num_customers": len(df)
        }
    
    def simulate_fixed_customers(self, num_customers: int,
                                arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                num_servers: int = 1) -> pd.DataFrame:
        """
        Fixed number of customers simulation.
        """
        self.reset()
        self.initialize_servers(num_servers)
        
        rows = []
        cumulative_time = 0.0
        
        # Get lambda for CP calculation
        lam = arrival_params.get('rate', 0.5)
        if arrival_dist in ["Uniform", "Normal", "Gamma"]:
            # Estimate mean from distribution
            if arrival_dist == "Uniform":
                a = arrival_params.get("min", 0)
                b = arrival_params.get("max", 10)
                mean_inter = (a + b) / 2
            elif arrival_dist == "Normal":
                mean_inter = arrival_params.get("mean", 5)
            elif arrival_dist == "Gamma":
                shape = arrival_params.get("shape", 2)
                scale = arrival_params.get("scale", 1)
                mean_inter = shape * scale
            else:
                mean_inter = 1/lam if lam > 0 else 1
            
            if mean_inter > 0:
                lam = 1 / mean_inter
        
        for i in range(num_customers):
            # Generate interarrival time
            interarrival = self.generate_interarrival(arrival_dist, arrival_params, lam)
            
            # Calculate arrival time
            arrival_time = cumulative_time + interarrival
            cumulative_time = arrival_time
            
            # Calculate CP using CDF
            cp = self.calculate_cdf(arrival_time, arrival_dist, arrival_params, lam)
            cp = max(0.0, min(1.0, cp))
            
            # Calculate previous CP
            if i == 0:
                cp_prev = 0.0
            else:
                # Simple progression
                cp_prev = cp * (i / (i + 1))
            
            # Generate service time
            mu = service_params.get('rate', 1.0)
            service_time = self.generate_service_time(service_dist, service_params, mu)
            
            # Find available server
            if num_servers == 1:
                server_available_time = self.servers[0]
                start_time = max(arrival_time, server_available_time)
                end_time = start_time + service_time
                self.servers[0] = end_time
                server_name = "S1"
            else:
                available_server = min(range(num_servers), key=lambda x: self.servers[x])
                server_available_time = self.servers[available_server]
                start_time = max(arrival_time, server_available_time)
                end_time = start_time + service_time
                self.servers[available_server] = end_time
                server_name = f"S{available_server + 1}"
            
            # Calculate metrics
            wait_time = start_time - arrival_time
            turnaround_time = end_time - arrival_time
            response_time = wait_time
            
            # Store as discrete integers
            rows.append([
                i + 1,
                int(round(arrival_time)),    # DISCRETE
                int(round(service_time)),    # DISCRETE  
                server_name,
                int(round(start_time)),      # DISCRETE
                int(round(end_time)),        # DISCRETE
                int(round(wait_time)),       # DISCRETE
                int(round(turnaround_time)), # DISCRETE
                int(round(response_time)),   # DISCRETE
                round(cp, 5),                # CP
                round(cp_prev, 5)            # CP_Lookup
            ])
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID", "Arrival", "Service", "Server", "Start", "End", 
            "Wait", "Turnaround", "Response", "CP", "CP_Lookup"
        ])
        
        # Calculate metrics
        self.calculate_metrics(df, num_servers)
        
        return df
    
    def generate_interarrival(self, dist_name: str, params: Dict, lam: float = 0.5) -> float:
        """Generate interarrival time from distribution."""
        if dist_name in ["Poisson", "Exponential"]:
            rate = params.get('rate', lam)
            return max(0.1, np.random.exponential(1/rate))
        elif dist_name == "Uniform":
            a = params.get("min", 0)
            b = params.get("max", 10)
            return max(0.1, random.uniform(a, b))
        elif dist_name == "Normal":
            mean = params.get("mean", 5)
            std = params.get("stddev", 1)
            inter = random.normalvariate(mean, std)
            return max(0.1, inter)
        elif dist_name == "Gamma":
            shape = params.get("shape", 2)
            scale = params.get("scale", 1)
            inter = random.gammavariate(shape, scale)
            return max(0.1, inter)
        else:
            return max(0.1, np.random.exponential(1/lam))
    
    # Backward compatibility methods
    def simulate_single_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                 service_dist: str, service_params: Dict,
                                 lam: float, mu: float) -> pd.DataFrame:
        return self.simulate_cp_based(arrival_dist, arrival_params, 
                                     service_dist, service_params, 
                                     lam, mu, num_servers=1)
    
    def simulate_multi_server_cp(self, arrival_dist: str, arrival_params: Dict,
                                service_dist: str, service_params: Dict,
                                lam: float, mu: float, num_servers: int) -> pd.DataFrame:
        return self.simulate_cp_based(arrival_dist, arrival_params,
                                     service_dist, service_params,
                                     lam, mu, num_servers)
    
    def simulate_single_server_fixed(self, num_customers: int,
                                    arrival_dist: str, arrival_params: Dict,
                                    service_dist: str, service_params: Dict) -> pd.DataFrame:
        return self.simulate_fixed_customers(num_customers, arrival_dist, arrival_params,
                                            service_dist, service_params, num_servers=1)
    
    def simulate_multi_server_fixed(self, num_customers: int,
                                   arrival_dist: str, arrival_params: Dict,
                                   service_dist: str, service_params: Dict,
                                   num_servers: int) -> pd.DataFrame:
        return self.simulate_fixed_customers(num_customers, arrival_dist, arrival_params,
                                            service_dist, service_params, num_servers)
    
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
            "Simulation Duration": f"{df['End'].max():.0f}",
            "Server Utilization (%)": f"{self.metrics.get('utilization', 0):.2f}",
            "Average Service Time": f"{df['Service'].mean():.0f}",
            "Average Wait Time": f"{df['Wait'].mean():.0f}",
            "Average Turnaround Time": f"{df['Turnaround'].mean():.0f}",
            "Average Response Time": f"{df['Response'].mean():.0f}",
            "Maximum Wait Time": f"{df['Wait'].max():.0f}",
            "Minimum Wait Time": f"{df['Wait'].min():.0f}",
            "Std Deviation Wait": f"{df['Wait'].std():.0f}",
            "Throughput (customers/time)": f"{self.metrics.get('throughput', 0):.2f}"
        }
        
        return stats