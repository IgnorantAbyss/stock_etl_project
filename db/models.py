from sqlalchemy import BigInteger, Boolean, Date, DateTime, Numeric, Text
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

# 技術指標table物件
class TechnicalIndicator(Base):
    # 對應 technical_indicators 資料表
    __tablename__ = "technical_indicators"

    # 股票代號，與 trade_date 組成複合主鍵
    ticker: Mapped[str] = mapped_column(Text, primary_key=True)

    # 交易日期，與 ticker 組成複合主鍵
    trade_date: Mapped[Date] = mapped_column(Date, primary_key=True)

    # 5 日簡單移動平均
    sma_5: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 20 日簡單移動平均
    sma_20: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 60 日簡單移動平均
    sma_60: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 20 日平均成交量
    volume_avg_20d: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 當日成交量相對 20 日平均量
    volume_ratio_20d: Mapped[float | None] = mapped_column(Numeric(18, 6))

    # 指標資料來源
    source: Mapped[str] = mapped_column(Text, nullable=False)

    # 資料建立時間
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    # 資料更新時間
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

# 公司主檔 table 物件
class Company(Base):
    # 對應 companies 資料表
    __tablename__ = "companies"

    # 股票代號，作為公司主檔主鍵
    ticker: Mapped[str] = mapped_column(Text, primary_key=True)

    # 公司名稱
    company_name: Mapped[str | None] = mapped_column(Text)

    # 交易所，例如 NASDAQ / NYSE
    exchange: Mapped[str | None] = mapped_column(Text)

    # 大產業分類
    sector: Mapped[str | None] = mapped_column(Text)

    # 細產業分類
    industry: Mapped[str | None] = mapped_column(Text)

    # 公司所屬國家
    country: Mapped[str | None] = mapped_column(Text)

    # 交易幣別
    currency: Mapped[str | None] = mapped_column(Text)

    # 是否仍作為目前追蹤標的
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
        nullable=False,
    )

    # 公司資料來源
    source: Mapped[str] = mapped_column(Text, nullable=False)

    # 資料建立時間
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    # 資料更新時間
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )