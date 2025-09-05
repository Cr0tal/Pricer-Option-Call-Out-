# app.py
from __future__ import annotations

import io, json, tempfile, os
from datetime import datetime, date
from typing import Any, Dict
from flask import Flask, render_template, request, send_file

from app.utils import year_fraction
from app.data import fetch_market_data
from app.black_scholes import BSInputs, price as bs_price, greeks as bs_greeks
from app.monte_carlo import price_mc
from app.implied_vol import implied_vol_bs

app = Flask(__name__)


@app.route("/diag")
def diag():
    import sys
    pkgs = {}
    try:
        import reportlab; pkgs["reportlab"] = getattr(reportlab, "Version", "OK")
    except Exception as e:
        pkgs["reportlab"] = f"ERROR: {e}"
    for name in ["numpy","scipy","matplotlib","pandas","yfinance","flask"]:
        try:
            mod = __import__(name)
            pkgs[name] = getattr(mod, "__version__", "OK")
        except Exception as e:
            pkgs[name] = f"ERROR: {e}"
    return {"python": sys.version, "sys_path_head": sys.path[:3], "packages": pkgs}

# --- Import robuste pour PDF ---
try:
    from app.report import build_pdf_report
    _REPORT_IMPORT_ERROR = None
except Exception as _e:
    build_pdf_report = None  # type: ignore
    _REPORT_IMPORT_ERROR = str(_e)

def _parse_float(val: str | None) -> float | None:
    try:
        if val is None or val == "":
            return None
        return float(val)
    except ValueError:
        return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", year=date.today().year, results=None, error=None)

@app.route("/price", methods=["POST"])
def price_route():
    try:
        ticker = request.form.get("ticker", "").strip()
        K = _parse_float(request.form.get("strike"))
        maturity_str = request.form.get("maturity")
        r_pct = _parse_float(request.form.get("rate")) or 0.0
        q_pct_manual = _parse_float(request.form.get("div_yield"))
        vol_pct_manual = _parse_float(request.form.get("vol"))
        option_type = request.form.get("option_type", "call")
        n_paths = int(request.form.get("n_paths", 10000))
        n_steps = int(request.form.get("n_steps", 1))
        market_price = _parse_float(request.form.get("market_price"))

        if not ticker or K is None or maturity_str is None:
            raise ValueError("Merci de fournir ticker, strike et maturité.")

        maturity = datetime.strptime(maturity_str, "%Y-%m-%d").date()
        T = year_fraction(maturity)

        md = fetch_market_data(ticker)
        S0 = md.spot
        q = q_pct_manual / 100.0 if q_pct_manual is not None else (md.dividend_yield or 0.0)
        sigma = vol_pct_manual / 100.0 if vol_pct_manual is not None else (md.hist_vol or 0.2)
        r = r_pct / 100.0

        bs_in = BSInputs(S=S0, K=K, T=T, r=r, q=q, sigma=sigma)
        bs_val = bs_price(bs_in, option_type=option_type)
        g = bs_greeks(bs_in)
        mc_val = price_mc(S0=S0, K=K, T=T, r=r, q=q, sigma=sigma, n_paths=n_paths, n_steps=n_steps, rng_seed=42, option_type=option_type)

        iv = None
        if market_price is not None:
            iv = implied_vol_bs(market_price=market_price, S=S0, K=K, T=T, r=r, q=q, option_type=option_type)

        inputs = {
            "ticker": ticker, "S0": round(S0, 6), "K": K, "T": round(T, 6),
            "r": round(r, 6), "q": round(q, 6), "sigma_used": round(sigma, 6),
            "method": "BS + Monte Carlo", "n_paths": n_paths, "n_steps": n_steps, "option_type": option_type
        }
        results = {
            "bs_price": round(bs_val, 6) if bs_val is not None else None,
            "mc_price": round(mc_val, 6) if mc_val is not None else None,
            "mc_stderr": None,
            "implied_vol": round(iv, 6) if iv is not None else None,
            "greeks": {k: round(v, 6) for k, v in g.items()} if g else None,
        }
        payload_json = json.dumps({"inputs": inputs, "results": results})
        return render_template("index.html", year=date.today().year, inputs=inputs, results=results, payload_json=payload_json, error=None)
    except Exception as e:
        return render_template("index.html", year=date.today().year, results=None, error=str(e))

@app.route("/report", methods=["POST"])
def report_route():
    if (build_pdf_report is None) or (not callable(build_pdf_report)):
        msg = (
            "La génération de PDF est indisponible : "
            + (_REPORT_IMPORT_ERROR or "import app.report échoué.")
            + "\n\nDiagnostic rapide :\n"
              "1) Sélectionne le bon interpréteur Python dans VS Code\n"
              "2) Installe les dépendances dans cet environnement :\n"
              "   pip install -r requirements.txt\n"
              "3) Teste : python -c \"import reportlab, matplotlib, numpy, scipy; print('OK')\""
        )
        return msg, 500

    payload = request.form.get("payload")
    if not payload:
        return "Missing payload", 400
    data = json.loads(payload)
    inputs: Dict[str, Any] = data.get("inputs", {})
    results: Dict[str, Any] = data.get("results", {})
    option_type = inputs.get("option_type", "call")

    output = io.BytesIO()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "report.pdf")
        build_pdf_report(path, inputs=inputs, results=results, option_type=option_type)
        with open(path, "rb") as f:
            output.write(f.read())
    output.seek(0)
    filename = f"valuation_{inputs.get('ticker','TICK')}_{inputs.get('option_type','call')}.pdf"
    return send_file(output, mimetype="application/pdf", as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
