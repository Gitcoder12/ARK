"""Standalone ARK Workbench launcher.

Run with: streamlit run app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ark.dashboard import render_dashboard  # noqa: E402

render_dashboard()
