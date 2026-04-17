# API Tests

## GET /db/tickers
```bash
curl http://localhost:8000/db/tickers
```

## GET /db/traders
```bash
curl http://localhost:8000/db/traders
```

## GET /db/transactions/stats
```bash
curl "http://localhost:8000/db/transactions/stats?include_risky=false"
```

## POST /db/transactions/lookup
```bash
curl -X POST http://localhost:8000/db/transactions/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "year_start": 2024, "year_end": 2024,
    "month_start": 1, "month_end": 1,
    "day_start": 15, "day_end": 15,
    "hour_start": 19, "hour_end": 19,
    "minute_start": 1, "minute_end": 10,
    "second_start": 1, "second_end": 1,
    "include_buy": true, "include_sell": true,
    "include_risky": false, "reverse_timestamp": false
  }'
```

## POST /db/traded/per-ticker
```bash
curl -X POST http://localhost:8000/db/traded/per-ticker \
  -H "Content-Type: application/json" \
  -d '{"use_volume": true, "action": "absolute", "include_risky": false}'
```

## POST /db/net-position/per-ticker
```bash
curl -X POST http://localhost:8000/db/net-position/per-ticker \
  -H "Content-Type: application/json" \
  -d '{"use_volume": true, "include_risky": false}'
```

## POST /db/transactions/per-trader
```bash
curl -X POST http://localhost:8000/db/transactions/per-trader \
  -H "Content-Type: application/json" \
  -d '{"action": "absolute", "include_risky": false}'
```

## POST /db/hourly-data
```bash
curl -X POST http://localhost:8000/db/hourly-data \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "is_buy": true, "include_risky": false}'
```

## POST /db/hourly-stats
```bash
curl -X POST http://localhost:8000/db/hourly-stats \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "is_buy": true, "include_risky": false}'
```

## POST /db/risky/lookup
```bash
curl -X POST http://localhost:8000/db/risky/lookup \
  -H "Content-Type: application/json" \
  -d '{"risk_level": "low"}'
```

## GET /db/risky/counts
```bash
curl http://localhost:8000/db/risky/counts
```

## GET /db/risky/by-hour
```bash
curl http://localhost:8000/db/risky/by-hour
```

## GET /db/risky/by-trader
```bash
curl http://localhost:8000/db/risky/by-trader
```

## POST /db/risky/soft-delete-by-id

**Modify the UUID every time after server restart!**
```bash
curl -X POST http://localhost:8000/db/risky/soft-delete-by-id \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "3da8f1fb-209c-4468-952f-e323b9f9f1e8"}'
```


## GET /db/ranking/ticker
```bash
curl "http://localhost:8000/db/ranking/ticker?include_risky=false"
```

## GET /db/ranking/trader
```bash
curl "http://localhost:8000/db/ranking/trader?include_risky=false"
```

## GET /ai/insights
```bash
curl http://localhost:8000/ai/insights
```
