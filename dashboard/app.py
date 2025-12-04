import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = Path(__file__).resolve().parent.parent
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import yfinance as yf
import altair as alt
from utils import is_market_open, load_historical_data, load_json, get_path

config = load_json(get_path("config", "kafka_config.json"))
ISSUERS = load_json(get_path("config", "stocks.json"))
TICKERS = list(ISSUERS.keys())
STOCKS_DATA = ROOT / "data" / "stock_prices.csv"

st.set_page_config(page_title="Aktien Echtzeit Dashboard", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400&display=swap');
* {
    font-family: 'Inter Tight', sans-serif !important;
    color: white;    
}
html {
    background-color: #101010;
}
h1 {
    font-weight: 500 !important;
}
header {
    display: none !important;
}
.stMainBlockContainer {
    padding: 2rem 1rem 2rem;
}
[data-testid="stAlertContainer"] {
    display: inline-flex;    
    background-color: #DDFFF7; 
    padding: 0.5rem 1rem
}
[data-testid="stAlertContentInfo"] p {
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
st.title("Deine wichtigsten Aktien im direkten Vergleich")
st.text("Frische Börsendaten direkt verarbeitet und übersichtlich dargestellt.")

def load_data():
    if STOCKS_DATA.exists():
        df = pd.read_csv(STOCKS_DATA)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

if is_market_open():
    st.info("Live-Modus aktiv")
    df = load_data() 
    st_autorefresh(interval=5000, key="refresh")
else:
    st.warning("Börse geschlossen. Zeige letzte Kurse von Yahoo.")
    df = load_historical_data(TICKERS)


# def fetch_last_yahoo(symbol, n=300):
#     df = yf.download(symbol, period="5d", interval="1m")
#     df = df.tail(n)
#     df = df.reset_index()
#     df["timestamp"] = pd.to_datetime(df["Datetime"])
#     df["symbol"] = symbol
#     df["price"] = df["Close"]
#     return df[["timestamp", "symbol", "price"]]


# ---------- Hole Daten aus CSV oder Yahoo ----------


    # Markt geschlossen → fallback
    # frames = [fetch_last_yahoo(sym) for sym in TICKERS]
    # df = pd.concat(frames)
    # return df


# ---------------- UI -------------------
   

# Aktuelle Werte (pro Symbol)

latest = df.sort_values("timestamp").groupby("symbol").tail(500)

row = st.container()
with row:
    colA, colB, colC = st.columns(3)
    colD, colE, colF = st.columns(3)
    # colE, colF = st.columns(2)
    columns = [colA, colB, colC, colD, colE, colF]

    for sym, col in zip(TICKERS, columns):
        d = latest[latest["symbol"] == sym].sort_values("timestamp")
        if len(d) < 2:
            col.metric(ISSUERS[sym], "—", delta="—")
            continue

        current = d["price"].iloc[-1]
        prev = d["price"].iloc[-2]
        delta = round(current - prev, 3)
        pct = round((delta / prev) * 100, 2)

        col.metric(
            label=f"{ISSUERS[sym]} ({sym})",
            value=f"${current:.2f}",
            delta=f"{delta:+.2f} ({pct:+.2f}%)",
            chart_data=d["price"],
            chart_type="line",
            border=True
        )






# import streamlit as st
# import pandas as pd
# import altair as alt
# import time
# from pathlib import Path
# from datetime import datetime, timedelta, timezone

# st.set_page_config(page_title="Live Aktien Dashboard", layout="wide")
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700&display=swap');
# h1, h2, h3, h4, h5, h6 {
#     font-family: 'Inter Tight', sans-serif !important;
# }
# [class^="st-emotion-cache"] h1,
# [class^="st-emotion-cache"] h2,
# [class^="st-emotion-cache"] h3,
# [class^="st-emotion-cache"] h4,
# [class^="st-emotion-cache"] h5,
# [class^="st-emotion-cache"] h6 {
#     font-family: 'Inter', sans-serif !important;
# }
# </style>
# """, 
# unsafe_allow_html=True)

# CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "stock_prices.csv"
# REFRESH_DEFAULT = 5                 
# OLD_DATA_THRESHOLD = 60        
# SHOW_OLD_DATA = 300          
# MAX_POINTS_TO_PLOT = 200            
# STOCKS = ["AAPL", "TSLA", "NVDA", "MSFT"]

# st.title("Aktienkurse im Vergleich")

# refreshrate = 5
# placeholder = st.empty()

# symbols = ["AAPL", "TSLA", "NVDA", "MSFT"]
# symbol_titles = {
#     "AAPL": "Apple",
#     "TSLA": "Tesla",
#     "NVDA": "Nvidia",
#     "MSFT": "Microsoft"
# }

# while True:
#     if CSV_PATH.exists():
#         df = pd.read_csv(CSV_PATH)

#         df["timestamp"] = pd.to_datetime(df["timestamp"])
#         df["time_full"] = df["timestamp"].dt.strftime("%d.%m.%y %H:%M")

#         latest = df.tail(300)

#         with placeholder.container():

#             col1, col2 = st.columns(2)
#             col3, col4 = st.columns(2)
#             cols = [col1, col2, col3, col4]

#             for col, sym in zip(cols, symbols):
#                 stock_df = latest[latest["symbol"] == sym]
#                 if not stock_df.empty:
#                     col.write(f"#### {symbol_titles[sym]}")
#                     col.metric("", "425", "1.2%")

#                     chart = (
#                         alt.Chart(stock_df)
#                         .mark_line()
#                         .encode(
#                             x=alt.X("timestamp:T", title=""),
#                             y=alt.Y(
#                                 "price:Q",
#                                 title="Preis",
#                                 scale=alt.Scale(zero=False)  
#                             ),
#                             tooltip=["time_full", "symbol", "price"]
#                         )
#                         .properties(height=220)
#                     )

#                     col.altair_chart(chart, width='stretch')

#                 else:
#                     col.write(f"{sym} – noch keine Daten")       
#     else:
#         st.warning("CSV existiert noch nicht. Starte Producer & Consumer.")
#     time.sleep(REFRESH_DEFAULT)

