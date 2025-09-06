# **Option Pricer Call/Put** 

**Outil complet de valorisation d’options européennes**  


---

##  Features / Fonctionnalités

- **modèle Black–Scholes** (call & put)  
- **Simulation Monte Carlo** avec configuration de pas  
- **volatilité Implicite**  
- **Les Grecs**: Δ, Γ, Vega, Θ, ρ  
- **Data automatique** (prix spot , hist. vol, dividends via `yfinance`)  
- **Génération de rapport PDf** avec inputs, resultats, Grecs,graphique payoff   
- **interface web** pdf téléchargeable   

---


##  Installation & Usage

### 1. Clone le repository 
```bash
git clone https://github.com/<TON_USERNAME>/option-pricer-flask.git
cd option-pricer-flask

```
### 2 crée et activé un environement 

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
ouvrir à -> http://127.0.0.1:5000


Exemple:
Ticker: AAPL  
Strike (K): 270  
Maturity: 2025-12-20  
Rate (r): 2%  
Volatilité: laissé vide pour utlisé la colatilité historique  
Prix de marché:   
L'app calcule le prix Black-Sholes,le prix Monte Carlo, les Grecs, la volatilité implicite et génère un.  rapport PDF.  

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

