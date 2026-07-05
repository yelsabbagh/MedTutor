from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from agents.coordinator_agent import CoordinatorAgent
from agents.schemas import MEDICAL_DISCLAIMER, WorkflowResult


SAMPLE_PATH = Path("sample_data/sample_respiratory_lecture.txt")


def main() -> None:
    st.set_page_config(page_title="MedTutor Agent", page_icon="MT", layout="wide")
    _inject_css()

    st.title("MedTutor Agent")
    st.caption("Multi-agent medical exam coaching from lecture PDFs or pasted notes.")

    with st.sidebar:
        st.header("Lecture Source")
        input_mode = st.radio("Input", ["Use sample lecture", "Upload PDF/TXT", "Paste text"], label_visibility="collapsed")
        topic = st.text_input("Topic focus", placeholder="Example: COPD diagnosis")
        count = st.slider("Items", min_value=1, max_value=10, value=5)
        task_label = st.radio(
            "Task",
            ["Generate MCQs", "Generate OSCE cases", "Generate study blueprint", "Validate existing MCQs"],
        )
        run = st.button("Run workflow", type="primary", use_container_width=True)

    lecture_text, pdf_bytes, source_name = _read_input(input_mode)
    existing_mcqs_json = ""
    if task_label == "Validate existing MCQs":
        existing_mcqs_json = st.text_area(
            "Existing MCQs JSON",
            height=220,
            placeholder='[{"id":"mcq_001","question":"...","options":[...],"correct_answer":"B","explanations":{...}}]',
        )

    st.info(MEDICAL_DISCLAIMER)

    if not run:
        _render_welcome_preview(lecture_text, source_name)
        return

    if not lecture_text.strip() and not pdf_bytes and task_label != "Validate existing MCQs":
        st.error("Add lecture text, upload a file, or use the sample lecture before running the workflow.")
        return

    coordinator = CoordinatorAgent()
    try:
        with st.spinner("Running coordinator and specialist agents..."):
            result = coordinator.run(
                task=_task_value(task_label),
                lecture_text=lecture_text,
                pdf_bytes=pdf_bytes,
                source_name=source_name,
                topic=topic,
                count=count,
                existing_mcqs_json=existing_mcqs_json,
            )
    except Exception as exc:  # pragma: no cover - shown in UI
        st.exception(exc)
        return

    _render_result(result)


def _read_input(input_mode: str) -> tuple[str, bytes | None, str]:
    if input_mode == "Use sample lecture":
        text = SAMPLE_PATH.read_text(encoding="utf-8") if SAMPLE_PATH.exists() else ""
        st.subheader("Sample Lecture")
        st.text_area("Source text", value=text, height=280, disabled=True, label_visibility="collapsed")
        return text, None, SAMPLE_PATH.name

    if input_mode == "Upload PDF/TXT":
        uploaded = st.file_uploader("Upload lecture", type=["pdf", "txt"])
        if not uploaded:
            return "", None, "uploaded_lecture"
        data = uploaded.getvalue()
        if uploaded.name.lower().endswith(".pdf"):
            st.caption(f"Uploaded PDF: {uploaded.name}")
            return "", data, uploaded.name
        text = data.decode("utf-8", errors="replace")
        st.text_area("Uploaded text", value=text, height=280, disabled=True)
        return text, None, uploaded.name

    text = st.text_area("Paste lecture text", height=280, placeholder="Paste lecture notes here...")
    return text, None, "pasted_text"


def _task_value(task_label: str) -> str:
    return {
        "Generate MCQs": "mcq",
        "Generate OSCE cases": "osce",
        "Generate study blueprint": "blueprint",
        "Validate existing MCQs": "validate",
    }[task_label]


def _render_welcome_preview(lecture_text: str, source_name: str) -> None:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Workflow")
        st.write(
            "Choose a task in the sidebar, then run the coordinator. "
            "The demo shows retrieval, generation, validation, and export steps as an agent trace."
        )
    with right:
        st.metric("Source", source_name)
        st.metric("Characters", f"{len(lecture_text):,}")


