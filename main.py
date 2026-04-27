from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, engine, Base
from models import StockData
from datetime import date, timedelta

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Dashboard API")

# Serve the frontend from the templates folder
app.mount("/static", StaticFiles(directory="templates"), name="static")

# ___ Route 1: Home page _________________________________
@app.get("/")
def home():
    return FileResponse("templates/index.html")


# ___ Route 2: List all companies _________________________________
@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    symbols = db.query(StockData.symbol).distinct().all()
    return {"companies": [s[0] for s in symbols]}


# ___Route 3: Last 30 days of stock data
@app.get("/data/{symbol}")
def get_stock_data(symbol: str, db: Session = Depends(get_db)):
    records = (
        db.query(StockData)
        .filter(StockData.symbol == symbol.upper())
        .order_by(StockData.data)
        .limit(30)
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    return {
        "symbol": symbol.upper(),
        "data": [
            {
                "date": str(r.data),
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "daily_return": r.daily_return,
                "moving_avg_7": r.moving_avg_7d,
            }
            for r in records
        ],
    }


# ___ Route 4: 52-week summary _________________________________
@app.get("/summary/{symbol}")
def get_summary(symbol: str, db: Session = Depends(get_db)):
    records = (
        db.query(StockData)
        .filter(StockData.symbol == symbol.upper())
        .all()

    )

    if not records:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    closes = [r.close for r in records]

    return {
        "symbol": symbol.upper(),
        "week52_high": records[0].week_52_high,
        "week52_low": records[0].week_52_low,
        "avg_close": round(sum(closes) / len(closes), 2),
        "total_days": len(records)
    }



# ____ Route 5: Compare two stocks (Bonus) _________________________________
@app.get("/compare")
def compare_stock(symbol1: str, symbol2: str, db: Session = Depends(get_db)):
    result = {}
    for symbol in [symbol1.upper(), symbol2.upper()]:
        records = (
            db.query(StockData)
            .filter(StockData.symbol == symbol)
            .all()
        )

        if not records:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        closes = [r.close for r in records]
        result[symbol] = {
            "week52_high": records[0].week_52_high,
            "week52_low": records[0].week_52_low,
            "avg_close": round(sum(closes) / len(closes), 2),
            "latest_close": closes[-1],
        }
    return result
