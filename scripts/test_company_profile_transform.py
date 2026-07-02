import argparse

from extractors.company_profile_extractor import extract_company_profiles
from transformers.company_profile_transformer import transform_company_profiles

def parse_args():
    # 建立CLI參數解析器
    parser = argparse.ArgumentParser(
        description='公司主檔transform測試'
    )

    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NVDA", "TSM"],
        help="Ticker list, example: --tickers AAPL MSFT NVDA TSM"
    )

    return parser.parse_args()

def main():
    # 解析CLI參數
    args = parse_args()

    company_profiles, failed_tickers = extract_company_profiles(args.tickers)

    companies_df = transform_company_profiles(company_profiles)

    print("\n========== Company Profile Transform Test ==========")
    print(f"Input tickers: {len(args.tickers)}")
    print(f"Extract success: {len(company_profiles)}")
    print(f"Extract failed: {len(failed_tickers)}")
    print(f"Transformed rows: {len(companies_df)}")

    if not companies_df.empty:
        print("\nTransformed companies:")
        print(companies_df.to_string(index=False))

        print("\nDtypes:")
        print(companies_df.dtypes)

    if failed_tickers:
        print("\nFailed:")
        for ticker, reason in failed_tickers.items():
            print(f"- {ticker}: {reason}")

    print("====================================================\n")


if __name__ == "__main__":
    main()