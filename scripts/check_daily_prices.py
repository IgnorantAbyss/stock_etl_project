from sqlalchemy import select

from db.database import SessionLocal
from db.models import DailyPrice

# ORM僅作查詢 當前資料結構為data frame 使用迴圈逐列加入資料庫反而失去效率
def main():
    # 建立一個資料庫 session
    with SessionLocal() as session:
        # 建立 ORM 查詢語句，查詢前 5 筆 daily_prices
        stmt = select(DailyPrice).limit(5)

        # 執行查詢並取出 ORM 物件清單
        rows = session.scalars(stmt).all()

        # 逐筆印出查詢結果
        for row in rows:
            print(
                row.ticker,
                row.trade_date,
                row.open_price,
                row.close_price,
                row.volume,
            )


if __name__ == "__main__":
    main()