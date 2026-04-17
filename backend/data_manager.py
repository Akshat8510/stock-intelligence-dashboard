import yfinance as yf
import pandas as pd
import numpy as np

class StockDataManager:
    def __init__(self):
        # Initial list of companies (NSE & Global)
        self.companies = {
            "INFY": "INFY.NS",
            "TCS": "TCS.NS",
            "RELIANCE": "RELIANCE.NS",
            "AAPL": "AAPL",
            "GOOGL": "GOOGL"
        }

    def fetch_stock_data(self, symbol: str, period="1y"):
        """Fetches data and applies transformations."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return None

        # --- DATA CLEANING ---
        df.reset_index(inplace=True)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        # --- CALCULATED METRICS ---
        # 1. Daily Return = (Close - Open) / Open
        df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
        
        # 2. 7-Day Moving Average
        df['MA7'] = df['Close'].rolling(window=7).mean()
        
        # 3. Custom Metric: Volatility (7-day Rolling Std Dev of returns)
        # This shows how 'risky' the stock has been recently
        df['Volatility'] = df['Daily_Return'].rolling(window=7).std()

        # Handle missing values after rolling calculations
        df = df.fillna(0)
        
        return df

    def get_summary_metrics(self, df):
        """Calculates 52-week High, Low, and Average."""
        summary = {
            "52_week_high": round(df['High'].max(), 2),
            "52_week_low": round(df['Low'].min(), 2),
            "avg_close": round(df['Close'].mean(), 2),
            "current_price": round(df['Close'].iloc[-1], 2)
        }
        return summary