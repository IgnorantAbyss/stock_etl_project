# 匯入 yfinance，用來取得 Yahoo Finance 行情資料
import yfinance as yf


def yfinance_extract(tickers):
    # 收集成功取得資料的 ticker DataFrame
    dfs = {}

    # 收集抓取失敗或無資料的 ticker
    failed_tickers = {}

    # 逐支 ticker 抓取資料，避免單一失敗影響整批
    for ticker in tickers:
        try:
            # 從 yfinance 取得單支股票最近一個月日線資料
            df = yf.download(
                tickers=ticker,
                period="1mo",
                interval="1d",
                auto_adjust=False,
            )

            # 空資料代表 ticker 可能錯誤或來源暫時無資料
            if df.empty:
                failed_tickers[ticker] = "yfinance 回傳空資料"
                continue

            # 以 ticker 作為 key，保留原始資料與股票代號的對應
            dfs[ticker] = df

        except Exception as e:
            # 記錄單支 ticker 錯誤，避免中斷整批任務
            failed_tickers[ticker] = str(e)

    # 回傳成功資料與失敗紀錄
    return dfs, failed_tickers