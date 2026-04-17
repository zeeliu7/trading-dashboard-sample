from shiny import App
from shiny.ui import page_navbar, nav_panel

from modules.overview import overview_ui, overview_server
from modules.transactions_dashboard import transactions_ui, transactions_server
from modules.risky_dashboard import risky_ui, risky_server
from modules.risky_action import risky_action_ui, risky_action_server
from modules.ai_display import ai_ui, ai_server

app_ui = page_navbar(
    nav_panel("Overview", overview_ui("overview")),
    nav_panel("Transactions", transactions_ui("transactions")),
    nav_panel("Risky Data", risky_ui("risky")),
    nav_panel("Risky Action", risky_action_ui("risky_action")),
    nav_panel("AI Insight", ai_ui("ai")),
    title="Trading Dashboard",
    id="navbar",
)

def server(input, output, session):
    overview_server("overview")
    transactions_server("transactions")
    risky_server("risky")
    risky_action_server("risky_action")
    ai_server("ai")

app = App(app_ui, server)
