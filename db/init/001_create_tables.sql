-- db/init/001_create_tables.sql
-- 這個 SQL 會在 PostgreSQL container 第一次初始化時自動執行。
-- 注意：只有資料庫資料夾是空的時候才會自動執行。
-- 如果 .docker/postgres-data 已經存在，修改這個檔案不會自動重新套用。

CREATE TABLE IF NOT EXISTS daily_prices (
    -- 股票代號，例如 AAPL、NVDA、MSFT。
    ticker TEXT NOT NULL,

    -- 交易日期，例如 2026-05-22。
    trade_date DATE NOT NULL,

    -- 開盤價。
    open_price NUMERIC(18, 6),

    -- 最高價。
    high_price NUMERIC(18, 6),

    -- 最低價。
    low_price NUMERIC(18, 6),

    -- 收盤價。
    close_price NUMERIC(18, 6),

    -- 還原收盤價，用來處理配息、拆股後的可比較價格。
    adjusted_close NUMERIC(18, 6),

    -- 成交量，代表當天成交股數。
    volume BIGINT,

    -- 資料來源，例如 alpha_vantage、yfinance、fmp。
    source TEXT NOT NULL,

    -- 這筆資料寫入資料庫的時間。
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 同一支股票同一天只能有一筆行情。
    PRIMARY KEY (ticker, trade_date)
);