import argparse
import pandas as pd
from sqlalchemy import select

from db.database import engine
from db.models import DailyPrice, Company
from extractors.company_profile_extractor import extract_company_profiles
from transformers.company_profile_transformer import transform_company_profiles
from validators.company_profile_validator import validate_company_profiles
from loaders.company_profile_loader import upsert_company_profiles


def parse_args():
    # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(
        description="Run company profile ETL."
    )

    # 指定要處理的股票清單；未指定時從 daily_prices 讀取現有 ticker
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Ticker list, example: --tickers AAPL MSFT NVDA TSM",
    )

    return parser.parse_args()


def read_distinct_tickers_from_daily_prices():
    # 從 daily_prices 讀取目前已有行情資料的 ticker
    stmt = (
        select(DailyPrice.ticker)
        .distinct()
        .order_by(DailyPrice.ticker)
    )

    # 將查詢結果轉成 DataFrame
    df = pd.read_sql(stmt, con=engine)

    # 回傳 ticker list
    return df["ticker"].tolist()


def read_companies_after_upsert():
    # 查詢 companies 寫入後結果，用於摘要檢查
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

    # 將 companies 查詢結果轉成 DataFrame
    return pd.read_sql(stmt, con=engine)


def print_company_profile_etl_summary(summary):
    # 印出任務摘要標題
    print("\n========== Company Profile ETL Summary ==========")

    print(f"Ticker source: {summary['ticker_source']}")
    print(f"Total tickers: {summary['total_tickers']}")
    print(f"Extract success: {summary['extract_success']}")
    print(f"Extract failed: {summary['extract_failed']}")
    print(f"Transformed rows: {summary['transformed_rows']}")
    print(f"Affected rows: {summary['affected_rows']}")

    if summary["success_tickers"]:
        print("\nSuccess:")
        for ticker in summary["success_tickers"]:
            print(f"- {ticker}")

    if summary["failed_tickers"]:
        print("\nFailed:")
        for ticker, reason in summary["failed_tickers"].items():
            print(f"- {ticker}: {reason}")

    print("=================================================\n")


def main():
    # 解析 CLI 參數
    args = parse_args()

    # 有指定 tickers 時使用 CLI；否則從 daily_prices 取得現有 ticker
    if args.tickers:
        tickers = args.tickers
        ticker_source = "CLI"
    else:
        tickers = read_distinct_tickers_from_daily_prices()
        ticker_source = "daily_prices"

    # 建立任務摘要
    summary = {
        "ticker_source": ticker_source,
        "total_tickers": len(tickers),
        "extract_success": 0,
        "extract_failed": 0,
        "transformed_rows": 0,
        "affected_rows": 0,
        "success_tickers": [],
        "failed_tickers": {},
    }

    # 若沒有任何 ticker，印出摘要後結束
    if not tickers:
        print_company_profile_etl_summary(summary)
        return

    # Extract：取得公司主檔 raw profile
    profiles, failed_tickers = extract_company_profiles(tickers)

    summary["extract_success"] = len(profiles)
    summary["extract_failed"] = len(failed_tickers)
    summary["success_tickers"] = list(profiles.keys())
    summary["failed_tickers"] = failed_tickers

    # Transform：轉成 companies schema
    companies_df = transform_company_profiles(profiles)

    summary["transformed_rows"] = len(companies_df)

    # 若沒有可寫入資料，印出摘要後結束
    if companies_df.empty:
        print_company_profile_etl_summary(summary)
        return

    # Validate：檢查 companies 資料品質
    validate_company_profiles(companies_df)

    # Load：upsert 寫入 companies
    affected_rows = upsert_company_profiles(companies_df)

    summary["affected_rows"] = len(affected_rows)

    # 印出 ETL summary
    print_company_profile_etl_summary(summary)

    # 額外印出目前 companies table，方便第一次執行時檢查
    companies_after_upsert = read_companies_after_upsert()

    print("Companies table preview:")
    print(companies_after_upsert.to_string(index=False))


if __name__ == "__main__":
    main()