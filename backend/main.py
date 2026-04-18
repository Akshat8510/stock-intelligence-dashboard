from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .data_manager import StockDataManager

app = FastAPI(
    title="Stock Intelligence Dashboard API",
    description="A mini financial data platform for stock market analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = StockDataManager()

# --- Serve Frontend ---
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", include_in_schema=False)
def serve_home():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Stock Intelligence API is running. Visit /docs for API documentation."}


# --- API Endpoints ---

@app.get("/companies", summary="List all available companies")
def get_companies():
    return manager.companies


# :path tells FastAPI to capture everything including dots (e.g. INFY.NS)
@app.get("/data/{symbol:path}", summary="Get last 30 days of stock data")
def get_stock_data(symbol: str):
    """
    Returns the last 30 days of stock data for a given ticker symbol.
    Falls back to mock data if Yahoo Finance is unreachable.
    """
    df = manager.fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data for '{symbol}'.")
    return df.tail(30).to_dict(orient="records")


@app.get("/summary/{symbol:path}", summary="Get 52-week summary metrics")
def get_summary(symbol: str):
    """
    Returns 52-week high/low, average close, current price, momentum score and trend.
    """
    df = manager.fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data for '{symbol}'.")
    return manager.get_summary_metrics(df)


@app.get("/compare", summary="Compare two stocks side by side")
def compare_stocks(
    symbol1: str = Query(..., description="First ticker, e.g. INFY.NS"),
    symbol2: str = Query(..., description="Second ticker, e.g. TCS.NS")
):
    """
    Returns normalised (base 100) performance for two tickers over the last 30 days.
    """
    df1 = manager.fetch_stock_data(symbol1)
    df2 = manager.fetch_stock_data(symbol2)

    if df1 is None:
        raise HTTPException(status_code=404, detail=f"No data for '{symbol1}'.")
    if df2 is None:
        raise HTTPException(status_code=404, detail=f"No data for '{symbol2}'.")

    df1_tail = df1.tail(30).copy()
    df2_tail = df2.tail(30).copy()

    df1_tail["Normalised"] = (df1_tail["Close"] / df1_tail["Close"].iloc[0]) * 100
    df2_tail["Normalised"] = (df2_tail["Close"] / df2_tail["Close"].iloc[0]) * 100

    return {
        symbol1: df1_tail[["Date", "Close", "Daily_Return", "Normalised"]].to_dict(orient="records"),
        symbol2: df2_tail[["Date", "Close", "Daily_Return", "Normalised"]].to_dict(orient="records"),
    }


@app.get("/gainers-losers", summary="Top 3 daily gainers and losers")
def get_gainers_losers():
    results = []
    for name, symbol in manager.companies.items():
        df = manager.fetch_stock_data(symbol)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            results.append({
                "name":         name,
                "symbol":       symbol,
                "daily_return": round(float(latest["Daily_Return"]) * 100, 2),
                "close":        round(float(latest["Close"]), 2)
            })

    results.sort(key=lambda x: x["daily_return"], reverse=True)
    return {
        "gainers": results[:3],
        "losers":  results[-3:][::-1]
    }