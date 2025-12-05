"""
Analytical formulas for queueing systems.
"""
import math
from typing import Dict, Tuple, Optional

class QueueAnalytics:
    """Analytical calculations for various queueing models."""
    
    @staticmethod
    def mm1(lambda_: float, mu: float) -> Dict[str, float]:
        """M/M/1 queue analytical formulas."""
        rho = lambda_ / mu
        
        if rho >= 1:
            return {"error": "Unstable system (ρ ≥ 1)"}
        
        results = {
            "ρ (Utilization)": rho,
            "L (Avg in system)": rho / (1 - rho),
            "Lq (Avg in queue)": rho**2 / (1 - rho),
            "W (Avg time in system)": 1 / (mu - lambda_),
            "Wq (Avg wait in queue)": rho / (mu * (1 - rho)),
            "P0 (Prob system empty)": 1 - rho
        }
        
        # Additional metrics
        results["P(System has n customers)"] = lambda n: (1 - rho) * (rho**n)
        
        return results
    
    @staticmethod
    def mmc(lambda_: float, mu: float, c: int) -> Dict[str, float]:
        """M/M/c queue analytical formulas."""
        rho = lambda_ / (c * mu)
        r = lambda_ / mu
        
        if rho >= 1:
            return {"error": "Unstable system (ρ ≥ 1)"}
        
        # Calculate P0 (probability system empty)
        sum_term = sum((r**k) / math.factorial(k) for k in range(c))
        p0_term = (r**c) / (math.factorial(c) * (1 - rho))
        p0 = 1.0 / (sum_term + p0_term)
        
        # Calculate Lq (average number in queue)
        lq = (p0 * (r**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
        
        # Calculate other metrics
        wq = lq / lambda_
        w = wq + 1 / mu
        l = lambda_ * w
        
        results = {
            "ρ (Utilization)": rho,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "P0 (Prob system empty)": p0
        }
        
        return results
    
    @staticmethod
    def mg1(lambda_: float, service_mean: float, service_variance: float) -> Dict[str, float]:
        """M/G/1 queue analytical formulas (Pollaczek-Khinchine)."""
        rho = lambda_ * service_mean
        
        if rho >= 1:
            return {"error": "Unstable system (ρ ≥ 1)"}
        
        # Pollaczek-Khinchine formula
        cs2 = service_variance / (service_mean**2)  # Squared coefficient of variation
        
        lq = (lambda_**2 * service_variance + rho**2) / (2 * (1 - rho))
        wq = lq / lambda_
        w = wq + service_mean
        l = lambda_ * w
        
        results = {
            "ρ (Utilization)": rho,
            "L (Avg in system)": l,
            "Lq (Avg in queue)": lq,
            "W (Avg time in system)": w,
            "Wq (Avg wait in queue)": wq,
            "Cs² (Service SCV)": cs2
        }
        
        return results
    
    @staticmethod
    def gg1(lambda_: float, mu: float, 
            ca2: float = 1.0, cs2: float = 1.0) -> Dict[str, float]:
        """G/G/1 queue approximation (Kingman's formula)."""
        rho = lambda_ / mu
        
        if rho >= 1:
            return {"error": "Unstable system (ρ ≥ 1)"}
        
        # Kingman's approximation for G/G/1
        wq_approx = (rho / (mu * (1 - rho))) * ((ca2 + cs2) / 2)
        lq_approx = lambda_ * wq_approx
        w_approx = wq_approx + 1 / mu
        l_approx = lambda_ * w_approx
        
        results = {
            "ρ (Utilization)": rho,
            "L (Avg in system - approx)": l_approx,
            "Lq (Avg in queue - approx)": lq_approx,
            "W (Avg time in system - approx)": w_approx,
            "Wq (Avg wait in queue - approx)": wq_approx,
            "Ca² (Arrival SCV)": ca2,
            "Cs² (Service SCV)": cs2
        }
        
        return results
    
    @staticmethod
    def calculate_all(lambda_: float, mu: float, c: int = 1,
                      service_variance: float = None,
                      arrival_scv: float = 1.0,
                      service_scv: float = 1.0) -> Dict[str, Dict]:
        """Calculate all analytical metrics for comparison."""
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
        
        return results