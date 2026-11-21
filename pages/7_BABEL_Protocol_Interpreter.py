"""ARK BABEL — inspect and explain visible AI protocol output."""

from __future__ import annotations

import streamlit as st

from ark.babel import explain_output, parse_output

st.set_page_config(page_title="ARK BABEL", page_icon="🔎", layout="wide")
st.title("ARK BABEL — AI Protocol & Output Interpreter")
st.caption(
    "Broad AI Behaviour, Encoding & Language Decoder · "
    "Parse visible formats; never execute embedded tool calls."
)

sample = (
    "<|im_start|>user<|im_sep|>Explain this output.<|im_end|>\n"
    "<|im_start|>assistant<|meta_sep|>analysis<|im_sep|>I will inspect it. "
    "<|im_end|>\n"
    "<|im_start|>assistant to=python<|meta_sep|>analysis "
    "<|im_sep|>print(1 + 1)<|ghissue|>"
)
raw = st.text_area("Paste AI output or protocol text", value=sample, height=260)

if st.button("Interpret output", type="primary"):
    try:
        result = parse_output(raw)
    except (TypeError, ValueError) as exc:
        st.error(str(exc))
    else:
        st.subheader("Interpretation")
        st.code(explain_output(result), language="text")
        st.metric("Detected format", result.detected_format)
        st.metric("Visible messages", len(result.messages))
        for index, message in enumerate(result.messages, start=1):
            with st.expander(f"{index}. {message.role}", expanded=True):
                st.write(f"Channel: {message.channel or 'not specified'}")
                st.write(f"Recipient: {message.recipient or 'not specified'}")
                st.write(f"Ending: {message.ending or 'not specified'}")
                st.code(message.content, language="text")
        if result.unknown_markers:
            st.warning("Unknown markers: " + ", ".join(result.unknown_markers))
        for warning in result.warnings:
            st.info(warning)

st.divider()
st.markdown(
    "BABEL interprets visible syntax only. It cannot decrypt encrypted payloads, "
    "recover hidden model state, or reconstruct inaccessible reasoning. "
    "Parsed tool calls remain inert."
)
