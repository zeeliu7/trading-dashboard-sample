import os
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
from langchain.agents import create_agent

from ai.tools import all_tools

load_dotenv()


SYSTEM_PROMPT = """You are a trading data analyst reviewing transaction records for an asset management company.

You have access to two groups of tools connected to the transaction database:

Overview tools — call these first to understand the context:
- tool_total_transactions_stats: overview of all transactions
- tool_risky_data_counts: overview of flagged transactions by severity

Research tools — use these to investigate specific areas once you have context:
- tool_return_unique_tickers: discover available tickers
- tool_return_unique_trader_ids: discover available trader IDs
- tool_total_traded_per_ticker: trading volume or value per ticker
- tool_net_position_per_ticker: net position after all transactions per ticker
- tool_total_transactions_per_trader: transaction counts per trader
- tool_risky_data_by_hour: risky transaction breakdown by hour
- tool_risky_data_by_trader: risky transaction breakdown by trader
- tool_get_hourly_stats: price statistics for a specific ticker and action

Certain tools will include a `include_risky` parameter, which is set to False by default.
Set `include_risky=True` to include flagged transactions.
Be consistent about your choice throughout the process, and mention your choice in your final output.

Utilize the research tools based on the overview data for in-depth analysis."""


INSIGHT_PROMPT = """Analyze the trading data and produce a structured insight report covering:
1. Trading patterns — overall activity, buy/sell balance, dominant tickers and traders
2. Concentration risk — whether activity is overly concentrated in specific tickers, traders, or time windows
3. Unusual activity — risky or flagged transactions, unknown trader IDs, abnormal time clustering

Be specific about the numbers, trader IDs, and tickers you have used for your report.

Write in a professional, structured style and no emojis. Your report will directly support the senior manager of the trading department."""


def build_agent():
    model = os.getenv("MODEL")
    api_key = os.getenv("API_KEY")
    temperature = os.getenv("TEMPERATURE")
    llm = ChatLiteLLM(model=model, api_key=api_key or None, temperature=float(temperature) if temperature else None)
    return create_agent(llm, all_tools, system_prompt=SYSTEM_PROMPT)


curr_agent = None

def get_agent():
    global curr_agent
    if curr_agent is None:
        curr_agent = build_agent()
    return curr_agent


def generate_insight() -> str:
    result = get_agent().invoke({"messages": [{"role": "user", "content": INSIGHT_PROMPT}]})
    return result["messages"][-1].content
