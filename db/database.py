from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import Settings


def get_database_url():

    settings = Settings()
    # 組合 PostgreSQL SQLAlchemy 連線字串
    return (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


# 建立全專案共用 engine
engine = create_engine(
    get_database_url(),
    echo=False,
    future=True,
)


# 建立 Session 工廠，用於 ORM 查詢與交易管理
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db_session():
    # 建立一個新的資料庫 session
    session = SessionLocal()

    try:
        # 回傳 session 給呼叫端使用
        yield session

    finally:
        # 使用完畢後關閉 session
        session.close()