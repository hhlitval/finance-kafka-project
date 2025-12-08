import json
import csv
import os
from kafka import KafkaConsumer
from utils import load_json, get_path

config = load_json(get_path("config", "kafka_config.json"))
topic = config["topic_name"]
csv_path = get_path("data", "stock_prices.csv")
file_exists = os.path.isfile(csv_path)
csv_file = open(csv_path, "a", newline="")
csv_writer = csv.writer(csv_file)

if not file_exists:
    csv_writer.writerow(["timestamp", "symbol", "price"])  

consumer = KafkaConsumer(
    topic,
    bootstrap_servers=config["bootstrap_servers"],
    group_id="stock-dashboard-consumer",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)
print("[Consumer] Listening for incoming Kafka messages")

try:
    for message in consumer:
        data = message.value
        timestamp = data["timestamp"]
        symbol = data["symbol"]
        price = data["price"]
        csv_writer.writerow([timestamp, symbol, price])
        csv_file.flush()
        print(f"[Consumer] ← {timestamp} | {symbol}: {price}")
except KeyboardInterrupt:
    print("\n[Consumer] Manual termination detected.")
finally:
    csv_file.close()
    consumer.close()
