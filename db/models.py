from sqlalchemy import BigInteger, Date, DateTime, Numeric, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    # 建立 SQLAlchemy ORM declarative base
    pass


class DailyPrice(Base):
    # 對應 PostgreSQL daily_prices 資料表
    __tablename__ = "daily_prices"

    # 股票代號，與 trade_date 組成複合主鍵
    ticker: Mapped[str] = mapped_column(Text, primary_key=True)

    # 交易日期，與 ticker 組成複合主鍵
    trade_date: Mapped[Date] = mapped_column(Date, primary_key=True)

    # 開盤價
    open_price: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 最高價
    high_price: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 最低價
    low_price: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 收盤價
    close_price: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 調整後收盤價
    adjusted_close: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 成交量
    volume: Mapped[int | None] = mapped_column(BigInteger)

    # 資料來源
    source: Mapped[str] = mapped_column(Text, nullable=False)

    # 資料寫入時間
    ingested_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )