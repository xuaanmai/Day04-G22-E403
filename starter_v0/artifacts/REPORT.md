# Day 04 Lab v2 Report — G22 Research Agent

## Team

- Team: G22
- Members: nhóm 5 người
- Provider/model: Google Gemini / `gemini-3.5-flash`
- UI local: `http://localhost:8501`

> Trạng thái evidence: code và artifact đã hoàn thiện. Một số run chưa đạt điều
> kiện metric hợp lệ do Gemini 429/503. Không dùng các metric đó để khẳng định
> cải thiện cho đến khi `provider_error_cases=0` và `measured_cases=total_cases`.

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

G22 Research Agent tìm tin trên web, tìm bài đăng Twitter/X theo chủ đề hoặc tài
khoản, đọc URL, hỏi lại khi thiếu dữ liệu, xếp hạng nguồn và tạo digest có trace
tool minh bạch. Agent dùng Gemini để chọn tool nhưng thực thi tool bằng code thật.

## A2. Các tool

| Tool | Chức năng | Tool mới? |
|---|---|---|
| `clarify` | Hỏi thông tin thiếu hoặc xin xác nhận | Không |
| `timeline` | Lấy bài gần đây của một tài khoản | Không |
| `social_search` | Tìm bài xã hội theo chủ đề | Không |
| `lookup` | Tìm nguồn web/tin tức | Không |
| `fetch` | Đọc một URL cụ thể | Không |
| `format` | Tạo digest Markdown từ item có sẵn | Không |
| `send` | Gửi Telegram sau xác nhận | Không |
| `source_ranker` | Xếp hạng nguồn theo heuristic minh bạch | **Có** |

Các implementation optional `policy`, `papers`, `paper_text` vẫn nằm trong
registry nhưng declaration được tắt ở v2/v3 để cô lập core routing.

## A3. Câu hỏi mẫu

1. “Tin AI hôm nay có gì nổi bật?”
2. “Lấy 5 bài đăng mới nhất của Sam Altman.”
3. “Tóm tắt URL này: https://ai.google.dev/gemini-api/docs”
4. “Tìm tin AI hôm nay và thêm các bài đăng phổ biến về AI trên Twitter.”
5. “Xếp hạng các nguồn vừa tìm theo độ tin cậy.”

## A4. Kịch bản demo

| Scenario | Trace cần thấy | Câu chuyện cải thiện |
|---|---|---|
| Thiếu tài khoản | `clarify(text)` | v0 đoán tài khoản; v1+ hỏi lại |
| Tin hôm nay | `lookup(topic=news,timeframe=day)` | Prompt mới chuẩn hóa timeframe |
| Gửi Telegram | `clarify(yes_no)` trước `send` | v3 tăng ưu tiên confirmation boundary |
| Hai nguồn | `lookup` + `social_search` | Cho phép nhiều tool độc lập |
| Xếp hạng nguồn | `source_ranker` | Tool mới của nhóm, không tốn API |

# PHẦN B — Chi tiết và bằng chứng

## B1. Version evidence

| Version | Thay đổi | Hypothesis | Kết quả quan sát | Tính hợp lệ |
|---|---|---|---|---|
| v0 | Starter baseline | Declaration mơ hồ gây routing sai | 11/19 measured pass; accuracy 0.5789 | Không hợp lệ: 1 provider error |
| v1 | Viết lại prompt và mô tả/schema tool | Quy tắc cụ thể tăng routing/args | 15/16 measured pass; accuracy 0.9375 | Không hợp lệ: 4 provider errors |
| v2 | Bỏ 3 optional declarations | Giảm cạnh tranh giữa tool | Run dùng model đã ngừng phục vụ | Không hợp lệ: 20 provider errors |
| v3 | Siết confirmation yes/no | Sửa R12 wrong boundary | Chưa có full run | Cần rerun |

Metric v1 cho thấy tín hiệu tốt nhưng không được xem là kết luận chính thức vì
chưa đo đủ 20 case.

## B2. Failure analysis

| Case | Quan sát | Nguyên nhân | Fix |
|---|---|---|---|
| R03/R09/R10/M06 v1 | 429 hoặc 503 | 5 RPM và tải cao của Gemini | Key rotation, delay 13s, retry transient |
| R12 v1 | `clarify(text)` thay vì `yes_no` | Model ưu tiên hỏi nội dung hơn xác nhận action | v3 quy định confirmation có ưu tiên cao hơn |
| v2 run cũ | 404 toàn bộ | Model override không còn cho user mới | Dùng model mặc định từ provider |

## B3. Team eval

`data/eval_group.json` có đúng 10 case: 5 single-turn và 5 multi-turn.

| Case | Kiểm tra | Expected |
|---|---|---|
| G22_S01_news_month | Web news + timeframe tháng | `lookup` |
| G22_S02_missing_account | Thiếu tài khoản | `clarify(text)` |
| G22_S03_top_social | Top + limit | `social_search` |
| G22_S04_send_boundary | Xác nhận trước gửi | `clarify(yes_no)` |
| G22_S05_meta_no_tool | Câu hỏi khả năng | Không tool |
| G22_M01_carry_news_topic | Carry timeframe, đổi topic | `lookup` |
| G22_M02_url_after_clarify | URL bổ sung ở lượt sau | `fetch` |
| G22_M03_switch_social_to_timeline | Chuyển loại nguồn | `timeline` |
| G22_M04_cancel_request | Hủy yêu cầu | Không tool |
| G22_M05_confirm_send | Gửi sau xác nhận | `send(confirmed=true)` |

## B4. Tool mới

`source_ranker` là local formatter không có side effect. Smoke test đã trả một
nguồn, điểm 87.0, `error=None`. Điểm dựa trên HTTPS, domain ưu tiên, recency và
relevance; output luôn có disclaimer vì heuristic không thay thế fact-check.

## B5. UI và transcript

`app.py` tái sử dụng `run_model_tool_loop` từ `chat.py`, hiển thị:

- request và response;
- từng round, tool name, args, result/error;
- artifact version và model;
- bảng so sánh summary của các run JSON;
- transcript JSON được lưu tự động trong `transcripts/`.

Chạy bằng:

```powershell
streamlit run app.py
```

## B6. Reflection

- Routing, missing-info, carry-over và action boundary thuộc system prompt.
- Khi nào dùng/không dùng tool và convention args thuộc `tools.yaml`.
- Tool result lỗi cần review thủ công dù routing có thể PASS.
- Bước tiếp theo là chạy lại full v1–v3 và group suite với pool key đã cấu hình,
  sau đó chỉ điền metric khi không còn provider error.
