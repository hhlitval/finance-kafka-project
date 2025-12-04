import json
import csv
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

# def fetch_last_yahoo(symbol, n=300):
#     df = yf.download(symbol, period="5d", interval="1m")
#     df = df.tail(n)
#     df = df.reset_index()
#     df["timestamp"] = pd.to_datetime(df["Datetime"])
#     df["symbol"] = symbol
#     df["price"] = df["Close"]
#     return df[["timestamp", "symbol", "price"]]

### TODO

def fetch_last_yahoo(symbol, n=300):
    df = yf.download(symbol, period="5d", interval="1m")
    
    if df.empty:
        print(f"Keine Daten für {symbol} gefunden.")
        return pd.DataFrame(columns=["timestamp", "symbol", "price"]) 
        
    df = df.tail(n)
    df = df.reset_index()        
    df["timestamp"] = pd.to_datetime(df["Datetime"])
    df["symbol"] = symbol
    df["price"] = df["Close"]   

    return df[["timestamp", "symbol", "price"]]


# NEUE und KORRIGIERTE Hauptfunktion
def load_historical_data(tickers): 
    # Daten für alle Ticker abrufen und zusammenführen
    frames = [fetch_last_yahoo(sym) for sym in tickers]
    df = pd.concat(frames)

    csv_path = get_path("data", "stock_prices.csv")
    
    # 1. Zeitstempel-Formatierung
    # Konvertiert den Timestamp in den gewünschten ISO-8601 String mit Mikrosekunden:
    # Bsp.: 2025-12-03T16:08:04.418973+00:00
    df["timestamp"] = df["timestamp"].dt.to_iso8601(timespec='microseconds')
    
    # 2. Status prüfen (wird die Datei neu erstellt?)
    file_exists = os.path.exists(csv_path)
    
    # 3. Den gesamten DataFrame in die CSV-Datei schreiben
    df.to_csv(
        csv_path, 
        mode='a',              # Modus 'a' (append) zum Anhängen an die Datei
        index=False,           # Verhindert, dass der Pandas-Index (0, 1, 2, ...) geschrieben wird
        header=not file_exists # Schreibt die Kopfzeile nur, wenn die Datei NEU ist
    )
    
    # Bestätigung
    if not file_exists:
        print(f"Daten (inkl. Header) erfolgreich in {csv_path} gespeichert.")
    else:
        print(f"Daten erfolgreich an {csv_path} angehängt.")
        
def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern"))
    if now.weekday() >= 5: 
        return False
    return dtime(9, 30) <= now.time() <= dtime(16, 0)