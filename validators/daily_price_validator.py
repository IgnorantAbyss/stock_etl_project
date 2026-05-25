def validate_daily_prices(df):
    # 建立檢查欄位清單，用以確認 Transform 後的 DataFrame 符合 daily_prices 格式
    required_columns = [
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

    # 收集所有錯誤訊息，避免每次只能針對單點進行除錯
    errors = []

    # 找出 DataFrame 中缺少的必要欄位
    missing_columns = [col for col in required_columns if col not in df.columns]

    # 缺少必要欄位時，後續檢查無法安全執行，直接中止
    if missing_columns:
        raise ValueError(f"缺少必要欄位：{missing_columns}")

    # ticker 是股票識別欄位，不可為空
    if df["ticker"].isna().any():
        # df["ticker"].isna()會產生一個Ture/False遮罩
        # 傳入給df可以把True列資料取出 取得其index後轉換為list
        bad_rows = df[df["ticker"].isna()].index.tolist()
        errors.append(f"ticker 有空值，出錯列 index：{bad_rows}")

    # trade_date 是每日行情日期，也是主鍵組成之一，不可為空
    if df["trade_date"].isna().any():
        bad_rows = df[df["trade_date"].isna()].index.tolist()
        errors.append(f"trade_date 有空值，出錯列 index：{bad_rows}")

    # 建立核心價格欄位清單，用以檢查 OHLC 是否完整
    price_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
    ]

    # 逐一檢查 OHLC 欄位是否有空值
    for col in price_columns:
        if df[col].isna().any():
            bad_rows = df[df[col].isna()].index.tolist()
            errors.append(f"{col} 有空值，出錯列 index：{bad_rows}")

    # volume 是成交量欄位，不可為空
    if df["volume"].isna().any():
        bad_rows = df[df["volume"].isna()].index.tolist()
        errors.append(f"volume 有空值，出錯列 index：{bad_rows}")

    # 成交量不應為負數
    if (df["volume"] < 0).any():
        bad_rows = df[df["volume"] < 0].index.tolist()
        errors.append(f"volume 不可小於 0，出錯列 index：{bad_rows}")

    # 最高價不可小於最低價
    if (df["high_price"] < df["low_price"]).any():
        bad_rows = df[df["high_price"] < df["low_price"]].index.tolist()
        errors.append(f"high_price 不可小於 low_price，出錯列 index：{bad_rows}")

    # 最高價不可小於開盤價
    if (df["high_price"] < df["open_price"]).any():
        bad_rows = df[df["high_price"] < df["open_price"]].index.tolist()
        errors.append(f"high_price 不可小於 open_price，出錯列 index：{bad_rows}")

    # 最高價不可小於收盤價
    if (df["high_price"] < df["close_price"]).any():
        bad_rows = df[df["high_price"] < df["close_price"]].index.tolist()
        errors.append(f"high_price 不可小於 close_price，出錯列 index：{bad_rows}")

    # 最低價不可大於開盤價
    if (df["low_price"] > df["open_price"]).any():
        bad_rows = df[df["low_price"] > df["open_price"]].index.tolist()
        errors.append(f"low_price 不可大於 open_price，出錯列 index：{bad_rows}")

    # 最低價不可大於收盤價
    if (df["low_price"] > df["close_price"]).any():
        bad_rows = df[df["low_price"] > df["close_price"]].index.tolist()
        errors.append(f"low_price 不可大於 close_price，出錯列 index：{bad_rows}")

    # 檢查 ticker + trade_date 是否違反每日行情唯一性
    # duplicated檢查 以subset為組合 是否有重複資料列
    # keep=False表示 只要是重複群組裡面的資料，全部標成 True。 
    # 如果是預設(first) 只會標記第二筆
    duplicated_mask = df.duplicated(subset=["ticker", "trade_date"], keep=False)

    # 重複資料會影響 PostgreSQL 主鍵與後續 upsert 判斷
    if duplicated_mask.any():
        # df.loc[列條件, 欄位條件]
        # 取出True列的"ticker", "trade_date"
        duplicated_rows = df.loc[duplicated_mask, ["ticker", "trade_date"]]
        duplicated_text = duplicated_rows.to_string(index=True)
        errors.append(f"ticker + trade_date 不可重複，重複資料如下：\n{duplicated_text}")

    # 若存在任一品質錯誤，阻止資料進入 Load 階段
    if errors:
        raise ValueError("\n\n".join(errors))

    # 所有檢查通過，回傳 True 給主流程判斷
    return True