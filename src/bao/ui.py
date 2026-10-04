"""Launch Bao's Streamlit web interface.

This compatibility entry point keeps ``python -m bao.ui`` working while the
application's supported UI is implemented in :mod:`bao.streamlit_app`.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Start Streamlit on Bao's local default address and port."""
    app_path = Path(__file__).with_name("streamlit_app.py")
    port = os.environ.get("BAO_SERVER_PORT", "7860")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        port,
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
