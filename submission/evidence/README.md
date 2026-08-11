# Evidence index

Các file dưới đây được tạo từ lần chạy thật trong repository và dữ liệu đọc qua authenticated Langfuse Cloud API. Không file nào chứa API key, prompt input/output đầy đủ hoặc PII thô.

| File | Mốc | Nội dung |
|---|---|---|
| `cp0-baseline-reproduced.txt` | CP0 | Baseline tái lập từ commit `cd84f4f`: 30/100 |
| `gate-pytest.txt` | Gate | Kết quả cuối: 31 tests passed |
| `gate-validate-logs.txt` | CP1 | 126 records, 51 correlation IDs, 0 PII leak, 100/100 |
| `gate-validate-dashboard.txt` | CP2 | Dashboard contract 6/6 panel |
| `cp1-a-correlation-headers.png` | CP1 / A | Response header/body dùng cùng correlation ID |
| `cp1-a-pytest-pass.png` | CP1 / A | Ảnh public tests tại CP1 |
| `cp1-a-validator-100.png` | CP1 / A–B | Ảnh validator đạt 100/100 |
| `cp1-pii-redaction.png` | CP1 / B | Ảnh email/phone/card đã redact |
| `cp1-correlation-pii-redaction.jsonl` | CP1 / A–B | Log JSON có CID, metadata và redaction |
| `cp1-langfuse-correlation-traces.json` | CP1 / A–E | Mapping 10 trace ban đầu với correlation ID |
| `cp2-dashboard-6-panels.png` | CP2 / C | Dashboard runtime đủ 6 panel, 60 phút, đơn vị và threshold |
| `cp2-dashboard-runtime.html` | CP2 / C | Dashboard HTML có thể tái lập từ `data/logs.jsonl` |
| `cp2-langfuse-trace-list.png` | CP2 / E | Snapshot 12 traces đọc từ Langfuse Cloud API |
| `cp2-langfuse-traces.json` | CP2 / E | Dữ liệu máy đọc của 12 traces và observations |
| `cp2-prompt-versioning.png` | CP2 / E | Prompt v1/v2, hai trace, promote và rollback |
| `cp2-prompt-version-traces.json` | CP2 / E | Trace baseline v1 và candidate v2 với cùng input |
| `cp2-prompt-label-rollback.json` | CP2 / E | Production promote v2 rồi rollback về v1 |
| `challenge-00-metrics-baseline.json` | CP3 / E | Metrics baseline lịch sử: P95 khoảng 155ms |
| `challenge-01-metrics-incident.json` | CP3 / E | Metrics incident lịch sử: P95 khoảng 2658ms |
| `challenge-02-log-evidence.jsonl` | CP3 / E | Năm log `refund` từ lần challenge ban đầu |
| `cp3-dashboard-incident.png` | CP3 / C–E | Dashboard incident, P95 2652ms vượt ngưỡng challenge 2000ms |
| `cp3-challenge-trace-waterfall.json` | CP3 / E | Trace `12c262…`, retrieve 2.501s, generate 0.152s |
| `cp3-trace-waterfall.png` | CP3 / E | Waterfall render từ observation timing thật |
| `cp3-challenge-correlated-log.jsonl` | CP3 / E | Log có cùng CID `req-c0ffee13` với trace incident |
| `cp3-log-evidence.png` | CP3 / E | Ảnh log thô và mapping CID ↔ trace ID |
| `cp3-metrics-recovery.json` | CP3 / E | Recovery sau disable + restart: P95 960ms, error 0% |

## Trạng thái

- [x] CP1 correlation ID, enrichment, PII redaction và validator.
- [x] Tối thiểu 10 traces có metadata.
- [x] Child spans `retrieve` và `generate`.
- [x] Prompt v1/v2, labels, hai trace và rollback.
- [x] Dashboard runtime đủ sáu nhóm chỉ số.
- [x] Challenge Metrics → Trace → Logs → Root cause → Recovery.
- [ ] Nếu rubric yêu cầu đúng ảnh native Langfuse UI, chụp thêm danh sách traces, prompt versions và waterfall trực tiếp trong UI. Các PNG hiện tại là snapshot render từ dữ liệu API thật, không giả lập số liệu.
- [ ] Cập nhật commit SHA cuối trong `submission/REPORT.md` sau khi merge.

Xem [báo cáo](../REPORT.md) và [kịch bản demo](../DEMO.md).
