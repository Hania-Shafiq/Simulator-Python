"""
Analytical formulas for queueing systems and sensitivity analysis.
"""
import math
from typing import Dict, List, Tuple, Optional
import numpy as np

class QueueAnalytics:
    """Analytical calculations for various queueing models and sensitivity analysis."""
    
    @staticmethod
    def get_scv_for_distribution(dist_name: str, params: dict = None) -> float:
        """Calculate SCV (Squared Coefficient of Variation) for a distribution."""
        if dist_name in ["Exponential", "Poisson"]:
            return 1.0  # Markovian: SCV = 1
        elif dist_name == "Uniform":
            if params and 'min' in params and 'max' in params:
                a = params['min']
                b = params['max']
                mean = (a + b) / 2
                variance = ((b - a) ** 2) / 12
                return variance / (mean ** 2) if mean != 0 else 0
            return 1.0/3.0  # Approximate for uniform
        elif dist_name == "Normal":
            if params and 'mean' in params and 'stddev' in params:
                mean = params['mean']
                stddev = params['stddev']
                return (stddev ** 2) / (mean ** 2) if mean != 0 else 0
            return 0.25  # Assuming std = 0.5 * mean
        elif dist_name == "Gamma":
            if params and 'shape' in params:
                shape = params['shape']
                return 1.0 / shape if shape > 0 else 1.0
            return 0.5  # Default for Gamma(shape=2)
        return 1.0  # Default to Markovian

    @staticmethod
    def get_queue_type_analytical(lambda_: float, mu: float, c: int,
                                  arrival_dist: str, service_dist: str,
                                  arrival_params: dict = None,
                                  service_params: dict = None) -> Dict:
        """
        Unified method to get analytical results based on actual distributions.
        """
        # Calculate SCV for arrivals and service
        ca2 = QueueAnalytics.get_scv_for_distribution(arrival_dist, arrival_params)
        cs2 = QueueAnalytics.get_scv_for_distribution(service_dist, service_params)
        
        rho = lambda_ / (c * mu)
        
        if rho >= 1:
            return {"error": f"Unstable system: ρ = {rho:.4f} ≥ 1"}
        
        # Determine if Markovian
        is_markovian_arrival = arrival_dist in ["Exponential", "Poisson"]
        is_markovian_service = service_dist in ["Exponential", "Poisson"]
        
        # Choose appropriate analytical method
        if is_markovian_arrival and is_markovian_service:
            # M/M/c queue
            if c == 1:
                results = QueueAnalytics.mm1(lambda_, mu)
                results["Queue Type"] = "M/M/1"
            else:
                results = QueueAnalytics.mmc(lambda_, mu, c)
                results["Queue Type"] = f"M/M/{c}"
        elif is_markovian_arrival and not is_markovian_service:
            # M/G/c queue
            if c == 1:
                # M/G/1
                service_mean = 1 / mu
                service_variance = service_mean**2 * cs2  # Var = mean² * SCV
                results = QueueAnalytics.mg1(lambda_, service_mean, service_variance)
                results["Queue Type"] = "M/G/1"
            else:
                # M/G/c - use G/G/c approximation with Ca²=1
                results = QueueAnalytics.ggc_approx(lambda_, mu, c, ca2=1.0, cs2=cs2)
                results["Queue Type"] = f"M/G/{c} (Approximation)"
        elif not is_markovian_arrival and is_markovian_service:
            # G/M/c queue
            if c == 1:
                # G/M/1 - use G/G/1 approximation with Cs²=1
                results = QueueAnalytics.gg1(lambda_, mu, ca2=ca2, cs2=1.0)
                results["Queue Type"] = "G/M/1 (Approximation)"
            else:
                # G/M/c - use G/G/c approximation with Cs²=1
                results = QueueAnalytics.ggc_approx(lambda_, mu, c, ca2=ca2, cs2=1.0)
                results["Queue Type"] = f"G/M/{c} (Approximation)"
        else:
            # G/G/c queue
            if c == 1:
                results = QueueAnalytics.gg1(lambda_, mu, ca2, cs2)
                results["Queue Type"] = "G/G/1 (Approximation)"
            else:
                results = QueueAnalytics.ggc_approx(lambda_, mu, c, ca2, cs2)
                results["Queue Type"] = f"G/G/{c} (Approximation)"
        
        # Add SCV information
        results["SCV Arrival (Ca²)"] = ca2
        results["SCV Service (Cs²)"] = cs2
        
        # Add distribution info
        results["Arrival Distribution"] = arrival_dist
        results["Service Distribution"] = service_dist
        
        # Mark if exact or approximate
        if "Approximation" not in results.get("Queue Type", ""):
            results["Calculation Method"] = "Exact Formula"
        else:
            results["Calculation Method"] = "Approximation Formula"
        
        return results

    @staticmethod
    def calculate_for_distributions(lambda_: float, mu: float, c: int,
                                   arrival_dist: str, service_dist: str,
                                   arrival_params: dict = None,
                                   service_params: dict = None) -> Dict:
        """
        Calculate all analytical metrics for given distributions.
        """
        return QueueAnalytics.get_queue_type_analytical(
            lambda_, mu, c, arrival_dist, service_dist, arrival_params, service_params
        )
    
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
        
        results = {
            "ρ (Utilization)": rho,
            "P0 (Prob system empty)": p0,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "Server Idle (%)": (1 - rho) * 100,
            "Server Busy (%)": rho * 100,
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
        
        results = {
            "ρ (Utilization per server)": rho,
            "P0 (Prob system empty)": p0,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "P(W > 0) (Prob of waiting)": p_wait,
            "Server Idle (%)": (1 - rho) * 100,
        }
        
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
            "L (Avg in system)": l_approx,
            "Lq (Avg in queue)": lq_approx,
            "W (Avg time in system)": w_approx,
            "Wq (Avg wait in queue)": wq_approx,
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
            "L (Avg in system)": l_approx,
            "Lq (Avg in queue)": lq_approx,
            "W (Avg time in system)": w_approx,
            "Wq (Avg wait in queue)": wq_approx,
        }
        
        return results

    @staticmethod
    def calculate_sensitivity(lambda_range: List[float], mu: float, c: int = 1,
                              arrival_dist: str = "Exponential",
                              service_dist: str = "Exponential",
                              arrival_params: dict = None,
                              service_params: dict = None,
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
        arrival_dist : str
            Arrival distribution name
        service_dist : str
            Service distribution name
        arrival_params : dict
            Arrival distribution parameters
        service_params : dict
            Service distribution parameters
        ca2 : float
            Squared coefficient of variation for arrivals (for G/G models)
        cs2 : float
            Squared coefficient of variation for service (for G/G models)
        
        Returns:
        --------
        Dict with lists of metrics for each λ value
        """
        # Calculate SCV if not provided
        if ca2 == 1.0 and arrival_dist:
            ca2 = QueueAnalytics.get_scv_for_distribution(arrival_dist, arrival_params)
        if cs2 == 1.0 and service_dist:
            cs2 = QueueAnalytics.get_scv_for_distribution(service_dist, service_params)
        
        results = {
            'lambda': lambda_range,
            'rho': [],
            'wq': [],
            'w': [],
            'lq': [],
            'l': [],
            'utilization': [],
            'status': [],
            'ca2': [ca2] * len(lambda_range),
            'cs2': [cs2] * len(lambda_range)
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
            
            # Determine formula based on distributions
            is_markovian_arrival = arrival_dist in ["Exponential", "Poisson"]
            is_markovian_service = service_dist in ["Exponential", "Poisson"]
            
            if is_markovian_arrival and is_markovian_service:
                # M/M/c formulas
                if c == 1:
                    # M/M/1
                    wq = rho / (mu * (1 - rho))
                    lq = lam * wq
                else:
                    # M/M/c
                    r = lam / mu
                    sum_part = sum([(r**k) / math.factorial(k) for k in range(c)])
                    last_term = (r**c) / (math.factorial(c) * (1 - rho))
                    p0 = 1.0 / (sum_part + last_term)
                    lq = (p0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
                    wq = lq / lam
            else:
                # Use G/G/c approximation with appropriate SCV values
                if c == 1:
                    # G/G/1 - Kingman's approximation
                    wq_mm1 = rho / (mu * (1 - rho))
                    wq = wq_mm1 * ((ca2 + cs2) / 2)
                    lq = lam * wq
                else:
                    # G/G/c - Allen-Cunneen approximation
                    # First calculate M/M/c as baseline
                    r = lam / mu
                    sum_part = sum([(r**k) / math.factorial(k) for k in range(c)])
                    last_term = (r**c) / (math.factorial(c) * (1 - rho))
                    p0 = 1.0 / (sum_part + last_term)
                    lq_mmc = (p0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
                    wq_mmc = lq_mmc / lam
                    wq = wq_mmc * ((ca2 + cs2) / 2)
                    lq = lam * wq
            
            w = wq + 1 / mu
            l = lam * w
            
            results['wq'].append(wq)
            results['w'].append(w)
            results['lq'].append(lq)
            results['l'].append(l)
            results['utilization'].append(rho * 100)
            results['status'].append('Stable')
        
        return results

# Helper functions
def calculate_scv(mean: float, variance: float) -> float:
    """Calculate squared coefficient of variation."""
    if mean == 0:
        return 0.0
    return variance / (mean ** 2)