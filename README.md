# Stock Intelligence Dashboard

A mini financial data platform built with FastAPI, yfinance, and Chart.js.

## Features

- **Live stock data** fetched from Yahoo Finance via `yfinance`
- **Calculated metrics**: Daily Return, 7-Day Moving Average, Volatility, Momentum Score
- **52-week summary** with trend classification (Bullish / Bearish / Neutral)
- **Compare two stocks** — normalised to base 100 for fair side-by-side charting
- **Top gainers & losers** panel based on the latest trading day
- **Interactive frontend** — dark-themed, built with Tailwind CSS and Chart.js
- **Swagger API docs** at `http://127.0.0.1:8000/docs`

## Project Structure

```
stock-intelligence-dashboard/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + all endpoints
│   └── data_manager.py  # Data fetching, cleaning, and metric calculation
├── frontend/
│   ├── index.html       # Dashboard UI
│   ├── script.js        # API calls, chart rendering, compare logic
│   └── style.css        # Custom styles (Tailwind + overrides)
├── requirements.txt
└── README.md
```

## Setup

**1. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the server**
```bash
uvicorn backend.main:app --reload
```

The app will be available at `http://127.0.0.1:8000`.  
The frontend dashboard is served at the root URL.  
Swagger docs are at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/companies` | GET | List all tracked companies |
| `/data/{symbol}` | GET | Last 30 days of stock data with metrics |
| `/summary/{symbol}` | GET | 52-week high, low, avg, momentum |
| `/compare?symbol1=X&symbol2=Y` | GET | Normalised comparison of two stocks |
| `/gainers-losers` | GET | Top 3 daily gainers and losers |

## Metrics Explained

| Metric | Formula | Purpose |
|---|---|---|
| Daily Return | `(Close - Open) / Open` | Intraday price movement |
| 7-Day MA | `Close.rolling(7).mean()` | Smoothed trend line |
| Volatility | `Daily_Return.rolling(7).std()` | Short-term risk proxy |
| Momentum Score | `Close / MA20` | Trend strength relative to 20-day average |

**Trend classification**:  
- `Momentum > 1.02` → **Bullish**  
- `Momentum < 0.98` → **Bearish**  
- Otherwise → **Neutral**

## Usage Tips

- Click any stock in the sidebar to load its dashboard.
- **Ctrl+click** (or **Cmd+click** on Mac) to select two stocks for comparison, then click "Compare →".
- The gainers/losers panel at the top of the sidebar refreshes on each page load.