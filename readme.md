# 美股市場資料 ETL / Data Warehouse / Dashboard 專案

## 1. 專案簡介

本專案目標是建立一套可重跑、可追溯、可擴充的美股市場資料 ETL / Data Warehouse / Dashboard 系統。

目前已完成行情資料與技術指標資料的核心 ETL 流程，包含：

- 使用 Docker Compose 建立 PostgreSQL 開發環境
- 使用 yfinance 擷取美股 OHLCV 行情資料
- 將 raw market data 轉換為標準化 `daily_prices` schema
- 建立資料品質檢查 validator
- 使用 SQLAlchemy Core + PostgreSQL `ON CONFLICT` 實作 upsert
- 支援多股票批次處理、日期區間 backfill 與 CLI 參數化
- 建立 `technical_indicators` 衍生分析表
- 從 `daily_prices` 計算 SMA 與成交量指標
- 將 technical indicators validate 後 upsert 入 PostgreSQL
- 建立 technical indicators ETL CLI

本專案重點不是股票推薦，而是展示資料工程能力：Extract、Transform、Load、Data Quality、Backfill、Upsert、Observability、Data Warehouse 建模與後續排程 / Dashboard 擴充能力。

---

## 2. 專案目標

最終目標：

> 建立一套可重跑、可追溯、可擴充的美股資料 ETL 管線，整合行情、技術指標、公司主檔、財報、事件資料與新聞資料，透過 PostgreSQL 建立標準化資料模型，並使用 Airflow 排程與 Streamlit Dashboard 進行分析展示。

核心能力包含：

- Extract：從資料來源擷取資料
- Transform：清洗、標準化、欄位轉換與衍生指標計算
- Validate：入庫前資料品質檢查
- Load / Upsert：寫入 PostgreSQL 並支援可重跑
- Backfill：補載歷史日期區間資料
- Observability：任務摘要、成功 / 失敗紀錄、affected rows
- Data Warehouse：建立可分析的資料模型
- CLI：支援參數化執行
- Orchestration：後續使用 Airflow 排程
- Visualization：後續使用 Streamlit 建立 Dashboard
- Documentation：README、ERD、架構圖與面試說明

---

## 3. 目前專案結構

```text
stock-etl-project/
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   └── config.py
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── init/
│       ├── 001_create_tables.sql
│       └── 002_create_technical_indicators.sql
├── extractors/
│   ├── __init__.py
│   └── yfinance_extractor.py
├── transformers/
│   ├── __init__.py
│   ├── daily_price_transformer.py
│   └── technical_indicator_transformer.py
├── validators/
│   ├── __init__.py
│   ├── daily_price_validator.py
│   └── technical_indicator_validator.py
├── loaders/
│   ├── __init__.py
│   ├── daily_price_loader.py
│   └── technical_indicator_loader.py
├── scripts/
│   ├── run_multi_stock_etl.py
│   ├── check_daily_prices.py
│   ├── test_technical_indicator_transform.py
│   ├── test_technical_indicator_upsert.py
│   └── run_technical_indicator_etl.py
├── data/
│   ├── raw/
│   └── processed/
└── src/
    └── stock_etl/
        └── __init__.py
```

目前仍保留淺層模組結構，例如 `extractors/`、`transformers/`、`validators/`、`loaders/`。等專案穩定後，可再整理回 `src/stock_etl/`。

---

## 4. 技術棧

| 類別 | 技術 |
|---|---|
| 語言 | Python |
| 資料處理 | Pandas |
| 資料來源 | yfinance |
| 資料庫 | PostgreSQL |
| ORM / SQL 工具 | SQLAlchemy Core / SQLAlchemy ORM models |
| 環境管理 | pipenv |
| 本機服務 | Docker Compose |
| DB 管理工具 | DBeaver |
| 後續排程 | Airflow |
| 後續 Dashboard | Streamlit |

---

## 5. 資料表設計

### 5.1 `daily_prices`

用途：保存標準化後的每日 OHLCV 行情資料。

```sql
CREATE TABLE IF NOT EXISTS daily_prices (
    ticker TEXT NOT NULL,
    trade_date DATE NOT NULL,
    open_price NUMERIC(18, 6),
    high_price NUMERIC(18, 6),
    low_price NUMERIC(18, 6),
    close_price NUMERIC(18, 6),
    adjusted_close NUMERIC(18, 6),
    volume BIGINT,
    source TEXT NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, trade_date)
);
```

主鍵：

```text
ticker + trade_date
```

設計目的：

- 每支股票每天只保留一筆行情資料
- 可支援 upsert 重跑
- 可透過 `source` 保留資料來源追蹤

---

### 5.2 `technical_indicators`

用途：保存從 `daily_prices` 衍生出的技術指標資料。

