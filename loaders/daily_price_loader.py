from db.database import engine


def load_daily_prices(df):
    # 開啟 transaction，成功 commit，失敗 rollback
    with engine.begin() as conn:
        # 將 DataFrame 追加寫入 daily_prices
        df.to_sql(
            name="daily_prices",
            con=conn,
            if_exists="append",
            index=False,
        )

    # 回傳寫入筆數，方便主流程確認
    return len(df)