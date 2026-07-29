# Runbook hoàn tất evidence

## Gemini key rotation

Đặt key trong `.env` (không commit):

```env
GEMINI_API_KEY=...
GEMINI_API_KEY_1=...
GEMINI_API_KEY_2=...
GEMINI_API_KEY_3=...
```

Provider tự xoay key sau mỗi request và chuyển key tiếp theo khi gặp 429.

## Chạy evidence cuối

```powershell
python scripts/preflight_provider.py --provider gemini
python run_eval.py --provider gemini --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider gemini --version v3 --suite group --eval-cases data/eval_group.json
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv
streamlit run app.py
```

Chỉ dùng run có `provider_error_cases=0` và
`measured_cases=total_cases` trong report.
