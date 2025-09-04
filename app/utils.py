# app/utils.py
from __future__ import annotations

from datetime import datetime, date

def year_fraction(maturity_date: date, today: date | None = None) -> float:
    """ACT/365F year fraction between today and maturity_date."""
    if today is None:
        today = date.today()
    delta_days = (maturity_date - today).days
    return max(delta_days, 0) / 365.0