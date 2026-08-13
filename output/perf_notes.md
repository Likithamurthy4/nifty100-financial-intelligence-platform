New-Item -ItemType Directory -Force .\output | Out-Null
@"
# Day 43 — Performance Notes

## Screener API Load Test

- Concurrent requests: 10
- Successful requests: 10/10
- HTTP status: 200 for all requests
- Total execution time: 0.436 seconds
- Target: under 10 seconds
- Result: PASS

## Company Profile Performance

| Ticker | Load Time |
|---|---:|
| TCS | 0.0551 seconds |
| RELIANCE | 0.0201 seconds |
| HDFCBANK | 0.0210 seconds |
| INFY | 0.0184 seconds |
| ICICIBANK | 0.0190 seconds |

- Target: under 3 seconds per company
- Result: PASS
- Slowest: TCS at 0.0551 seconds

## End-to-End Integration

- FastAPI port: 8000
- Streamlit port: 8501
- Both services started simultaneously
- FastAPI health endpoint: HTTP 200
- Streamlit: HTTP 200
- Result: PASS

## Performance Bottlenecks

No significant performance bottlenecks were observed during testing.

The API and dashboard database queries completed well within the required thresholds.

## SQLite Optimisation

No additional indexes were required based on the measured performance.
"@ | Set-Content .\output\perf_notes.md