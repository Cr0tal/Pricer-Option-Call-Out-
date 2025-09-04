# 📈 Option Pricer Flask

**🇫🇷 Outil complet de valorisation d’options européennes**  
**🇬🇧 Full-stack European Option Pricing Tool**

---

## ✨ Features / Fonctionnalités

- **Black–Scholes model** (call & put)  
- **Monte Carlo simulation** with configurable paths & steps  
- **Implied Volatility** calculation (Brent root-finding)  
- **Greeks**: Δ, Γ, Vega, Θ, ρ  
- **Automatic data retrieval** (spot price, hist. vol, dividends via `yfinance`)  
- **PDF Report generation** with inputs, results, Greeks, payoff chart  
- **Flask web interface** for easy parameter input + one-click PDF download  

---


##  Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/<TON_USERNAME>/option-pricer-flask.git
cd option-pricer-flask

```
### 2 Create & activate a virtual environment

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt

```
## 4. Run locally
```bash
python app.py
```
Open your browser at http://127.0.0.1:5000


Example (Exemple)
Ticker: AAPL
Strike (K): 150
Maturity: 2025-12-20
Rate (r): 2%
Volatility: leave empty to use historical vol
Market price: optional, for IV calculation
The app computes Black–Scholes price, Monte Carlo price, Greeks, implied volatility, and generates a custom PDF report.
'''

'''
Tech Stack
Python 3.10+
Flask (web)
yfinance (market data)
numpy, scipy (math, stats)
matplotlib (plotting)
reportlab (PDF generation)
'''

