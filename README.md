# Trading Dashboard Sample

## About

A trading dashboard that turns raw transaction CSV data into a live, queryable, and AI-analyzed workspace. Load your data, explore it through a rich multi-filter UI, catch suspicious entries before they become problems, and get a focused AI-generated report — all without leaving the browser.

### What you can do

**Slice and dice your transaction history**
Filter transactions by any combination of time range, ticker, trader, quantity, price, and action (BUY/SELL). Results update instantly in a sortable data grid, backed by an indexed SQLite database so lookups stay fast even as data grows.

**Catch data quality issues automatically**
On load, every transaction is scanned for suspicious duplicates and assigned a risk level — high (fully identical entries), medium (same trade, different price), or low (same participants, different action). Flagged entries are surfaced in a dedicated view so you can investigate them in context. Entries are never deleted outright; a **soft-delete** pattern marks them as removed while preserving the full audit trail, so nothing is irreversibly lost.

**Get AI-generated market insights without burning tokens**
An on-demand AI agent reads your data and produces a structured report covering trading patterns, concentration risk, and unusual activity. Rather than dumping the entire dataset into a prompt, the agent first calls lightweight overview tools to orient itself, then autonomously decides which tickers, traders, or time windows merit a closer look — fetching only the data it actually needs. The result is focused analysis at a fraction of the cost of a naive approach. An example is included as `example_ai_insight.pdf`.

**Manage your data from the dashboard**
Soft-delete suspicious transactions by ID directly from the UI. The overview page updates in real time to reflect only clean data, while flagged entries remain accessible for review.

### How it's built

```
CSV → Pandas (ingestion & risk flagging)
         ↓
      SQLite (indexed on ticker & timestamp)
         ↕
   FastAPI REST API  ←→   LangChain ReAct Agent
         ↕
  Shiny for Python UI
```

The FastAPI layer exposes 19 validated endpoints covering transaction queries, per-ticker and per-trader analytics, hourly VWAP/volatility statistics, and risky data management. All inputs are validated with Pydantic before touching the database. The Shiny frontend communicates with the API entirely through HTTP, keeping the UI and backend independently runnable.

## How to run this program

1. Install all required packages with `pip install --upgrade -r requirements.txt`.
    - **IMPORTANT**: Please ensure your `langchain` package is `v1.2.13`. Unfortunately `v1.2.14` might break the program. You can check your version using `pip show langchain`.
2. Set up your `.env` by doing the following:
    1. In the root directory, run `cp .env.example .env`
    2. Replace `TRANSACTION_FILE_NAME`'s value to path to your dataset (CSV only). A sample CSV with simulated data is provided.
    3. Replace `DB_PATH`'s value with the path to store your database. A default path is provided.
    4. Replace `MODEL`'s value with your chosen model. Check [LiteLLM providers](https://docs.litellm.ai/docs/providers).
        - LiteLLM supports local model deployment using [Ollama](https://docs.litellm.ai/docs/providers/ollama)!
    5. (Optional) Replace `API_KEY`'s value with your API key.
    6. (Optional) Replace `TEMPERATURE`'s value with a float between `0.0` and `2.0`.
3. Open one terminal, navigate to root directory of this project, and run `uvicorn app:app --port 8000`.
4. Open another terminal, navigate to root directory of this project, and run `shiny run ui/app.py --port 3000`.
5. Open your browser and go to `http://127.0.0.1:3000/`. You may now use the dashboard.

## Acknowledgement

This project was initially developed for a hackathon-style technical assessment. All transactions included in `sample_transactions.csv` are simulated data with generic numbers using `generate_simulated_data.py`.