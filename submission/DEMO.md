# Kịch bản demo — Day 13 Observability (Thành viên E)

Demo khoảng 5 phút theo đúng luồng chấm: **Metrics → Traces → Logs → Root cause → Fix**.

Phân vai liên quan: A — API & Middleware; B — Security/PII; C — Metrics & Dashboard; D — SLO & Alerts; E — QA, Tracing và điều tra challenge. Thành viên E dẫn dắt phần demo này, nhưng sử dụng kết quả đã tích hợp của cả nhóm.

## 0. Chuẩn bị trước khi demo

### Windows Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env       # chỉ chạy nếu chưa có .env
uvicorn app.main:app --env-file .env --port 8000
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env   # chỉ chạy nếu chưa có .env
uvicorn app.main:app --env-file .env --port 8000
```

Giữ server ở Terminal 1. Trong Terminal 2, activate cùng môi trường rồi kiểm tra:

```bash
curl http://127.0.0.1:8000/health
```

Trong PowerShell có thể dùng `curl.exe` thay cho `curl`.

## 1. Gate kỹ thuật (~1 phút)

```bash
python -m pytest -q
python scripts/validate_logs.py
python scripts/validate_dashboard.py
```

Kết quả gate tích hợp cuối: **31 tests passed**, log **100/100 và 0 PII leak**, dashboard contract **6/6 panel**. Khi demo, đọc kết quả vừa chạy; không khẳng định số liệu cũ nếu lần chạy mới khác.

## 2. Baseline metrics (~30 giây)

Đảm bảo incident đang tắt và server vừa được khởi động để metrics in-memory bắt đầu từ trạng thái sạch, sau đó chạy:

```bash
python scripts/inject_incident.py --disable
python scripts/load_test.py --concurrency 5
curl http://127.0.0.1:8000/metrics
```

Evidence hiện có ghi nhận baseline: traffic 20, p95 khoảng **155 ms**, error rate **0%**, quality trung bình **0.88**.

## 3. Kích hoạt challenge và phát hiện triệu chứng từ Metrics (~1 phút)

```bash
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
curl http://127.0.0.1:8000/metrics
```

Evidence hiện có ghi nhận p95 tăng từ khoảng **155 ms** lên **2658 ms**, trong khi error rate vẫn **0%**. Đây là sự cố latency, không phải lỗi request.

Lưu ý khi trình bày ngưỡng:

- **2000 ms** là ngưỡng dùng để nhận diện/chấm challenge này.
- Alert `HighLatencyP95` hiện được cấu hình tại `config/alert_rules.yaml` là **`latency_p95_ms > 3000ms for 3m`**.
- Vì vậy không nói rằng giá trị 2658 ms đã kích hoạt alert 3000 ms; chỉ nói nó đã vượt ngưỡng challenge 2000 ms. Nếu nhóm muốn alert thực sự fire ở kịch bản này, Thành viên D phải chủ động đổi rule và cập nhật runbook/báo cáo cho nhất quán.

## 4. Khoanh vùng bằng Trace (~30 giây)

Mở Langfuse hoặc evidence đã xác minh, chọn trace `12c262a2d660163a683ea05e6b6ae083` bằng `correlation_id=req-c0ffee13`. Waterfall cho thấy parent `run` mất 4.329 giây, child `retrieve` mất **2.501 giây**, còn `generate` chỉ mất **0.152 giây**. Đây là bằng chứng khoanh vùng nút thắt tại RAG retrieval.

Evidence: `submission/evidence/cp3-trace-waterfall.png` và `cp3-challenge-trace-waterfall.json`. Ảnh PNG được render từ observation timing đọc bằng authenticated Langfuse Cloud API; nếu Coach yêu cầu đúng native UI, mở trace ID trên và chụp thêm trực tiếp trong Langfuse.

## 5. Chứng minh root cause bằng Logs (~1 phút)

Windows Git Bash:

```bash
grep '"feature": "refund"' data/logs.jsonl | grep response_sent
```

Windows PowerShell:

```powershell
Get-Content data/logs.jsonl | Select-String '"feature": "refund"' | Select-String 'response_sent'
```

Hoặc đối chiếu `submission/evidence/cp3-challenge-correlated-log.jsonl`. Hai dòng request/response dùng cùng `correlation_id=req-c0ffee13`, khớp trace ID ở bước 4; response log ghi latency 4329ms. Log chỉ dùng `user_id_hash` và không lộ PII.

## 6. Khắc phục và xác minh phục hồi (~45 giây)

Tắt incident trước:

```bash
python scripts/inject_incident.py --disable
```

Endpoint `/metrics` dùng metrics tích lũy trong bộ nhớ, nên tắt incident **không tự xóa** các request chậm đã ghi nhận. Dừng server bằng `Ctrl+C`, khởi động lại ở Terminal 1 để reset metrics in-memory:

```bash
uvicorn app.main:app --env-file .env --port 8000
```

Sau đó chạy lại từ Terminal 2:

```bash
python scripts/load_test.py --concurrency 5
curl http://127.0.0.1:8000/metrics
```

Chỉ tuyên bố đã phục hồi khi lần đo sạch cho thấy latency trở về gần baseline. Hướng xử lý phòng ngừa: timeout, retry có giới hạn, cache cho vector store và theo dõi latency theo feature/span.

## Evidence tham chiếu

- Gate: `evidence/gate-pytest.txt`, `evidence/gate-validate-logs.txt`, `evidence/gate-validate-dashboard.txt`.
- CP1: `evidence/cp1-a-correlation-headers.png`, `evidence/cp1-a-pytest-pass.png`, `evidence/cp1-a-validator-100.png`, `evidence/cp1-pii-redaction.png`.
- CP2: `evidence/cp2-dashboard-6-panels.png`, `evidence/cp2-langfuse-trace-list.png`, `evidence/cp2-prompt-versioning.png` và các file JSON đối chiếu.
- CP3: `evidence/cp3-dashboard-incident.png`, `evidence/cp3-trace-waterfall.png`, `evidence/cp3-log-evidence.png`, `evidence/cp3-challenge-correlated-log.jsonl` và `evidence/cp3-metrics-recovery.json`.
- Khuyến nghị cuối: chụp thêm native Langfuse UI cho danh sách trace/waterfall nếu Lab Coach áp dụng đúng yêu cầu ảnh giao diện.
