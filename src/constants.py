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

##MLB's detailedState comes in many "Prefix: Reason" variants (e.g. "Delayed: Rain",
##"Suspended: COVID-19", "Manager challenge: Tag play") that a flat set of exact
##strings can't catch — classified by prefix instead so a reason suffix we haven't
##hardcoded doesn't silently fall through to "no game" downstream. Order matters:
##more specific prefixes (e.g. "Delayed Start") are checked before broader relatives
##(e.g. "Delayed").
UPCOMING_PREFIXES = ("Scheduled", "Pre-Game", "Warmup", "Delayed Start")
FINAL_PREFIXES = ("Final", "Game Over", "Completed Early")
LIVE_PREFIXES = (
    "In Progress", "Instant Replay", "Delayed", "Suspended",
    "Manager challenge", "Umpire review", "Umpire Challenge", "Player challenge",
)


def classify_game_status(detailed_state: str) -> str | None:
    """Classify a raw MLB detailedState string into 'upcoming' / 'live' / 'final'.
    Returns None for statuses that don't get a box score (Postponed, Cancelled,
    Forfeit, Unknown, etc.)."""
    for prefix in UPCOMING_PREFIXES:
        if detailed_state.startswith(prefix):
            return "upcoming"
    for prefix in FINAL_PREFIXES:
        if detailed_state.startswith(prefix):
            return "final"
    for prefix in LIVE_PREFIXES:
        if detailed_state.startswith(prefix):
            return "live"
    return None
