"""
Probability distributions for queue simulation.
"""
import math
import random
from typing import Optional, Tuple

def exponential(rate: float) -> float:
    """Generate exponential random variable with given rate (λ)."""
    return -math.log(random.random()) / rate

def uniform(min_val: float, max_val: float) -> float:
    """Generate uniform random variable in [min_val, max_val]."""
    return min_val + random.random() * (max_val - min_val)

def normal(mean: float, stddev: float) -> float:
    """Generate normal random variable using Box-Muller transform."""
    u1 = random.random()
    u2 = random.random()
    while u1 == 0:
        u1 = random.random()
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mean + stddev * z0

def gamma(shape: float, scale: float) -> float:
    """
    Generate gamma distributed random variable.
    Uses Marsaglia and Tsang's method for shape >= 1,
    Johnk's generator for shape < 1.
    """
    if shape < 1.0:
        # Johnk's generator for shape < 1
        while True:
            u = random.random()
            v = random.random()
            if u + v <= 1.0:
                break
        x = u / (u + v)
        y = -math.log(random.random())
        return x * y * scale
    else:
        # Marsaglia and Tsang's method for shape >= 1
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            z = normal(0, 1)
            v = 1.0 + c * z
            if v <= 0:
                continue
            v = v * v * v
            u = random.random()
            
            if u < 1.0 - 0.0331 * (z * z * z * z):
                return d * v * scale
            
            if math.log(u) < 0.5 * z * z + d * (1.0 - v + math.log(v)):
                return d * v * scale

def get_scv(mean: float, variance: float) -> float:
    """Calculate squared coefficient of variation."""
    if mean == 0:
        return 0.0
    return variance / (mean * mean)

def get_distribution_params(dist_name: str, params_str: str) -> dict:
    """Parse distribution parameters from string."""
    params = {}
    
    if dist_name in ["Exponential", "Poisson"]:
        # Rate parameter
        if params_str:
            params['rate'] = float(params_str)
    
    elif dist_name == "Uniform":
        if params_str:
            if "," in params_str:
                a, b = map(float, params_str.split(","))
                params['min'] = a
                params['max'] = b
            else:
                mean = float(params_str)
                params['min'] = max(0, mean * 0.5)
                params['max'] = mean * 1.5
    
    elif dist_name == "Normal":
        if params_str:
            if "," in params_str:
                mean, stddev = map(float, params_str.split(","))
                params['mean'] = mean
                params['stddev'] = stddev
            else:
                params['stddev'] = float(params_str)
    
    elif dist_name == "Gamma":
        if params_str:
            if "," in params_str:
                shape, scale = map(float, params_str.split(","))
                params['shape'] = shape
                params['scale'] = scale
            else:
                params['shape'] = float(params_str)
    
    return params

def generate_random(dist_name: str, params: dict) -> float:
    """Generate random number from specified distribution."""
    # Ensure positive values for queueing systems
    if dist_name in ["Exponential", "Poisson"]:
        val = exponential(params.get('rate', 1.0))
    elif dist_name == "Uniform":
        val = uniform(params.get('min', 0.5), params.get('max', 1.5))
    elif dist_name == "Normal":
        val = normal(params.get('mean', 1.0), params.get('stddev', 0.2))
        val = max(0.01, val)  # Ensure positive
    elif dist_name == "Gamma":
        val = gamma(params.get('shape', 2.0), params.get('scale', 0.5))
        val = max(0.01, val)
    else:
        # Default to exponential
        val = exponential(1.0)
    
    return val