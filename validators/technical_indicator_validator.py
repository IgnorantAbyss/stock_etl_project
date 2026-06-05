import pandas as pd


def validate_technical_indicators(df: pd.DataFrame) -> None:
    """
    驗證 technical_indicators DataFrame 是否符合入庫前基本品質要求。
    """

    required_columns = [
        "ticker",
        "trade_date",
        "sma_5",
        "sma_20",
        "sma_60",
        "volume_avg_20d",
        "volume_ratio_20d",
        "source",
    ]

    errors = []

    # 建立檢查欄位清單，用以確認 Transform 後的 DataFrame
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        errors.append(f"缺少必要欄位: {missing_columns}")

    # 欄位缺失時先中止後續檢查，避免 KeyError 干擾真正錯誤
    if errors:
        raise ValueError("\n".join(errors))

    # 確認 ticker 有值，避免無法對應股票代號
    if df["ticker"].isna().any():
        errors.append("ticker 不可為空")

    # 確認 trade_date 有值，避免無法形成時間序列主鍵
    if df["trade_date"].isna().any():
        errors.append("trade_date 不可為空")

    # 確認 source 有值，保留資料來源追溯能力
    if df["source"].isna().any():
        errors.append("source 不可為空")

    # 確認 ticker + trade_date 不重複，避免 upsert 主鍵衝突來源不明
    # df.duplicated會產出[True,False...] 若有重複主鍵產True否則False
    # df[True...]會產出True的index之資料列
    duplicated_rows = df[df.duplicated(subset=["ticker", "trade_date"], keep=False)]
    # 檢查是否有主鍵衝突資料列
    if not duplicated_rows.empty:
        errors.append(
            "ticker + trade_date 不可重複，重複筆數: "
            f"{len(duplicated_rows)}"
        )

    # volume_avg_20d 若有值，應符合成交量平均值不為負的基本邏輯
    invalid_volume_avg = df[
        df["volume_avg_20d"].notna() & (df["volume_avg_20d"] < 0)
    ]

    if not invalid_volume_avg.empty:
        errors.append(
            "volume_avg_20d 若有值，必須 >= 0，異常筆數: "
            f"{len(invalid_volume_avg)}"
        )

    # volume_ratio_20d 若有值，應符合成交量比率不為負的基本邏輯
    invalid_volume_ratio = df[
        df["volume_ratio_20d"].notna() & (df["volume_ratio_20d"] < 0)
    ]

    if not invalid_volume_ratio.empty:
        errors.append(
            "volume_ratio_20d 若有值，必須 >= 0，異常筆數: "
            f"{len(invalid_volume_ratio)}"
        )

    # 收集所有錯誤訊息，避免每次只能針對單點除錯
    if errors:
        raise ValueError("\n".join(errors))