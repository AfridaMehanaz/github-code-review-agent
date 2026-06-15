"""Streamlit UI: pick a file from samples/, run LLM review, show structured output.

No GitHub access. No write-back. Read-only local files + LLM call.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from src.reviewer import review_code, format_review_markdown

load_dotenv()

st.set_page_config(page_title="Code Review Agent", page_icon="🔍", layout="wide")
st.title("🔍 GitHub Code Review Agent")
st.caption("Local code review via LLM. Reads files from samples/, no GitHub write access.")

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


def list_samples():
    if not os.path.isdir(SAMPLES_DIR):
        return []
    return sorted(
        f for f in os.listdir(SAMPLES_DIR)
        if os.path.isfile(os.path.join(SAMPLES_DIR, f)) and not f.startswith(".")
    )


tab_sample, tab_paste = st.tabs(["From samples/", "Paste code"])

code = None
filename = "unknown"

with tab_sample:
    samples = list_samples()
    if samples:
        choice = st.selectbox("Choose a sample file", samples)
        if choice:
            path = os.path.join(SAMPLES_DIR, choice)
            with open(path, "r") as f:
                file_code = f.read()
            st.code(file_code, language="python")
            if st.button("Review this file", key="review_sample"):
                code = file_code
                filename = choice
    else:
        st.info("No files in samples/ yet.")

with tab_paste:
    pasted = st.text_area("Paste code or diff", height=300)
    paste_filename = st.text_input("Filename (for context)", value="pasted_code.py")
    if st.button("Review pasted code", key="review_paste"):
        if pasted.strip():
            code = pasted
            filename = paste_filename
        else:
            st.warning("Paste some code first.")

if code is not None:
    if not os.environ.get("LLM_API_KEY"):
        st.error("LLM_API_KEY not set. Copy .env.example to .env and add your key.")
    else:
        with st.spinner("Reviewing..."):
            try:
                review = review_code(code, filename=filename)
            except Exception as e:
                st.error(f"Review failed: {e}")
                review = None

        if review:
            st.subheader("Summary")
            st.write(review["summary"] or "_none_")

            cols = st.columns(4)
            sections = [
                ("🐛 Bugs", "bugs"),
                ("🔒 Security Issues", "security_issues"),
                ("🎨 Style Issues", "style_issues"),
                ("💡 Suggestions", "suggestions"),
            ]
            for col, (title, key) in zip(cols, sections):
                with col:
                    st.markdown(f"**{title}**")
                    items = review.get(key, [])
                    if items:
                        for item in items:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown("_none_")

            st.divider()
            md = format_review_markdown(review, filename=filename)
            st.download_button("Download review as markdown", md, file_name=f"review_{filename}.md")
