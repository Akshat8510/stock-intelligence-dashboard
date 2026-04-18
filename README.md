# 📈 Stock Data Intelligence Dashboard

> A full-stack financial data platform built as part of the Jarnox Internship Assignment.
> Fetches real-world stock data, processes it with Pandas, serves it via FastAPI, and visualises it with an interactive Chart.js dashboard.

---

## 🗺️ What This Project Does

Think of this project as a mini Bloomberg Terminal — but one you built yourself.

1. **It fetches stock prices** from Yahoo Finance (INFY, TCS, Reliance, Apple, Google, etc.)
2. **It crunches the numbers** — calculates returns, moving averages, volatility, and momentum
3. **It serves that data** through a clean REST API built with FastAPI
4. **It draws the charts** on a dark-themed web dashboard using Chart.js

If Yahoo Finance is unreachable (common in India due to DNS issues), the app **automatically generates realistic mock data** so the dashboard always works.

---

## ✨ Features at a Glance

| Feature | What it does |
|---|---|
| 📊 Price Chart | Line chart of Close price + 7-Day Moving Average for last 30 days |
| 📉 Volatility Chart | Bar chart of rolling 7-day volatility (risk indicator) |
| 🏷️ Trend Badge | Auto-labels each stock as Bullish / Bearish / Neutral |
| 🏆 Gainers & Losers | Sidebar panel showing today's top 3 movers |
| ⚖️ Compare Mode | Ctrl+click two stocks to compare normalised performance |
| 🔁 Mock Fallback | Generates realistic random-walk data if live fetch fails |
| 📖 Swagger Docs | Auto-generated API docs at `/docs` |

---

## 🛠️ Tech Stack

```
Backend   →  Python 3.10+, FastAPI, Uvicorn
Data      →  Pandas, NumPy, yfinance, Requests
Frontend  →  HTML5, Tailwind CSS, Chart.js, Vanilla JS
```

---

## ⚙️ Setup in 4 Steps

### Step 1 — Clone the repo
```bash
git clone https://github.com/Akshat8510/stock-intelligence-dashboard.git
cd stock-intelligence-dashboard
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Start the server
```bash
python -m uvicorn backend.main:app --reload
```

Then open **`http://127.0.0.1:8000`** in your browser.
API docs are at **`http://127.0.0.1:8000/docs`**.

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/companies` | GET | Returns all tracked company names and ticker symbols |
| `/data/{symbol}` | GET | Last 30 days of OHLCV data + calculated metrics |
| `/summary/{symbol}` | GET | 52-week high/low, avg close, momentum score, trend |
| `/compare?symbol1=X&symbol2=Y` | GET | Normalised base-100 comparison of two stocks |
| `/gainers-losers` | GET | Top 3 daily gainers and losers across all companies |

> **Note:** Symbols with dots (like `INFY.NS`) are handled correctly using FastAPI's `{symbol:path}` routing.

### Example
```bash
# Get Infosys summary
curl http://127.0.0.1:8000/summary/INFY.NS

# Compare TCS vs Infosys
curl "http://127.0.0.1:8000/compare?symbol1=TCS.NS&symbol2=INFY.NS"
```

---

## 📐 Metrics Explained

| Metric | Formula | Why it matters |
|---|---|---|
| Daily Return | `(Close - Open) / Open` | How much the stock moved in a single day |
| 7-Day MA | `Close.rolling(7).mean()` | Smooths out noise to show the short-term trend |
| Volatility | `Daily_Return.rolling(7).std()` | Higher = riskier, more unpredictable price swings |
| Momentum Score | `Close / MA20` | > 1.02 = Bullish, < 0.98 = Bearish, else Neutral |

---

## 💡 Design Decisions Worth Noting

### Why `:path` in FastAPI routes?
NSE ticker symbols contain dots (e.g. `INFY.NS`). FastAPI's default `{symbol}` pattern stops at the dot and returns a 404. Using `{symbol:path}` tells FastAPI to capture the full string including dots.

### Why mock data?
Yahoo Finance frequently blocks or rate-limits requests from Indian networks. Rather than showing a broken dashboard, the app detects a failed fetch and generates a realistic random-walk price series using each stock's real-world base price (₹1,500 for Infosys, ₹3,800 for TCS, etc.), so the charts always look meaningful.

### Why normalised comparison?
Comparing a ₹3,800 TCS share directly with a ₹1,500 Infosys share on the same chart is misleading. Both are rebased to 100 on day one, so the chart shows **percentage growth** — an apples-to-apples comparison.

### Why load movers in the background?
Fetching all 7 stocks at once on page load would freeze the sidebar for several seconds. The movers panel is loaded asynchronously (no `await`) so the watchlist appears instantly and the panel fills in once the data arrives.

---

## 📂 Project Structure

```
stock-intelligence-dashboard/
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, all route definitions
│   └── data_manager.py   # Data fetching, cleaning, metrics, mock fallback
├── frontend/
│   ├── index.html        # Dashboard layout
│   ├── script.js         # API calls, chart rendering, compare logic
│   └── style.css         # Tailwind overrides, active/compare link styles
├── requirements.txt
└── README.md
```

---

## 🐛 Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| 404 on `/data/INFY.NS` | Old route without `:path` | Make sure `main.py` uses `{symbol:path}` |
| Empty charts | Yahoo Finance blocked | App falls back to mock data automatically — just refresh |
| `Module not found` error | Wrong working directory | Run `uvicorn` from the project root, not from inside `backend/` |
| Port already in use | Another uvicorn is running | Run `Ctrl+C` in the old terminal first |

---

## 📬 Submission

Built by **Akshat** for the Jarnox Internship Assignment.
Submitted to: support@jarnox.com