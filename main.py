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


# チャートに表示する範囲をスライドで表示し、それぞれをymin, ymaxに代入
st.sidebar.write("株価の範囲指定") # サイドバーに表示
ymin, ymax = st.sidebar.slider(
    '範囲を指定してください。',
    0.0, 5000.0, (0.0, 5000.0)
) # サイドバーに表示


df = get_data(selected_period, tickers)

companies = st.multiselect(
    '会社名を選択してください。',
    list(df.index),
    ['google', 'apple','TOYOTA'],
)


data = df.loc[companies] # 取得したデータから抽出するための配列で絞ってdataに代入
st.write("株価 ", data.sort_index()) # dataにあるindexを表示
data = data.T.reset_index() # dataを抽出して転置

# 企業ごとの別々のカラムにデータを表示する必要ないので企業を１つのカラムに統一
data = pd.melt(data, id_vars=['Date']).rename(
    columns={'value': 'Stock Prices'}
)

# dataとスライドバーで設定した最大最小値を元にalt.Chartを使って株価チャートを作成
chart = (
    alt.Chart(data)
    .mark_line(opacity=0.8, clip=True)
    .encode(
        x="Date:T",
        y=alt.Y("Stock Prices:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
        color='Name:N'
    )
)

# 作成したチャートをstreamlitで表示
st.altair_chart(chart, use_container_width=True)
