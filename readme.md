# Stock ETL Project

這是一個金融市場資料 ETL 練習專案，目標是建立一套可重跑、可追溯、可擴充的股票資料管線。

第一階段先處理美股每日行情資料 OHLCV：

- open price：開盤價
- high price：最高價
- low price：最低價
- close price：收盤價
- adjusted close：調整後收盤價
- volume：成交量

目前專案已完成第一版單支股票 ETL：

```text
Extract → Transform → Validate → Load
```

目前尚未完成 upsert，因此現階段重跑同一批資料時，仍可能因為 `ticker + trade_date` 主鍵重複而產生錯誤。

---

## 1. 專案結構

```text
stock-etl-project/
├── docker-compose.yml
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
│       └── 001_create_tables.sql
├── data/
│   ├── raw/
│   └── processed/
├── loaders/
│   ├── __init__.py
│   └── daily_price_loader.py
├── validators/
│   ├── __init__.py
│   └── daily_price_validator.py
├── scripts/
│   ├── transform_one_stock.py
│   └── check_daily_prices.py
└── src/
    └── stock_etl/
        └── __init__.py
```

目前專案先採用淺層模組結構，方便使用：

```bash
pipenv run python -m scripts.transform_one_stock
```

後續若專案規模擴大，可再逐步整理成：

```text
src/stock_etl/
├── config/
├── db/
├── extractors/
├── transformers/
├── validators/
└── loaders/
```

---

## 2. 環境需求

本專案目前需要：

- Docker Desktop
- Docker Compose
- DBeaver 或其他 PostgreSQL GUI 工具
- Python 3.x
- Pipenv

目前 Python 主要套件：

```text
pandas
yfinance
sqlalchemy
psycopg2-binary
pydantic-settings
```

套件安裝方式：

```bash
pipenv install pandas yfinance sqlalchemy psycopg2-binary pydantic-settings
```

---

## 3. PostgreSQL 啟動方式

本專案使用 Docker Compose 啟動 PostgreSQL。

請先在專案根目錄建立 `.env` 檔案。

範例內容：

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=stock_user
POSTGRES_PASSWORD=stock_password
POSTGRES_DB=stock_etl
```

說明：

```text
POSTGRES_HOST 是 PostgreSQL 主機位置，本機 Docker 開發環境通常是 localhost。
POSTGRES_PORT 是 PostgreSQL 對外連線 port，預設是 5432。
POSTGRES_USER 是 PostgreSQL 初始化時建立的使用者名稱。
POSTGRES_PASSWORD 是該使用者的密碼。
POSTGRES_DB 是 PostgreSQL 初始化時建立的資料庫名稱。
```

注意：

```text
.env 不會提交到 GitHub。
GitHub 上只保留 .env.example 作為範例。
```

---

## 4. 啟動 PostgreSQL

在專案根目錄執行：

```bash
docker compose up -d
```

指令說明：

```text
docker compose
讀取目前資料夾底下的 docker-compose.yml。

up
啟動 docker-compose.yml 裡定義的服務。

