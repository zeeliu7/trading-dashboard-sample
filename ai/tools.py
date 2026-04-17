import json
import sqlite3
import threading
from typing import Optional
from langchain.tools import tool
from db import *

_db_path = None
_local = threading.local()

def set_conn(conn):
    global _db_path
    _db_path = conn.execute("PRAGMA database_list").fetchone()[2]

def _get_conn():
    if not hasattr(_local, 'conn'):
        _local.conn = sqlite3.connect(_db_path, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


# --------------------- Overview tools ---------------------

@tool
def tool_total_transactions_stats(include_risky: bool = False) -> str:
    """
    Returns a high-level summary of all transactions: date range, total count, buy/sell volumes and dollar values, number of tickers and traders involved.
    Use this to understand the overall scale and composition of the market data.
    Set `include_risky=True` to include flagged transactions.
    """
    return total_transactions_stats(_get_conn(), include_risky)


@tool
def tool_risky_data_counts() -> str:
    """
    Returns the count of risky transactions broken down by risk level (high/medium/low).
    Use this to understand the severity of data quality issues before investigation on specific traders or time patterns where problematic data cluster.
    """
    return risky_data_counts(_get_conn())


# --------------------- Research tools ---------------------

@tool
def tool_return_unique_tickers() -> str:
    """
    Returns a list of all unique ticker symbols present in the transactions database.
    You may use tickers inside the list for further research, such as `tool_total_traded_per_ticker()` and `tool_net_position_per_ticker()`.
    """
    return json.dumps(return_unique_tickers(_get_conn()))


@tool
def tool_return_unique_trader_ids() -> str:
    """
    Returns a list of all unique trader IDs in the database.
    All missing trader IDs have been filled with 'unknown'.
    You may use trader IDs inside this list for further research, such as `tool_total_transactions_per_trader()`.
    """
    return json.dumps(return_unique_trader_ids(_get_conn()))


@tool
def tool_total_traded_per_ticker(
    tickers: Optional[list] = None,
    include_risky: bool = False,
    use_volume: bool = True,
    action: str = "absolute"
) -> str:
    """
    Returns total traded quantity (use_volume=True) or dollar value (use_volume=False).
    It will return data for each of the tickers you listed in `tickers`, or all tickers when `tickers=None`.
    `action` can be 'buy', 'sell', or 'absolute' (combined).
    Use this to understand the distribution of transactions among tickers.
    Set `include_risky=True` to include flagged transactions.
    """
    return total_traded_per_ticker(_get_conn(), tickers, include_risky, use_volume, action)


@tool
def tool_net_position_per_ticker(
    tickers: Optional[list] = None,
    include_risky: bool = False,
    use_volume: bool = True
) -> str:
    """
    Returns the net position (buys minus sells) per ticker, in quantity (use_volume=True) or dollar value (use_volume=False).
    It will return data for each of the tickers you listed in `tickers`, or all tickers when `tickers=None`.
    Use this to understand the pattern across all transactions for each ticker.
    Set `include_risky=True` to include flagged transactions.
    """
    return net_position_per_ticker(_get_conn(), tickers, include_risky, use_volume)


@tool
def tool_total_transactions_per_trader(
    trader_ids: Optional[list] = None,
    include_risky: bool = False,
    action: str = "absolute"
) -> str:
    """
    Returns the transaction count per trader ID.
    `action` can be 'buy', 'sell', or 'absolute' (combined).
    It will return data for each of the trader IDs you listed in `trader_ids`, or all tickers when `trader_ids=None`.
    Use this to understand the most active traders and abnormal trading activities.
    Set `include_risky=True` to include flagged transactions.
    """
    return total_transactions_per_trader_id(_get_conn(), trader_ids, include_risky, action)


@tool
def tool_risky_data_by_hour() -> str:
    """
    Returns counts of high/medium/low risk transactions per hour, along with each hour's total transaction count.
    Use this to detect whether flagged activities cluster at particular hours.
    """
    return risky_data_by_hour(_get_conn())


@tool
def tool_risky_data_by_trader() -> str:
    """
    Returns counts of high/medium/low risk transactions per trader, along with each trader's total transaction count.
    Use this to identify which traders are responsible for the most risky activity and their risky fraction overall.
    Note: if the trader ID is 'unknown', it means the original data was missing, and the trader could be anyone appeared in the system or not.
    """
    return risky_data_by_trader_id(_get_conn())


@tool
def tool_get_hourly_stats(ticker: str, is_buy: bool, include_risky: bool = False) -> str:
    """
    Returns hourly price statistics for a specific ticker and action (buy/sell): starting/ending hour, max, min, mean, standard deviation, and VWAP.
    Use this to analyze price behavior and volatility for a particular stock.
    `ticker` requires a specific ticker: call `tool_return_unique_tickers()` if you need the list of tickers available.
    Set `include_risky=True` to include flagged transactions.
    """
    return get_hourly_stats(_get_conn(), ticker, is_buy, include_risky)


# --------------------- All tools ---------------------

all_tools = [
    tool_total_transactions_stats,
    tool_risky_data_counts,
    tool_return_unique_tickers,
    tool_return_unique_trader_ids,
    tool_total_traded_per_ticker,
    tool_net_position_per_ticker,
    tool_total_transactions_per_trader,
    tool_risky_data_by_hour,
    tool_risky_data_by_trader,
    tool_get_hourly_stats,
]