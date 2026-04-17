import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shiny import module, ui, render, reactive

from api import get_transaction_stats, get_ticker_ranking, get_trader_id_ranking, get_risky_counts


@module.ui
def overview_ui():
    return ui.div(
        ui.layout_columns(
            ui.input_checkbox("include_risky", "Include risky data", value=False),
            ui.input_action_button("refresh", "Refresh"),
        ),
        ui.layout_columns(
            ui.div(ui.h5("Summary"),     ui.output_ui("stats_col")),
            ui.div(ui.h5("Top Tickers"), ui.output_ui("ticker_ranking_col")),
            ui.div(ui.h5("Top Traders"), ui.output_ui("trader_ranking_col")),
            ui.div(ui.h5("Risky Data"),  ui.output_ui("risky_counts_col")),
            col_widths=[3, 3, 3, 3],
        ),
    )


@module.server
def overview_server(input, output, session):

    @reactive.calc
    def fetch_data():
        input.refresh()
        include_risky = bool(input.include_risky())
        stats        = get_transaction_stats(include_risky=include_risky)["data"]
        ticker_rank  = get_ticker_ranking(include_risky=include_risky)["data"]
        trader_rank  = get_trader_id_ranking(include_risky=include_risky)["data"]
        risky_counts = get_risky_counts()["data"]
        return stats, ticker_rank, trader_rank, risky_counts

    @render.ui
    def stats_col():
        stats, _, _, _ = fetch_data()
        labels = {
            "starting_timestamp": "Start",
            "ending_timestamp":   "End",
            "total_transactions": "Total transactions",
            "buy_volume":         "Buy volume",
            "buy_dollar":         "Buy value",
            "sell_volume":        "Sell volume",
            "sell_dollar":        "Sell value",
            "total_tickers":      "Tickers",
            "total_traders":      "Traders",
        }
        rows = [ui.p(f"{label}: {stats[key]}") for key, label in labels.items()]
        return ui.div(*rows)

    @render.ui
    def ticker_ranking_col():
        _, ticker_rank, _, _ = fetch_data()
        names, volumes = ticker_rank
        rows = [ui.p(f"{n}: {v}") for n, v in zip(names, volumes)]
        return ui.div(*rows)

    @render.ui
    def trader_ranking_col():
        _, _, trader_rank, _ = fetch_data()
        names, counts = trader_rank
        rows = [ui.p(f"{n}: {c}") for n, c in zip(names, counts)]
        return ui.div(*rows)

    @render.ui
    def risky_counts_col():
        _, _, _, risky_counts = fetch_data()
        rows = [ui.p(f"{level}: {count}") for level, count in risky_counts.items()]
        return ui.div(*rows)
