# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: **K3 – B51**
- Repository URL: <https://github.com/dangkhoi3107/Day13-K3-Observability-B51>
- Commit SHA cuối: **Cập nhật sau khi merge nhánh tích hợp vào `main`**
- Thành viên và vai trò:
  - **Phạm Nguyễn Đăng Khôi - 2A202601243 — Thành viên A (API & Middleware):** Correlation ID middleware, log enrichment và exception handler.
  - **Trần Đức Bảo Trung - 2A202601269 — Thành viên B (Security Engineer):** PII scrubbing, regex và kiểm chứng log không lộ PII.
  - **Vi Minh Hiển - 2A202601743 — Thành viên C (Metrics & Dashboard):** `error_rate_pct` và dashboard sáu nhóm chỉ số.
  - **Nguyễn Đặng Đức - 2A202601787 — Thành viên D (SRE & Alerts Engineer):** SLO, alert rules và alert runbook.
  - **Đỗ Tuấn Sơn - 2A202601051 — Thành viên E (QA & Chief Investigator):** load test, trace RAG/LLM, điều tra challenge, evidence, demo và báo cáo.

## 2. Kết quả kỹ thuật

- Điểm baseline CP0 của `validate_logs.py`: **30/100**, tái lập từ commit `cd84f4f` trước CP1 ([kết quả tái lập](evidence/cp0-baseline-reproduced.txt)).
- Điểm cuối của `validate_logs.py`: **100/100**, 126 log records, 51 correlation IDs và 0 PII leak ([ảnh validator CP1](evidence/cp1-a-validator-100.png), [gate cuối](evidence/gate-validate-logs.txt)).
- Public tests: **31 passed** ([ảnh CP1](evidence/cp1-a-pytest-pass.png), [gate tích hợp cuối](evidence/gate-pytest.txt)).
- Dashboard contract: **HỢP LỆ: 6/6 panel** ([kết quả validator](evidence/gate-validate-dashboard.txt)).
- Traces đã xác minh qua Langfuse Cloud API: **12 trace có `correlation_id`** ([ảnh danh sách](evidence/cp2-langfuse-trace-list.png), [dữ liệu máy đọc](evidence/cp2-langfuse-traces.json)).
- Evidence waterfall: [ảnh waterfall incident](evidence/cp3-trace-waterfall.png), [observation timing từ Langfuse API](evidence/cp3-challenge-trace-waterfall.json).
- Dashboard runtime sáu panel: [ảnh dashboard](evidence/cp2-dashboard-6-panels.png), [HTML tái lập](evidence/cp2-dashboard-runtime.html).

## 3. Logging và tracing

