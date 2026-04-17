import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from datetime import datetime
from shiny import module, ui, render, reactive

from api import get_transaction_stats, get_tickers, get_trader_ids, lookup_transactions


def _parse_time(s):
    """Parse HH:MM:SS. Returns (h, m, s) or None."""
    parts = s.strip().split(":")
    if len(parts) != 3:
        return None
    try:
        h, m, sec = int(parts[0]), int(parts[1]), int(parts[2])
        if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= sec <= 59):
            return None
        return h, m, sec
    except ValueError:
        return None


def _parse_nonneg_float(s):
    """Returns (float, None) on success or (None, error_str) on failure."""
    if not s or not s.strip():
        return None, None
    try:
        n = float(s.strip())
        if n < 0:
            return None, f"'{s}' must be >= 0"
        return n, None
    except ValueError:
        return None, f"'{s}' is not a number"


@module.ui
def transactions_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h5("Time Range"),
            ui.p("Start"),
            ui.layout_columns(
                ui.input_date("date_start", "Date"),
                ui.input_text("time_start", "Time (HH:MM:SS)", value="00:00:00"),
                col_widths=6,
            ),
            ui.p("End"),
            ui.layout_columns(
                ui.input_date("date_end", "Date"),
                ui.input_text("time_end", "Time (HH:MM:SS)", value="23:59:59"),
                col_widths=6,
            ),
            ui.output_ui("time_range_hint"),
            ui.output_ui("time_error"),
            ui.hr(),
            ui.h5("Tickers"),
            ui.output_ui("ticker_checkboxes"),
            ui.hr(),
            ui.h5("Trader IDs"),
            ui.output_ui("trader_checkboxes"),
            ui.hr(),
            ui.h5("Quantity & Price"),
            ui.layout_columns(
                ui.input_text("quantity_start", "Quantity min"),
                ui.input_text("quantity_end",   "Quantity max"),
                col_widths=6,
            ),
            ui.layout_columns(
                ui.input_text("price_start", "Price min"),
                ui.input_text("price_end",   "Price max"),
                col_widths=6,
            ),
            ui.output_ui("numeric_error"),
            ui.hr(),
            ui.h5("Options"),
            ui.input_checkbox("include_buy",       "Include BUY",        value=True),
            ui.input_checkbox("include_sell",      "Include SELL",       value=True),
            ui.input_checkbox("include_risky",     "Include risky rows", value=False),
            ui.input_checkbox("reverse_timestamp", "Newest first",       value=False),
            ui.hr(),
            ui.input_action_button("apply", "Apply Filters"),
            width=380,
        ),
        ui.output_data_frame("transactions_table"),
    )


@module.server
def transactions_server(input, output, session):
    stats      = get_transaction_stats(include_risky=True)["data"]
    ts_min     = datetime.strptime(stats["starting_timestamp"], "%Y-%m-%d %H:%M:%S")
    ts_max     = datetime.strptime(stats["ending_timestamp"],   "%Y-%m-%d %H:%M:%S")
    tickers    = sorted(get_tickers()["data"])
    trader_ids = sorted(get_trader_ids()["data"])

    @render.ui
    def time_range_hint():
        return ui.p(
            f"Data spans between {ts_min.strftime('%Y-%m-%d %H:%M:%S')} and {ts_max.strftime('%Y-%m-%d %H:%M:%S')}",
            style="font-size:0.85em; color:gray;"
        )

    @render.ui
    def ticker_checkboxes():
        return ui.input_checkbox_group(
            "tickers", None, choices=tickers, selected=tickers, inline=True
        )

    @render.ui
    def trader_checkboxes():
        return ui.input_checkbox_group(
            "trader_ids", None, choices=trader_ids, selected=trader_ids, inline=True
        )

    @render.ui
    def time_error():
        errors = []
        if _parse_time(input.time_start()) is None:
            errors.append("Start time must be HH:MM:SS")
        if _parse_time(input.time_end()) is None:
            errors.append("End time must be HH:MM:SS")
        if errors:
            return ui.p(" | ".join(errors), style="color:red; font-size:0.85em;")
        return ui.p("")

    @render.ui
    def numeric_error():
        errors = []
        for label, val in [
            ("Quantity min",   input.quantity_start()),
            ("Quantity max",   input.quantity_end()),
            ("Price min", input.price_start()),
            ("Price max", input.price_end()),
        ]:
            _, err = _parse_nonneg_float(val)
            if err:
                errors.append(f"{label}: {err}")
        if errors:
            return ui.p(" | ".join(errors), style="color:red; font-size:0.85em;")
        return ui.p("")

    @reactive.calc
    @reactive.event(input.apply)
    def fetch_transactions():
        d_start = input.date_start()
        d_end   = input.date_end()
        t_start = _parse_time(input.time_start())
        t_end   = _parse_time(input.time_end())

        if not d_start or not d_end or t_start is None or t_end is None:
            return []

        dt_start = datetime(d_start.year, d_start.month, d_start.day, *t_start)
        dt_end   = datetime(d_end.year,   d_end.month,   d_end.day,   *t_end)

        # Clamp to valid range
        dt_start = max(dt_start, ts_min)
        dt_end   = min(dt_end,   ts_max)

        if dt_start > dt_end:
            return []

        def safe_num(val):
            n, err = _parse_nonneg_float(val)
            return n if err is None else None

        payload = {
            "year_start":   dt_start.year,    "year_end":   dt_end.year,
            "month_start":  dt_start.month,   "month_end":  dt_end.month,
            "day_start":    dt_start.day,      "day_end":    dt_end.day,
            "hour_start":   dt_start.hour,     "hour_end":   dt_end.hour,
            "minute_start": dt_start.minute,   "minute_end": dt_end.minute,
            "second_start": dt_start.second,   "second_end": dt_end.second,
            "tickers":      list(input.tickers())    if input.tickers()    else [],
            "trader_ids":   list(input.trader_ids()) if input.trader_ids() else [],
            "quantity_start": safe_num(input.quantity_start()),
            "quantity_end":   safe_num(input.quantity_end()),
            "price_start":    safe_num(input.price_start()),
            "price_end":      safe_num(input.price_end()),
            "include_buy":       bool(input.include_buy()),
            "include_sell":      bool(input.include_sell()),
            "include_risky":     bool(input.include_risky()),
            "reverse_timestamp": bool(input.reverse_timestamp()),
        }

        result = lookup_transactions(payload)
        return result.get("data", [])

    @render.data_frame
    def transactions_table():
        data = fetch_transactions()
        if not data:
            return render.DataGrid(pd.DataFrame())
        return render.DataGrid(pd.DataFrame(data), filters=True)
