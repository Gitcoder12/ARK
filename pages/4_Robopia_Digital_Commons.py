"""Compatibility landing page for the retired Robopia display name."""

import streamlit as st

st.set_page_config(page_title="ARKWorld — Legacy Name", page_icon="🌍", layout="wide")
st.title("This simulation is now part of ARKWorld")
st.caption(
    "Robopia was the original name of the digital commons prototype. "
    "The project has been renamed and placed inside the ARKWorld simulation hub."
)
st.page_link(
    "pages/4_ARKWorld_Digital_Commons.py",
    label="Open ARKWorld Digital Commons",
    icon="🌐",
)
st.page_link("arkworld.py", label="Return to ARKWorld hub", icon="🏠")
st.info(
    "Nothing was deleted. The original engine and Python import path are retained "
    "for compatibility; ARKWorld is the canonical user-facing name."
)
