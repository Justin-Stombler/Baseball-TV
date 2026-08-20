from pathlib import Path
from datetime import time as dt_time
from zoneinfo import ZoneInfo


# src/constants.py -> repo root is one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FONTS_DIR = PROJECT_ROOT / "fonts"

##game-day timezone/cutover, used anywhere "today's game" needs to be determined
GAME_DAY_TIMEZONE = ZoneInfo("America/New_York")
CUTOVER_TIME = dt_time(12, 30)  # before this ET time, keep showing the prior completed game

FINAL_STATUSES = {"Final", "Game Over", "Completed Early"}
UPCOMING_STATUSES = {"Scheduled", "Pre-Game", "Warmup"}
LIVE_STATUSES = {"In Progress", "Manager Challenge", "Review", "Delayed", "Delayed Start", "Suspended"}
