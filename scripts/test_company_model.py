import pandas as pd
from sqlalchemy import select

from db.database import engine
from db.models import Company


def main():
    # 建立 companies 查詢語句，確認 Company model 可正常對應資料表
    stmt = (
        select(
            Company.ticker,
            Company.company_name,
            Company.exchange,
            Company.sector,
            Company.industry,
            Company.country,
            Company.currency,
            Company.is_active,
            Company.source,
            Company.created_at,
            Company.updated_at,
        )
        .order_by(Company.ticker)
    )

    # 將查詢結果轉成 DataFrame，方便檢查欄位
    df = pd.read_sql(stmt, con=engine)

    print("\n========== Company Model Test ==========")
    print(df.head(20).to_string(index=False))
    print("\nColumns:")
    print(list(df.columns))
    print(f"\nRows: {len(df)}")
    print("========================================\n")


if __name__ == "__main__":
    main()