"""
Analytical formulas for queueing systems and sensitivity analysis.
"""
import math
from typing import Dict, List, Tuple, Optional
import numpy as np

class QueueAnalytics:
    """Analytical calculations for various queueing models and sensitivity analysis."""
    
    @staticmethod
    def mm1(lambda_: float, mu: float) -> Dict[str, float]:
        """
        M/M/1 queue analytical formulas.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate (μ)
        
        Returns:
        --------
        Dict with analytical metrics
        """
        if lambda_ <= 0 or mu <= 0:
            return {"error": "λ and μ must be positive numbers"}
        
        rho = lambda_ / mu
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1. λ must be < μ."}
        
        # Basic formulas for M/M/1
        p0 = 1 - rho  # Probability system empty
        l = rho / (1 - rho)  # Avg number in system
        lq = rho**2 / (1 - rho)  # Avg number in queue
        wq = rho / (mu * (1 - rho))  # Avg wait in queue
        w = wq + 1 / mu  # Avg time in system
        
        # Probability of n customers in system: Pn = (1 - ρ) * ρ^n
        def p_n(n: int) -> float:
            return (1 - rho) * (rho ** n)
        
        # Probability of waiting time > t
        def p_wait_gt_t(t: float) -> float:
            return rho * math.exp(-mu * (1 - rho) * t)
        
        results = {
            "ρ (Utilization)": rho,
            "P0 (Prob system empty)": p0,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "Server Idle (%)": (1 - rho) * 100,
            "Server Busy (%)": rho * 100,
            "P(System has ≤ 5 customers)": sum(p_n(i) for i in range(6)),
            "P(System has > 5 customers)": 1 - sum(p_n(i) for i in range(6)),
            "P(Wait > avg wait)": p_wait_gt_t(wq)
        }
        
        # Store formulas for later use if needed
        results["_formulas"] = {
            "P_n": p_n,
            "P_wait_gt_t": p_wait_gt_t
        }
        
        return results
    
    @staticmethod
    def mmc(lambda_: float, mu: float, c: int) -> Dict[str, float]:
        """
        M/M/c queue analytical formulas.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate per server (μ)
        c : int
            Number of servers
        
        Returns:
        --------
        Dict with analytical metrics
        """
        if lambda_ <= 0 or mu <= 0 or c <= 0:
            return {"error": "λ, μ, and c must be positive numbers"}
        
        rho = lambda_ / (c * mu)  # Server utilization
        r = lambda_ / mu  # Offered load
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1. λ must be < {c * mu}."}
        
        # Calculate P0 (probability all servers idle)
        sum_term = 0
        for n in range(c):
            sum_term += (r ** n) / math.factorial(n)
        
        p0_term = (r ** c) / (math.factorial(c) * (1 - rho))
        p0 = 1.0 / (sum_term + p0_term)
        
        # Calculate Lq (average number in queue)
        lq = (p0 * (r ** c) * rho) / (math.factorial(c) * ((1 - rho) ** 2))
        
        # Calculate other metrics
        wq = lq / lambda_
        w = wq + 1 / mu
        l = lambda_ * w  # Little's Law: L = λW
        
        # Probability of waiting (Erlang-C formula)
        p_wait = (p0 * (r ** c)) / (math.factorial(c) * (1 - rho))
        
        # Probability all servers busy
        p_all_busy = p_wait
        
        results = {
            "ρ (Utilization per server)": rho,
            "r (Offered load)": r,
            "P0 (Prob system empty)": p0,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "P(W > 0) (Prob of waiting)": p_wait,
            "P(All servers busy)": p_all_busy,
            "Server Idle (%)": (1 - rho) * 100,
            "System Capacity": c * mu,
            "Traffic Intensity": lambda_ / (c * mu)
        }
        
        # Additional probability calculations
        def p_n(n: int) -> float:
            """Probability of n customers in system."""
            if n < 0:
                return 0
            if n < c:
                return ((r ** n) / math.factorial(n)) * p0
            else:
                return ((r ** n) / (math.factorial(c) * (c ** (n - c)))) * p0
        
        results["P(System has ≤ 5 customers)"] = sum(p_n(i) for i in range(6))
        results["P(System has > 5 customers)"] = 1 - sum(p_n(i) for i in range(6))
        
        return results
    
    @staticmethod
    def mg1(lambda_: float, service_mean: float, service_variance: float) -> Dict[str, float]:
        """
        M/G/1 queue analytical formulas (Pollaczek-Khinchine formula).
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        service_mean : float
            Mean service time (E[S])
        service_variance : float
            Variance of service time (Var[S])
        
        Returns:
        --------
        Dict with analytical metrics
        """
        if lambda_ <= 0 or service_mean <= 0:
            return {"error": "λ and service mean must be positive"}
        
        rho = lambda_ * service_mean  # Utilization
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1"}
        
        # Pollaczek-Khinchine formula
        cs2 = service_variance / (service_mean ** 2)  # Squared coefficient of variation
        
        lq = (lambda_**2 * service_variance + rho**2) / (2 * (1 - rho))
        wq = lq / lambda_
        w = wq + service_mean
        l = lambda_ * w
        
        results = {
            "ρ (Utilization)": rho,
            "E[S] (Mean service time)": service_mean,
            "Var[S] (Service variance)": service_variance,
            "Cs² (Service SCV)": cs2,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "Server Idle (%)": (1 - rho) * 100,
            "Pollaczek-Khinchine Used": True
        }
        
        return results
    
    @staticmethod
    def gg1(lambda_: float, mu: float, 
            ca2: float = 1.0, cs2: float = 1.0) -> Dict[str, float]:
        """
        G/G/1 queue approximation (Kingman's formula).
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate (μ)
        ca2 : float
            Squared coefficient of variation for arrivals
        cs2 : float
            Squared coefficient of variation for service
        
        Returns:
        --------
        Dict with analytical metrics (approximate)
        """
        if lambda_ <= 0 or mu <= 0:
            return {"error": "λ and μ must be positive numbers"}
        
        rho = lambda_ / mu
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1"}
        
        # Kingman's approximation for G/G/1
        wq_mm1 = (rho / (mu * (1 - rho)))  # Wq for M/M/1
        wq_approx = wq_mm1 * ((ca2 + cs2) / 2)
        
        lq_approx = lambda_ * wq_approx
        w_approx = wq_approx + 1 / mu
        l_approx = lambda_ * w_approx
        
        results = {
            "ρ (Utilization)": rho,
            "Ca² (Arrival SCV)": ca2,
            "Cs² (Service SCV)": cs2,
            "L (Avg in system - approx)": l_approx,
            "Lq (Avg in queue - approx)": lq_approx,
            "W (Avg time in system - approx)": w_approx,
            "Wq (Avg wait in queue - approx)": wq_approx,
            "Wq_M/M/1 (for comparison)": wq_mm1,
            "Approximation Factor": (ca2 + cs2) / 2,
            "Note": "Results are approximate using Kingman's formula"
        }
        
        return results
    
    @staticmethod
    def ggc_approx(lambda_: float, mu: float, c: int,
                   ca2: float = 1.0, cs2: float = 1.0) -> Dict[str, float]:
        """
        G/G/c queue approximation (Allen-Cunneen approximation).
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate per server (μ)
        c : int
            Number of servers
        ca2 : float
            Squared coefficient of variation for arrivals
        cs2 : float
            Squared coefficient of variation for service
        
        Returns:
        --------
        Dict with analytical metrics (approximate)
        """
        if lambda_ <= 0 or mu <= 0 or c <= 0:
            return {"error": "λ, μ, and c must be positive numbers"}
        
        rho = lambda_ / (c * mu)
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1"}
        
        # First calculate M/M/c metrics
        mmc_results = QueueAnalytics.mmc(lambda_, mu, c)
        if "error" in mmc_results:
            return mmc_results
        
        wq_mmc = mmc_results["Wq (Avg wait in queue)"]
        
        # Allen-Cunneen approximation
        wq_approx = wq_mmc * ((ca2 + cs2) / 2)
        
        lq_approx = lambda_ * wq_approx
        w_approx = wq_approx + 1 / mu
        l_approx = lambda_ * w_approx
        
        results = {
            "ρ (Utilization per server)": rho,
            "Ca² (Arrival SCV)": ca2,
            "Cs² (Service SCV)": cs2,
            "L (Avg in system - approx)": l_approx,
            "Lq (Avg in queue - approx)": lq_approx,
            "W (Avg time in system - approx)": w_approx,
            "Wq (Avg wait in queue - approx)": wq_approx,
            "Wq_M/M/c (for comparison)": wq_mmc,
            "Approximation Factor": (ca2 + cs2) / 2,
            "Note": "Results are approximate using Allen-Cunneen formula"
        }
        
        return results
    
    @staticmethod
    def calculate_all(lambda_: float, mu: float, c: int = 1,
                      service_variance: float = None,
                      arrival_scv: float = 1.0,
                      service_scv: float = 1.0) -> Dict[str, Dict]:
        """
        Calculate all analytical metrics for comparison across different models.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate (μ)
        c : int
            Number of servers
        service_variance : float, optional
            Variance of service time for M/G/1
        arrival_scv : float
            Squared coefficient of variation for arrivals
        service_scv : float
            Squared coefficient of variation for service
        
        Returns:
        --------
        Dict with results for each queue model
        """
        results = {}
        
        # M/M/1
        results["M/M/1"] = QueueAnalytics.mm1(lambda_, mu)
        
        # M/M/c if c > 1
        if c > 1:
            results[f"M/M/{c}"] = QueueAnalytics.mmc(lambda_, mu, c)
        
        # M/G/1 if service variance provided
        if service_variance is not None:
            service_mean = 1 / mu
            results["M/G/1"] = QueueAnalytics.mg1(lambda_, service_mean, service_variance)
        
        # G/G/1 approximation
        results["G/G/1 (Approx)"] = QueueAnalytics.gg1(lambda_, mu, arrival_scv, service_scv)
        
        # G/G/c approximation if c > 1
        if c > 1:
            results[f"G/G/{c} (Approx)"] = QueueAnalytics.ggc_approx(lambda_, mu, c, 
                                                                     arrival_scv, service_scv)
        
        return results
    
    @staticmethod
    def calculate_sensitivity(lambda_range: List[float], mu: float, c: int = 1,
                              queue_type: str = "MM1", 
                              ca2: float = 1.0, cs2: float = 1.0) -> Dict[str, List]:
        """
        Calculate sensitivity metrics over a range of lambda values.
        
        Parameters:
        -----------
        lambda_range : List[float]
            Range of λ values to analyze
        mu : float
            Service rate (μ)
        c : int
            Number of servers
        queue_type : str
            Type of queue: "MM1", "MMC", "MG1", "GG1", "GGC"
        ca2 : float
            Squared coefficient of variation for arrivals (for G/G models)
        cs2 : float
            Squared coefficient of variation for service (for G/G models)
        
        Returns:
        --------
        Dict with lists of metrics for each λ value
        """
        results = {
            'lambda': lambda_range,
            'rho': [],
            'wq': [],
            'w': [],
            'lq': [],
            'l': [],
            'utilization': [],
            'status': []
        }
        
        for lam in lambda_range:
            rho = lam / (c * mu)
            results['rho'].append(rho)
            
            # Check stability
            if rho >= 1:
                results['wq'].append(float('inf'))
                results['w'].append(float('inf'))
                results['lq'].append(float('inf'))
                results['l'].append(float('inf'))
                results['utilization'].append(100.0)
                results['status'].append('Unstable')
                continue
            
            # Calculate based on queue type
            if queue_type == "MM1" or (queue_type == "MMC" and c == 1):
                # M/M/1 formulas
                wq = rho / (mu * (1 - rho))
                w = wq + 1 / mu
                lq = lam * wq
                l = lam * w
                
            elif queue_type == "MMC" and c > 1:
                # M/M/c formulas
                r = lam / mu
                sum_part = sum([(r**k) / math.factorial(k) for k in range(c)])
                last_term = (r**c) / (math.factorial(c) * (1 - rho))
                p0 = 1.0 / (sum_part + last_term)
                
                lq = (p0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
                wq = lq / lam
                w = wq + 1 / mu
                l = lq + r
                
            elif queue_type == "MG1":
                # M/G/1 approximation (using Cs² = 1 for M/M/1 as baseline)
                wq_mm1 = rho / (mu * (1 - rho))
                wq = wq_mm1 * ((1 + cs2) / 2)  # Adjust for service time distribution
                w = wq + 1 / mu
                lq = lam * wq
                l = lam * w
                
            elif queue_type == "GG1":
                # G/G/1 approximation
                wq_mm1 = rho / (mu * (1 - rho))
                wq = wq_mm1 * ((ca2 + cs2) / 2)
                w = wq + 1 / mu
                lq = lam * wq
                l = lam * w
                
            elif queue_type == "GGC" and c > 1:
                # G/G/c approximation
                # First calculate M/M/c
                r = lam / mu
                sum_part = sum([(r**k) / math.factorial(k) for k in range(c)])
                last_term = (r**c) / (math.factorial(c) * (1 - rho))
                p0 = 1.0 / (sum_part + last_term)
                lq_mmc = (p0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
                wq_mmc = lq_mmc / lam
                
                # Apply Allen-Cunneen adjustment
                wq = wq_mmc * ((ca2 + cs2) / 2)
                w = wq + 1 / mu
                lq = lam * wq
                l = lam * w
                
            else:
                # Default to M/M/1
                wq = rho / (mu * (1 - rho))
                w = wq + 1 / mu
                lq = lam * wq
                l = lam * w
            
            results['wq'].append(wq)
            results['w'].append(w)
            results['lq'].append(lq)
            results['l'].append(l)
            results['utilization'].append(rho * 100)
            results['status'].append('Stable')
        
        return results
    
    @staticmethod
    def calculate_optimal_servers(lambda_: float, mu: float, 
                                  target_wq: float = None,
                                  target_rho: float = 0.8) -> Dict:
        """
        Calculate optimal number of servers based on targets.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate per server (μ)
        target_wq : float, optional
            Target average wait time in queue
        target_rho : float
            Target server utilization (default 0.8)
        
        Returns:
        --------
        Dict with recommendations
        """
        if lambda_ <= 0 or mu <= 0:
            return {"error": "λ and μ must be positive numbers"}
        
        # Minimum servers needed for stability
        min_servers = math.ceil(lambda_ / mu)
        
        results = {
            "Minimum servers for stability": min_servers,
            "Target utilization": target_rho,
            "Recommendations": []
        }
        
        # Check different numbers of servers
        for c in range(min_servers, min_servers + 6):
            rho = lambda_ / (c * mu)
            
            if rho >= 1:
                continue
            
            # Calculate M/M/c metrics
            mmc_result = QueueAnalytics.mmc(lambda_, mu, c)
            if "error" in mmc_result:
                continue
            
            wq = mmc_result["Wq (Avg wait in queue)"]
            utilization = mmc_result["ρ (Utilization per server)"]
            
            recommendation = {
                "Servers": c,
                "Utilization": round(utilization, 4),
                "Avg Wait (Wq)": round(wq, 4),
                "Cost Efficiency": round(utilization / c, 4)
            }
            
            # Check against targets
            if target_wq is not None and wq <= target_wq:
                recommendation["Meets Wait Target"] = "Yes"
            else:
                recommendation["Meets Wait Target"] = "No"
            
            if utilization <= target_rho:
                recommendation["Meets Utilization Target"] = "Yes"
            else:
                recommendation["Meets Utilization Target"] = "No"
            
            results["Recommendations"].append(recommendation)
        
        # Find best based on utilization target
        best_by_utilization = None
        for rec in results["Recommendations"]:
            if rec["Meets Utilization Target"] == "Yes":
                if best_by_utilization is None or rec["Utilization"] > best_by_utilization["Utilization"]:
                    best_by_utilization = rec
        
        if best_by_utilization:
            results["Best by Utilization Target"] = f"c = {best_by_utilization['Servers']} (Utilization: {best_by_utilization['Utilization']:.2%})"
        
        # Find best based on wait time target
        if target_wq is not None:
            best_by_wait = None
            for rec in results["Recommendations"]:
                if rec["Meets Wait Target"] == "Yes":
                    if best_by_wait is None or rec["Avg Wait (Wq)"] < best_by_wait["Avg Wait (Wq)"]:
                        best_by_wait = rec
            
            if best_by_wait:
                results["Best by Wait Target"] = f"c = {best_by_wait['Servers']} (Wq: {best_by_wait['Avg Wait (Wq)']:.4f})"
        
        return results
    
    @staticmethod
    def calculate_cost_analysis(lambda_: float, mu: float, 
                                server_cost: float = 100.0,
                                wait_cost: float = 50.0) -> Dict:
        """
        Perform cost analysis for different numbers of servers.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate per server (μ)
        server_cost : float
            Cost per server per time unit
        wait_cost : float
            Cost per customer per time unit of waiting
        
        Returns:
        --------
        Dict with cost analysis
        """
        if lambda_ <= 0 or mu <= 0:
            return {"error": "λ and μ must be positive numbers"}
        
        min_servers = math.ceil(lambda_ / mu)
        
        results = {
            "Parameters": {
                "λ": lambda_,
                "μ": mu,
                "Server Cost": server_cost,
                "Wait Cost": wait_cost
            },
            "Cost Analysis": []
        }
        
        # Analyze different numbers of servers
        for c in range(min_servers, min_servers + 6):
            rho = lambda_ / (c * mu)
            
            if rho >= 1:
                continue
            
            # Calculate M/M/c metrics
            mmc_result = QueueAnalytics.mmc(lambda_, mu, c)
            if "error" in mmc_result:
                continue
            
            lq = mmc_result["Lq (Avg in queue)"]
            wq = mmc_result["Wq (Avg wait in queue)"]
            
            # Calculate costs
            total_server_cost = c * server_cost
            total_wait_cost = lq * wait_cost
            total_cost = total_server_cost + total_wait_cost
            
            cost_analysis = {
                "Servers (c)": c,
                "Utilization": round(rho, 4),
                "Lq": round(lq, 4),
                "Wq": round(wq, 4),
                "Server Cost": round(total_server_cost, 2),
                "Wait Cost": round(total_wait_cost, 2),
                "Total Cost": round(total_cost, 2),
                "Cost per Customer": round(total_cost / lambda_, 4)
            }
            
            results["Cost Analysis"].append(cost_analysis)
        
        # Find optimal number of servers (minimum total cost)
        if results["Cost Analysis"]:
            optimal = min(results["Cost Analysis"], key=lambda x: x["Total Cost"])
            results["Optimal Servers"] = optimal["Servers (c)"]
            results["Minimum Total Cost"] = optimal["Total Cost"]
            results["Optimal Utilization"] = optimal["Utilization"]
        
        return results
    
    @staticmethod
    def generate_queue_summary(lambda_: float, mu: float, c: int = 1) -> str:
        """
        Generate a formatted summary of queue performance.
        
        Parameters:
        -----------
        lambda_ : float
            Arrival rate (λ)
        mu : float
            Service rate (μ)
        c : int
            Number of servers
        
        Returns:
        --------
        Formatted summary string
        """
        if c == 1:
            results = QueueAnalytics.mm1(lambda_, mu)
            queue_type = "M/M/1"
        else:
            results = QueueAnalytics.mmc(lambda_, mu, c)
            queue_type = f"M/M/{c}"
        
        if "error" in results:
            return f"ERROR: {results['error']}"
        
        summary = []
        summary.append(f"QUEUE ANALYSIS SUMMARY - {queue_type}")
        summary.append("=" * 50)
        summary.append(f"Parameters: λ = {lambda_}, μ = {mu}, c = {c}")
        summary.append("")
        summary.append("PERFORMANCE METRICS:")
        summary.append("-" * 30)
        
        for key, value in results.items():
            if not key.startswith("_") and not callable(value):
                if isinstance(value, float):
                    summary.append(f"{key:25}: {value:10.4f}")
                else:
                    summary.append(f"{key:25}: {value:10}")
        
        # Add stability check
        rho = lambda_ / (c * mu)
        if rho < 0.7:
            stability = "Excellent (ρ < 0.7)"
        elif rho < 0.85:
            stability = "Good (0.7 ≤ ρ < 0.85)"
        elif rho < 0.95:
            stability = "Moderate (0.85 ≤ ρ < 0.95)"
        else:
            stability = "Poor (ρ ≥ 0.95)"
        
        summary.append("")
        summary.append("STABILITY ASSESSMENT:")
        summary.append("-" * 30)
        summary.append(f"Utilization (ρ): {rho:.4f}")
        summary.append(f"Stability Level: {stability}")
        
        # Add capacity information
        summary.append("")
        summary.append("CAPACITY INFORMATION:")
        summary.append("-" * 30)
        summary.append(f"System Capacity: {c * mu:.2f} customers/time unit")
        summary.append(f"Current Load: {lambda_:.2f} customers/time unit")
        summary.append(f"Spare Capacity: {c * mu - lambda_:.2f} customers/time unit")
        
        return "\n".join(summary)
    
    @staticmethod
    def compare_queues(lambda_values: List[float], mu: float, c: int = 1) -> Dict:
        """
        Compare queue performance for different arrival rates.
        
        Parameters:
        -----------
        lambda_values : List[float]
            Different arrival rates to compare
        mu : float
            Service rate (μ)
        c : int
            Number of servers
        
        Returns:
        --------
        Dict with comparison results
        """
        comparison = {
            "λ values": lambda_values,
            "ρ values": [],
            "Wq values": [],
            "L values": [],
            "Stability": []
        }
        
        for lam in lambda_values:
            rho = lam / (c * mu)
            comparison["ρ values"].append(rho)
            
            if rho >= 1:
                comparison["Wq values"].append(float('inf'))
                comparison["L values"].append(float('inf'))
                comparison["Stability"].append("Unstable")
                continue
            
            if c == 1:
                results = QueueAnalytics.mm1(lam, mu)
            else:
                results = QueueAnalytics.mmc(lam, mu, c)
            
            if "error" in results:
                comparison["Wq values"].append(float('nan'))
                comparison["L values"].append(float('nan'))
                comparison["Stability"].append("Error")
            else:
                comparison["Wq values"].append(results["Wq (Avg wait in queue)"])
                comparison["L values"].append(results["L (Avg in system)"])
                
                if rho < 0.7:
                    stability = "Excellent"
                elif rho < 0.85:
                    stability = "Good"
                elif rho < 0.95:
                    stability = "Moderate"
                else:
                    stability = "Poor"
                
                comparison["Stability"].append(stability)
        
        return comparison

# Helper functions for common calculations
def calculate_scv(mean: float, variance: float) -> float:
    """Calculate squared coefficient of variation."""
    if mean == 0:
        return 0.0
    return variance / (mean ** 2)

def calculate_erlang_b(a: float, n: int) -> float:
    """
    Calculate Erlang-B formula (blocking probability for M/M/n/n queue).
    
    Parameters:
    -----------
    a : float
        Offered traffic in Erlangs (a = λ/μ)
    n : int
        Number of servers (and no waiting room)
    
    Returns:
    --------
    Blocking probability
    """
    numerator = (a ** n) / math.factorial(n)
    denominator = sum((a ** k) / math.factorial(k) for k in range(n + 1))
    return numerator / denominator

def calculate_erlang_c(a: float, n: int) -> float:
    """
    Calculate Erlang-C formula (probability of waiting in M/M/n queue).
    
    Parameters:
    -----------
    a : float
        Offered traffic in Erlangs (a = λ/μ)
    n : int
        Number of servers
    
    Returns:
    --------
    Probability of waiting
    """
    numerator = (a ** n) / math.factorial(n) * (n / (n - a))
    denominator = sum((a ** k) / math.factorial(k) for k in range(n)) + numerator
    return numerator / denominator

def calculate_little_law(lambda_: float, w: float) -> float:
    """Calculate L using Little's Law: L = λW."""
    return lambda_ * w

def calculate_wait_from_lq(lambda_: float, lq: float) -> float:
    """Calculate Wq from Lq: Wq = Lq/λ."""
    return lq / lambda_ if lambda_ > 0 else 0

def validate_parameters(lambda_: float, mu: float, c: int = 1) -> Tuple[bool, str]:
    """Validate queue parameters."""
    if lambda_ <= 0:
        return False, "Arrival rate (λ) must be positive"
    if mu <= 0:
        return False, "Service rate (μ) must be positive"
    if c <= 0:
        return False, "Number of servers (c) must be positive"
    
    rho = lambda_ / (c * mu)
    if rho >= 1:
        return False, f"System unstable: ρ = {rho:.4f} ≥ 1. λ must be < {c * mu}"
    
    return True, "Parameters valid"