- Correlation ID được nhận từ `x-request-id` hoặc sinh theo dạng `req-xxxxxxxx`, bind vào structlog và trả về response header/body.
- Evidence correlation ID: [response header/body](evidence/cp1-a-correlation-headers.png), [mapping Langfuse trace](evidence/cp1-langfuse-correlation-traces.json).
- Log có metadata `service`, `env`, `model`, `session_id`, `feature`, `user_id_hash` và `correlation_id`.
- PII được scrub đệ quy trước khi render console/file JSON. Evidence: [ảnh email/phone/card đã redact](evidence/cp1-pii-redaction.png), [JSONL đã redact](evidence/cp1-correlation-pii-redaction.jsonl).
- Parent trace `LabAgent.run` có prompt metadata và `correlation_id`; sub-component `retrieve` và `generate` được bọc child span để waterfall phân tách RAG/LLM.
- Evidence trace waterfall: [waterfall `run → retrieve/generate`](evidence/cp3-trace-waterfall.png). Ảnh được render từ observation timing đã đọc bằng Langfuse Cloud API; nhóm nên chụp thêm native Langfuse UI nếu Lab Coach yêu cầu đúng giao diện.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: **Version 1 — `baseline`, `production`**.
- Version/label candidate: **Version 2 — `candidate`**.
- Cùng input `Explain the refund window and required evidence.` đã được chạy với hai label:
  - Baseline v1: [trace `b236091e…e74be7d3`](https://cloud.langfuse.com/project/cmso2n8xc03skad0dx174qce9/traces/b236091e76679ab20f7748ace74be7d3), CID `req-ae5c996d`.
  - Candidate v2: [trace `35387c38…8705df7e`](https://cloud.langfuse.com/project/cmso2n8xc03skad0dx174qce9/traces/35387c38cb0c88072009c70a8705df7e), CID `req-b11a6a55`.
- Evidence: [ảnh prompt versions và rollback](evidence/cp2-prompt-versioning.png), [hai trace/version](evidence/cp2-prompt-version-traces.json), [promotion rồi rollback](evidence/cp2-prompt-label-rollback.json).
- `production` đã được promote sang v2 và rollback về v1; trạng thái cuối là **production → v1**.

Không ghi giả prompt version trong code. App sử dụng managed prompt khi Langfuse khả dụng và ghi `local-fallback` khi không lấy được prompt.

## 5. Dashboard, SLO và alerts

- `python scripts/validate_dashboard.py`: **HỢP LỆ: 6/6 panel**.
- Dashboard spec và contract: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md), [`config/dashboard.yaml`](../config/dashboard.yaml).
- Dashboard gồm: latency P50/P95/P99, traffic, error rate/breakdown, cost, input/output tokens và quality proxy; time range 60 phút, refresh 30 giây và threshold theo contract.
- Evidence dashboard runtime: [ảnh đủ sáu panel](evidence/cp2-dashboard-6-panels.png), được render trực tiếp từ `data/logs.jsonl` bằng [`scripts/render_dashboard.py`](../scripts/render_dashboard.py).
- SLO:
  - `latency_p95_ms` ≤ 3000ms, target 99.5%.
  - `error_rate_pct` ≤ 2%, target 99.0%.
  - `daily_cost_usd` ≤ 2.5 USD, target 100%.
  - `quality_score_avg` ≥ 0.75, target 95%.
- Alert rules và runbook: [`config/alert_rules.yaml`](../config/alert_rules.yaml), [`docs/alerts.md`](../docs/alerts.md). Ba rule hiện tại là `HighErrorRate`, `HighLatencyP95` và `DegradingQualityScore`.
- `HighLatencyP95` dùng ngưỡng **3000ms**; ngưỡng **2000ms** ở challenge chỉ là ngưỡng nhận diện incident, không phải alert hiện tại.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`.
- Incident: `rag_slow`; feature bị ảnh hưởng: `refund`; ngưỡng challenge: 2000ms.
- Triệu chứng metrics: P95 tăng từ khoảng **155ms** lên khoảng **2658ms**, trong khi `error_rate_pct = 0` và quality gần như ổn định. Evidence: [baseline](evidence/challenge-00-metrics-baseline.json), [incident](evidence/challenge-01-metrics-incident.json).
- Metrics runtime sau incident: P95 **2652ms**, vượt ngưỡng challenge 2000ms nhưng chưa vượt SLO/alert 3000ms ([ảnh dashboard incident](evidence/cp3-dashboard-incident.png)).
- Log/correlation ID liên quan: request `refund`, CID `req-c0ffee13`, latency 4329ms ([ảnh log](evidence/cp3-log-evidence.png), [JSONL cùng request](evidence/cp3-challenge-correlated-log.jsonl)).
- Trace ID incident: [`12c262a2d660163a683ea05e6b6ae083`](https://cloud.langfuse.com/project/cmso2n8xc03skad0dx174qce9/traces/12c262a2d660163a683ea05e6b6ae083), cùng CID `req-c0ffee13`.
- Root cause: waterfall cho thấy parent `run` mất 4.329s, child `retrieve` mất **2.501s**, còn `generate` chỉ mất **0.152s**. Vì incident chính thức bật `rag_slow`, bằng chứng khoanh vùng nguyên nhân tại `mock_rag.retrieve()`.
- Fix action: tắt incident; trong hệ thống thật cần timeout, retry giới hạn, cache và fallback cho vector store.
- Preventive measure: theo dõi P95 theo feature, đặt latency budget theo child span và dùng alert symptom-based.
- Recovery: sau khi tắt incident và restart API để reset metrics in-memory, clean load có P95 **960ms**, error rate 0% ([metrics recovery](evidence/cp3-metrics-recovery.json)).

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| A — Phạm Nguyễn Đăng Khôi | Middleware correlation ID, enrichment, exception handler, trace metadata và CP1 evidence | [Commit middleware](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/commit/72e3b1e6824a10b3ee829311eb0b033646426da2), [commit trace CID](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/commit/ed7725faa17801a2d5b1283963c3a33875aed167) | Nối một request qua response, structured log và trace metadata |
| B — Trần Đức Bảo Trung | PII scrubbing đệ quy, regex và regression tests | [PR #1](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/pull/1) | Chặn PII tại logging pipeline trước khi ghi |
| C — Vi Minh Hiển | `error_rate_pct`, tests và dashboard spec sáu nhóm chỉ số | [PR #2](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/pull/2) | Tính error rate an toàn và ánh xạ metrics vào dashboard |
| D — Nguyễn Đặng Đức | SLO, ba alert symptom-based và runbook | [PR #3](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/pull/3) | Liên kết SLI/SLO với alert và quy trình phản ứng sự cố |
| E — Đỗ Tuấn Sơn | Load test, challenge evidence, child trace RAG/LLM, demo và báo cáo | [Commit challenge draft](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/commit/624c8adfb39672f45795033f4d79b282140db75a) | Điều tra theo luồng Metrics → Traces → Logs |

## 8. Checklist trước khi nộp

- [x] CP1 code, tests, correlation ID, enrichment và PII redaction.
- [x] `validate_logs.py` đạt 100/100.
- [x] Dashboard contract đủ 6/6 panel.
- [x] SLO, alert rules và runbook.
- [x] Danh sách 12 traces từ Langfuse Cloud API, có correlation ID và prompt metadata.
- [x] Waterfall đầy đủ `run → retrieve/generate` từ observation timing thật.
- [x] Prompt v1/v2, hai trace theo label, promote và rollback `production`.
- [x] Ảnh dashboard runtime sáu panel.
- [x] Trace ID, waterfall, metrics và log cùng correlation ID cho challenge chính thức.
- [x] Gate cuối: 31 tests pass, log 100/100, dashboard 6/6.
- [ ] Chụp thêm native Langfuse UI nếu Coach bắt buộc evidence phải đúng giao diện thay vì snapshot từ authenticated API.
- [x] Cập nhật commit SHA cuối sau khi merge vào `main`.
