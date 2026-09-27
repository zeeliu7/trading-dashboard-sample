import json
import statistics

def return_unique_tickers(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT ticker "
        "FROM transactions "
        "WHERE soft_delete = 0"
    )
    return [row["ticker"] for row in cursor.fetchall()]

def return_unique_trader_ids(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT trader_id "
        "FROM transactions "
        "WHERE soft_delete = 0"
    )
    return [row["trader_id"] for row in cursor.fetchall()]

def transactions_lookup(conn, year_start, year_end, month_start, month_end, day_start, day_end, hour_start, hour_end, minute_start, minute_end, second_start, second_end, tickers, quantity_start, quantity_end, price_start, price_end, trader_ids, include_buy=True, include_sell=True, include_risky=False, reverse_timestamp=False):
    if not include_buy and not include_sell:
        return json.dumps([])

    params = []
    query = "SELECT * FROM transactions WHERE soft_delete = 0"

    if year_start and month_start and day_start and hour_start and minute_start and second_start:
        ts_start = f"{year_start:04d}-{month_start:02d}-{day_start:02d} {hour_start:02d}:{minute_start:02d}:{second_start:02d}"
        query += " AND timestamp >= ?"
        params.append(ts_start)

    if year_end and month_end and day_end and hour_end and minute_end and second_end:
        ts_end = f"{year_end:04d}-{month_end:02d}-{day_end:02d} {hour_end:02d}:{minute_end:02d}:{second_end:02d}"
        query += " AND timestamp <= ?"
        params.append(ts_end)

    if tickers:
        placeholders = ",".join("?" * len(tickers))
        query += f" AND ticker IN ({placeholders})"
        params.extend(tickers)

    if include_buy and not include_sell:
        query += " AND action = 'BUY'"
    if include_sell and not include_buy:
        query += " AND action = 'SELL'"

    if quantity_start:
        query += " AND quantity >= ?"
        params.append(quantity_start)
    if quantity_end:
        query += " AND quantity <= ?"
        params.append(quantity_end)

    if price_start:
        query += " AND price >= ?"
        params.append(price_start)
    if price_end:
        query += " AND price <= ?"
        params.append(price_end)

    if not include_risky:
        query += " AND is_risky = 0"

    if trader_ids:
        placeholders = ",".join("?" * len(trader_ids))
        query += f" AND trader_id IN ({placeholders})"
        params.extend(trader_ids)

    if reverse_timestamp:
        query += " ORDER BY timestamp DESC"
    else:
        query += " ORDER BY timestamp ASC"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    return json.dumps(rows)

# action: ["buy", "sell", "absolute"]
def total_traded_per_ticker(conn, tickers, include_risky, use_volume, action):
    if not tickers:
        tickers = return_unique_tickers(conn)
    if not tickers:
        return json.dumps({})

    risky_clause = "" if include_risky else " AND is_risky = 0"
    sum_clause = "SUM(quantity)" if use_volume else "SUM(quantity * price)"

    if action == "buy":
        action_clause = " AND action = 'BUY'"
    elif action == "sell":
        action_clause = " AND action = 'SELL'"
    else:
        action_clause = ""

    placeholders = ",".join("?" * len(tickers))
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT ticker, {sum_clause} AS total "
        f"FROM transactions "
        f"WHERE ticker IN ({placeholders}) "
        f"AND soft_delete = 0{risky_clause}{action_clause} "
        f"GROUP BY ticker",
        tickers
    )
    totals = {row["ticker"]: row["total"] or 0 for row in cursor.fetchall()}
    return json.dumps({t: totals.get(t, 0) for t in tickers})

def net_position_per_ticker(conn, tickers, include_risky, use_volume):
    if not tickers:
        tickers = return_unique_tickers(conn)
    if not tickers:
        return json.dumps({})

    risky_clause = "" if include_risky else " AND is_risky = 0"
    value_expr = "quantity" if use_volume else "quantity * price"

    placeholders = ",".join("?" * len(tickers))
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT ticker, "
        f"SUM(CASE WHEN action = 'BUY' THEN {value_expr} ELSE -{value_expr} END) AS net "
        f"FROM transactions "
        f"WHERE ticker IN ({placeholders}) "
        f"AND soft_delete = 0{risky_clause} "
        f"GROUP BY ticker",
        tickers
    )
    nets = {row["ticker"]: row["net"] or 0 for row in cursor.fetchall()}
    return json.dumps({t: nets.get(t, 0) for t in tickers})

