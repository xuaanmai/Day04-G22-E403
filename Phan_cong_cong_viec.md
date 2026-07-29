# 📋 SỔ TAY PHÂN CÔNG & CHECKLIST — DAY 04 LAB V2 (RESEARCH AGENT TOOL EVAL)

> 💡 **Hướng dẫn**: Mỗi thành viên mở đúng file được phân công trong `starter_v0/` và thực hiện checklist theo từng Mốc. Vòng lặp bắt buộc: **sửa 1 hypothesis → chạy 1 version → soi evidence → ghi log → mới đi tiếp.**

---

## 👥 1. BẢNG PHÂN VAI & FILE ĐẢM NHẬN

| Vai trò (Role) | File/Khu vực đảm nhận | Nhiệm vụ chính | Người đảm nhận |
|:---|:---|:---|:---|
| **Role 1: Prompt & Routing Lead** | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv` | Setup provider, chạy baseline v0, đọc `observed_mismatch`/`failures`, đặt hypothesis và sửa prompt/tool declaration qua v1→v2→v3 | ___________ |
| **Role 2: Tool Engineer** | `tools/<tool_name>/` (TOOL.md + tool.py), `tools/__init__.py` | Viết tool mới (≥1, cố >3 nếu muốn bonus), đăng ký tool, đảm bảo tool trả lỗi có kiểm soát (không crash), smoke-test trực tiếp | ___________ |
| **Role 3: Eval Designer** | `data/eval_group.json` | Thiết kế đúng 10 case (5 single-turn `query` + 5 multi-turn `turns`), phủ đủ 6 `failure_type`, điền `metadata.what_it_tests` | ___________ |
| **Role 4: Core Developer / Integrator (UI)** | `app.py`, deploy | **Đầu mối kéo code cả nhóm (`git pull`)**, dựng UI (khuyến nghị Streamlit) tái dùng `run_model_tool_loop` trong `chat.py`, hiển thị trace/version, setup Cloudflare Tunnel | ___________ |
| **Role 5: Observability & Report** | `chat.py` transcripts, `artifacts/REPORT.md` | Chạy live chat 3 turn bắt buộc, soi run JSON/transcript, viết Report Phần A (trước 11:30) và Phần B (sau debate) | ___________ |

> 🌟 **VAI TRÒ NÒNG CỐT CỦA ROLE 4**: Sau khi Role 1, 2, 3 đẩy file lên Git, **Role 4 gõ `git pull`** gom toàn bộ artifact/tool/eval về máy, rồi lắp UI gọi đúng `run_model_tool_loop` trong `chat.py` — **không viết agent loop riêng**, chỉ tái sử dụng.

---

## ⏱️ 2. CHECKLIST THEO CHECKPOINT (K3 buổi sáng 09:00–13:00)

### 📍 CHECKPOINT 0: Kickoff (09:00–09:15)

- [ ] **Cả nhóm**: Mở `starter_v0/`, đọc lướt `README.md` và `TOOL-SETUP.md`, chốt vai trò theo bảng trên.
- [ ] **Role 4**: Clone/pull repo, đảm bảo mọi người đều có `starter_v0/` local.
- [ ] 🔄 **Đồng bộ Git**: `git add .` ➔ `git commit -m "Checkpoint 0: chia vai"` ➔ `git push`.

---

### 📍 CHECKPOINT 1: Setup (09:15–09:40)

- [ ] **Cả nhóm**: Tạo venv, `pip install -r requirements.txt`, copy `.env.example` → `.env`, điền API key provider (theo `TOOL-SETUP.md`).
- [ ] **Role 1**: Chạy `python scripts/preflight_provider.py --provider openrouter` xác nhận provider sống.
- [ ] **Role 2**: Đọc trước `TOOL.md` của các tool có sẵn (`clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`) để chuẩn bị viết tool mới.
- [ ] **Role 3**: Đọc `starter_v0/samples/eval_group.schema.example.json` để nắm đúng schema (2 case mẫu, không tính vào 10 case).
- [ ] **Role 4**: Kiểm tra Streamlit hoặc framework UI đã chọn chạy được (`streamlit --version`).
- [ ] ⚠️ **Lưu ý**: Không để lộ `.env`, không commit API key.
- [ ] 🔄 **Đồng bộ Git**: `git commit -m "Checkpoint 1: setup xong"` ➔ `git push`.

---

### 📍 CHECKPOINT 2: Baseline v0 (09:40–10:15)

- [ ] **Role 1**: Chạy fixed base eval làm `v0`:
  ```bash
  python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
  ```
  Đọc `summary.case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`, `provider_error_cases`, `measured_cases`. Xác nhận `provider_error_cases = 0` và `measured_cases = total_cases`.
- [ ] **Role 1 & Role 5**: Cùng đọc 1 case fail trong run JSON (`observed_mismatch`, `failures`, `actual_tool_calls`, `tool_results`) để thống nhất hypothesis đầu tiên cho v1.
- [ ] **Role 4**: Dựng UI local, hiển thị được request/response + trace tool (tên, args, round/status, result/error) + `artifact_version`.
- [ ] **Role 2**: Bắt đầu code tool mới song song (không phụ thuộc kết quả v0).
- [ ] **Role 3**: Bắt đầu phác thảo 10 eval case (chưa cần hoàn thiện).
- [ ] 🔄 **Đồng bộ Git**: `git commit -m "Checkpoint 2: baseline v0"` ➔ `git push`.

---

### 📍 CHECKPOINT 3: v1 + Tool mới (10:15–10:50)

- [ ] **Role 1**: Đặt đúng **một hypothesis** (VD: mô tả tool chưa nói rõ "khi nào dùng"), sửa **đúng một thứ** trong `system_prompt.md` hoặc `tools.yaml`, rồi chạy:
  ```bash
  python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
  ```
- [ ] **Role 2**: Hoàn thiện tool mới — `TOOL.md`, `tool.py`, đăng ký trong `tools/__init__.py`, thêm declaration vào `tools.yaml`, smoke-test trực tiếp.
- [ ] **Role 4**: `git pull` kéo prompt/tool mới, cập nhật UI để hiển thị đúng version/tool mới trong trace.
- [ ] **Role 1**: So metric v0 → v1, ghi vào `artifacts/version_log.csv` (đủ cột: `version, author, changed_artifact, artifact_version, prompt_hash, tools_hash, reason, hypothesis, metric_name, metric_before, metric_after, run_file`).
- [ ] ⚠️ **Nếu đổi tên tool**: phải sync đủ 8 file (system_prompt, tools.yaml, TOOL.md, `tools/__init__.py`, eval_base.json, eval_research_extension.json, eval_group.json nếu có nhắc, REPORT.md).
- [ ] 🔄 **Đồng bộ Git**: `git commit -m "Checkpoint 3: v1 + tool moi"` ➔ `git push`.

---

### 📍 Nghỉ (10:50–11:05)

---

### 📍 CHECKPOINT 4: Eval + v2 (11:05–11:30)

- [ ] **Role 3**: Hoàn thiện đúng **10 case** trong `data/eval_group.json` (5 single-turn + 5 multi-turn), mỗi case có `id`, `phase: "B"`, `failure_type` (một trong `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`), `expect` (`tool_calls` hoặc `no_tool`), `metadata.what_it_tests`. Multi-turn: phần tử cuối của `turns` phải là user turn đang được chấm.
- [ ] **Role 1**: Đặt hypothesis thứ 2, sửa tiếp `system_prompt.md`/`tools.yaml`, chạy:
  ```bash
  python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
  ```
  Ghi `version_log.csv`.
- [ ] **Role 1 hoặc Role 3**: Chạy suite group với v3 sau khi eval sẵn sàng:
  ```bash
  python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
  ```
  *(có thể tạm chạy thử sớm để canh lỗi format trước, chạy chính thức ở Checkpoint 6)*
- [ ] **Role 4**: Deploy Cloudflare Tunnel:
  ```bash
  cloudflared tunnel --url http://localhost:8501
  ```
  Lấy URL `trycloudflare.com`, test từ thiết bị khác, paste vào `REPORT.md` Phần A.
- [ ] **Role 5**: Viết xong **Report Phần A** (giới thiệu agent, tool có gì, thử bằng câu hỏi nào) trước 11:30.
- [ ] **Cả nhóm**: Rehearse 3–5 scenario demo, chuẩn bị fallback run/transcript nếu mạng chập chờn.
- [ ] 🔄 **Đồng bộ Git**: `git commit -m "Checkpoint 4: eval group + v2 + report A"` ➔ `git push`.

---

### 📍 CHECKPOINT 5: Demo → Ship (11:30–12:40)

**Showdown (11:30–12:15)**
- [ ] **Role 5**: Giới thiệu agent, dùng Report Phần A.
- [ ] **Role 4**: Chạy live demo qua UI/link tunnel, show trace + so sánh version.
- [ ] **Role 1**: Giải thích routing đã cải thiện thế nào qua v0→v2 (evidence từ run JSON).
- [ ] **Cả nhóm**: Trả lời câu hỏi/câu bẫy từ giảng viên hoặc nhóm khác.

**v3 + Report B (12:15–12:35)**
- [ ] **Role 1**: Áp dụng feedback từ showdown, sửa hypothesis cuối, chạy:
  ```bash
  python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
  ```
  Ghi `version_log.csv` (đủ v0, v1, v2, v3).
- [ ] **Role 5**: Chạy live chat 3 turn bắt buộc qua `chat.py` (request bình thường; request thiếu info rồi bổ sung; request nhạy cảm cần confirm), log transcript vào `transcripts/`.
- [ ] **Role 5**: Hoàn thiện **Report Phần B** (bảng đầy đủ v0–v3, failure analysis, eval cases, live chat, reflection) dựa trên log thật.
- [ ] **Role 2**: Đảm bảo tool mới vẫn hoạt động ổn định ở v3 (re-test nếu cần).

**Final gate (12:35–12:40)**
- [ ] **Role 4**: Kiểm tra checklist nộp bài đủ file (xem mục 3 bên dưới), khóa artifact.
- [ ] **Cả nhóm**: Xác nhận không lộ `.env`, API key trong log/screenshot/poster.
- [ ] 🔄 **Đồng bộ Git**: `git commit -m "Checkpoint 5: v3 + report B + final gate"` ➔ `git push`.

---

### 📍 CHECKPOINT 6: Kahoot Recap (12:40–13:00)

- [ ] **Cả nhóm**: Tham gia recap, không cần thao tác code.

---

## 📦 3. CHECKLIST FILE NỘP (submit `starter_v0/`)

- [ ] `artifacts/system_prompt.md`
- [ ] `artifacts/tools.yaml`
- [ ] `artifacts/version_log.csv` (đủ v0, v1, v2, v3)
- [ ] `artifacts/REPORT.md` (Phần A + Phần B)
- [ ] `data/eval_group.json` (đúng 10 case)
- [ ] `runs/*.json`
- [ ] `analysis/*.csv` (nếu có parse run logs)
- [ ] `transcripts/*.transcript.json`
- [ ] Code UI (`app.py`) + implementation tool mới + `requirements.txt`
- [ ] ❌ **Không nộp**: `.env`, API keys, `.venv/`, cache/build output

---

## 🔁 4. QUY TRÌNH GIT (nhắc lại)

**Trước khi gõ code**:
```bash
git pull
```

**Đẩy code lên cho nhóm**:
```bash
git add .
git commit -m "Role X: cap nhat noi dung"
git push
```

*(Nếu push bị chặn do bạn khác push trước: `git pull` rồi `git push` lại là xong!)*

> ⚠️ Trong mỗi vòng tối ưu (Checkpoint 3, 4, 5), **chỉ Role 1 được sửa** `artifacts/system_prompt.md` và `artifacts/tools.yaml` để tránh conflict — các thay đổi khác (tool mới, eval case) diễn ra song song ở file riêng.
