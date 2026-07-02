import pandas as pd


def transform_company_profiles(profiles: dict) -> pd.DataFrame:
    # 收集轉換後的公司主檔資料
    rows = []

    for ticker, info in profiles.items():
        # 從 raw profile 中抽取 companies table 需要的欄位
        row = {
            "ticker": ticker,
            "company_name": info.get("shortName") or info.get("longName"),
            "exchange": info.get("exchange"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "currency": info.get("currency") or info.get("financialCurrency"),
            "is_active": True,
            "source": "yfinance",
        }

        rows.append(row)

    # 將標準化後的公司主檔資料轉成 DataFrame
    return pd.DataFrame(rows)