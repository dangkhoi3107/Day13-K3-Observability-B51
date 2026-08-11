# Evidence index

| File | Mốc | Nội dung |
|---|---|---|
| `gate-pytest.txt` | Gate | Kết quả `python -m pytest -q` — 29 passed |
| `gate-validate-logs.txt` | CP1 | Kết quả `validate_logs.py` — 100/100, 0 PII leak |
| `gate-validate-dashboard.txt` | CP2 | Kết quả `validate_dashboard.py` — 6/6 panel |
| `cp1-a-correlation-headers.jpg` | CP1 | Response header mang correlation ID |
| `cp1-a-pytest-pass.jpg` | CP1 | Ảnh pytest pass |
| `cp1-a-validator-100.png` | CP1 | Ảnh validator 100/100 |
| `challenge-00-metrics-baseline.json` | CP3 | Metrics trước incident (p95 ~155ms) |
| `challenge-01-metrics-incident.json` | CP3 | Metrics khi incident (p95 ~2658ms) — triệu chứng |
| `challenge-02-log-evidence.jsonl` | CP3 | 5 log line `refund` challenge, latency ~2658ms, đã redact PII |

Pending (cần Langfuse key — Role 2/3): 2 trace prompt version, trace waterfall, ảnh dashboard runtime.
Xem chi tiết điều tra trong [`../REPORT.md`](../REPORT.md) mục 6 và kịch bản demo trong [`../DEMO.md`](../DEMO.md).
