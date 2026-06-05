CREATE TABLE IF NOT EXISTS technical_indicators (
    ticker TEXT NOT NULL,
    trade_date DATE NOT NULL,

    sma_5 NUMERIC(18, 6),
    sma_20 NUMERIC(18, 6),
    sma_60 NUMERIC(18, 6),

    volume_avg_20d NUMERIC(18, 6),
    volume_ratio_20d NUMERIC(18, 6),

    source TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (ticker, trade_date)
);