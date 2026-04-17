import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shiny import module, ui, render, reactive

from api import get_ai_insights


@module.ui
def ai_ui():
    return ui.div(
        ui.input_action_button("generate", "Generate Insights (Takes ~2 minutes)"),
        ui.output_ui("insight_display"),
    )


@module.server
def ai_server(input, output, session):

    @reactive.extended_task
    async def fetch_insight():
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, get_ai_insights)
        return result.get("insight", "No insight returned.")

    @reactive.effect
    @reactive.event(input.generate)
    def _trigger():
        fetch_insight()

    @render.ui
    def insight_display():
        status = fetch_insight.status()
        if status == "running":
            return ui.p("Generating insights, please wait...")
        if status == "success":
            return ui.markdown(fetch_insight.result())
        if status == "error":
            return ui.p(f"Error: {fetch_insight.error()}")
        return ui.div()
