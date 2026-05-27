import pandas as pd


def daily_price_transform(dfs):
    # 收集每支 ticker 轉換後的 DataFrame
    frames = []

    # 逐支 ticker 處理 raw DataFrame
    for ticker, raw_df in dfs.items():
        # 使用副本進行轉換，避免修改 Extract 原始資料
        df = raw_df.copy()

        # 空資料不進行轉換
        if df.empty:
            continue

        # 移除 yfinance MultiIndex 中的 ticker 層級
        if df.columns.nlevels > 1:
            df.columns = df.columns.droplevel(1)

        # 清除欄位軸名稱，避免殘留 Price 顯示
        df.columns.name = None

        # 將日期 index 命名為 trade_date
        df.index.name = "trade_date"

        # 將日期 index 轉成一般欄位
        df = df.reset_index()

        # 將 yfinance 欄位名稱轉成 daily_prices 欄位名稱
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

        # 新增股票代號欄位
        df["ticker"] = ticker

        # 新增資料來源欄位
        df["source"] = "yfinance"

        # 將 timestamp 日期轉成純 date
        df["trade_date"] = df["trade_date"].dt.date

        # 調整成 daily_prices 寫入順序
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

        # 收集本支 ticker 轉換結果
        frames.append(df)
        print(ticker,'共有:',len(df),'筆資料')

    # 若沒有任何成功轉換資料，回傳空 DataFrame
    if not frames:
        return pd.DataFrame()

    # 一次合併所有 ticker 的轉換結果
    result = pd.concat(frames, ignore_index=True)

    # 回傳多 ticker daily_prices DataFrame
    return result