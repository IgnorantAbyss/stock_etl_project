import argparse

from extractors.company_profile_extractor import extract_company_profiles
from transformers.company_profile_transformer import transform_company_profiles
from validators.company_profile_validator import validate_company_profiles


def parse_args():
    # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(
        description="Test company profile validation."
    )

    # 指定要測試驗證的 ticker 清單
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NVDA", "TSM"],
        help="Ticker list, example: --tickers AAPL MSFT NVDA TSM",
    )

    return parser.parse_args()


def main():
    # 解析 CLI 參數
    args = parse_args()

    # Extract：取得公司主檔 raw profile
    profiles, failed_tickers = extract_company_profiles(args.tickers)

    # Transform：轉換成 companies schema
    companies_df = transform_company_profiles(profiles)

    print("\n========== Company Profile Validate Test ==========")
    print(f"Input tickers: {len(args.tickers)}")
    print(f"Extract success: {len(profiles)}")
    print(f"Extract failed: {len(failed_tickers)}")
    print(f"Transformed rows: {len(companies_df)}")

    if not companies_df.empty:
        # Validate：檢查 companies 資料品質
        validate_company_profiles(companies_df)
        print("Validation passed")

        print("\nValidated companies:")
        print(companies_df.to_string(index=False))

    if failed_tickers:
        print("\nFailed:")
        for ticker, reason in failed_tickers.items():
            print(f"- {ticker}: {reason}")

    print("===================================================\n")


if __name__ == "__main__":
    main()