| 欄位 | 說明 |
|---|---|
| ticker | 股票代號 |
| trade_date | 交易日 |
| sma_5 | 5 日簡單移動平均 |
| sma_20 | 20 日簡單移動平均 |
| sma_60 | 60 日簡單移動平均 |
| volume_avg_20d | 20 日平均成交量 |
| volume_ratio_20d | 當日成交量 / 20 日平均成交量 |
| source | 指標來源 |
| created_at | 第一次建立時間 |
| updated_at | 最近一次更新時間 |

主鍵：

```text
ticker + trade_date
```

設計目的：

- 將衍生分析資料與原始行情資料分離
- 支援後續 Dashboard 與 SQL 分析查詢
- 保留 `created_at` 與 `updated_at` 以追蹤資料變動

---

## 6. 已完成階段

### Phase 0：Docker + PostgreSQL 開發環境

已完成：

- 使用 Docker Compose 建立 PostgreSQL
- 使用 `.env` 管理 DB 帳密與設定
- 使用 volume / bind mount 保存 PostgreSQL 實體資料
- 使用 `db/init/*.sql` 初始化資料表
- 使用 `.gitignore` 排除敏感資訊與本機資料
- 使用 DBeaver 驗證 DB 與 table

目的：

- 建立可重現的本機開發環境
- 確保資料持久化
- 管理敏感資訊與 Git 邊界

---

### Phase 1：單支股票 OHLCV ETL

已完成：

- 使用 yfinance 抓取單支股票 OHLCV
- 處理 yfinance MultiIndex columns
- 將 Date index reset 成 `trade_date`
- 將欄位轉換成 `daily_prices` schema
- 補上 `ticker` 與 `source`
- 將 `trade_date` 轉成 date
- 建立 `validate_daily_prices(df)`

目的：

- 將 raw market data 轉成可入庫的標準化資料模型
- 建立 Extract → Transform → Validate 的基本流程

---

### Phase 2A：多股票批次 ETL

已完成：

- Extract 回傳 `{ticker: raw_df}`
- 失敗 ticker 記錄於 `failed_tickers`
- 單一 ticker 失敗不影響整批任務
- Transform 將多支股票合併成 long-format DataFrame
- 共用 `validate_daily_prices(df)`
- 共用 `upsert_daily_prices(df)`

目的：

- 支援多股票批次處理
- 建立錯誤隔離能力
- 維持資料格式一致性

---

### Phase 2B：Multi Stock ETL Summary

已完成：

- 統計 total tickers
- 統計 success tickers
- 統計 failed tickers 與失敗原因
- 統計 raw rows by ticker
- 統計 transformed rows
- 統計 affected rows
- 印出批次任務摘要

目的：

- 建立 ETL Observability 雛形
- 讓每次執行結果可追蹤、可除錯

---

### Phase 2C：日期區間 Backfill

已完成：

- yfinance extractor 支援 `start_date` / `end_date`
- 若指定 `start_date` 但未指定 `end_date`，由外層 script 補今天日期
- upsert 支援重跑，相同資料不會重複更新

目的：

- 支援歷史資料補載
- 建立增量更新與回補資料的基礎能力

---

### Phase 2D：CLI 參數化

已完成：

`run_multi_stock_etl.py` 支援：

- `--tickers`
- `--start-date`
- `--end-date`
- `--period`
- `--interval`

範例：

```bash
pipenv run python -m scripts.run_multi_stock_etl --tickers AVGO ORCL --start-date 2026-01-01
```

目的：

- 不需修改程式碼即可更換 ticker、日期與資料頻率
- 為未來 Airflow 或排程工具建立可呼叫入口

---

### Phase 3A：建立 `technical_indicators` table

已完成：

- 建立 `technical_indicators` 資料表
- 使用 `ticker + trade_date` 作為主鍵
- 建立 SMA 與成交量指標欄位
- 建立 `created_at` / `updated_at`

目的：

- 建立第一張衍生分析表
- 將技術指標與原始行情資料分離

---

### Phase 3B：計算 technical indicators DataFrame

已完成：

- 從 `daily_prices` 讀取 ticker、trade_date、close_price、volume、source
- 使用 `sort_values(["ticker", "trade_date"])` 確保時間序列順序
- 使用 `groupby("ticker")` 分股票計算
- 使用 `transform(lambda s: s.rolling(window).mean())` 計算 SMA
- 計算：
  - `sma_5`
  - `sma_20`
  - `sma_60`
  - `volume_avg_20d`
  - `volume_ratio_20d`

目的：

- 從原始行情資料產生衍生技術指標
- 建立 Data Warehouse 分析表的 transform 邏輯

---

### Phase 3C：technical_indicators Validate + Upsert

已完成：

