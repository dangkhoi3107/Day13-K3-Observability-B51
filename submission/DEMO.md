# Kịch bản demo — Day 13 Observability (Role 4)

Demo ~5 phút theo đúng luồng chấm: **Metrics → Traces → Logs → Root cause → Fix**.
Chuẩn bị 2 terminal đã `source .venv/bin/activate`.

## 0. Chuẩn bị (trước khi vào phòng chấm)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --env-file .env --port 8000   # Terminal 1
```

Kiểm tra sức khỏe:

```bash
curl -s http://127.0.0.1:8000/health        # -> {"ok":true,...}
```

## 1. Gate — mọi thứ chạy được (~1 phút)

```bash
python -m pytest -q                          # 29 passed
python scripts/validate_logs.py              # Estimated Score: 100/100
python scripts/validate_dashboard.py         # HỢP LỆ: 6/6 panel
```

Nói: "Gate xanh — 29 test pass, log 100/100, dashboard 6/6 panel."

## 2. Baseline metrics (~30s)

```bash
python scripts/load_test.py --concurrency 5
curl -s http://127.0.0.1:8000/metrics        # p95 ~155ms, error 0%, quality ~0.88
```

Nói: "Baseline lành mạnh: p95 ~155ms."

## 3. Kích hoạt challenge & quan sát TRIỆU CHỨNG từ Metrics (~1 phút)

```bash
python scripts/inject_incident.py                       # đọc config/challenge.json (rag_slow, refund)
python scripts/load_test.py --challenge --concurrency 5
curl -s http://127.0.0.1:8000/metrics        # p95 vọt lên ~2658ms  <-- triệu chứng
```

Nói: "Metrics báo triệu chứng: p95 155ms → 2658ms, vượt ngưỡng alert 2000ms. Error vẫn 0% → đây là vấn đề LATENCY, không phải lỗi/chất lượng."

## 4. Khoanh vùng bằng Trace (~30s)

Nói: "Toàn bộ độ trễ dồn vào span **retrieval** (`mock_rag.retrieve`) chạy trước LLM; token/cost bình thường → không phải cost spike hay tool fail. Feature bị ảnh hưởng: `refund`."

## 5. Chứng minh Root cause bằng Log (~1 phút)

```bash
grep '"feature": "refund"' data/logs.jsonl | grep response_sent
# hoặc xem sẵn: submission/evidence/challenge-02-log-evidence.jsonl
```

Nói: "5 request `refund` challenge đều latency ~2658ms, correlation_id ví dụ `req-7c9cae93`, không lộ PII (dùng `user_id_hash`). Root cause: incident `rag_slow` chèn `time.sleep(2.5)` vào retrieval."

## 6. Fix & Preventive (~30s)

```bash
python scripts/inject_incident.py --disable
curl -s http://127.0.0.1:8000/metrics        # p95 trở lại baseline
```

Nói: "Fix: gỡ độ trễ nhân tạo; trong hệ thật đặt timeout + retry giới hạn + cache cho vector store. Preventive: alert `HighLatencyP95` symptom-based, latency budget theo span, theo dõi p95 theo feature."

## Evidence tham chiếu

- `evidence/gate-pytest.txt`, `evidence/gate-validate-logs.txt`, `evidence/gate-validate-dashboard.txt`
- `evidence/challenge-00-metrics-baseline.json`, `evidence/challenge-01-metrics-incident.json`
- `evidence/challenge-02-log-evidence.jsonl`
- `evidence/cp1-a-*` (correlation header, pytest, validator 100)
