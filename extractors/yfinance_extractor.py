import yfinance as yf

from datetime import date


def yfinance_extract(
    tickers,
    period="1mo",
    interval="1d",
    start_date=None,
    end_date=None,
):
    # 收集成功取得資料的 ticker DataFrame
    dfs = {}

    # 收集抓取失敗或無資料的 ticker
    failed_tickers = {}

    # 逐支 ticker 抓取資料，避免單一失敗影響整批
    for ticker in tickers:
        try:
            # 有指定 start_date 時，使用日期區間模式
            if start_date:
                df = yf.download(
                    tickers=ticker,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    auto_adjust=False,
                )

            # 未指定 start_date 時，使用 period 模式
            else:
                df = yf.download(
                    tickers=ticker,
                    period=period,
                    interval=interval,
                    auto_adjust=False,
                )

            # 空資料代表 ticker 錯誤、區間無資料或來源暫時無資料
            if df.empty:
                failed_tickers[ticker] = "yfinance 回傳空資料"
                continue

            # 以 ticker 作為 key，保留原始資料與股票代號對應
            dfs[ticker] = df

        except Exception as e:
            # 記錄單支 ticker 錯誤，避免中斷整批任務
            failed_tickers[ticker] = str(e)

    # 回傳成功資料與失敗紀錄
    return dfs, failed_tickers