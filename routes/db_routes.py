import json
from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator

from db import *

router = APIRouter(prefix="/db")

curr_conn = None

def set_conn(conn):
    global curr_conn
    curr_conn = conn


# --------------------- Pydantic Models ---------------------

class TransactionsLookupRequest(BaseModel):
    year_start:   int
    year_end:     int
    month_start:  int
    month_end:    int
    day_start:    int
    day_end:      int
    hour_start:   int
    hour_end:     int
    minute_start: int
    minute_end:   int
    second_start: int
    second_end:   int
    tickers:      Optional[List[str]] = None
    quantity_start: Optional[float] = None
    quantity_end:   Optional[float] = None
    price_start:    Optional[float] = None
    price_end:      Optional[float] = None
    trader_ids:     Optional[List[str]] = None
    include_buy:       bool = True
    include_sell:      bool = True
    include_risky:     bool = False
    reverse_timestamp: bool = False

    @model_validator(mode='after')
    def check_start_before_end(self):
        dt_start = datetime(self.year_start, self.month_start, self.day_start, self.hour_start, self.minute_start, self.second_start)
        dt_end = datetime(self.year_end, self.month_end, self.day_end, self.hour_end, self.minute_end, self.second_end)
        if dt_start > dt_end:
            raise ValueError("Start datetime must be before end datetime")
        return self


class TradedPerTickerRequest(BaseModel):
    tickers:      Optional[List[str]] = None
    include_risky: bool = False
    use_volume:    bool = True
    action: Literal['buy', 'sell', 'absolute'] = 'absolute'


class NetPositionRequest(BaseModel):
    tickers:      Optional[List[str]] = None
    include_risky: bool = False
    use_volume:    bool = True


class TransactionsPerTraderRequest(BaseModel):
    trader_ids:    Optional[List[str]] = None
    include_risky: bool = False
    action: Literal['buy', 'sell', 'absolute'] = 'absolute'


class HourlyRequest(BaseModel):
    ticker:        str
    is_buy:        bool
    include_risky: bool = False


class RiskyLookupRequest(BaseModel):
    risk_level: Literal['high', 'medium', 'low']


class SoftDeleteByIdRequest(BaseModel):
    transaction_id: str



# --------------------- Endpoints ---------------------

def _ok(data):
    return JSONResponse(content={"status": "success", "data": data})

def _err(e):
    return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.get("/tickers")
def get_tickers():
    try:
        return _ok(return_unique_tickers(curr_conn))
    except Exception as e:
        return _err(e)


@router.get("/traders")
def get_traders():
    try:
        return _ok(return_unique_trader_ids(curr_conn))
    except Exception as e:
        return _err(e)


@router.get("/transactions/stats")
def get_transactions_stats(include_risky: bool = False):
    try:
        return _ok(json.loads(total_transactions_stats(curr_conn, include_risky)))
    except Exception as e:
        return _err(e)


@router.post("/transactions/lookup")
def get_transactions_lookup(request: TransactionsLookupRequest):
    try:
        data = transactions_lookup(
            curr_conn,
            request.year_start,   request.year_end,
            request.month_start,  request.month_end,
            request.day_start,    request.day_end,
            request.hour_start,   request.hour_end,
            request.minute_start, request.minute_end,
            request.second_start, request.second_end,
            request.tickers,
            request.quantity_start, request.quantity_end,
            request.price_start,    request.price_end,
            request.trader_ids,
            request.include_buy,
            request.include_sell,
            request.include_risky,
            request.reverse_timestamp,
        )
        return _ok(json.loads(data))
    except Exception as e:
        return _err(e)


@router.post("/traded/per-ticker")
def get_traded_per_ticker(request: TradedPerTickerRequest):
    try:
        data = total_traded_per_ticker(curr_conn, request.tickers or [], request.include_risky, request.use_volume, request.action)
        return _ok(json.loads(data))
    except Exception as e:
        return _err(e)


@router.post("/net-position/per-ticker")
def get_net_position_per_ticker(request: NetPositionRequest):
    try:
        data = net_position_per_ticker(curr_conn, request.tickers or [], request.include_risky, request.use_volume)
        return _ok(json.loads(data))
    except Exception as e:
        return _err(e)


@router.post("/transactions/per-trader")
def get_transactions_per_trader(request: TransactionsPerTraderRequest):
    try:
        data = total_transactions_per_trader_id(curr_conn, request.trader_ids or [], request.include_risky, request.action)
        return _ok(json.loads(data))
    except Exception as e:
        return _err(e)


@router.post("/hourly-data")
def get_hourly_data_endpoint(request: HourlyRequest):
    try:
        return _ok(json.loads(get_hourly_data(curr_conn, request.ticker, request.is_buy, request.include_risky)))
    except Exception as e:
        return _err(e)


@router.post("/hourly-stats")
def get_hourly_stats_endpoint(request: HourlyRequest):
    try:
        return _ok(json.loads(get_hourly_stats(curr_conn, request.ticker, request.is_buy, request.include_risky)))
    except Exception as e:
        return _err(e)


@router.post("/risky/lookup")
def get_risky_data(request: RiskyLookupRequest):
    try:
        return _ok(json.loads(risky_data_lookup(curr_conn, request.risk_level)))
    except Exception as e:
        return _err(e)


@router.get("/risky/counts")
def get_risky_counts():
    try:
        return _ok(json.loads(risky_data_counts(curr_conn)))
    except Exception as e:
        return _err(e)


@router.get("/risky/by-hour")
def get_risky_by_hour():
    try:
        return _ok(json.loads(risky_data_by_hour(curr_conn)))
    except Exception as e:
        return _err(e)


@router.get("/risky/by-trader")
def get_risky_by_trader():
    try:
        return _ok(json.loads(risky_data_by_trader_id(curr_conn)))
    except Exception as e:
        return _err(e)



@router.post("/risky/soft-delete-by-id")
def post_soft_delete_by_id(request: SoftDeleteByIdRequest):
    try:
        soft_delete_by_transaction_id(curr_conn, request.transaction_id)
        return _ok(None)
    except Exception as e:
        return _err(e)



@router.get("/ranking/ticker")
def get_ticker_ranking_endpoint(include_risky: bool = False):
    try:
        return _ok(get_ticker_ranking(curr_conn, include_risky))
    except Exception as e:
        return _err(e)


@router.get("/ranking/trader")
def get_trader_id_ranking_endpoint(include_risky: bool = False):
    try:
        return _ok(get_trader_id_ranking(curr_conn, include_risky))
    except Exception as e:
        return _err(e)
