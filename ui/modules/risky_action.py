import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shiny import module, ui, render, reactive

from api import soft_delete_by_id


@module.ui
def risky_action_ui():
    return ui.div(
        ui.h5("Soft Delete Transaction"),
        ui.input_text("delete_transaction_id", "Transaction ID"),
        ui.input_action_button("delete", "Delete"),
        ui.output_ui("delete_result"),
    )


@module.server
def risky_action_server(input, output, session):
    delete_msg = reactive.value(None)

    @reactive.effect
    @reactive.event(input.delete)
    def _delete():
        result = soft_delete_by_id(input.delete_transaction_id())
        delete_msg.set(result.get("status", "done"))

    @render.ui
    def delete_result():
        msg = delete_msg()
        return ui.p(msg) if msg else ui.div()
