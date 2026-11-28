"""Standalone ARK mission and purpose page."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ark.mission import render_why_we_build  # noqa: E402

render_why_we_build(st)
