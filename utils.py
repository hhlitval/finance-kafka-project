import json
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dtime
import pytz

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(*parts):
    return os.path.join(ROOT_DIR, *parts)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_stock_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")

        if data is None or data.empty:
            print(f"[WARN] Keine Intraday-Daten für {symbol} erhalten.")
            return None

        latest_price = data["Close"].iloc[-1]
        return float(latest_price)

    except Exception as e:
        print(f"[ERROR] Fehler beim Abrufen von {symbol}: {e}")
        return None

def build_message(symbol, price, timestamp):
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "timestamp": timestamp
    }

def fetch_last_yahoo(symbol, n=300):
    df = yf.download(symbol, period="5d", interval="1m", auto_adjust=True)
    df = df.tail(n)
    df = df.reset_index()        
    df["timestamp"] = pd.to_datetime(df["Datetime"])
    df["symbol"] = symbol
    df["price"] = df["Close"]   
    return df[["timestamp", "symbol", "price"]]

def load_historical_data(tickers): 
    frames = [fetch_last_yahoo(sym) for sym in tickers]
    df = pd.concat(frames)
    return df

def load_live_data(stocks_data):
    if stocks_data.exists():
        df = pd.read_csv(stocks_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
    
def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern"))
    if now.weekday() >= 5: 
        return False
    return dtime(9, 30) <= now.time() <= dtime(16, 0)

def get_previous_close(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d", interval="1d")
        if hist.shape[0] >= 2:
            prev_close = hist["Close"].iloc[-2]
            return float(prev_close)
        elif hist.shape[0] == 1:
            return float(hist["Close"].iloc[-1])
        else:
            return None
    except Exception:
        return None