-d
detached mode，代表背景執行，不會佔住目前的 terminal。
```

---

## 5. 檢查 container 是否啟動

```bash
docker ps
```

如果成功，應該可以看到類似：

```text
stock_etl_postgres
```

---

## 6. 查看 PostgreSQL container log

```bash
docker logs stock_etl_postgres
```

用途：

```text
檢查 PostgreSQL 是否正常啟動。
如果資料庫初始化失敗，也可以從 logs 找錯誤原因。
```

---

## 7. 停止服務

```bash
docker compose down
```

說明：

```text
這會停止並移除 docker-compose 建立的 container。
但如果有掛載 ./.docker/postgres-data，資料庫實體資料仍會保留。
```

---

## 8. PostgreSQL 掛載邏輯

本專案使用 bind mount 將 PostgreSQL 實體資料掛載到：

```text
./.docker/postgres-data
```

對應到 container 內部的：

```text
/var/lib/postgresql/data
```

意思是：

```text
PostgreSQL 實際資料會保存在專案資料夾的 .docker/postgres-data 底下。
即使 container 被刪除，只要 .docker/postgres-data 還在，資料庫資料就還在。
```

注意：

```text
.docker/postgres-data 是本機資料庫實體資料，不會提交到 GitHub。
```

原因：

```text
1. PostgreSQL 實體資料不是一般文字檔，不適合用 Git 管理。
2. 資料庫檔案體積可能很大。
3. 不同系統或 PostgreSQL 版本可能造成相容性問題。
4. GitHub 應管理程式碼、設定範例、SQL schema，而不是資料庫實體檔。
```

---

## 9. 異地部署資料如何處理？

因為 `.docker/postgres-data` 不會提交到 GitHub，所以在另一台電腦 `git clone` 後，資料庫會是新的空資料庫。

標準流程是：

```text
git clone 專案
↓
複製 .env.example 成 .env
↓
docker compose up -d
↓
PostgreSQL 初始化資料庫與資料表
↓
重新執行 ETL，把資料寫入資料庫
```

如果未來需要搬移既有資料，可以使用：

```text
pg_dump
```

將資料庫匯出成 SQL 備份檔，再到另一台電腦還原。

---

## 10. Port 使用說明

PostgreSQL 預設使用 port 5432。

本專案預設將 Windows 主機的 5432 對應到 container 內的 5432：

```yaml
ports:
  - "5432:5432"
```

意思是：

```text
localhost:5432 → container 裡的 PostgreSQL:5432
```

如果本機 5432 已經被占用，可以改成：

```yaml
ports:
  - "5433:5432"
```

此時 `.env` 與 DBeaver 連線 port 都要改成：

```text
5433
```

---

## 11. 檢查 5432 port 是否被占用

Windows PowerShell：

```powershell
netstat -ano | findstr :5432
```

如果看到 `LISTENING`，代表 5432 已經被某個程式占用。

可以用 PID 查詢是哪個程式：

```powershell
tasklist | findstr <PID>
```

也可以使用：

```powershell
Get-NetTCPConnection -LocalPort 5432
```

---

## 12. DBeaver 連線方式

使用 DBeaver 建立 PostgreSQL 連線：

```text
Host: localhost
Port: 5432
Database: stock_etl
Username: stock_user
Password: stock_password
```

如果 docker-compose.yml 改成：

```yaml
ports:
  - "5433:5432"
```

則 DBeaver port 請改成：

```text
5433
```

---

## 13. Git 管理規則

會提交到 GitHub：

```text
docker-compose.yml
.env.example
.gitignore
README.md
config/
db/
loaders/
validators/
scripts/
src/
```

不會提交到 GitHub：

```text
.env
.docker/
data/raw/
data/processed/
```

原因：

```text
.env 可能包含帳號密碼。
.docker/ 是 PostgreSQL 實體資料。
data/raw/ 和 data/processed/ 可能包含大量資料或暫存資料。
```

---

## 14. daily_prices 資料表設計

目前資料表：

```text
daily_prices
```

目前 schema：

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

設計說明：

```text
ticker + trade_date 是自然主鍵。
同一支股票在同一個交易日只應該有一筆每日行情資料。
pandas 的 row index 不需要存進資料庫。
如果未來需要資料庫內部流水號，可以另外設計 id，但第一版不需要。
```

---

## 15. 目前開發進度

目前已完成第一版單支股票 ETL 雛形：

```text
Extract → Transform → Validate → Load
```

目前資料來源：

```text
yfinance
```

目前測試股票：

```text
TSM
```

目前目標資料表：

```text
daily_prices
```

目前已完成：

```text
1. 使用 yfinance 擷取單一股票最近一個月 OHLCV。
2. 處理 yfinance 回傳的 MultiIndex columns。
3. 將 Date index 轉換為 trade_date 欄位。
4. 將欄位名稱轉換為 daily_prices schema 格式。
5. 補上 ticker 與 source 欄位。
6. 建立 daily_prices 資料品質檢查 function。
7. 使用 Pydantic Settings 統一讀取 .env。
8. 使用 SQLAlchemy 建立 PostgreSQL engine 與 SessionLocal。
9. 建立 DailyPrice ORM model。
10. 將通過 Validate 的 DataFrame 寫入 PostgreSQL。
11. 使用 ORM 查詢 daily_prices，確認資料已成功入庫。
```

目前尚未完成：

```text
1. upsert
2. 重跑不重複
3. 多支股票批次處理
4. 技術指標計算
5. Airflow 排程
6. Streamlit Dashboard
```

---

## 16. Extract：使用 yfinance 擷取每日行情

目前使用 yfinance 擷取單一股票資料。

範例：

```python
df = yf.download(
    tickers=ticker,
    period="1mo",
    interval="1d",
    auto_adjust=False,
)
```

目前理解：

```text
yfinance 可以一次抓取多支股票，因此回傳的 columns 可能是 MultiIndex。
即使只抓一支股票，也可能出現 Price / Ticker 兩層欄位。
```

原始欄位可能類似：

```text
MultiIndex([('Adj Close', 'TSM'),
            (    'Close', 'TSM'),
            (     'High', 'TSM'),
            (      'Low', 'TSM'),
            (     'Open', 'TSM'),
            (   'Volume', 'TSM')],
           names=['Price', 'Ticker'])
