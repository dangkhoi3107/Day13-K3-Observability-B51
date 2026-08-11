# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
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
| Thành viên D (SRE & Alerts Engineer) | CP2: Thiết lập SLO (`config/slo.yaml`), định nghĩa Alert Rules (`config/alert_rules.yaml`) và soạn thảo Alert Runbook (`docs/alerts.md`) | Branch `dangduc` | Hiểu rõ cách liên kết chỉ số SLI/SLO với Symptom-based Alerts và quy trình Runbook phản ứng nhanh với sự cố AI |

