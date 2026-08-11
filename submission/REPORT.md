# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm K3 – B51 <!-- xác nhận lại tên nhóm chính thức nếu Lab Coach quy định -->
- Repository URL: https://github.com/dangkhoi3107/Day13-K3-Observability-B51
- Commit SHA cuối: `<cập nhật SHA của commit cuối sau khi push>` (gate chạy trên `26cdb24`)
- Thành viên và vai trò:
  - Phạm Nguyễn Đăng Khôi (`dangkhoi3107`) — Role 1A: Correlation ID & log enrichment; Role 3: `error_rate_pct` + metrics
  - Trần Trung (`Shrood`) — Role 1B: PII scrubbing global (`logging_config.py`, `pii.py`)
  - Vi Minh Hiển (`hien`) — Role 1A/1B: middleware correlation ID, structlog scrub pipeline, PII regex; hỗ trợ alert rules
  - Đặng Đức (`mondaydd`) — SRE: SLO, alert rules, runbook (CP2)
  - Sơn (`sondo1307`) — Role 4: Gate tích hợp, report, evidence & demo

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (41 log records, 0 field thiếu, 0 PII leak) — xem [`evidence/gate-validate-logs.txt`](evidence/gate-validate-logs.txt)
- Tổng số traces: **20 correlation ID** trên `data/logs.jsonl` (baseline + challenge). Trace Langfuse (waterfall UI, ≥10 traces có metadata) yêu cầu cấu hình `LANGFUSE_*` — thuộc phần Role 2, chạy khi có key project chung/cloud.
- Số PII leak còn lại: **0** (validator + grep thủ công trên evidence đều không phát hiện email/phone/card nguyên văn)
- Link/đường dẫn dashboard: nguồn chuẩn là `data/logs.jsonl` theo [`config/dashboard.yaml`](../config/dashboard.yaml); contract validator báo **6/6 panel** — xem [`evidence/gate-validate-dashboard.txt`](evidence/gate-validate-dashboard.txt)

Gate tích hợp (chạy lại toàn bộ trước khi nộp):

| Kiểm tra | Lệnh | Kết quả |
|---|---|---|
| Unit/public tests | `python -m pytest -q` | **29 passed** ([`evidence/gate-pytest.txt`](evidence/gate-pytest.txt)) |
| Log quality | `python scripts/validate_logs.py` | **100/100** |
| Dashboard contract | `python scripts/validate_dashboard.py` | **HỢP LỆ: 6/6 panel** |
| Health check | `GET /health` | `ok: true` |

## 3. Logging và tracing

- Evidence correlation ID: mỗi request có `correlation_id` (định dạng `req-xxxxxxxx`) truyền xuyên suốt từ middleware → log; response trả header correlation ID. Xem [`evidence/cp1-a-correlation-headers.jpg`](evidence/cp1-a-correlation-headers.jpg) và các dòng log trong [`evidence/challenge-02-log-evidence.jsonl`](evidence/challenge-02-log-evidence.jsonl).
- Evidence PII redaction: log dùng `user_id_hash` thay cho user_id thật; email/SĐT/số thẻ được scrub trước khi ghi (structlog `scrub_event` processor + regex trong `app/pii.py`). Validator báo `Potential PII leaks detected: 0`.
- Evidence trace waterfall: **Pending** — cần `LANGFUSE_*` key để sinh trace waterfall trên Langfuse (Role 2). Trong lần gate này `tracing_enabled=false` nên chưa có ảnh waterfall; log đã có đầy đủ span-level latency để đối chiếu.
- Giải thích một span đáng chú ý: span **retrieval** (`app/mock_rag.retrieve`) là bước gọi vector store trước LLM. Đây chính là span phình to trong incident (xem mục 6): bình thường ~155ms, khi `rag_slow` bật thì thêm `sleep(2.5s)` → toàn request lên ~2.66s.

## 4. Prompt versioning

- Prompt name: `day13-chat` (mặc định từ `LANGFUSE_PROMPT_NAME`)
- Version/label baseline: `production` (label) — khi không có key, app dùng `local-v1`, `source=local-fallback`
- Version/label candidate: **Pending** — tạo prompt v2 + label `staging`/`candidate` trên Langfuse (Role 2)
- Trace ID của mỗi version: **Pending** — sinh sau khi cấu hình Langfuse; app đã ghi sẵn `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source` vào metadata trace/generation (`app/agent.py`).
- Bằng chứng đổi label hoặc rollback: **Pending** — thao tác đổi label/rollback trên Langfuse UI theo [`docs/PROMPT_VERSIONING.md`](../docs/PROMPT_VERSIONING.md).

> Ghi chú gate: code đã sẵn sàng cho prompt versioning (metadata được emit đúng); phần còn thiếu chỉ là key Langfuse để lấy evidence UT. Đây là hạng mục duy nhất chưa đủ evidence tại thời điểm gate.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel** (latency, traffic, errors, cost, tokens, quality)
- Evidence dashboard: contract tại [`config/dashboard.yaml`](../config/dashboard.yaml), nguồn `data/logs.jsonl`; ảnh dashboard runtime từ log là hạng mục Role 3.
- SLO đã chọn và lý do (theo [`config/slo.yaml`](../config/slo.yaml)):
  - `latency_p95_ms` ≤ 3000ms (Target 99.5%): Bảo đảm trải nghiệm chat mượt, phản hồi không quá trễ.
  - `error_rate_pct` ≤ 2% (Target 99.0%): Đảm bảo tính sẵn sàng và độ tin cậy của hệ thống AI.
  - `daily_cost_usd` ≤ $2.5 (Target 100.0%): Kiểm soát ngân sách gọi LLM API.
  - `quality_score_avg` ≥ 0.75 (Target 95.0%): Duy trì độ chính xác và chất lượng phản hồi.
