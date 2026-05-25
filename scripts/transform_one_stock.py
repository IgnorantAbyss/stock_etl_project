# scripts/transform_one_stock.py

# 匯入 yfinance，用來從 Yahoo Finance 取得股票行情資料。
import yfinance as yf
import pandas as pd


# 指定股票代號。
# TSM 是台積電在美股市場的 ADR ticker。
ticker = "TSM"


# 從 yfinance 下載最近 1 個月的每日行情資料。
# tickers=ticker：指定要抓哪一支股票。
# period="1mo"：抓最近 1 個月。
# interval="1d"：每日一筆資料。
# auto_adjust=False：保留 Close 與 Adj Close，方便我們分別存進資料庫。
df = yf.download(
    tickers=ticker,
    period="1mo",
    interval="1d",
    auto_adjust=False,
)


# 先印出原始欄位，觀察 yfinance 回傳格式。
# 你目前看到的是 MultiIndex：
# ('Open', 'TSM')
# ('High', 'TSM')
# ...
print("=== 原始欄位 ===")
print(df.columns)


# df.columns.nlevels 代表欄位有幾層。
# 一般單層欄位會是 1。
# MultiIndex 欄位會大於 1。
#
# 你目前是：
# 第 1 層 Price：Open、High、Low、Close...
# 第 2 層 Ticker：TSM
#
# 因為現在一次只抓一支股票，所以第 2 層 Ticker 暫時是重複資訊。
# 我們把它拿掉，讓欄位變成單層欄位。
if df.columns.nlevels > 1:
    df.columns = df.columns.droplevel(1)


# yfinance 的 MultiIndex 原本有欄位軸名稱 Price。
# droplevel 後，pandas 可能仍然保留 columns.name = "Price"。
# 這會讓 print(df) 時看起來上方多一個 Price。
#
# 這行是把欄位軸名稱清掉。
# 注意：這不是刪除資料欄位，只是清除顯示用的欄位軸名稱。
df.columns.name = None
print("\n=== 修改columns.name ===")
print(df.head())


# 原本日期在 df.index 裡。
# 先把 index 的名稱設定成 trade_date。
# 這樣等一下 reset_index() 後，日期欄位就會直接叫 trade_date。
df.index.name = "trade_date"
print("\n=== 修改index.name ===")
print(df.head())

# reset_index() 會把 index 變成一般欄位。
# 原本：
# index = 日期
#
# 轉換後：
# trade_date 會成為一般欄位。
df = df.reset_index()
print("\n=== 轉換trade_date為一般欄位 ===")
print(df.head())

# 把 yfinance 的欄位名稱改成我們資料庫 daily_prices 使用的欄位名稱。
# 這是 Transform 的一部分：把外部資料來源格式改成內部標準格式。
df = df.rename(
    columns={
        "Open": "open_price",
        "High": "high_price",
        "Low": "low_price",
        "Close": "close_price",
        "Adj Close": "adjusted_close",
        "Volume": "volume",
    }
)


# 新增 ticker 欄位。
# 因為資料庫每一筆資料都要知道這筆價格屬於哪一支股票。
df["ticker"] = ticker


# 新增 source 欄位。
# 之後如果資料來自 Alpha Vantage、FMP、SEC 等來源，
# 可以用 source 追蹤這筆資料從哪裡來。
df["source"] = "yfinance"


# trade_date 目前通常是 pandas Timestamp，例如：
# 2026-05-01 00:00:00
#
# .dt.date 會把它轉成純日期：
# 2026-05-01
#
# 這樣比較符合 PostgreSQL DATE 欄位。
df["trade_date"] = df["trade_date"].dt.date


# 調整欄位順序。
# 讓 DataFrame 的欄位順序跟 daily_prices 資料表接近。
df = df[
    [
        "ticker",
        "trade_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume",
        "source",
    ]
]

# 印出整理後資料。
print("\n=== 整理後資料 ===")
print(df.head())



from validators.daily_price_validator import validate_daily_prices
validate_daily_prices(df)

print("資料品質檢查通過，可以進入下一步 Load。")

from loaders.daily_price_loader import test_database_connection, load_daily_prices
print(test_database_connection())

inserted_count = load_daily_prices(df)

print(f"資料寫入完成，共寫入 {inserted_count} 筆資料。")

