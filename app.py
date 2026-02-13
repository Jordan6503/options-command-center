import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Options Command Center", layout="wide")
st.title("📈 Options Command Center")

# Combined Universe (S&P + Dow + Nasdaq sample large caps)
TICKERS = list(set([
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA",
    "BRK-B","JPM","V","UNH","HD","PG","MA","DIS",
    "BAC","XOM","KO","PFE","PEP","INTC","IBM",
    "GS","MCD","NKE","BA","ADBE","AVGO","COST"
]))

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_market():
    results = []

    for ticker in TICKERS:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if len(hist) < 50:
                continue

            close = hist["Close"]
            rsi = calculate_rsi(close).iloc[-1]

            daily_change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
            five_day_change = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]) * 100

            ma50 = close.rolling(50).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else ma50

            # Classification Logic
            if abs(daily_change) > 2 and rsi > 55:
                category = "⚡ Day Trade Call"
            elif abs(daily_change) > 2 and rsi < 45:
                category = "⚡ Day Trade Put"
            elif five_day_change > 3 and rsi > 50:
                category = "🔄 Swing Call"
            elif five_day_change < -3 and rsi < 50:
                category = "🔄 Swing Put"
            elif ma50 > ma200:
                category = "🏦 Long-Term Bullish"
            else:
                category = "🏦 Long-Term Bearish"

            results.append([
                ticker,
                round(daily_change,2),
                round(five_day_change,2),
                round(rsi,2),
                category
            ])

        except:
            continue

    df = pd.DataFrame(results, columns=[
        "Ticker",
        "Daily %",
        "5-Day %",
        "RSI",
        "Signal"
    ])

    return df.sort_values(by="Daily %", ascending=False)

df = scan_market()

st.subheader("📈 Top Gainers")
st.dataframe(df.sort_values(by="Daily %", ascending=False).head(5))

st.subheader("📉 Top Losers")
st.dataframe(df.sort_values(by="Daily %").head(5))

st.subheader("⚡ Day Trade Setups")
st.dataframe(df[df["Signal"].str.contains("Day Trade")])

st.subheader("🔄 Swing Trade Setups")
st.dataframe(df[df["Signal"].str.contains("Swing")])

st.subheader("🏦 Long-Term Options Holds")
st.dataframe(df[df["Signal"].str.contains("Long-Term")])

st.success("Scan Complete")
