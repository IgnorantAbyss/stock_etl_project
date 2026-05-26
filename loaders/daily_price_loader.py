from sqlalchemy import func, or_
from sqlalchemy.dialects.postgresql import insert

from db.database import engine
from db.models import DailyPrice

def load_daily_prices(df):
    # 開啟 transaction，成功 commit，失敗 rollback
    with engine.begin() as conn:
        # 將 DataFrame 追加寫入 daily_prices
        df.to_sql(
            name="daily_prices",
            con=conn,
            if_exists="append",
            index=False,
        )

    # 回傳寫入筆數，方便主流程確認
    return len(df)


def upsert_daily_prices(df):
    # 空 DataFrame 不進行寫入，避免產生無意義 SQL
    if df.empty:
        return 0

    # 將 DataFrame 轉成 list[dict]，方便 SQLAlchemy 批次寫入
    # orient="records"是 Pandas 內建的一個參數設定值，用來決定轉換後的資料型態
    # records會將每一列資料轉換為一個dict 裝在list中
    records = df.to_dict(orient="records")

    # 取得 daily_prices table 物件
    table = DailyPrice.__table__

    # 建立 PostgreSQL INSERT 語句，目標是 daily_prices
    stmt = insert(table).values(records)

    # 定義「主鍵衝突時怎麼更新」 主要功能為取得主鍵衝突時的資料 
    # 與該筆衝突insert資料相同
    update_columns = {
        # excluded表示 因主鍵衝突被擋的資料
        # 如果這筆資料 INSERT 時發生主鍵衝突，
        # 那就用「這次原本要插入的新 close_price」
        # 去更新資料表裡舊的 close_price。
        "open_price": stmt.excluded.open_price,
        "high_price": stmt.excluded.high_price,
        "low_price": stmt.excluded.low_price,
        "close_price": stmt.excluded.close_price,
        "adjusted_close": stmt.excluded.adjusted_close,
        "volume": stmt.excluded.volume,
        "source": stmt.excluded.source,
        # func為sqlalchemy模組 用來在python呼叫資料庫底層的原生函數
        # 在SQL寫入當前時間
        "ingested_at": func.current_timestamp(),   
    }

    # 建立欄位差異判斷，只在資料不同時才 UPDATE
    # is_distinct_from 避免NULL比較
    update_where = or_(
        table.c.open_price.is_distinct_from(stmt.excluded.open_price),
        table.c.high_price.is_distinct_from(stmt.excluded.high_price),
        table.c.low_price.is_distinct_from(stmt.excluded.low_price),
        table.c.close_price.is_distinct_from(stmt.excluded.close_price),
        table.c.adjusted_close.is_distinct_from(stmt.excluded.adjusted_close),
        table.c.volume.is_distinct_from(stmt.excluded.volume),
        table.c.source.is_distinct_from(stmt.excluded.source),
    )
    # 這時還沒執行新增語法


    # ticker + trade_date 衝突時，改成更新既有資料
    # 把INSERT INTO daily_prices ...

    # 升級為
    # INSERT INTO daily_prices ...
    # ON CONFLICT (ticker, trade_date)
    # DO UPDATE SET ...
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "trade_date"],
        set_=update_columns,
        where=update_where,
    ).returning(
            DailyPrice.__table__.c.ticker,
            DailyPrice.__table__.c.trade_date,
            DailyPrice.__table__.c.open_price,
            DailyPrice.__table__.c.high_price,
            DailyPrice.__table__.c.low_price,
            DailyPrice.__table__.c.close_price,
            DailyPrice.__table__.c.adjusted_close,
            DailyPrice.__table__.c.volume,
            DailyPrice.__table__.c.source,
            DailyPrice.__table__.c.ingested_at,
        )
    
    # 使用 transaction 執行 upsert，成功 commit，失敗 rollback
    with engine.begin() as conn:
        result = conn.execute(upsert_stmt)

        # 將 PostgreSQL RETURNING 回傳的資料轉成 list[dict]
        affected_rows = result.mappings().all()

    # 回傳受影響筆數，方便主流程確認結果
    return affected_rows