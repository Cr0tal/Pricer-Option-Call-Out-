# app/black_scholes.py
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Literal, Dict

from scipy.stats import norm

OptionType = Literal["call", "put"]

@dataclass
class BSInputs:
    S: float           # Spot price
    K: float           # Strike
    T: float           # Year fraction to maturity
    r: float           # Risk-free rate (annualized, continuous/simple approx OK)
    q: float = 0.0     # Continuous dividend yield
    sigma: float = 0.2 # Volatility (annualized)

def _d1_d2(S: float, K: float, T: float, r: float, q: float, sigma: float):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        # Avoid invalid math; handle at price() level
        return float("nan"), float("nan")
    vol_sqrt_T = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / vol_sqrt_T
    d2 = d1 - vol_sqrt_T
    return d1, d2

def price(inputs: BSInputs, option_type: OptionType = "call") -> float:
    S, K, T, r, q, sigma = inputs.S, inputs.K, inputs.T, inputs.r, inputs.q, inputs.sigma
    if T <= 0:
        # At expiry, option value equals intrinsic value
        if option_type == "call":
            return max(S - K, 0.0)
        return max(K - S, 0.0)
    if sigma <= 0 or S <= 0 or K <= 0:
        return float("nan")
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    if option_type == "call":
        return S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)

def greeks(inputs: BSInputs) -> Dict[str, float]:
    S, K, T, r, q, sigma = inputs.S, inputs.K, inputs.T, inputs.r, inputs.q, inputs.sigma
    # Handle T -> 0 separately to avoid div by zero
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {k: float("nan") for k in ["delta_call", "delta_put", "gamma", "vega", "theta_call", "theta_put", "rho_call", "rho_put"]}
    d1, d2 = _d1_d2(S, K, T, r, q, sigma)
    pdf_d1 = math.exp(-0.5 * d1 * d1) / math.sqrt(2.0 * math.pi)
    disc_r = math.exp(-r * T)
    disc_q = math.exp(-q * T)

    delta_call = disc_q * norm.cdf(d1)
    delta_put = disc_q * (norm.cdf(d1) - 1.0)
    gamma = (disc_q * pdf_d1) / (S * sigma * math.sqrt(T))
    vega = S * disc_q * pdf_d1 * math.sqrt(T)           # per 1.0 of vol
    theta_call = (-(S * disc_q * pdf_d1 * sigma) / (2 * math.sqrt(T))
                  - r * K * disc_r * norm.cdf(d2)
                  + q * S * disc_q * norm.cdf(d1))
    theta_put = (-(S * disc_q * pdf_d1 * sigma) / (2 * math.sqrt(T))
                 + r * K * disc_r * norm.cdf(-d2)
                 - q * S * disc_q * norm.cdf(-d1))
    rho_call = K * T * disc_r * norm.cdf(d2)
    rho_put = -K * T * disc_r * norm.cdf(-d2)

    return {
        "delta_call": delta_call,
        "delta_put": delta_put,
        "gamma": gamma,
        "vega": vega,
        "theta_call": theta_call,
        "theta_put": theta_put,
        "rho_call": rho_call,
        "rho_put": rho_put,
    }