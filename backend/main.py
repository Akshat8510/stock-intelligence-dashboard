from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .data_manager import StockDataManager

app = FastAPI(title="Stock Intelligence Dashboard API")

# Enable CORS so our Frontend can talk to our Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = StockDataManager()

@app.get("/companies")
def get_companies():
    """Returns a list of available company symbols."""
    return manager.companies

@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    """Returns last 30 days of stock data for a symbol."""
    df = manager.fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Return last 30 rows as a list of dictionaries
    return df.tail(30).to_dict(orient="records")

@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    """Returns 52-week summary metrics."""
    df = manager.fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return manager.get_summary_metrics(df)

@app.get("/compare")
def compare_stocks(s1: str, s2: str):
    """Bonus: Compare two stocks performance."""
    df1 = manager.fetch_stock_data(s1).tail(30)
    df2 = manager.fetch_stock_data(s2).tail(30)
    
    return {
        s1: df1[['Date', 'Close']].to_dict(orient="records"),
        s2: df2[['Date', 'Close']].to_dict(orient="records")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)