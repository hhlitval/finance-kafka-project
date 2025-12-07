# Real-Time Stock Dashboard with Apache Kafka & Streamlit (DE)

A real-time stock dashboard built with Apache Kafka, Streamlit, and Yahoo Finance. The dashboard displays live stock prices, metrics with deltas, and falls back to historical data when the stock market is closed.

![Portfolio Screenshot](./assets/preview.webp)

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [How to run](#how-to-run)
- [License](#license)
- [Author](#author)

## Tech Stack

- Python 3.10+
- Apache Kafka
- Streamlit
- Altair
- Yahoo Finance API (yfinance)
- Pandas / NumPy

## Architecture Overview

![Project Structure](./assets/project_arch.png)

## Features

### Real-Time Data (When Market Is Open)

- A Kafka producer fetches a stock price every 5 seconds..
- A Kafka consumer streams the latest values into the dashboard.
- Streamlit updates metrics + charts automatically.
- Delta values are calculated against previous close.

### Automatic Market-Closed Fallback

When the market is closed (weekends, holidays, after-hours):

- Kafka producer/consumer do not start.
- Dashboard loads and displays the last 300 historical values from Yahoo Finance.

### UI Language Note

- UI is in German language. The code and documentation are written in English.

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hhlitval/stocks-kafka-project.git
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start Docker Desktop (Windows/macOS) or ensure Docker Engine is running (Linux)**
4. **Run the main entrypoint**
   ```bash
   python start.py
   ```

## License

This project is open-source and licensed under the [MIT License](LICENSE).

## Author

**Designed & developed by [Alex Litvin](https://alexlitvin.com)**
