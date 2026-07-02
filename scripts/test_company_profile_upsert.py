import argparse
import pandas as pd
from sqlalchemy import select

from db.database import engine
from db.models import Company
from extractors.company_profile_extractor import extract_company_profiles
from transformers.company_profile_transformer import transform_company_profiles
from validators.company_profile_validator import validate_company_profiles
from loaders.company_profile_loader import upsert_company_profiles


def parse_args():
    # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(
        description="Test company profile upsert."
    )

    # 指定要測試寫入的 ticker 清單
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NVDA", "TSM"],
        help="Ticker list, example: --tickers AAPL MSFT NVDA TSM",
    )

    return parser.parse_args()


def read_companies_sample():
    # 建立 companies 查詢語句，確認 upsert 寫入結果
    stmt = (
        select(
            Company.ticker,
            Company.company_name,
            Company.exchange,
            Company.sector,
            Company.industry,
            Company.country,
            Company.currency,
            Company.is_active,
            Company.source,
            Company.created_at,
            Company.updated_at,
        )
        .order_by(Company.ticker)
    )

    # 將查詢結果轉成 DataFrame
    return pd.read_sql(stmt, con=engine)


def main():
    # 解析 CLI 參數
    args = parse_args()

    # Extract：取得公司主檔 raw profile
    profiles, failed_tickers = extract_company_profiles(args.tickers)

    # Transform：轉換成 companies schema
    companies_df = transform_company_profiles(profiles)

    print("\n========== Company Profile Upsert Test ==========")
    print(f"Input tickers: {len(args.tickers)}")
    print(f"Extract success: {len(profiles)}")
    print(f"Extract failed: {len(failed_tickers)}")
    print(f"Transformed rows: {len(companies_df)}")

    if companies_df.empty:
        print("No company profiles to upsert.")
        return

    # Validate：檢查 companies 資料品質
    validate_company_profiles(companies_df)
    print("Validation passed")

    # Load：寫入 companies
    affected_rows = upsert_company_profiles(companies_df)
    print(f"Affected rows: {len(affected_rows)}")

    if affected_rows:
        affected_df = pd.DataFrame(affected_rows)
        print("\nAffected rows:")
        print(affected_df.to_string(index=False))
    else:
        print("\nNo rows inserted or updated. Data may already be up to date.")

    # 查詢 companies 寫入後資料
    sample_df = read_companies_sample()

    print("\nCompanies table:")
    print(sample_df.to_string(index=False))

    if failed_tickers:
        print("\nFailed:")
        for ticker, reason in failed_tickers.items():
            print(f"- {ticker}: {reason}")

    print("=================================================\n")


if __name__ == "__main__":
    main()