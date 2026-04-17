import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from shiny import module, ui, render, reactive

from api import get_risky_lookup


@module.ui
def risky_ui():
    return ui.div(
        ui.layout_columns(
            ui.input_radio_buttons(
                "risk_level", None,
                choices=["high", "medium", "low"],
                selected="high",
                inline=True,
            ),
            ui.input_action_button("check", "Check"),
            col_widths=[6, 6],
        ),
        ui.output_data_frame("risky_table"),
    )


@module.server
def risky_server(input, output, session):
    data = reactive.value([])

    @reactive.effect
    @reactive.event(input.check)
    def _fetch():
        result = get_risky_lookup(input.risk_level())
        data.set(result.get("data", []))

    @render.data_frame
    def risky_table():
        rows = data()
        if not rows:
            return render.DataGrid(pd.DataFrame())
        return render.DataGrid(pd.DataFrame(rows), filters=True)
