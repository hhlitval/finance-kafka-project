import subprocess
import time
from pathlib import Path
from utils import is_market_open

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
producer_proc = None
consumer_proc = None
docker_started = False

def start_kafka_services():
    global producer_proc, consumer_proc, docker_started

    if not docker_started:
        print("Starting Docker Compose")
        subprocess.Popen(["docker-compose", "up", "-d"]).wait()
        docker_started = True

    if producer_proc is None or producer_proc.poll() is not None:
        print("Starting Producer")
        producer_proc = subprocess.Popen([str(VENV_PYTHON), "-m", "producer.producer_stocks"])

    if consumer_proc is None or consumer_proc.poll() is not None:
        print("Starting Consumer")
        consumer_proc = subprocess.Popen([str(VENV_PYTHON), "-m", "consumer.consumer"])  

def stop_kafka_services():
    global producer_proc, consumer_proc, docker_started

    if producer_proc:
        print("Stopping Producer")
        producer_proc.terminate()
        producer_proc = None

    if consumer_proc:
        print("Stopping Consumer")
        consumer_proc.terminate()
        consumer_proc = None

    # if docker_started:
    #     print("Stopping Docker Compose")
    #     subprocess.Popen(["docker-compose", "down"]).wait()
    #     docker_started = False


def main():
    market_open_prev = is_market_open()

    if market_open_prev:
        print("Market open -> Starting real-time pipeline")
        start_kafka_services()
    else:
        print("Market closed -> Using historical data only")

    print("Starting Streamlit")
    streamlit_proc = subprocess.Popen(["streamlit", "run", "dashboard/app.py"])

    try:
        while True:
            time.sleep(60)

            market_open_now = is_market_open()

            if market_open_now and not market_open_prev:
                print("\n Market opened -> starting Kafka pipeline")
                start_kafka_services()

            if not market_open_now and market_open_prev:
                print("\n Market closed -> stopping Kafka pipeline")
                stop_kafka_services()

            market_open_prev = market_open_now

    except KeyboardInterrupt:
        print("\n Shutting down everything...")
        stop_kafka_services()
        streamlit_proc.terminate()

if __name__ == "__main__":
    main()