```

目前第一版先移除 ticker 這層欄位，後續再手動補上 `ticker` 欄位。

---

## 17. Transform：整理成 daily_prices 格式

Transform 目標是將 yfinance 原始資料整理成 `daily_prices` 可以寫入的格式。

目前整理後欄位：

```text
ticker
trade_date
open_price
high_price
low_price
close_price
adjusted_close
volume
source
```

目前處理內容：

```text
1. 移除 MultiIndex columns 的 ticker 層級。
2. 清除 columns.name，避免顯示殘留 Price。
3. 將 Date index 命名為 trade_date。
4. 使用 reset_index 將日期 index 轉成一般欄位。
5. 將 yfinance 欄位名稱轉成資料庫欄位名稱。
6. 新增 ticker 欄位。
7. 新增 source 欄位。
8. 將 trade_date 轉成日期格式。
9. 調整欄位順序，使其接近資料表 schema。
```

整理後資料格式：

```text
ticker | trade_date | open_price | high_price | low_price | close_price | adjusted_close | volume | source
TSM    | 2026-04-23 | ...        | ...        | ...       | ...         | ...            | ...    | yfinance
```

---

## 18. Validate：資料品質檢查

目前已建立：

```text
validators/daily_price_validator.py
```

主要 function：

```python
validate_daily_prices(df)
```

目前檢查項目：

```text
1. 必要欄位是否存在。
2. ticker 是否有空值。
3. trade_date 是否有空值。
4. open_price / high_price / low_price / close_price 是否有空值。
5. volume 是否有空值。
6. volume 是否小於 0。
7. high_price 是否小於 low_price。
8. high_price 是否小於 open_price。
9. high_price 是否小於 close_price。
10. low_price 是否大於 open_price。
11. low_price 是否大於 close_price。
12. ticker + trade_date 是否重複。
```

目前策略：

```text
如果資料品質檢查失敗，直接 raise ValueError。
如果資料品質檢查通過，回傳 True。
```

這一步的目的：

```text
在資料寫入 PostgreSQL 前，先阻擋明顯異常或不完整的行情資料。
```

目前尚未加入：

```text
1. warning 分級。
2. 錯誤資料另存。
3. validation log。
4. blocking error / non-blocking warning 區分。
```

這些會在後續資料品質強化階段再補上。

---

## 19. Config：使用 Pydantic Settings 管理環境變數

目前已建立：

```text
config/config.py
```

用途：

```text
統一讀取 .env，集中管理資料庫連線設定。
```

目前設定包含：

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

這樣做的原因：

```text
1. 避免在不同檔案中重複使用 os.getenv。
2. 避免資料庫帳密散落在程式碼裡。
3. 方便未來切換本機、Docker、測試或正式環境。
4. 讓資料庫設定集中在單一 config 模組。
```

---

## 20. Database Access Layer：SQLAlchemy engine / SessionLocal / ORM model

目前已建立：

```text
db/database.py
db/models.py
```

`db/database.py` 負責：

```text
1. 建立 PostgreSQL SQLAlchemy connection URL。
2. 建立全專案共用 engine。
3. 建立 SessionLocal。
4. 提供 ORM 查詢時使用的 session。
```

`db/models.py` 目前建立：

```text
DailyPrice ORM model
```

對應 PostgreSQL 資料表：

```text
daily_prices
```

目前 DailyPrice 使用複合主鍵：

```text
ticker + trade_date
```

原因：

```text
同一支股票在同一個交易日只應該有一筆每日行情資料。
```

目前 ORM 的用途：

```text
1. 定義資料表對應的 Python class。
2. 讓程式可以用 ORM 查詢 daily_prices。
3. 為後續擴充 companies、technical_indicators 等資料表建立基礎。
```

注意：

```text
大量 DataFrame 寫入目前不使用 ORM for-loop 寫入。
```

原因：

```text
DataFrame 是批次資料結構，逐列轉成 ORM object 再寫入效能較低。
目前寫入仍使用 DataFrame / SQLAlchemy engine 進行批次寫入。
```

---

## 21. Load：寫入 PostgreSQL

目前已建立：

```text
loaders/daily_price_loader.py
```

目前寫入方式：

```text
使用 pandas DataFrame.to_sql 寫入 daily_prices。
```

目前策略：

```text
if_exists="append"
```

意思是：

```text
將 DataFrame 內容追加寫入既有 daily_prices 資料表。
```

目前已確認：

```text
1. Python 可以成功連線 PostgreSQL。
2. 通過 Validate 的 TSM 每日行情可以寫入 daily_prices。
3. DBeaver 可以查到寫入後的資料。
4. ORM 可以從 daily_prices 查詢資料。
```

目前限制：

```text
目前使用 append 寫入，重跑同一批資料時可能遇到主鍵衝突。
```

可能錯誤：

```text
duplicate key value violates unique constraint
```

這代表：

```text
PostgreSQL 正確阻擋 ticker + trade_date 重複資料。
```

下一步會改成：

```text
ON CONFLICT (ticker, trade_date) DO UPDATE
```

也就是 upsert。

---

## 22. 目前執行方式

執行單支股票 ETL 測試：

```bash
pipenv run python -m scripts.transform_one_stock
```

目前此流程包含：

```text
1. 從 yfinance 擷取 TSM 最近一個月 OHLCV。
2. 將原始資料轉換為 daily_prices schema。
3. 執行 validate_daily_prices。
4. 寫入 PostgreSQL daily_prices。
```

執行 ORM 查詢測試：

```bash
pipenv run python -m scripts.check_daily_prices
```

用途：

```text
確認 DailyPrice ORM model 可以正確對應 daily_prices 資料表，並成功查詢資料。
```

---

## 23. DBeaver 驗證 SQL

查詢 daily_prices 內容：

```sql
SELECT *
FROM daily_prices
ORDER BY trade_date;
```

查詢資料筆數：

```sql
SELECT COUNT(*)
FROM daily_prices;
```

檢查是否存在重複主鍵資料：

```sql
SELECT ticker, trade_date, COUNT(*)
FROM daily_prices
GROUP BY ticker, trade_date
HAVING COUNT(*) > 1;
```

預期結果：

```text
不應該查出任何資料。
```

原因：

```text
daily_prices 使用 ticker + trade_date 作為主鍵，同一支股票同一天只能有一筆資料。
```

---

## 24. 目前階段成果

目前已完成第一版單支股票 ETL：

```text
Extract → Transform → Validate → Load
```

目前可以作為履歷展示的內容：

```text
建立美股每日行情 ETL 流程，使用 yfinance 擷取 OHLCV 資料，將原始 MultiIndex 欄位轉換為標準化資料表格式，加入資料品質檢查，並透過 SQLAlchemy 寫入 PostgreSQL。
```

更工程化的描述：

```text
使用 Pydantic Settings 管理環境變數，透過 SQLAlchemy 建立 PostgreSQL engine、Session 與 ORM model，將資料庫連線、資料表映射與資料寫入邏輯模組化。
```

目前專案已具備：

```text
1. 可重現的 PostgreSQL 開發環境。
2. 單一股票 OHLCV Extract / Transform。
3. Load 前資料品質檢查。
4. PostgreSQL 寫入。
5. ORM 查詢驗證。
6. 初步資料庫存取層模組化。
```

---

## 25. 下一步：Upsert

下一步目標：

```text
讓 ETL 可以重跑、不重複、可更新。
```

目前問題：

```text
使用 append 寫入時，如果重跑同一段資料，會因為 ticker + trade_date 已存在而產生主鍵衝突。
```

下一步會實作：

```sql
ON CONFLICT (ticker, trade_date) DO UPDATE
```

目標行為：

```text
1. 如果 ticker + trade_date 不存在，新增資料。
2. 如果 ticker + trade_date 已存在，更新 open/high/low/close/adjusted_close/volume/source/ingested_at。
3. 讓 ETL 支援重跑。
4. 避免重複資料。
5. 讓資料來源修正歷史資料時，可以更新既有資料。
```

完成 upsert 後，第一階段會形成更完整的履歷節點：

```text
完成單一股票 OHLCV Extract → Transform → Validate → Load → Upsert 流程，支援資料重跑與主鍵去重。
```

---

## 26. 後續開發計畫

### 第一階段：單支股票 ETL

```text
1. 使用 Docker 啟動 PostgreSQL。已完成
2. 建立 daily_prices 資料表。已完成
3. 用 DBeaver 確認資料庫可連線。已完成
4. 用 Python 抓一支股票的 OHLCV。已完成
5. 清洗欄位名稱與日期格式。已完成
6. 加入資料品質檢查。已完成
7. 寫入 daily_prices。已完成
8. 實作 upsert，確認重跑不會產生重複資料。下一步
```

### 第二階段：多支股票批次 ETL

```text
1. 建立 ticker list。
2. 對多支股票批次執行 Extract / Transform / Validate / Load。
3. 處理單一 ticker 失敗不影響整批任務。
4. 紀錄成功與失敗 ticker。
5. 支援指定日期區間 backfill。
```

### 第三階段：技術指標

```text
1. 從 daily_prices 讀取 close_price。
2. 計算 SMA5、SMA20、SMA60。
3. 計算 volume_avg_20d。
4. 計算 volume_ratio_20d。
5. 建立 technical_indicators 表。
6. 將技術指標寫入資料庫。
```

### 第四階段：公司主檔

```text
1. 建立 companies table。
2. 儲存 ticker、company_name、exchange、sector、industry、country、source。
3. 理解 fact table 與 dimension table 的差異。
4. 讓 daily_prices 可以連到公司主檔。
```

### 第五階段：財報資料

```text
1. 加入季度財報資料。
2. 建立 financial_statements table。
3. 整合日頻行情與季頻財報。
4. 計算 revenue YoY、QoQ、profit margin。
```

### 第六階段：Airflow 排程

```text
1. 將 ETL function 包成 Airflow task。
2. 建立 daily_market_etl DAG。
3. 加入 retry、failure log、manual backfill。
```

### 第七階段：Streamlit Dashboard

```text
1. 查詢單支股票股價走勢。
2. 顯示成交量。
3. 顯示 SMA5、SMA20、SMA60。
4. 顯示資料更新時間與資料來源。
5. 顯示後續財報與事件分析結果。
```

---


