import yfinance as yf
import pandas as pd

#list of Indian stocks we want to fetch data for
SYMBOLS = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'WIPRO.NS']

def fetch_and_clean(symbol):
    print(f"fetching data for {symbol}...")

    #download 1 year of data from Yahoo Finance
    df = yf.download(symbol, period='1y', auto_adjust = True)

    #if no data come back, Skip this symbol
    if df.empty:
        print(f"no data found for {symbol}")
        return None
    
    #Reset index so date become a normal column
    df.reset_index(inplace=True)

    #Flatten column names (yfinance sometimes return multilevel column names)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    #Rename columns to lowercase for consistency
    df.rename(columns={
              "Date": "date",
              "Open": "open",
              "High": "high",
              "Low": "low",
              "Close": "close",
              "Volume": "volume"
              }, inplace=True)
    
    #Keep only the columns we need
    df = df[["date", "open", "high", "low", "close", "volume"]]

    #Handle missing values -  drop rows where close price value is missing
    df.dropna(subset=["close"], inplace = True)

    #Covert date column to proper date format
    df["date"] = pd.to_datetime(df["date"])

    #------ Add calculated metrics -------

    #Dailyreturn = (close price - open price) / open price
    df["daily_return"] = (df["close"] - df["open"]) / df["open"]

    # 7Day Moving Average of close price
    df["moving_avg_7d"] = df["close"].rolling(window=7).mean()

    #52 Week High and Low (same value repeated per row for east api access)
    df["52_week_low"] = df["close"].min()
    df["52_week_high"] = df["close"].max()

    #Add stock symbol as a column
    df["symbol"] = symbol.replace(".NS", "")
    print(f"Done! {len(df)} rows fetched for {symbol}")
    return df

def fetch_all():
    all_data = []
    for symbol in SYMBOLS:
        df = fetch_and_clean(symbol)
        if df is not None:
            all_data.append(df)



    #Combine all the stocks into one big dataframe
    combined = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal rows across all stocks: {len(combined)}")
    return combined

#Test it by running this file directly
if __name__ == "__main__":
    data = fetch_all()
    print(data.head())



from sqlalchemy.orm import Session
from database import engine, Base
from models import StockData

def save_to_db(df):
    # Create the database tables if it doesn't exist
    Base.metadata.create_all(bind=engine)

    from database import SessionLocal
    db = SessionLocal()

    # Clear old data so we don't get duplicates
    db.query(StockData).delete()

    # Insert each row into the database
    for _, row in df.iterrows():
        record = StockData(
            symbol=row["symbol"],
            data=row["date"].date(),
            open=round(float(row["open"]), 2),
            high=round(float(row["high"]), 2),
            low=round(float(row["low"]), 2),
            close=round(float(row["close"]), 2),
            volume=float(row["volume"]),
            daily_return=round(float(row["daily_return"]), 4),
            moving_avg_7d=round(float(row["moving_avg_7d"]), 2) if not pd.isna(row["moving_avg_7d"]) else None,
            week_52_low=round(float(row["52_week_low"]), 2),
            week_52_high=round(float(row["52_week_high"]), 2)

        )
        db.add(record)

    db.commit()
    db.close()
    print("All data saved to database!")


# Update the bottom of the file to also save 
if __name__ == "__main__":
    data = fetch_all()
    print(data.head())
    save_to_db(data)
        




 