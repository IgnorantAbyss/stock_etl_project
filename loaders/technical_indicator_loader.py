from sqlalchemy import func, or_
from sqlalchemy.dialects.postgresql import insert

from db.database import engine
from db.models import TechnicalIndicator

def upsert_technical_indicators(df):
    # 空 DataFrame 不進行寫入，避免產生無意義 SQL
    if df.empty:
        return 0
    
    # 將 Pandas NaN 轉成 None，讓資料庫儲存為 SQL NULL
    clean_df = df.astype(object).where(df.notna(), None)

    # 將 DataFrame 轉成 list[dict]，方便 SQLAlchemy 批次寫入
    # orient="records"是 Pandas 內建的一個參數設定值，用來決定轉換後的資料型態
    # records會將每一列資料轉換為一個dict 裝在list中
    records = clean_df.to_dict(orient="records")

    # 取得 TechnicalIndicator table 物件
    table = TechnicalIndicator.__table__

    # 建立 PostgreSQL INSERT 語句，目標是 TechnicalIndicator
    stmt = insert(table).values(records)

    # 定義「主鍵衝突時怎麼更新」 主要功能為取得主鍵衝突時的資料 
    # 與該筆衝突insert資料相同
    update_columns = {
        # excluded表示 因主鍵衝突被擋的資料
        "sma_5": stmt.excluded.sma_5,
        "sma_20": stmt.excluded.sma_20,
        "sma_60": stmt.excluded.sma_60,
        "volume_avg_20d": stmt.excluded.volume_avg_20d,
        "volume_ratio_20d": stmt.excluded.volume_ratio_20d,
        "source": stmt.excluded.source,
        # func為sqlalchemy模組 用來在python呼叫資料庫底層的原生函數
        # 在SQL寫入當前時間
        "updated_at": func.current_timestamp(),   
    }

    # 建立欄位差異判斷，只在資料不同時才 UPDATE
    # is_distinct_from 避免NULL比較
    update_where = or_(
        table.c.sma_5.is_distinct_from(stmt.excluded.sma_5),
        table.c.sma_20.is_distinct_from(stmt.excluded.sma_20),
        table.c.sma_60.is_distinct_from(stmt.excluded.sma_60),
        table.c.volume_avg_20d.is_distinct_from(stmt.excluded.volume_avg_20d),
        table.c.volume_ratio_20d.is_distinct_from(stmt.excluded.volume_ratio_20d),
        table.c.source.is_distinct_from(stmt.excluded.source),
    )
    # 這時還沒執行新增語法


    # ticker + trade_date 衝突時，改成更新既有資料
    # 把INSERT INTO TechnicalIndicator ...

    # 升級為
    # INSERT INTO TechnicalIndicator ...
    # ON CONFLICT (ticker, trade_date)
    # DO UPDATE SET ...
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "trade_date"],
        set_=update_columns,
        where=update_where,
    ).returning(
            TechnicalIndicator.__table__.c.ticker,
            TechnicalIndicator.__table__.c.trade_date,
            TechnicalIndicator.__table__.c.sma_5,
            TechnicalIndicator.__table__.c.sma_20,
            TechnicalIndicator.__table__.c.sma_60,
            TechnicalIndicator.__table__.c.volume_avg_20d,
            TechnicalIndicator.__table__.c.volume_ratio_20d,
            TechnicalIndicator.__table__.c.source,
            TechnicalIndicator.__table__.c.created_at,
            TechnicalIndicator.__table__.c.updated_at,
        )
    
    # 使用 transaction 執行 upsert，成功 commit，失敗 rollback
    with engine.begin() as conn:
        result = conn.execute(upsert_stmt)

        # 將 PostgreSQL RETURNING 回傳的資料轉成 list[dict]
        affected_rows = result.mappings().all()

    # 回傳實際新增或更新的資料列，方便主流程檢查結果
    return affected_rows