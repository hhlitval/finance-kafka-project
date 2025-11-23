import json
import time
from kafka import KafkaProducer
from utils import load_json, get_stock_price, build_message
from datetime import datetime, timezone

# 1. Konfigurationen laden
config = load_json("../config/kafka_config.json")
symbols = load_json("../config/symbols.json")["symbols"]

# 2. Producer initialisieren
producer = KafkaProducer(
    bootstrap_servers=config["bootstrap_servers"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# symbol = "MSFT"
topic = config["topic_name"]
interval = config["interval_seconds"]

print(f"Starte Streaming für die Aktien...")

# 3. Endlosschleife für Daten streamen
while True:
    timestamp = datetime.now(timezone.utc).isoformat()

    for symbol in symbols:
      price = get_stock_price(symbol)

      if price is not None:
          message = build_message(symbol, price, timestamp)
          
          producer.send(topic, value=message)
          producer.flush()

          print(f"[Producer {symbol}] → gesendet: {message}")

      else:
          print(f"[Producer {symbol}] Keine Daten für {symbol} erhalten.")

    time.sleep(interval)
