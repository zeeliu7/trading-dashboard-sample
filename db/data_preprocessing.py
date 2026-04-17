import uuid
import pandas as pd


def preprocess_data(csv_file_name: str, conn):
    df = pd.read_csv(csv_file_name)

    df['trader_id'] = df['trader_id'].fillna('unknown')
    df.insert(0, 'transaction_id', [str(uuid.uuid4()) for _ in range(len(df))])
    df['is_risky'] = False
    df['risk_level'] = 'safe'
    df['soft_delete'] = False

    high_cols = ['timestamp', 'ticker', 'action', 'quantity', 'price', 'trader_id']
    medium_cols = ['timestamp', 'ticker', 'action', 'quantity', 'trader_id']
    low_cols = ['timestamp', 'ticker', 'quantity', 'trader_id']

    high_mask = df.duplicated(subset=high_cols, keep=False)
    medium_mask = df.duplicated(subset=medium_cols, keep=False) & ~high_mask
    low_mask = df.duplicated(subset=low_cols, keep=False) & ~high_mask & ~medium_mask

    df.loc[high_mask, 'risk_level'] = 'high'
    df.loc[medium_mask, 'risk_level'] = 'medium'
    df.loc[low_mask, 'risk_level'] = 'low'
    df.loc[high_mask | medium_mask | low_mask, 'is_risky'] = True

    df = df.sort_values('timestamp').reset_index(drop=True)

    df.to_sql('transactions', conn, if_exists='replace', index=False)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_ticker ON transactions(ticker)")
    conn.commit()
