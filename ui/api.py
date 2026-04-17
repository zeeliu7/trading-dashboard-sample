import requests

BASE_URL = "http://localhost:8000"


def get_transaction_stats(include_risky=True):
    return requests.get(f"{BASE_URL}/db/transactions/stats", params={"include_risky": include_risky}).json()

def get_tickers():
    return requests.get(f"{BASE_URL}/db/tickers").json()

def get_trader_ids():
    return requests.get(f"{BASE_URL}/db/traders").json()

def lookup_transactions(payload):
    return requests.post(f"{BASE_URL}/db/transactions/lookup", json=payload).json()

def get_risky_counts():
    return requests.get(f"{BASE_URL}/db/risky/counts").json()

def get_risky_by_hour():
    return requests.get(f"{BASE_URL}/db/risky/by-hour").json()

def get_risky_by_trader():
    return requests.get(f"{BASE_URL}/db/risky/by-trader").json()

def get_risky_lookup(risk_level):
    return requests.post(f"{BASE_URL}/db/risky/lookup", json={"risk_level": risk_level}).json()

def soft_delete_by_id(transaction_id):
    return requests.post(f"{BASE_URL}/db/risky/soft-delete-by-id", json={"transaction_id": transaction_id}).json()


def get_ticker_ranking(include_risky=False):
    return requests.get(f"{BASE_URL}/db/ranking/ticker", params={"include_risky": include_risky}).json()

def get_trader_id_ranking(include_risky=False):
    return requests.get(f"{BASE_URL}/db/ranking/trader", params={"include_risky": include_risky}).json()

def get_ai_insights():
    return requests.get(f"{BASE_URL}/ai/insights").json()