def _render_result(result: WorkflowResult) -> None:
    trace_col, safety_col = st.columns([2, 1])
    with trace_col:
        st.subheader("Agent Trace")
        for step in result.trace:
            css_class = "trace-warning" if step.status == "warning" else "trace-ok"
            st.markdown(
                f"<div class='trace-row {css_class}'><strong>{step.agent}</strong>"
                f"<span>{step.action}</span><p>{step.detail}</p></div>",
                unsafe_allow_html=True,
            )

    with safety_col:
        st.subheader("Safety")
        safety = result.safety or {}
        if safety.get("safe", True):
            st.success("No obvious prompt-injection or PHI patterns detected.")
        else:
            st.warning("Safety warnings found. Review before using the output.")
        st.json(safety, expanded=False)

    tabs = st.tabs(["Output", "Blueprint", "Sources", "Downloads"])
    with tabs[0]:
        if result.mcqs:
            _render_mcqs(result.mcqs, result.validation)
        elif result.osce_cases:
            _render_osce(result.osce_cases)
        else:
            st.json(result.blueprint)

    with tabs[1]:
        st.json(result.blueprint)

    with tabs[2]:
        chunks = result.retrieved_chunks or result.chunks
        for chunk in chunks:
            label = f"{chunk.chunk_id} - {chunk.source}"
            if chunk.page:
                label += f" page {chunk.page}"
            with st.expander(label):
                st.write(chunk.text)

    with tabs[3]:
        _render_downloads(result.exports)


def _render_mcqs(mcqs: list[dict[str, Any]], validation: dict[str, Any]) -> None:
    if validation:
        if validation.get("valid"):
            st.success(validation.get("summary", "MCQs passed validation."))
        else:
            st.warning(validation.get("summary", "Some MCQs need review."))
    for mcq in mcqs:
        with st.expander(f"{mcq.get('id', 'MCQ')} - Answer {mcq.get('correct_answer')}"):
            st.markdown(f"**{mcq['question']}**")
            for option in mcq["options"]:
                st.write(f"{option['label']}. {option['text']}")
            st.markdown("**Explanations**")
            st.json(mcq.get("explanations", {}), expanded=False)
            st.caption("Sources: " + ", ".join(mcq.get("source_chunks", [])))


def _render_osce(cases: list[dict[str, Any]]) -> None:
    for case in cases:
        with st.expander(case["station_title"], expanded=True):
            st.markdown("**Stem**")
            st.write(case["stem"])
            st.markdown("**Examiner Questions**")
            for question in case["examiner_questions"]:
                st.write(f"- {question}")
            st.markdown("**Expected Answers**")
            for answer in case["expected_answers"]:
                st.write(f"- {answer}")
            st.caption("Sources: " + ", ".join(case.get("source_chunks", [])))


def _render_downloads(exports: dict[str, str]) -> None:
    visible = {name: path for name, path in exports.items() if not name.startswith("_")}
    if not visible:
        st.write("No exports created.")
        return
    for name, path in visible.items():
        content_key = "_" + name.replace(".", "_").replace("questions_json", "questions_json")
        content = _content_for_download(name, exports)
        mime = "application/json" if name.endswith(".json") else "text/csv" if name.endswith(".csv") else "text/markdown"
        st.download_button(
            label=f"Download {name}",
            data=content,
            file_name=name,
            mime=mime,
            use_container_width=True,
        )
        st.caption(f"Saved locally: {path}")


def _content_for_download(name: str, exports: dict[str, str]) -> str:
    lookup = {
        "questions.json": "_questions_json",
        "mcqs.md": "_mcqs_markdown",
        "mcqs.csv": "_mcqs_csv",
        "osce_cases.json": "_osce_json",
        "osce_cases.md": "_osce_markdown",
        "study_blueprint.json": "_blueprint_json",
        "study_plan.md": "_blueprint_markdown",
    }
    key = lookup.get(name)
    if key and key in exports:
        return exports[key]
    path = Path(exports[name])
    return path.read_text(encoding="utf-8") if path.exists() else json.dumps(exports, indent=2)


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 2rem; max-width: 1180px; }
        .trace-row {
            border: 1px solid #d6dde6;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.55rem;
            background: #ffffff;
        }
        .trace-row span {
            color: #526071;
            font-size: 0.82rem;
            margin-left: 0.6rem;
            text-transform: uppercase;
        }
        .trace-row p { margin: 0.35rem 0 0; color: #26313f; }
        .trace-ok { border-left: 4px solid #21867a; }
        .trace-warning { border-left: 4px solid #b45309; }
        div[data-testid="stMetric"] {
            border: 1px solid #d6dde6;
            border-radius: 8px;
            padding: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
