# app/implied_vol.py
from __future__ import annotations
import math
from typing import Literal, Optional

# --- Imports robustes (package ou script direct) ---
if __package__ is None or __package__ == "":
    import sys, pathlib
    root = pathlib.Path(__file__).resolve().parents[1]  # .../option_pricer_flask
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from app.black_scholes import BSInputs, price
else:
    from .black_scholes import BSInputs, price

from scipy.optimize import brentq

OptionType = Literal["call", "put"]

def implied_vol_bs(
    market_price: float, S: float, K: float, T: float, r: float, q: float = 0.0,
    option_type: OptionType = "call", vol_lower: float = 1e-6, vol_upper: float = 5.0,
) -> Optional[float]:
    """Compute Black–Scholes implied volatility via Brent's method."""
    if T <= 0 or S <= 0 or K <= 0:
        return None

    def f(sig: float) -> float:
        return price(BSInputs(S, K, T, r, q, sig), option_type) - market_price

    try:
        iv = brentq(f, vol_lower, vol_upper, maxiter=200, xtol=1e-12)
        if not math.isfinite(iv) or iv <= 0:
            return None
        return float(iv)
    except ValueError:
        return None

if __name__ == "__main__":
    # Petit test si lancé directement
    mp = 10.0
    S, K, T, r, q = 100.0, 100.0, 0.5, 0.02, 0.0
    iv = implied_vol_bs(mp, S, K, T, r, q, option_type="call")
    print("Test implied vol:", iv)
