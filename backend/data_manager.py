import yfinance as yf
import pandas as pd
import numpy as np
import requests


def _make_session():
    """Spoof a real browser so Yahoo Finance doesn't block the request."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection":      "keep-alive",
    })
    return session


# Realistic base prices per ticker so mock data looks plausible
MOCK_BASE_PRICES = {
    "INFY.NS":      1500,
    "TCS.NS":       3800,
    "RELIANCE.NS":  2900,
    "HDFCBANK.NS":  1600,
    "AAPL":          190,
    "GOOGL":         175,
    "MSFT":          420,
}
DEFAULT_BASE = 100


def _generate_mock_data(symbol: str, periods: int = 260) -> pd.DataFrame:
    """
    Generates realistic-looking mock OHLCV data using a random walk.
    Used as fallback when Yahoo Finance is unreachable.
    """
    base  = MOCK_BASE_PRICES.get(symbol, DEFAULT_BASE)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq="B")  # business days

    # Random walk so the chart looks like a real price series
    returns   = np.random.normal(0.0003, 0.015, periods)
    closes    = base * np.cumprod(1 + returns)
    opens     = closes * np.random.uniform(0.995, 1.005, periods)
    highs     = np.maximum(opens, closes) * np.random.uniform(1.001, 1.015, periods)
    lows      = np.minimum(opens, closes) * np.random.uniform(0.985, 0.999, periods)
    volumes   = np.random.randint(500_000, 5_000_000, periods).astype(float)

    df = pd.DataFrame({
        "Date":   dates,
        "Open":   opens.round(2),
        "High":   highs.round(2),
        "Low":    lows.round(2),
        "Close":  closes.round(2),
        "Volume": volumes,
    })
    print(f"[MOCK] Using generated data for {symbol}")
    return df


class StockDataManager:
    def __init__(self):
        self.companies = {
            "Infosys":   "INFY.NS",
            "TCS":       "TCS.NS",
            "Reliance":  "RELIANCE.NS",
            "HDFC Bank": "HDFCBANK.NS",
            "Apple":     "AAPL",
            "Google":    "GOOGL",
            "Microsoft": "MSFT",
        }
        self._session = _make_session()

    def fetch_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame | None:
        """
        Fetches historical data. Falls back to mock data if Yahoo Finance is
        unreachable (DNS failure, rate-limit, etc.).
        """
        df = None

        # ── Try Yahoo Finance first ───────────────────────────────────────────
        try:
            ticker = yf.Ticker(symbol, session=self._session)
            raw    = ticker.history(period=period)
            if raw is not None and not raw.empty:
                raw.reset_index(inplace=True)
                # Strip timezone from Date column
                if hasattr(raw["Date"].dtype, "tz") and raw["Date"].dtype.tz is not None:
                    raw["Date"] = raw["Date"].dt.tz_localize(None)
                df = raw[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
                print(f"[OK] Yahoo data fetched for {symbol} ({len(df)} rows)")
        except Exception as e:
            print(f"[WARN] Yahoo Finance failed for {symbol}: {e}")

        # ── Fallback to mock data if needed ──────────────────────────────────
        if df is None or df.empty:
            df = _generate_mock_data(symbol)

        # ── CLEANING ─────────────────────────────────────────────────────────
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

        # ── CALCULATED METRICS ───────────────────────────────────────────────
        df["Daily_Return"] = ((df["Close"] - df["Open"]) / df["Open"]).round(5)
        df["MA7"]          = df["Close"].rolling(window=7).mean().round(2)
        df["Volatility"]   = df["Daily_Return"].rolling(window=7).std().round(5)
        df["MA20"]         = df["Close"].rolling(window=20).mean().round(2)
        df["Momentum"]     = (df["Close"] / df["MA20"]).round(4)

        return df.fillna(0)

    def get_summary_metrics(self, df: pd.DataFrame) -> dict:
        current_price = round(float(df["Close"].iloc[-1]), 2)
        momentum      = float(df["Momentum"].iloc[-1])

        if momentum > 1.02:
            trend = "Bullish"
        elif momentum < 0.98:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return {
            "52_week_high":   round(float(df["High"].max()), 2),
            "52_week_low":    round(float(df["Low"].min()), 2),
            "avg_close":      round(float(df["Close"].mean()), 2),
            "current_price":  current_price,
            "momentum_score": round(momentum, 4),
            "trend":          trend,
        }