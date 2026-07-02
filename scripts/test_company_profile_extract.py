import argparse
import pandas as pd

from extractors.company_profile_extractor import extract_company_profiles


def parse_args():
    # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(
        description="Test company profile extraction from yfinance."
    )

    # 指定要測試抓取的 ticker 清單
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NVDA", "TSM"],
        help="Ticker list, example: --tickers AAPL MSFT NVDA TSM",
    )

    return parser.parse_args()


def build_preview_df(profiles):
    # 將 raw profile 中目前關心的欄位整理成預覽表
    rows = []

    for ticker, info in profiles.items():
        rows.append(
            {
                "ticker": ticker,
                "company_name": info.get("shortName") or info.get("longName"),
                "exchange": info.get("exchange"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "currency": info.get("currency") or info.get("financialCurrency"),
                "quote_type": info.get("quoteType"),
            }
        )

    return pd.DataFrame(rows)


def main():
    # 解析 CLI 參數
    args = parse_args()

    # Extract：抓取公司主檔原始資料
    profiles, failed_tickers = extract_company_profiles(args.tickers)

    print("\n========== Company Profile Extract Test ==========")
    print(f"Total tickers: {len(args.tickers)}")
    print(f"Success tickers: {len(profiles)}")
    print(f"Failed tickers: {len(failed_tickers)}")

    if profiles:
        preview_df = build_preview_df(profiles)

        print("\nPreview:")
        print(preview_df.to_string(index=False))

        print("\nRaw keys sample:")
        first_ticker = next(iter(profiles))
        print(f"{first_ticker}:")
        print(list(profiles[first_ticker].keys())[:50])

    if failed_tickers:
        print("\nFailed:")
        for ticker, reason in failed_tickers.items():
            print(f"- {ticker}: {reason}")

    print("==================================================\n")


if __name__ == "__main__":
    main()