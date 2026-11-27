"""Searchable agent and experiment page for the ARKWorld Streamlit hub."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ark.dashboard import render_dashboard  # noqa: E402

render_dashboard()
