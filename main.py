import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt

tickers = {
    'apple': 'AAPL',
    'facebook': 'META',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'netflix': 'NFLX',
    'amazon': 'AMZN',
    'TOTO': '5332.T',
    'TOYOTA': '7203.T',
}

st.title('株価可視化アプリ')

st.sidebar.write("こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。")

# 対応する期間のリストを定義
valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y']

# ドロップダウンリストで選択できるようにする
selected_period = st.sidebar.selectbox('表示期間', valid_periods)

st.write(f"選択された期間: {selected_period}")

@st.cache_data
def get_data(period, tickers):
    df = pd.DataFrame()

    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=period)
        hist.index = pd.to_datetime(hist.index)
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

df = get_data(selected_period, tickers)

companies = st.multiselect(
    '会社名を選択してください。',
    list(df.index),
    ['google', 'apple','TOYOTA'],
)

data = df.loc[companies]
data = data.T.reset_index()

data = pd.melt(data, id_vars=['Date']).rename(
    columns={'value': 'Stock Prices'}
)

ymin, ymax = st.slider(
    '範囲を指定してください。',
    0.0, 5000.0, (0.0, 5000.0)
)

chart = (
    alt.Chart(data)
    .mark_line(opacity=0.8, clip=True)
    .encode(
        x="Date:T",
        y=alt.Y("Stock Prices:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
        color='Name:N'
    )
)

st.altair_chart(chart, use_container_width=True)
