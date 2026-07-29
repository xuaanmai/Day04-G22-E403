from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"
RUNS = ROOT / "runs"
TRANSCRIPTS = ROOT / "transcripts"
load_lab_env(ROOT)


def load_artifacts(version: str) -> tuple[str, list[dict[str, Any]], dict[str, str]]:
    prompt_path = ARTIFACTS / "system_prompt.md"
    tools_path = ARTIFACTS / "tools.yaml"
    prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    artifact = build_artifact_version(version, prompt_path, tools_path)
    return prompt, to_openai_tools(declarations), artifact_version_dict(artifact)


def save_transcript() -> Path:
    TRANSCRIPTS.mkdir(exist_ok=True)
    path = TRANSCRIPTS / f"{st.session_state.transcript_id}.transcript.json"
    payload = {
        "transcript_id": st.session_state.transcript_id,
        **st.session_state.artifact,
        "provider": "gemini",
        "model": st.session_state.model,
        "created_at": st.session_state.created_at,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "turns": st.session_state.turns,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def run_files() -> list[Path]:
    return sorted(RUNS.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def run_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "file": path.name,
        "version": data.get("version"),
        "artifact_version": data.get("artifact_version"),
        **(data.get("summary") or {}),
    }


st.set_page_config(page_title="G22 Research Agent", page_icon="🔎", layout="wide")
st.title("G22 Research Agent")
st.caption("Research bằng Gemini · tool trace minh bạch · transcript lưu tự động")

with st.sidebar:
    st.header("Cấu hình")
    version = st.selectbox("Artifact version", ["v3", "v2", "v1", "v0"])
    model_override = st.text_input("Model override", placeholder="Để trống dùng model mặc định")
    max_rounds = st.slider("Số tool round tối đa", 1, 6, 4)
    if st.button("Bắt đầu transcript mới", width="stretch"):
        for key in ("turns", "history", "transcript_id", "artifact", "model", "created_at"):
            st.session_state.pop(key, None)
        st.rerun()

prompt, tools, artifact = load_artifacts(version)
provider = make_provider("gemini")
selected_model = model_override or getattr(provider, "default_model", None)

if "turns" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.turns = []
    st.session_state.history = []
    st.session_state.transcript_id = f"{version}_gemini_ui_{timestamp}"
    st.session_state.created_at = datetime.now().isoformat(timespec="seconds")
    st.session_state.artifact = artifact
    st.session_state.model = selected_model

metric_cols = st.columns(4)
metric_cols[0].metric("Provider", "Gemini")
metric_cols[1].metric("Version", version)
metric_cols[2].metric("Model", selected_model or "default")
metric_cols[3].metric("Tool declarations", len(tools))
st.code(artifact["artifact_version"], language=None)

chat_tab, trace_tab, evidence_tab = st.tabs(["Chat", "Tool trace", "So sánh run"])

with chat_tab:
    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.write(turn.get("assistant_text") or turn.get("error") or "")

    if user_text := st.chat_input("Nhập yêu cầu nghiên cứu…"):
        with st.chat_message("user"):
            st.write(user_text)
        messages = [
            {"role": "system", "content": prompt},
            *trim_history(st.session_state.history, 5),
            {"role": "user", "content": user_text},
        ]
        turn: dict[str, Any] = {
            "turn_index": len(st.session_state.turns) + 1,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "user": user_text,
        }
        try:
            with st.spinner("Gemini đang chọn và chạy tool…"):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=model_override or None,
                    max_tool_rounds=max_rounds,
                )
            turn.update(result)
            st.session_state.history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": result["assistant_text"]},
            ])
            with st.chat_message("assistant"):
                st.write(result["assistant_text"])
        except Exception as exc:
            turn.update({
                "status": "provider_error",
                "assistant_text": "Gemini API gặp lỗi. Xem chi tiết trong tool trace.",
                "error": f"{type(exc).__name__}: {exc}",
                "rounds": [],
                "tool_events": [],
            })
            with st.chat_message("assistant"):
                st.error(turn["error"])
        turn["ended_at"] = datetime.now().isoformat(timespec="seconds")
        st.session_state.turns.append(turn)
        transcript_path = save_transcript()
        st.caption(f"Đã lưu: {transcript_path.name}")
        st.rerun()

with trace_tab:
    if not st.session_state.turns:
        st.info("Chưa có lượt chat. Tool name, args, round, result và error sẽ xuất hiện ở đây.")
    for turn in reversed(st.session_state.turns):
        with st.expander(
            f"Turn {turn['turn_index']} · {turn.get('status', 'unknown')} · {turn['user'][:70]}",
            expanded=turn["turn_index"] == len(st.session_state.turns),
        ):
            if turn.get("error"):
                st.error(turn["error"])
            for round_data in turn.get("rounds", []):
                st.markdown(f"**Round {round_data.get('round')}**")
                st.json({
                    "assistant_text": round_data.get("assistant_text"),
                    "tool_calls": round_data.get("tool_calls", []),
                    "tool_results": round_data.get("tool_results", []),
                })

with evidence_tab:
    files = run_files()
    if not files:
        st.warning("Chưa có run JSON.")
    else:
        summaries = [run_summary(path) for path in files]
        st.dataframe(summaries, width="stretch", hide_index=True)
        selected = st.selectbox("Mở run JSON", files, format_func=lambda path: path.name)
        selected_data = json.loads(selected.read_text(encoding="utf-8"))
        st.json({
            "artifact_version": selected_data.get("artifact_version"),
            "prompt_hash": selected_data.get("prompt_hash"),
            "tools_hash": selected_data.get("tools_hash"),
            "summary": selected_data.get("summary"),
        })
