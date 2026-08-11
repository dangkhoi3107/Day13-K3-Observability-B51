# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1: High Error Rate

- Tên: HighErrorRate
- Severity: P1-Critical
- SLI/SLO liên quan: `error_rate_pct` (SLO Target: ≤ 2% error rate)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` kéo dài liên tục trong 2 phút.
- Ảnh hưởng tới người dùng: Người dùng nhận được phản hồi lỗi HTTP 5xx / 4xx, không thể hoàn thành truy vấn Chat/RAG.
- Ba bước kiểm tra đầu tiên:
  1. Mở Panel 3 (`errors`) trên Dashboard để xác định tổng Error Rate và phân loại loại lỗi (`error_type` breakdown).
  2. Tra cứu file log `data/logs.jsonl` lọc theo `event == "request_failed"` để lấy `correlation_id` và thông báo exception gần nhất.
  3. Mở Langfuse UI tìm các Trace ID liên quan đến `correlation_id` lỗi để xác định span bị failure (ví dụ: LLM timeout hay RAG retrieval failed).
- Mitigation tạm thời:
  1. Nếu do sự cố LLM upstream/overload: Bật fallback response hoặc giảm traffic concurrency.
  2. Nếu do lỗi code mới release: Thực hiện rollback về commit stable gần nhất.
- Owner: SRE-Team

## Alert 2: High Latency P95

- Tên: HighLatencyP95
- Severity: P2-Warning
- SLI/SLO liên quan: `latency_p95_ms` (SLO Target: P95 ≤ 3000ms)
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000ms` kéo dài liên tục trong 3 phút.
- Ảnh hưởng tới người dùng: Trải nghiệm tương tác chat bị chậm đáng kể, giao diện bị treo phản hồi.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Panel 1 (`latency`) trên Dashboard để xác định khoảng thời gian latency P95 vượt ngưỡng 3000ms.
  2. Truy cập Langfuse Dashboard, lọc các Traces có tổng duration > 3000ms.
  3. Kiểm tra Waterfall view của Trace để khoanh vùng span chạy chậm (khoảng thời gian chậm nằm ở step RAG Context Retrieval hay LLM Generation span).
- Mitigation tạm thời:
  1. Kiểm tra prompt version hiện tại; nếu prompt candidate v2 gây chậm, thực hiện rollback prompt label về version v1 stable.
  2. Tạm thời giảm số lượng retrieved documents trong RAG pipeline nếu vector database bị nghẽn.
- Owner: SRE-Team

## Alert 3: Degrading Quality Score

- Tên: DegradingQualityScore
- Severity: P3-Info
- SLI/SLO liên quan: `quality_score_avg` (SLO Target: Average Score ≥ 0.75)
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` kéo dài liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: Chất lượng câu trả lời AI sa sút, phản hồi thiếu chính xác hoặc không đáp ứng yêu cầu người dùng.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Panel 6 (`quality`) trên Dashboard để xem xu hướng tụt dốc của điểm chất lượng trung bình.
  2. Kiểm tra log `response_sent` trong `data/logs.jsonl` để xem các `quality_score` thấp gắn với `prompt_version` nào.
  3. Mở Langfuse để so sánh chất lượng output giữa các phiên bản Prompt (`production` vs `candidate`).
- Mitigation tạm thời:
  1. Thực hiện chuyển đổi hoặc rollback `prompt_label` trong file cấu hình `.env` hoặc Langfuse về lại phiên bản stable.
  2. Thông báo đội ngũ Prompt Engineering kiểm tra lại prompt template.
- Owner: AI-Ops-Team

