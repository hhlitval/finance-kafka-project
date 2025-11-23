import json
import yfinance as yf

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
        "price": price,
        "timestamp": timestamp
    }
