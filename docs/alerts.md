# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighLatencyP95
- Severity: critical
- SLI/SLO liên quan: Latency P95 (SLO <= 3000ms)
- Điều kiện và thời gian duy trì: p95_latency_ms > 3000ms duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Phản hồi bị chậm, có thể dẫn tới timeout ở phía client.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Latency Percentiles trên Dashboard và Langfuse traces để xác định span bị chậm (RAG retrieve hay LLM generate).
  2. Kiểm tra log có `event == "response_sent"` để lọc các request có `latency_ms > 3000`.
  3. Kiểm tra xem có incident `rag_slow` hoặc quá tải upstream LLM không.
- Mitigation tạm thời: Tắt incident nếu đang test hoặc bật fallback cache/bỏ bớt context RAG.
- Owner: oncall-devops

## Alert 2

- Tên: HighErrorRate
- Severity: critical
- SLI/SLO liên quan: Error Rate (SLO <= 2%)
- Điều kiện và thời gian duy trì: error_rate_pct > 2% duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng nhận phản hồi lỗi HTTP 500 khi gọi API chat.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Error rate trên Dashboard để xem `error_type` phổ biến (ví dụ: TimeoutError, ValueError).
  2. Tra cứu log `event == "request_failed"` với `correlation_id` tương ứng để xem full stack trace.
  3. Kiểm tra kết nối tới Langfuse / LLM provider / RAG backend.
- Mitigation tạm thời: Chuyển hướng traffic sang LLM fallback model hoặc restart service API.
- Owner: oncall-devops

## Alert 3

- Tên: LowQualityScore
- Severity: warning
- SLI/SLO liên quan: Quality Score Average (SLO >= 0.75)
- Điều kiện và thời gian duy trì: quality_score_avg < 0.75 duy trì trong 10 phút
- Ảnh hưởng tới người dùng: Chất lượng câu trả lời bị suy giảm, câu trả lời không bám sát context hoặc bị redact nhầm.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel Quality Proxy trên Dashboard để xem xu hướng chất lượng.
  2. Lọc các trace trên Langfuse có `quality_score < 0.5` để đánh giá prompt version và retrieval context.
  3. Kiểm tra xem có phiên bản prompt mới (prompt candidate) vừa mới deploy gây suy giảm chất lượng không.
- Mitigation tạm thời: Rollback prompt version về phiên bản stable (production label).
- Owner: ai-team
