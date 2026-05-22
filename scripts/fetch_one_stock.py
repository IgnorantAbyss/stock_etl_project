# scripts/fetch_one_stock.py

# 匯入 yfinance 套件。
# yfinance 的用途是向 Yahoo Finance 取得股票行情資料。
# 這裡先用它來抓每日 OHLCV，方便我們觀察資料長相。
import yfinance as yf


# 指定要查詢的股票代號。
# AAPL 是 Apple Inc. 在美股市場上的 ticker。
ticker = "TSM"


# 使用 yf.download() 下載股票歷史行情。
# ticker=ticker：指定要下載哪一支股票。
# period="1mo"：代表下載最近 1 個月資料。
# interval="1d"：代表資料粒度是每日一筆。
# auto_adjust=False：保留原始 Close 與 Adj Close，方便我們理解兩者差異。
df = yf.download(
    tickers=ticker,
    period="1mo",
    interval="1d",
    auto_adjust=False,
)


# 印出前 5 筆資料。
# 觀察 yfinance 回傳的資料欄位與資料格式。
print("=== 前 5 筆資料 ===")
print(df.head())


# 印出欄位名稱。
# 目的：確認抓回來有哪些欄位，例如 Open、High、Low、Close、Adj Close、Volume。
print("\n=== 欄位名稱 ===")
print(df.columns)
# print(df['Adj Close'])


# 印出資料筆數。
# 目的：確認這次實際抓到幾個交易日的資料。
print("\n=== 資料筆數 ===")
print(len(df))


# 印出索引資訊。
# yfinance 回傳的日期通常會放在 DataFrame index 裡，而不是一般欄位。
# 之後我們會把 index 轉成 trade_date 欄位。
print("\n=== index 資訊 ===")
print(df.index)
date = df.index
# 逐筆取出資料 了解資料格式
for i in date:
    d = i
    o = df.loc[d,("Open", "TSM")]
    h = df.loc[d,('High', "TSM")]
    l = df.loc[d,('Low', "TSM")]
    c = df.loc[d,('Close', "TSM")]
    ac = df.loc[d,('Adj Close', "TSM")]
    v = df.loc[d,('Volume', "TSM")]
    print(f'日期: {d.date()}, Open: {o}, High: {h}, Low: {l}, Close: {c}, Adj Close: {ac}, Volume: {v}\n')