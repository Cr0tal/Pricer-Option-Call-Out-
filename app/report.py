# app/report.py
from __future__ import annotations
import io
from typing import Dict, Any, Literal

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import matplotlib
matplotlib.use("Agg")  # Backend non interactif pour serveur
import matplotlib.pyplot as plt
import numpy as np

OptionType = Literal["call", "put"]

def _payoff_points(option_type: OptionType, K: float, S_min: float, S_max: float, n: int = 200):
    S = np.linspace(S_min, S_max, n)
    payoff = np.maximum(S - K, 0.0) if option_type == "call" else np.maximum(K - S, 0.0)
    return S, payoff

def _plot_payoff_png(option_type: OptionType, K: float, S0: float) -> bytes:
    S_min = max(0.0, min(S0, K) * 0.2)
    S_max = max(S0, K) * 1.8 + 1e-6
    S, payoff = _payoff_points(option_type, K, S_min, S_max, n=300)
    fig, ax = plt.subplots()
    ax.plot(S, payoff, linewidth=2.0)
    ax.set_xlabel("Underlying Price at Maturity (S_T)")
    ax.set_ylabel("Payoff")
    ax.set_title(f"Payoff - {option_type.capitalize()} (K={K:.2f})")
    ax.grid(True, linestyle=":", linewidth=0.5)
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    return buf.getvalue()

def build_pdf_report(output_path: str, inputs: Dict[str, Any], results: Dict[str, Any], option_type: OptionType) -> str:
    """Construit un PDF (inputs, résultats, greeks, payoff) et l'enregistre sur output_path."""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>European Option Valuation Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Inputs & Market Data
    story.append(Paragraph("<b>Inputs & Market Data</b>", styles["Heading2"]))
    data_items = [["Parameter", "Value"]]
    for k in ["ticker","S0","K","T","r","q","sigma_used","method","n_paths","n_steps"]:
        if k in inputs and inputs[k] is not None:
            data_items.append([str(k), str(inputs[k])])
    t = Table(data_items, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Valuation results
    story.append(Paragraph("<b>Valuation Results</b>", styles["Heading2"]))
    res_items = [["Metric", "Value"]]
    for key in ["bs_price","mc_price","implied_vol","mc_stderr"]:
        if key in results and results[key] is not None:
            val = results[key]
            res_items.append([key, f"{val:.6f}" if isinstance(val, float) else str(val)])
    t2 = Table(res_items, hAlign="LEFT")
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # Greeks
    if "greeks" in results and isinstance(results["greeks"], dict):
        story.append(Paragraph("<b>Greeks</b>", styles["Heading2"]))
        g = results["greeks"]
        g_items = [["Greek", "Value"]] + [[k, f"{v:.6f}"] for k, v in g.items()]
        tg = Table(g_items, hAlign="LEFT")
        tg.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        story.append(tg)
        story.append(Spacer(1, 12))

    # Payoff chart
    story.append(Paragraph("<b>Payoff Chart</b>", styles["Heading2"]))
    png_bytes = _plot_payoff_png(option_type, inputs.get("K", 0.0), inputs.get("S0", 0.0))
    story.append(Image(io.BytesIO(png_bytes), width=480, height=320))
    story.append(Spacer(1, 24))

    doc.build(story)
    return output_path
