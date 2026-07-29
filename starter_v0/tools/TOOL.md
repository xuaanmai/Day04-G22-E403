---
name: source_ranker
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [sources, prefer_recent]
outputs: [ranked_sources, item_count]
side_effect: false
---

# Source Ranker

Xếp hạng danh sách nguồn nghiên cứu đã thu thập. Tool không truy cập mạng và
không xác minh nội dung; điểm số chỉ là tín hiệu hỗ trợ dựa trên domain, HTTPS,
độ mới và mức liên quan do nguồn đầu vào cung cấp.

Dùng sau `lookup`, `fetch`, `papers` hoặc khi người dùng đã đưa danh sách nguồn.
Không dùng thay cho công cụ tìm kiếm.
