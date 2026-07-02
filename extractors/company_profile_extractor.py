import yfinance as yf

def extract_company_profiles(tickers: list[str]):
    # 收集成功取得的公司原始資料
    profiles = {}

    # 收集失敗 ticker 與錯誤原因，避免單一失敗中斷整批
    failed_tickers = {}

    # 去除空白、轉大寫、移除重複 ticker
    normalized_tickers = list(
        dict.fromkeys(ticker.strip().upper() for ticker in tickers if ticker.strip())
    )

    for ticker in normalized_tickers:
        try:
            # 建立 yfinance ticker 物件
            stock = yf.Ticker(ticker)

            # 取得公司主檔原始資料
            info = stock.info

            # 防止資料來源回傳空資料
            if not isinstance(info, dict) or not info:
                failed_tickers[ticker] = "empty company profile"
                continue

            profiles[ticker] = info

        except Exception as e:
            failed_tickers[ticker] = str(e)

    return profiles, failed_tickers
