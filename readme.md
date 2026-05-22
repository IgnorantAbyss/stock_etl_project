# Stock ETL Project

這是一個金融市場資料 ETL 練習專案，目標是建立一套可重跑、可追溯、可擴充的股票資料管線。

第一階段先處理美股每日行情資料 OHLCV：

- open price：開盤價
- high price：最高價
- low price：最低價
- close price：收盤價
- adjusted close：還原收盤價
- volume：成交量

---

## 1. 專案結構

```text
stock-etl-project/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── db/
│   └── init/
│       └── 001_create_tables.sql
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
└── src/
    └── stock_etl/
        └── __init__.py
```

---

## 2. 環境需求

本專案第一階段需要：

- Docker Desktop
- Docker Compose
- DBeaver 或其他 PostgreSQL GUI 工具
- Python 3.x

---

## 3. PostgreSQL 啟動方式

本專案使用 Docker Compose 啟動 PostgreSQL。

請先在專案根目錄建立 `.env` 檔案。

範例內容：

```env
POSTGRES_USER=stock_user
POSTGRES_PASSWORD=stock_password
POSTGRES_DB=stock_etl
```

說明：

```text
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

此時 DBeaver 連線 port 要改成：

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
db/init/001_create_tables.sql
src/
scripts/
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

## 14. 後續開發計畫

第一階段：

```text
1. 使用 Docker 啟動 PostgreSQL
2. 建立 daily_prices 資料表
3. 用 DBeaver 確認資料庫可連線
```

第二階段：

```text
1. 用 Python 抓一支股票的 OHLCV
2. 清洗欄位名稱與日期格式
3. 寫入 daily_prices
4. 確認重跑不會產生重複資料
```

第三階段：

```text
1. 計算 SMA5、SMA20、SMA60
2. 建立 technical_indicators 表
3. 將技術指標寫入資料庫
```