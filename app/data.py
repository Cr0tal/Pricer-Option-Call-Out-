# app/data.py
from __future__ import annotations

from datetime import date, timedelta
from dataclasses import dataclass
import numpy as np
import pandas as pd
import yfinance as yf

@dataclass
class MarketData:
    spot: float
    hist_vol: float | None
    dividend_yield: float | None

def fetch_market_data(ticker: str, lookback_days: int = 365) -> MarketData:
    
    tkr = yf.Ticker(ticker)
    hist = tkr.history(period=f"{lookback_days}d")
    if hist is None or hist.empty:
        raise ValueError(f"No history returned for {ticker}")
    close = hist["Close"].dropna()
    spot = float(close.iloc[-1])

    # Volatilité Historique 
    rets = close.pct_change().dropna()
    vol = float(rets.std() * np.sqrt(252)) if not rets.empty else None

    # Approximation de la rentabilité du Dividende
    try:
        divs = tkr.dividends
        if divs is not None and not divs.empty:
            last_year = date.today() - timedelta(days=365)
            ttm = divs[divs.index.date >= last_year].sum()
            dividend_yield = float(ttm / spot) if spot > 0 and ttm > 0 else 0.0
        else:
            dividend_yield = 0.0
    except Exception:
        dividend_yield = 0.0

    return MarketData(spot=spot, hist_vol=vol, dividend_yield=dividend_yield)