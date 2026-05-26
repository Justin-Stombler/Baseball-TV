from pathlib import Path


# src/constants.py -> repo root is one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FONTS_DIR = PROJECT_ROOT / "fonts"