- 建立 `validate_technical_indicators(df)`
- 允許 SMA 前期因資料不足產生合理 NaN
- 檢查必要欄位、主鍵重複、source、成交量衍生指標合理性
- 建立 `upsert_technical_indicators(df)`
- 使用 SQLAlchemy Core + PostgreSQL `ON CONFLICT`
- 資料相同時不更新
- created_at 不更新
- updated_at 只在資料實際異動時刷新
- 建立測試 script 驗證 technical indicators upsert

目的：

- 將 technical indicators 正式寫入 PostgreSQL
- 確保衍生分析表也具備資料品質檢查與可重跑能力

---

### Phase 3D：technical_indicators ETL script / CLI 串接

已完成：

- 建立 `scripts/run_technical_indicator_etl.py`
- 支援：
  - `--tickers`
  - `--start-date`
  - `--end-date`
- 從 `daily_prices` 讀取資料
- 計算完整 technical indicators
- 再依 output 日期區間篩選要 upsert 的資料
- validate 後 upsert
- 印出 Technical Indicator ETL Summary
- 統計 rows by ticker

目的：

- 將 technical indicators 流程從測試 script 整理為正式 ETL CLI
- 為未來 Airflow DAG 串接做準備
- 避免直接只用日期區間讀資料造成 SMA 錯算

---

## 7. Upsert 設計說明

本專案使用 PostgreSQL `ON CONFLICT` 實作 upsert。

核心概念：

- 若 `(ticker, trade_date)` 不存在：INSERT
- 若 `(ticker, trade_date)` 已存在且欄位不同：UPDATE
- 若資料完全相同：不 UPDATE

技術要點：

- `stmt.excluded.xxx`：代表本次原本要 INSERT，但因主鍵衝突被擋下的新資料
- `is_distinct_from`：比一般 `!=` 更安全，可處理 NULL 比較
- `where=update_where`：只在資料真的不同時才更新
- `RETURNING`：回傳本次實際新增或更新的資料列

目的：

- 支援 ETL 可重跑
- 避免重跑時無意義刷新時間欄位
- 讓 affected rows 可以反映實際資料變動

---

## 8. 常用執行指令

### 啟動 PostgreSQL

```bash
docker compose up -d
```

### 執行多股票 daily price ETL

```bash
pipenv run python -m scripts.run_multi_stock_etl --tickers AAPL MSFT NVDA TSM --start-date 2026-01-01
```

### 測試 technical indicator transform

```bash
pipenv run python -m scripts.test_technical_indicator_transform
```

### 測試 technical indicator upsert

```bash
pipenv run python -m scripts.test_technical_indicator_upsert
```

### 執行正式 technical indicator ETL

```bash
pipenv run python -m scripts.run_technical_indicator_etl
```

### 指定 ticker 執行 technical indicator ETL

```bash
pipenv run python -m scripts.run_technical_indicator_etl --tickers AAPL MSFT
```

### 指定 ticker 與 output 日期區間

```bash
pipenv run python -m scripts.run_technical_indicator_etl --tickers AAPL --start-date 2026-02-01 --end-date 2026-03-01
```

---

## 9. 目前測試與驗證重點

### daily_prices ETL

應確認：

- Extract 成功 ticker 數量
- Failed ticker 是否被記錄
- Transformed rows 是否合理
- 第一次 upsert affected rows > 0
- 第二次重跑 affected rows = 0

### technical_indicators ETL

應確認：

- Input daily_prices rows > 0
- Transformed indicator rows 合理
- Output indicator rows 符合日期區間
- Rows by ticker 正確
- 第一次 upsert affected rows > 0 或符合預期
- 第二次重跑 affected rows = 0

---

## 10. 後續規劃

### Phase 3E：DBeaver 驗證 technical_indicators 與範例 SQL 查詢

待補。

---

### Phase 4：公司主檔 companies table / dimension table

待補。

---

### Phase 5：財報資料 ETL

待補。

---

### Phase 6：多來源資料設計與來源可信度 / 備援來源

待補。

---

### Phase 7：財報事件與股價反應分析

待補。

---

### Phase 8：新聞與事件資料

待補。

---

### Phase 9：Airflow 排程

待補。

---

### Phase 10：Streamlit Dashboard

待補。

---

### Phase 11：README、架構圖、ERD、面試講稿與作品包裝

待補。

---

## 11. 專案目前可放入履歷的描述

> 建立美股市場資料 ETL / Data Warehouse 專案，使用 Python、Pandas、SQLAlchemy、PostgreSQL 與 Docker Compose，完成多股票 OHLCV 擷取、資料標準化、資料品質檢查、PostgreSQL upsert、日期區間 backfill、CLI 參數化與 ETL summary。另建立 technical_indicators 衍生分析表，從 daily_prices 計算 SMA 與成交量指標，並透過 validate + upsert 寫入 PostgreSQL，確保資料可重跑、可追溯且不重複更新。
```
