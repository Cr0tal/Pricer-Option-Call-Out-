# app/monte_carlo.py
from __future__ import annotations
import numpy as np
from typing import Literal

OptionType = Literal["call", "put"]

def price_mc(
    S0: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
    n_paths: int = 10000,
    n_steps: int = 1,
    rng_seed: int | None = 42,
    option_type: OptionType = "call",
) -> float:
    """Monte Carlo pricing under risk-neutral GBM.
    If n_steps == 1, uses exact terminal distribution; else uses Euler steps.
    Returns discounted expected payoff.
    """
    if T <= 0:
        return max(S0 - K, 0.0) if option_type == "call" else max(K - S0, 0.0)
    rng = np.random.default_rng(rng_seed)
    if n_steps <= 1:
        Z = rng.standard_normal(n_paths)
        drift = (r - q - 0.5 * sigma**2) * T
        diffusion = sigma * np.sqrt(T) * Z
        ST = S0 * np.exp(drift + diffusion)
    else:
        dt = T / n_steps
        # Simulate log Euler steps
        Z = rng.standard_normal((n_paths, n_steps))
        increments = (r - q - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
        log_ST = np.log(S0) + increments.sum(axis=1)
        ST = np.exp(log_ST)

    if option_type == "call":
        payoff = np.maximum(ST - K, 0.0)
    else:
        payoff = np.maximum(K - ST, 0.0)

    return float(np.exp(-r * T) * payoff.mean())