import sys
import os
from datetime import datetime
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = Path(__file__).resolve().parent.parent
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from utils import load_json, get_path, is_market_open, load_historical_data, load_live_data, get_previous_close

config = load_json(get_path("config", "kafka_config.json"))
ISSUERS = load_json(get_path("config", "stocks.json"))
TICKERS = list(ISSUERS.keys())
STOCKS_DATA = ROOT / "data" / "stock_prices.csv"
METRICS_UPDATE_INTERVAL = 5

st.set_page_config(page_title="Aktien Echtzeit Dashboard", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500&display=swap');
* {
    font-family: 'Inter Tight', sans-serif !important;
    color: white;    
}
html {
    background-color: #101010;
}
h1 {
    font-weight: 450 !important;
}
header {
    display: none !important;
}
.stMainBlockContainer {
    padding: 4rem 1rem 2rem;
}
[data-testid="stAlertContainer"] {
    display: inline-flex;    
    background-color: #DDFFF7; 
    padding: 0.5rem 1rem
}
[data-testid="stAlertContentInfo"] p, [data-testid="stAlertContentWarning"] p {
    color: black;
}
.stApp {
    background-color: #101010; 
    max-width: 1440px; 
    margin: auto; 
}

.stMetric {
    background-color: #151515; 
     
}
[data-testid="stMetricChart"] svg {
    background-color: #151515 !important; 
}
</style>
""", 
unsafe_allow_html=True)
st.title("Deine Aktien im Vergleich")
st.text("Frische Börsendaten direkt verarbeitet und übersichtlich dargestellt.")

prev_close = {sym: get_previous_close(sym) for sym in TICKERS}

if is_market_open():
    st.info("Live-Modus aktiv")
    df = load_live_data(STOCKS_DATA) 
    st_autorefresh(interval=METRICS_UPDATE_INTERVAL*1000, key="refresh")
else:
    st.warning("Börse geschlossen. Zeige letzte Kurse von Yahoo Finance.")
    df = load_historical_data(TICKERS)

latest = df.sort_values("timestamp").groupby("symbol").tail(500)
row = st.container()
with row:
    colA, colB, colC = st.columns(3)
    colD, colE, colF = st.columns(3)
    columns = [colA, colB, colC, colD, colE, colF]

    for sym, col in zip(TICKERS, columns):
        d = latest[latest["symbol"] == sym].sort_values("timestamp")
        if len(d) < 2:
            col.metric(ISSUERS[sym], "—", delta="—")
            continue

        current = d["price"].iloc[-1]
        delta = round(current - prev_close[sym], 3)
        pct = round((delta / prev_close[sym]) * 100, 2)

        col.metric(
            label=f"{ISSUERS[sym]} ({sym})",
            value=f"${current:.2f}",
            delta=f"{delta:+.2f} ({pct:+.2f}%)",
            chart_data=round(d["price"], 2),
            chart_type="line",
            border=True
        )
st.markdown(f"""
<style>
    .footer {{
        h4, a {{
        color: #888888;
        font-size: 1rem;
        font-weight: 350;
        }}
        a,
        a:link,
        a:visited {{           
        text-decoration: underline;
    }}
        
}}
</style>
<footer class="footer">
    <h4>
        Created by
        <a href="https://www.alexlitvin.com" target="_blank">Alex Litvin</a> © {datetime.now().year}
    </h4>
</footer>
""", 
unsafe_allow_html=True)