import json
from collections import defaultdict


def risky_data_lookup(conn, risk_level):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * "
        "FROM transactions "
        "WHERE risk_level = ? AND soft_delete = 0",
        (risk_level,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    return json.dumps(rows)


def risky_data_counts(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT risk_level, COUNT(*) "
        "FROM transactions "
        "WHERE risk_level != 'safe' AND soft_delete = 0 "
        "GROUP BY risk_level"
    )
    return json.dumps({row[0]: row[1] for row in cursor.fetchall()})


def risky_data_by_hour(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT strftime('%Y-%m-%d %H', timestamp) AS hour, risk_level, COUNT(*) "
        "FROM transactions WHERE risk_level != 'safe' AND soft_delete = 0 "
        "GROUP BY hour, risk_level "
        "ORDER BY hour"
    )
    result = defaultdict(dict)
    for hour, risk_level, count in cursor.fetchall():
        result[hour][risk_level] = count

    cursor.execute(
        "SELECT strftime('%Y-%m-%d %H', timestamp) AS hour, COUNT(*) "
        "FROM transactions WHERE soft_delete = 0 "
        "GROUP BY hour"
    )
    totals = {row[0]: row[1] for row in cursor.fetchall()}
    for hour in result:
        result[hour]['total'] = totals[hour]

    return json.dumps(result)


def risky_data_by_trader_id(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT trader_id, risk_level, COUNT(*)"
        "FROM transactions "
        "WHERE risk_level != 'safe' AND soft_delete = 0 "
        "GROUP BY trader_id, risk_level "
        "ORDER BY trader_id"
    )
    result = defaultdict(dict)
    for trader_id, risk_level, count in cursor.fetchall():
        result[trader_id][risk_level] = count

    cursor.execute(
        "SELECT trader_id, COUNT(*) "
        "FROM transactions "
        "WHERE soft_delete = 0 "
        "GROUP BY trader_id "
        "ORDER BY trader_id"
    )
    totals = {row[0]: row[1] for row in cursor.fetchall()}
    for trader_id in result:
        result[trader_id]['total'] = totals[trader_id]

    return json.dumps(result)


def soft_delete_by_transaction_id(conn, transaction_id):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions "
        "SET soft_delete = 1 "
        "WHERE transaction_id = ?",
        (transaction_id,)
    )
    conn.commit()
