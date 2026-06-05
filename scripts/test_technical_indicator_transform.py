import pandas as pd
from sqlalchemy import select

from db.database import engine
from db.models import DailyPrice

from transformers.technical_indicator_transformer import calculate_technical_indicators
from validators.technical_indicator_validator import validate_technical_indicators
from loaders.technical_indicator_loader import upsert_technical_indicators

def read_daily_prices_for_indicator_test():
    # 讀取計算技術指標所需欄位
    # 資料工程操作大量資料及欄位時 不會為了 ORM 犧牲批次處理與 DataFrame 分析效率
    # sql = """
    # SELECT
    #     ticker,
    #     trade_date,
    #     close_price,
    #     volume,
    #     source
    # FROM daily_prices
    # ORDER BY ticker, trade_date
    # """

    # 建立結構化查詢，避免手寫 SQL 字串
    stmt = (
        select(
            DailyPrice.ticker,
            DailyPrice.trade_date,
            DailyPrice.close_price,
            DailyPrice.volume,
            DailyPrice.source,
        )
        .order_by(DailyPrice.ticker,DailyPrice.trade_date)
    )

    # 將查詢結果轉成 DataFrame，方便後續 Transform
    return pd.read_sql(stmt, con=engine)


def read_technical_indicators_sample():
    # 查詢寫入後的技術指標資料，用於確認 upsert 結果
    sql = """
    SELECT
        ticker,
        trade_date,
        sma_5,
        sma_20,
        sma_60,
        volume_avg_20d,
        volume_ratio_20d,
        source,
        created_at,
        updated_at
    FROM technical_indicators
    ORDER BY ticker, trade_date
    LIMIT 30
    """

    # 將 technical_indicators 查詢結果轉成 DataFrame
    return pd.read_sql(sql, con=engine)


def read_technical_indicator_counts():
    # 統計每支 ticker 的技術指標筆數
    sql = """
    SELECT
        ticker,
        COUNT(*) AS row_count
    FROM technical_indicators
    GROUP BY ticker
    ORDER BY ticker
    """

    # 將每支 ticker 的筆數查詢結果轉成 DataFrame
    return pd.read_sql(sql, con=engine)


def main():
    # 從 daily_prices 讀取來源資料
    price_df = read_daily_prices_for_indicator_test()

    print("\n========== Technical Indicator Upsert Test ==========")
    print(f"Input daily_prices rows: {len(price_df)}")

    # 若來源資料為空，直接結束測試
    if price_df.empty:
        print("daily_prices 沒有資料，請先執行 run_multi_stock_etl.py")
        return

    # 計算技術指標 DataFrame
    indicators_df = calculate_technical_indicators(price_df)

    print(f"Transformed indicator rows: {len(indicators_df)}")

    # 驗證 technical_indicators 入庫前資料品質
    validate_technical_indicators(indicators_df)

    print("Validation passed")

    # 寫入 technical_indicators
    affected_rows = upsert_technical_indicators(indicators_df)

    print(f"Affected rows: {len(affected_rows)}")

    # 顯示實際新增或更新的前幾筆資料
    if affected_rows:
        affected_df = pd.DataFrame(affected_rows)
        print("\nAffected rows sample:")
        print(affected_df.head(10).to_string(index=False))
    else:
        print("\nNo rows inserted or updated. Data may already be up to date.")

    # 查詢 technical_indicators 寫入結果
    sample_df = read_technical_indicators_sample()

    print("\ntechnical_indicators sample:")
    print(sample_df.to_string(index=False))

    # 查詢每支 ticker 寫入筆數
    count_df = read_technical_indicator_counts()

    print("\ntechnical_indicators row count by ticker:")
    print(count_df.to_string(index=False))

    print("====================================================\n")


if __name__ == "__main__":
    main()