"""
Enable the RFC2217 client for all tools in this Python environment.
"""

import site
from pathlib import Path

source: Path = Path(__file__).resolve().parent
pth: Path = Path(site.getsitepackages()[0]) / "dsig_serial.pth"
pth.write_text(f"{source}\nimport dsig_serial\n", encoding="utf-8")
