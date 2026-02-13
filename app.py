import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📱 Personal Options Command Center — Full Index Scanner")

@st.cache_data(ttl=900)
def get_sp500():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    return table[0]["Symbol"].tolist()

@st.cache_data(ttl=900)
def get_dow():
    table = pd.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")
    return table[1]["Symbol"].tolist()

@st.cache_data(ttl=900)
def get_nasdaq100():
    table = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100")
    return table[3]["Ticker"].tolist()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_sp500():
    return [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA",
        "BRK-B","JPM","V","UNH","HD","PG","MA","DIS",
        "BAC","XOM","KO","PFE","PEP"
    ]
def get_dow():
    return [
        "AAPL","MSFT","JPM","V","HD","PG","UNH","DIS",
        "KO","INTC","IBM","GS","MCD","NKE","BA"
    ]
def get_nasdaq():
    return [
        "AAPL","MSFT","NVDA","AMZN","META",
        "TSLA","GOOGL","ADBE","AVGO","COST"
    ]

# Combine and remove duplicates
tickers = list(set(sp500 + dow + nasdaq100))

results = []

st.info("Scanning S&P 500 + Dow + Nasdaq-100... Please wait.")

progress = st.progress(0)
total = len(tickers)

for i, ticker in enumerate(tickers):
    try:
        df = yf.download(ticker, period="6mo", progress=False)

        if len(df) < 200:
            continue

        df["50MA"] = df["Close"].rolling(50).mean()
        df["200MA"] = df["Close"].rolling(200).mean()
        df["RSI"] = rsi(df["Close"])

        latest = df.iloc[-1]
        prev_close = df["Close"].iloc[-2]
        percent_change = ((latest["Close"] - prev_close) / prev_close) * 100

        score = 0
        direction = "Neutral"

        if latest["Close"] > latest["50MA"]:
            score += 25
        if latest["Close"] > latest["200MA"]:
            score += 25
        if 40 < latest["RSI"] < 70:
            score += 25
        if df["Volume"].iloc[-1] > df["Volume"].rolling(20).mean().iloc[-1]:
            score += 25

        if latest["Close"] > latest["50MA"] and latest["RSI"] > 50:
            direction = "Bullish"
        elif latest["Close"] < latest["50MA"] and latest["RSI"] < 50:
            direction = "Bearish"

        results.append({
            "Ticker": ticker,
            "Price": round(latest["Close"], 2),
            "% Change": round(percent_change, 2),
            "Score": score,
            "Direction": direction
        })

    except:
        pass

    progress.progress((i + 1) / total)

df_results = pd.DataFrame(results)

gainers = df_results.sort_values("% Change", ascending=False)
losers = df_results.sort_values("% Change")
scored = df_results.sort_values("Score", ascending=False)

st.header("🔥 Top 20 Gainers Today")
st.dataframe(gainers.head(20))

st.header("🔻 Top 20 Losers Today")
st.dataframe(losers.head(20))

st.header("📈 Strongest Options Setups (Score 75+)")
st.dataframe(scored[scored["Score"] >= 75].head(20))

st.header("🔻 Bearish / Put Candidates")
st.dataframe(scored[scored["Direction"] == "Bearish"].head(20))

st.caption("Educational use only. Not financial advice.")
