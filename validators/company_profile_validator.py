import pandas as pd


def validate_company_profiles(df: pd.DataFrame) -> None:
    """
    驗證 companies DataFrame 是否符合入庫前基本品質要求。
    """

    required_columns = [
        "ticker",
        "company_name",
        "exchange",
        "sector",
        "industry",
        "country",
        "currency",
        "is_active",
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

    # 確認 ticker 有值，避免無法建立公司主檔主鍵
    if df["ticker"].isna().any() or (df["ticker"].astype(str).str.strip() == "").any():
        errors.append("ticker 不可為空")

    # 確認 company_name 有值，避免主檔無法辨識公司名稱
    if df["company_name"].isna().any() or (df["company_name"].astype(str).str.strip() == "").any():
        errors.append("company_name 不可為空")

    # 確認 source 有值，保留資料來源追溯能力
    if df["source"].isna().any() or (df["source"].astype(str).str.strip() == "").any():
        errors.append("source 不可為空")

    # 確認 is_active 有值，避免追蹤狀態不明
    if df["is_active"].isna().any():
        errors.append("is_active 不可為空")

    # 確認 ticker 不重複，避免 upsert 主鍵來源不明
    duplicated_rows = df[df.duplicated(subset=["ticker"], keep=False)]

    if not duplicated_rows.empty:
        errors.append(
            "ticker 不可重複，重複筆數: "
            f"{len(duplicated_rows)}"
        )

    # currency 若有值，通常應為三碼幣別，例如 USD
    invalid_currency = df[
        df["currency"].notna()
        & (df["currency"].astype(str).str.len() != 3)
    ]

    if not invalid_currency.empty:
        errors.append(
            "currency 若有值，長度應為 3，異常筆數: "
            f"{len(invalid_currency)}"
        )

    # 收集所有錯誤訊息，避免每次只能針對單點除錯
    if errors:
        raise ValueError("\n".join(errors))