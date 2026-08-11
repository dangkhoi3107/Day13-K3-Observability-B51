# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** ([evidence](evidence/cp1-a-validator-100.png))
- Tổng số traces: **10 trace mới có correlation ID** ([mapping trace ↔ log](evidence/cp1-langfuse-correlation-traces.json))
- Số PII leak còn lại: **0**
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: [Response headers và log metadata](evidence/cp1-a-correlation-headers.jpg); [Langfuse trace metadata](evidence/cp1-langfuse-correlation-traces.json)
- Evidence PII redaction: [Ảnh log đã redact](evidence/cp1-pii-redaction.png); [Log JSONL](evidence/cp1-correlation-pii-redaction.jsonl)
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel
- Evidence dashboard: `submission/evidence/`
- SLO đã chọn và lý do:
  - `latency_p95_ms` ≤ 3000ms (Target 99.5%): Bảo đảm trải nghiệm người dùng tương tác chat mượt mà, phản hồi không quá trễ.
  - `error_rate_pct` ≤ 2% (Target 99.0%): Đảm bảo tính sẵn sàng và độ tin cậy của hệ thống AI.
  - `daily_cost_usd` ≤ $2.5 (Target 100.0%): Kiểm soát ngân sách gọi LLM API.
  - `quality_score_avg` ≥ 0.75 (Target 95.0%): Duy trì độ chính xác và chất lượng phản hồi của AI.
- Alert rules và runbook: Cấu hình 3 quy tắc cảnh báo symptom-based tại `config/alert_rules.yaml` (`HighErrorRate`, `HighLatencyP95`, `DegradingQualityScore`) và quy trình xử lý sự cố tương ứng tại `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Thành viên A (API & Middleware) | CP1: Correlation ID middleware, log enrichment, exception handler và liên kết correlation ID với Langfuse trace | [Middleware và enrichment](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/commit/72e3b1e6824a10b3ee829311eb0b033646426da2); [Trace CID và evidence](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/commit/ed7725faa17801a2d5b1283963c3a33875aed167) | Truy vết một request xuyên suốt response, structured log và trace metadata |
| Thành viên B (Security Engineer) | CP1: PII scrubbing đệ quy, mở rộng regex và kiểm chứng log không lộ PII | [PR #1](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/pull/1) | Thiết kế processor che PII trước khi log được ghi hoặc render |
| Thành viên C (Metrics & Dashboard) | CP1: Bổ sung `error_rate_pct` và regression tests | [PR #2](https://github.com/dangkhoi3107/Day13-K3-Observability-B51/pull/2) | Tính error rate từ request thành công và thất bại, bao gồm trường hợp chưa có request |
| Thành viên D (SRE & Alerts Engineer) | CP2: Thiết lập SLO (`config/slo.yaml`), định nghĩa Alert Rules (`config/alert_rules.yaml`) và soạn thảo Alert Runbook (`docs/alerts.md`) | Branch `dangduc` | Hiểu rõ cách liên kết chỉ số SLI/SLO với Symptom-based Alerts và quy trình Runbook phản ứng nhanh với sự cố AI |

