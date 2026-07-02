import argparse
import pandas as pd
from datetime import date
from sqlalchemy import select

from db.database import engine
from db.models import DailyPrice
from transformers.technical_indicator_transformer import calculate_technical_indicators
from validators.technical_indicator_validator import validate_technical_indicators
from loaders.technical_indicator_loader import upsert_technical_indicators

def parse_args():
    # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(
        description="Run technical_indicator_etl."
    )

    # 指定要處理的股票清單
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Ticker list, example: --tickers TSM AAPL MSFT NVDA",
    )
    # 自訂起始時間
    parser.add_argument(
        "--start-date",
        default=None,
        help="Backfill start date, format: YYYY-MM-DD"
    )
    # 自訂結束時間
    parser.add_argument(
        "--end-date",
        default=None,
        help="Backfill end date, format: YYYY-MM-DD"
    )
    # 回傳解析後的CLI參數
    return parser.parse_args()


def read_daily_price_for_technical_indicators(tickers=None):
    '''按照股票類別及交易日期排序，讀取資料庫中的每日價格'''
    stmt = (
        select(
            DailyPrice.ticker,
            DailyPrice.trade_date,
            DailyPrice.close_price,
            DailyPrice.volume,
            DailyPrice.source
        ).order_by(DailyPrice.ticker,DailyPrice.trade_date)
    )
    # 指定 ticker 時，只讀取指定股票
    if tickers:
        stmt = stmt.where(DailyPrice.ticker.in_(tickers))

    # 將查詢結果轉成 DataFrame，方便後續 Transform
    return pd.read_sql(stmt,con=engine)

def date_range_filter(df,start_date=None,end_date=None):
    # 避免修改原dataframe
    filtered_df = df.copy()
    
    # 指定起始日 只保留起始日開始的資料
    if start_date:
        # pd.to_datetime 會先轉成Pandas 的時間物件 Timestamp('YYYY-MM-DD HH:MM:SS')
        # .date 將pandas時間物件轉為 datetime.date(2026, 2, 1) 
        # 因為從 PostgreSQL 讀出來的 trade_date 很可能是 Python 的 datetime.date
        # 轉為同型別進行比較
        filtered_df = filtered_df[filtered_df['trade_date'] >= pd.to_datetime(start_date).date()]
    # 指定結束日
    if end_date:
        filtered_df = filtered_df[filtered_df['trade_date'] <= pd.to_datetime(end_date).date()]

    # 回傳篩選後資料
    return filtered_df

def print_technical_indicator_etl_summary(summary):
    # 印出任務摘要標題
    print("\n========== Technical Indicator ETL Summary ==========")

    print(f"Tickers: {summary['tickers']}")
    print(f"Output start date: {summary['start_date']}")
    print(f"Output end date: {summary['end_date']}")
    print(f"Input daily_prices rows: {summary['input_rows']}")
    print(f"Transformed indicator rows: {summary['transformed_rows']}")
    print(f"Output indicator rows: {summary['output_rows']}")
    print(f"Affected rows: {summary['affected_rows']}")

    print("\nRows by ticker:")
    for ticker, row_count in summary["rows_by_ticker"].items():
        print(f"- {ticker}: {row_count}")

    print("====================================================\n")

def main():
    '''
    1. 從 daily_prices 讀資料
    2. 可選擇指定 ticker
    3. 可選擇指定日期區間
    4. 計算 technical_indicators
    5. validate
    6. upsert
    7. 印出 ETL summary
    '''

    # 帶入CLI參數
    args = parse_args()
    tickers = args.tickers
    start_date = args.start_date
    end_date = args.end_date

    # 建立任務摘要
    summary = {
        "tickers": args.tickers or "ALL",
        "start_date": args.start_date,
        "end_date": args.end_date,
        "input_rows": 0,
        "transformed_rows": 0,
        "output_rows": 0,
        "affected_rows": 0,
        "rows_by_ticker": {},
    }

    # 記錄來源資料筆數
    df = read_daily_price_for_technical_indicators(tickers=tickers)

    # 記錄來源資料筆數
    summary["input_rows"] = len(df)
    
    # 若來源資料為空，印出摘要後結束
    if df.empty:
        print_technical_indicator_etl_summary(summary)
        return
    
    # 計算技術指標
    indicator_df = calculate_technical_indicators(df)
    # 紀錄轉換為技術指標後的筆數
    summary['transformed_rows'] = len(indicator_df)

    # 依指定日期篩選本次要寫入的資料
    filtered_df = date_range_filter(
        df=indicator_df,
        start_date=start_date,
        end_date=end_date
        )
    
    # 紀錄本次預計輸出筆數
    summary['output_rows'] = len(filtered_df)

    # 紀錄每個ticker輸出筆數
    summary["rows_by_ticker"] = (
        filtered_df.groupby('ticker')
        .size()
        # 依照 ticker 名稱排序
        .sort_index()
        .to_dict()
    )

    # 若無可寫入資料 印出摘要後結束
    if filtered_df.empty:
        print_technical_indicator_etl_summary(summary)
        return
    
    # 驗證 technical indicator資料品質
    validate_technical_indicators(filtered_df)

    # upsert入資料庫
    affected_rows = len(upsert_technical_indicators(filtered_df))

    summary["affected_rows"] = affected_rows

    print_technical_indicator_etl_summary(summary)

if __name__ == "__main__":
    main()