- Alert rules và runbook: 3 quy tắc symptom-based tại [`config/alert_rules.yaml`](../config/alert_rules.yaml) (`HighErrorRate`, `HighLatencyP95`, `DegradingQualityScore`) và runbook tương ứng tại [`docs/alerts.md`](../docs/alerts.md).

## 6. Điều tra challenge

Challenge `config/challenge.json` đã được release. Điều tra theo luồng **Metrics → Traces → Logs → Root cause**.

- Challenge ID: `day13-k3-observability-v1` (cohort K3, incident `rag_slow`, feature bị ảnh hưởng `refund`, `seed=1303`)
- Triệu chứng từ metrics: `latency_p95` tăng vọt **155ms → 2658ms** (p99 155ms → 2660ms), vượt ngưỡng cảnh báo challenge 2000ms (dưới ngưỡng SLO 3000ms nên alert symptom kích hoạt sớm trước khi SLO vỡ). `error_rate_pct` vẫn 0%, `quality_avg` ~0.88 → loại trừ lỗi/chất lượng, khoanh vùng đây là vấn đề **latency**.
  - Before: [`evidence/challenge-00-metrics-baseline.json`](evidence/challenge-00-metrics-baseline.json)
  - After: [`evidence/challenge-01-metrics-incident.json`](evidence/challenge-01-metrics-incident.json)
- Trace ID liên quan: span **retrieval** (`app/mock_rag.retrieve`) trong generation trace của feature `refund` là span bất thường. Latency dồn hết vào bước retrieve (trước LLM), LLM/token bình thường (tokens_out ~129, cost ~$0.002) → không phải cost spike hay tool fail.
- Log line/correlation ID liên quan: 5 request challenge feature `refund` đều `latency_ms ≈ 2653–2660`, không có PII. Ví dụ `correlation_id=req-7c9cae93`, `session_id=k3-challenge-s02`, `feature=refund`, `latency_ms=2658`. Toàn bộ 5 dòng: [`evidence/challenge-02-log-evidence.jsonl`](evidence/challenge-02-log-evidence.jsonl).
- Root cause: incident `rag_slow` chèn `time.sleep(2.5)` vào bước truy hồi tài liệu `mock_rag.retrieve()` (mô phỏng vector store chậm/timeout). Toàn bộ độ trễ tăng thêm nằm ở span retrieval, không phải ở LLM.
- Fix action: gỡ/không kích hoạt độ trễ nhân tạo trong retrieval (`python scripts/inject_incident.py --disable`); trong hệ thật: đặt **timeout + retry có giới hạn** cho vector store, thêm **cache** kết quả retrieval, và fallback trả lời khi retrieval chậm.
- Preventive measure: giữ alert `HighLatencyP95` (symptom-based, ngưỡng 2000ms) để phát hiện sớm; đặt **latency budget theo span** (retrieval, LLM) để khoanh vùng nhanh; theo dõi p95 theo `feature` trên dashboard để cô lập tính năng bị ảnh hưởng (`refund`) ngay khi p95 lệch baseline.

## 7. Đóng góp cá nhân

Bảng dưới đối chiếu trực tiếp với lịch sử Git (`git log --all --author=...`).

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Phạm Nguyễn Đăng Khôi (`dangkhoi3107`) | Role 1A + Role 3: propagate correlation ID & enrich request logs (`app/main.py`, `app/middleware.py`, `scripts/load_test.py`); error rate + metrics (`app/metrics.py`, `tests/test_metrics.py`); harden PII scrubbing | `72e3b1e`, `89a5a29`, `65329d2`, `354399e`; merge PR #1/#2/#3 | Liên kết correlation ID xuyên request và cách tính error rate / percentile cho metrics |
| Trần Trung (`Shrood`) | Role 1B: global PII scrubbing (`app/logging_config.py`, `app/pii.py`) | `092701f` (PR #1 `TranTrung`) | Cách chặn PII ở tầng logging pipeline trước khi ghi |
| Vi Minh Hiển (`hien`) | Role 1A/1B: correlation ID middleware + response header, structlog `scrub_event`, regex PII (passport/địa chỉ VN); alert rules | `8ff3b9d`, `87ba430`, `b36aecb`, `f1059b1`, `68f1ad0`, `c40f283` (PR #2 `hien`) | Pipeline structlog và cách viết regex PII an toàn |
| Đặng Đức (`mondaydd`) | SRE/CP2: SLO (`config/slo.yaml`), alert rules (`config/alert_rules.yaml`), runbook (`docs/alerts.md`) | `4f3614d` (PR #3 `dangduc`) | Liên kết SLI/SLO với symptom-based alert và quy trình runbook |
| Sơn (`sondo1307`) | Role 4: Gate tích hợp (pytest/validators/health), điều tra challenge (Metrics→Traces→Logs), evidence & report, kịch bản demo | Branch `son` — commit report + evidence challenge (`challenge-00/01/02`, `gate-*`), `submission/DEMO.md` | Nối chuỗi Metrics → Traces → Logs để chứng minh root cause bằng bằng chứng cụ thể |

## 8. Hạng mục còn thiếu (bàn giao)

- **Prompt versioning evidence (Role 2):** cần cấu hình `LANGFUSE_*`, tạo prompt v1/v2, chụp 2 trace gắn version/label và 1 lần rollback.
- **Trace waterfall + ≥10 traces trên Langfuse UI (Role 2):** sinh sau khi có key.
- **Ảnh dashboard runtime 6 panel (Role 3):** render từ `data/logs.jsonl` (contract đã pass validator).

Mọi hạng mục khác (logging, PII, metrics, error rate, SLO, alert, runbook, điều tra challenge) đã có evidence đầy đủ và pass gate.
