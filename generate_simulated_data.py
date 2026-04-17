import random
import csv
from datetime import datetime, timedelta

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'META', 'AMZN', 'TSLA', 'NFLX', 'AMD', 'INTC']
ACTIONS = ['BUY', 'SELL']
TRADERS = [f'T{str(i).zfill(3)}' for i in range(1, 21)]  # T001–T020

PRICE_RANGES = {
    'AAPL': (150, 200), 'GOOGL': (100, 150), 'MSFT': (300, 400),
    'NVDA': (400, 500), 'META': (200, 300), 'AMZN': (150, 200),
    'TSLA': (200, 300), 'NFLX': (500, 600), 'AMD': (100, 150), 'INTC': (20, 50),
}

def random_timestamp(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def fmt_ts(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def random_price(ticker):
    lo, hi = PRICE_RANGES[ticker]
    return round(random.uniform(lo, hi), 2)

def random_qty():
    return random.choice([50, 100, 150, 200, 250, 500])

start_dt = datetime(2026, 1, 1, 9, 0, 0)
end_dt   = datetime(2026, 1, 3, 16, 0, 0)

rows = []

# ~950 normal rows (950 + 20 high + 16 medium + 14 low = 1000)
for _ in range(950):
    ticker = random.choice(TICKERS)
    trader = random.choice(TRADERS) if random.random() > 0.03 else ''  # ~3% missing trader_id
    rows.append({
        'timestamp': fmt_ts(random_timestamp(start_dt, end_dt)),
        'ticker': ticker,
        'action': random.choice(ACTIONS),
        'quantity': random_qty(),
        'price': random_price(ticker),
        'trader_id': trader,
    })

# High-risk duplicates: identical on all 6 fields (~10 pairs = 20 rows)
for _ in range(10):
    ticker = random.choice(TICKERS)
    ts = fmt_ts(random_timestamp(start_dt, end_dt))
    action = random.choice(ACTIONS)
    qty = random_qty()
    price = random_price(ticker)
    trader = random.choice(TRADERS)
    dup = {'timestamp': ts, 'ticker': ticker, 'action': action,
           'quantity': qty, 'price': price, 'trader_id': trader}
    rows.append(dup)
    rows.append(dup.copy())

# Medium-risk duplicates: same timestamp/ticker/action/quantity/trader_id, different price (~8 pairs = 16 rows)
for _ in range(8):
    ticker = random.choice(TICKERS)
    ts = fmt_ts(random_timestamp(start_dt, end_dt))
    action = random.choice(ACTIONS)
    qty = random_qty()
    trader = random.choice(TRADERS)
    lo, hi = PRICE_RANGES[ticker]
    price1 = round(random.uniform(lo, hi), 2)
    price2 = round(price1 + random.uniform(0.5, 2.0), 2)
    for p in (price1, price2):
        rows.append({'timestamp': ts, 'ticker': ticker, 'action': action,
                     'quantity': qty, 'price': p, 'trader_id': trader})

# Low-risk duplicates: same timestamp/ticker/quantity/trader_id, different action/price (~7 pairs = 14 rows)
for _ in range(7):
    ticker = random.choice(TICKERS)
    ts = fmt_ts(random_timestamp(start_dt, end_dt))
    qty = random_qty()
    trader = random.choice(TRADERS)
    for action in ('BUY', 'SELL'):
        rows.append({'timestamp': ts, 'ticker': ticker, 'action': action,
                     'quantity': qty, 'price': random_price(ticker), 'trader_id': trader})

# Shuffle and trim to exactly 1000
random.shuffle(rows)
rows = rows[:1000]

with open('sample_transactions.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'ticker', 'action', 'quantity', 'price', 'trader_id'])
    writer.writeheader()
    writer.writerows(rows)

print(f"Written {len(rows)} rows to sample_transactions.csv")
