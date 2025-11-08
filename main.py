import streamlit as st
import ccxt
import pandas as pd
import ta
import time
import os
from datetime import datetime

st.title("🤖 BingX Demo Trading Bot (RSI Strategy)")

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")

if not API_KEY or not API_SECRET:
    st.error("❌ Faltan las claves API. Configúralas en 'Secrets' en Streamlit Cloud.")
    st.stop()

exchange = ccxt.bingx({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'},
    'urls': {
        'api': {
            'public': 'https://open-api-vst.bingx.com/openApi',
            'private': 'https://open-api-vst.bingx.com/openApi',
        }
    }
})

symbol = 'BTC-USDT'
timeframe = '1m'
rsi_low = 30
rsi_high = 70
rsi_window = 14
tamaño_operacion = 0.001

st.sidebar.header("⚙️ Configuración")
rsi_low = st.sidebar.slider("RSI mínimo (BUY)", 10, 50, 30)
rsi_high = st.sidebar.slider("RSI máximo (SELL)", 50, 90, 70)

if st.button("▶️ Iniciar Bot"):
    st.write("Bot corriendo... (1 iteración de ejemplo)")

    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp','open','high','low','close','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=rsi_window).rsi()
        last_rsi = df['rsi'].iloc[-1]
        price = df['close'].iloc[-1]

        st.line_chart(df[['close','rsi']].set_index(df['timestamp']))

        if last_rsi <= rsi_low:
            st.success(f"🟢 Señal de COMPRA detectada | RSI={last_rsi:.2f}")
        elif last_rsi >= rsi_high:
            st.error(f"🔴 Señal de VENTA detectada | RSI={last_rsi:.2f}")
        else:
            st.info(f"⏸️ Sin acción | RSI={last_rsi:.2f}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