def total_transactions_per_trader_id(conn, trader_ids, include_risky, action):
    if not trader_ids:
        trader_ids = return_unique_trader_ids(conn)
    if not trader_ids:
        return json.dumps({})

    risky_clause = "" if include_risky else " AND is_risky = 0"

    if action == "buy":
        action_clause = " AND action = 'BUY'"
    elif action == "sell":
        action_clause = " AND action = 'SELL'"
    else:
        action_clause = ""

    placeholders = ",".join("?" * len(trader_ids))
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT trader_id, COUNT(*) AS total "
        f"FROM transactions "
        f"WHERE trader_id IN ({placeholders}) "
        f"AND soft_delete = 0{risky_clause}{action_clause} "
        f"GROUP BY trader_id",
        trader_ids
    )
    totals = {row["trader_id"]: row["total"] or 0 for row in cursor.fetchall()}
    return json.dumps({t: totals.get(t, 0) for t in trader_ids})

def get_hourly_data(conn, ticker, is_buy, include_risky):
    risky_clause  = "" if include_risky else " AND is_risky = 0"
    action_clause = " AND action = 'BUY'" if is_buy else " AND action = 'SELL'"
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT strftime('%Y-%m-%d %H', timestamp) AS hour, AVG(price) AS avg_price, SUM(quantity) AS volume "
        f"FROM transactions "
        f"WHERE ticker = ? AND soft_delete = 0{action_clause}{risky_clause} "
        f"GROUP BY hour "
        f"ORDER BY hour",
        [ticker]
    )

    rows = [{"hour": row["hour"], "avg_price": row["avg_price"], "volume": row["volume"]} for row in cursor.fetchall()]
    return json.dumps(rows)


def get_hourly_stats(conn, ticker, is_buy, include_risky):
    hourly_data = json.loads(get_hourly_data(conn, ticker, is_buy, include_risky))
    if not hourly_data:
        return json.dumps({})

    hours = [row["hour"] for row in hourly_data]
    avg_prices = [row["avg_price"] for row in hourly_data]
    volumes = [row["volume"] for row in hourly_data]

    # volume-weighted average price
    vwap = sum(p * v for p, v in zip(avg_prices, volumes)) / sum(volumes)
    sd = statistics.stdev(avg_prices) if len(avg_prices) > 1 else 0

    return json.dumps({
        "starting_hour": hours[0],
        "ending_hour": hours[-1],
        "max": max(avg_prices),
        "min": min(avg_prices),
        "mean": statistics.mean(avg_prices),
        "sd": sd,
        "vwap": vwap
    })

def total_transactions_stats(conn, include_risky):
    risky_clause = "" if include_risky else " AND is_risky = 0"

    cursor = conn.cursor()

    cursor.execute(
        f"SELECT MIN(timestamp), MAX(timestamp), COUNT(*) "
        f"FROM transactions "
        f"WHERE soft_delete = 0{risky_clause}"
    )
    start_ts, end_ts, total = cursor.fetchone()

    cursor.execute(
        f"SELECT SUM(quantity), SUM(quantity * price) "
        f"FROM transactions "
        f"WHERE action = 'SELL' AND soft_delete = 0{risky_clause}"
    )
    sell_volume, sell_dollar = cursor.fetchone()

    cursor.execute(
        f"SELECT SUM(quantity), SUM(quantity * price) "
        f"FROM transactions "
        f"WHERE action = 'BUY' AND soft_delete = 0{risky_clause}"
    )
    buy_volume, buy_dollar = cursor.fetchone()

    return json.dumps({
        "starting_timestamp": start_ts,
        "ending_timestamp": end_ts,
        "total_transactions": total,
        "sell_volume": sell_volume or 0,
        "sell_dollar": sell_dollar or 0,
        "buy_volume": buy_volume or 0,
        "buy_dollar": buy_dollar or 0,
        "total_tickers": len(return_unique_tickers(conn)),
        "total_traders": len(return_unique_trader_ids(conn))
    })

def get_ticker_ranking(conn, include_risky):
    risky_clause = "" if include_risky else " AND is_risky = 0"
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT ticker, SUM(quantity) AS volume "
        f"FROM transactions "
        f"WHERE soft_delete = 0{risky_clause} "
        f"GROUP BY ticker "
        f"ORDER BY volume DESC"
    )
    rows = cursor.fetchall() # no JSON here, using list to keep the order
    return [[r[0] for r in rows], [r[1] for r in rows]]


def get_trader_id_ranking(conn, include_risky):
    risky_clause = "" if include_risky else " AND is_risky = 0"
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT trader_id, COUNT(*) AS transaction_count "
        f"FROM transactions "
        f"WHERE soft_delete = 0{risky_clause} "
        f"GROUP BY trader_id "
        f"ORDER BY transaction_count DESC"
    )
    rows = cursor.fetchall()
    return [[r[0] for r in rows], [r[1] for r in rows]]
