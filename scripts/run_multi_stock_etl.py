from datetime import date

from extractors.yfinance_extractor import yfinance_extract
from transformers.daily_price_transformer import daily_price_transform
from validators.daily_price_validator import validate_daily_prices
from loaders.daily_price_loader import upsert_daily_prices


def print_etl_summary(summary):
    # 印出批次任務摘要標題
    print("\n========== Multi Stock ETL Summary ==========")

    if summary['start_date']:
        print('Extract起始日:', summary['start_date'])
    if summary['end_date']:
        print('Extract結束日:', summary['end_date'])

    # 顯示本次預計處理的 ticker 數量
    print(f"Total tickers: {summary['total_tickers']}")

    # 顯示成功 ticker 數量
    print(f"Success tickers: {len(summary['success_tickers'])}")

    # 顯示失敗 ticker 數量
    print(f"Failed tickers: {len(summary['failed_tickers'])}")

    # 顯示 Transform 後總筆數
    print(f"Transformed rows: {summary['transformed_rows']}")

    # 顯示 Upsert 實際影響筆數
    print(f"Affected rows: {summary['affected_rows']}")

    # 印出成功 ticker 明細
    print("\nSuccess:")
    for ticker in summary["success_tickers"]:
        raw_rows = summary["raw_rows_by_ticker"].get(ticker, 0)
        print(f"- {ticker}: raw rows = {raw_rows}")

    # 印出失敗 ticker 明細
    if summary["failed_tickers"]:
        print("\nFailed:")
        for ticker, reason in summary["failed_tickers"].items():
            print(f"- {ticker}: {reason}")
    
    
    # 印出批次任務摘要結尾
    print("============================================\n")


def main():
    # 建立本次批次 ETL 要處理的 ticker 清單
    tickers = ["TSM", "FAKE123", "AAPL", "MSFT", "NVDA"]

    

    # Extract：逐支 ticker 抓取 yfinance 原始資料
    start_date = "2026-01-01"
    end_date = ""
    effective_end_date = end_date or date.today().strftime("%Y-%m-%d")

    dfs, failed_tickers = yfinance_extract(
        tickers=tickers,
        start_date=start_date,
        end_date=effective_end_date,
    )
    # 建立本次 ETL 任務摘要
    summary = {
        "total_tickers": len(tickers),
        "success_tickers": [],
        "failed_tickers": {},
        "raw_rows_by_ticker": {},
        "transformed_rows": 0,
        "affected_rows": 0,
        "start_date": start_date,
        "end_date": effective_end_date,
    }

    # 記錄 Extract 失敗 ticker
    summary["failed_tickers"] = failed_tickers

    # 記錄 Extract 成功 ticker
    summary["success_tickers"] = list(dfs.keys())

    # 記錄每支 ticker 抓到的 raw rows
    summary["raw_rows_by_ticker"] = {
        ticker: len(raw_df) for ticker, raw_df in dfs.items()
    }

    # Transform：將多支 ticker raw data 合併成 daily_prices 格式
    df = daily_price_transform(dfs)

    # 記錄 Transform 後總筆數
    summary["transformed_rows"] = len(df)

    # 若沒有任何可寫入資料，印出摘要後結束
    if df.empty:
        print_etl_summary(summary)
        return

    # Validate：檢查 daily_prices 資料品質
    validate_daily_prices(df)

    # Load：使用 upsert 寫入 PostgreSQL
    affected_rows = upsert_daily_prices(df)

    # 記錄本次實際新增或更新筆數
    summary["affected_rows"] = len(affected_rows)

    # 印出本次 ETL 任務摘要
    print_etl_summary(summary)


if __name__ == "__main__":
    main()