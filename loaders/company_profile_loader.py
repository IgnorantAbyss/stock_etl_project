from sqlalchemy import func, or_
from sqlalchemy.dialects.postgresql import insert

from db.database import engine
from db.models import Company


def upsert_company_profiles(df):
    # 傳入資料為空則不做資料庫動作
    if df.empty:
        return []
    
    # 將 Pandas NaN 轉成 None，讓資料庫儲存為 SQL NULL
    # df.astype(object)：
    # 將整個 DataFrame 的資料型態（dtype）強制轉換為 object（物件型態）。
    # df.notna()：
    # 判斷 DataFrame 中的每個位置是否「不是遺漏值」，回傳由布林值（True/False）組成的結構。
    # .where(條件, 替換值)：根據條件保留原值，不符合條件的則替換。
    # 在這裡代表：如果不是遺漏值（True），就保留原來的值；如果是遺漏值（False），就替換為 None
    clean_df = df.astype(object).where(df.notna(),None)

    # 將每列轉成 dict，供 SQLAlchemy 批次寫入
    records = clean_df.to_dict(orient='records')

    # 取得公司主檔資料表物件
    table = Company.__table__

    # 建立 PostgreSQL INSERT 語句
    stmt = insert(table).values(records)

    # 定義主鍵衝突時要更新的欄位
    update_columns = {
        "company_name": stmt.excluded.company_name,
        "exchange": stmt.excluded.exchange,
        "sector": stmt.excluded.sector,
        "industry": stmt.excluded.industry,
        "country": stmt.excluded.country,
        "currency": stmt.excluded.currency,
        "is_active": stmt.excluded.is_active,
        "source": stmt.excluded.source,
        "updated_at": func.current_timestamp(),
    }

    # 僅在公司主檔內容異動時才執行 UPDATE
    update_where = or_(
        table.c.company_name.is_distinct_from(stmt.excluded.company_name),
        table.c.exchange.is_distinct_from(stmt.excluded.exchange),
        table.c.sector.is_distinct_from(stmt.excluded.sector),
        table.c.industry.is_distinct_from(stmt.excluded.industry),
        table.c.country.is_distinct_from(stmt.excluded.country),
        table.c.currency.is_distinct_from(stmt.excluded.currency),
        table.c.is_active.is_distinct_from(stmt.excluded.is_active),
        table.c.source.is_distinct_from(stmt.excluded.source),
    )

    # ticker 衝突時，改為更新既有公司主檔
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["ticker"],
        set_=update_columns,
        where=update_where,
    ).returning(
        table.c.ticker,
        table.c.company_name,
        table.c.exchange,
        table.c.sector,
        table.c.industry,
        table.c.country,
        table.c.currency,
        table.c.is_active,
        table.c.source,
        table.c.created_at,
        table.c.updated_at,
    )

    # 使用 transaction 執行 upsert，成功 commit，失敗 rollback
    with engine.begin() as conn:
        result = conn.execute(upsert_stmt)

        # 取得實際 INSERT 或 UPDATE 的資料列
        affected_rows = result.mappings().all()

    # 回傳實際新增或更新的資料列
    return affected_rows