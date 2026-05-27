from extractors.yfinance_extractor import yfinance_extract
from transformers.daily_price_transformer import daily_price_transform
from validators.daily_price_validator import validate_daily_prices
from loaders.daily_price_loader import upsert_daily_prices


def main():
    # 建立第一版測試 ticker 清單
    tickers = ["TSM", "AAPL", "MSFT", "NVDA"]

    # Extract：逐支 ticker 抓取 yfinance 原始資料
    dfs, failed_tickers = yfinance_extract(tickers)

    # 顯示 Extract 失敗 ticker，方便批次任務除錯
    if failed_tickers:
        print("以下 ticker 抓取失敗：")
        for ticker, reason in failed_tickers.items():
            print(f"{ticker}: {reason}")

    # Transform：將多支 ticker raw data 合併成 daily_prices 格式
    df = daily_price_transform(dfs)

    # 若沒有任何可寫入資料，直接結束流程
    if df.empty:
        print("沒有可寫入資料，流程結束。")
        return

    # Validate：檢查 daily_prices 資料品質
    validate_daily_prices(df)

    # Load：使用 upsert 寫入 PostgreSQL
    affected_rows = upsert_daily_prices(df)

    # 顯示本次實際新增或更新筆數
    print(f"多股票 ETL 完成，共影響 {len(affected_rows)} 筆資料。")

    # 顯示本次實際新增或更新的 ticker/date
    for row in affected_rows:
        print(
            f"{row['ticker']} | {row['trade_date']} | "
            f"close={row['close_price']} | volume={row['volume']}"
        )


if __name__ == "__main__":
    main()