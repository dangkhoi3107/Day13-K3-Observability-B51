# Đặc tả dashboard 6 nhóm chỉ số

`config/dashboard.yaml` là contract có thể kiểm tra bằng máy. Dashboard dùng
`data/logs.jsonl` làm nguồn lịch sử và bằng chứng chính; `GET /metrics` chỉ là
snapshot runtime để đối chiếu nhanh. Hướng dẫn dựng dashboard nằm tại
[DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

## Cấu hình chung

- Khoảng thời gian mặc định: 60 phút.
- Tự refresh: 30 giây.
- Mỗi panel phải hiện tên, đơn vị và đường threshold/SLO.
- Screenshot evidence phải thấy đủ sáu panel và khoảng thời gian đang chọn.

## Bố cục panel

| Nhóm / panel ID | Nguồn và trường dữ liệu | Cách hiển thị | Đơn vị | Ngưỡng |
| --- | --- | --- | --- | --- |
| Latency (`latency`) | Log `response_sent.latency_ms`; đối chiếu `/metrics`: `latency_p50`, `latency_p95`, `latency_p99` | Ba đường P50/P95/P99 theo thời gian | ms | P95 ≤ 3.000 ms |
| Traffic (`traffic`) | Đếm log `request_received`; đối chiếu `/metrics`: `traffic` (request thành công) | Cột request/phút và KPI tổng request | requests/min | ≥ 1 request/phút trong lúc load test |
| Errors (`errors`) | Log `request_failed.error_type` / tổng `request_received`; đối chiếu `/metrics`: `error_rate_pct`, `error_breakdown` | KPI error rate và bar chart theo loại lỗi | % và count | Error rate ≤ 2% |
| Cost (`cost`) | Log `response_sent.cost_usd`; đối chiếu `/metrics`: `avg_cost_usd`, `total_cost_usd` | Time series chi phí/phút, KPI trung bình và tổng | USD | Tổng ≤ 2,5 USD / cửa sổ |
| Tokens (`tokens`) | Log `response_sent.tokens_in`, `tokens_out`; đối chiếu `/metrics`: `tokens_in_total`, `tokens_out_total` | Hai series hoặc stacked bar input/output | tokens | Mỗi tổng ≤ 50.000 tokens / cửa sổ |
| Quality (`quality`) | Log `response_sent.quality_score`; đối chiếu `/metrics`: `quality_avg` | Time series và KPI điểm trung bình | score 0–1 | Trung bình ≥ 0,75 |

Error rate runtime được tính theo công thức:

```text
100 × tổng lỗi / (request thành công + tổng lỗi)
```

Khi chưa có request, `error_rate_pct` phải trả về `0.0` để tránh chia cho 0.
Chi tiết query, event, aggregation và threshold tương ứng nằm trong
`config/dashboard.yaml`.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
