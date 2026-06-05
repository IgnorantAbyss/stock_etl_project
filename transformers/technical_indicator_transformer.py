import pandas as pd

def calculate_technical_indicators(df):
    # 建立副本避免修改原資料
    price_df = df.copy()
    # 排序
    price_df = price_df.sort_values(['ticker','trade_date'])

    # 每支股票各自計算 5 日收盤價均線
    price_df['sma_5'] = (
        # 依照ticker groupby 並取close price
        price_df
        .groupby('ticker')['close_price']
        # transform 會把groupby的資料按key 分批傳入lambda
        .transform(lambda s:s.rolling(window=5).mean())
        )
    # 每支股票各自計算 20 日收盤價均線
    price_df['sma_20'] = (
        # 依照ticker groupby 並取close price
        price_df
        .groupby('ticker')['close_price']
        # transform 會把groupby的資料按key 分批傳入lambda
        .transform(lambda s:s.rolling(window=20).mean())
        )
    # 每支股票各自計算 60 日收盤價均線
    price_df['sma_60'] = (
        # 依照ticker groupby 並取close price
        price_df
        .groupby('ticker')['close_price']
        # transform 會把groupby的資料按key 分批傳入lambda
        .transform(lambda s:s.rolling(window=60).mean())
        )
    # 每支股票各自計算 20 日平均成交量
    price_df['volume_avg_20d'] = (
        # 依照ticker groupby 並取close price
        price_df
        .groupby('ticker')['volume']
        # transform 會把groupby的資料按key 分批傳入lambda
        .transform(lambda s:s.rolling(window=20).mean())
        )
    # 計算當日成交量相對 20 日均量倍率
    # 逐列計算
    # df["固定欄位"] = 固定值 → 整欄同一個值；
    # df["新欄位"] = df["欄位A"] / df["欄位B"] → Pandas 依 index 逐列計算。
    price_df['volume_ratio_20d'] = (
        price_df['volume'] / price_df['volume_avg_20d']
        )
    
    # 一層 []：通常取單一欄位，回傳 Series
    # 兩層 [[]]：取多個欄位，回傳 DataFrame
    result = price_df[
        [
            "ticker",
            "trade_date",
            "sma_5",
            "sma_20",
            "sma_60",
            "volume_avg_20d",
            "volume_ratio_20d",
            "source"
        ]
    ]

    return result

