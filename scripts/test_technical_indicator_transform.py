import pandas as pd

from db.database import engine
from transformers.technical_indicator_transformer import calculate_technical_indicators


def main():
    # 從 daily_prices 讀取計算技術指標需要的欄位
    sql = """
    SELECT
        ticker,
        trade_date,
        close_price,
        volume,
        source
    FROM daily_prices
    ORDER BY ticker, trade_date
    """

    # 將 SQL 查詢結果讀成 DataFrame
    df = pd.read_sql(sql, con=engine)

    # 計算 SMA 與成交量指標
    indicators_df = calculate_technical_indicators(df)

    # 顯示前幾筆結果，觀察前期 SMA 是否為空值
    print(indicators_df.head(30).to_string(index=False))

    # 顯示每支 ticker 最後幾筆，觀察 SMA 是否正常出現
    print(indicators_df.groupby("ticker").tail(5).to_string(index=False))


if __name__ == "__main__":
    main()