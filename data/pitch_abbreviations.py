##pitch abbreviations
from data.team_abbreviations import get_team_abbreviation


PITCH_ABBREVIATIONS = {
    "4-Seam Fastball": "4FB",
    "Changeup": "CHG",
    "Curveball": "CRV",
    "Cutter": "CUT",
    "Knuckleball": "KN",
    "Kunckle Curve": "KCV",
    "Sinker": "SNK",
    "Slider": "SLD",
    "Slurve": "SLV",
    "Split-Finger": "SPL",
    "Sweeper": "SWP",
}

PITCH_COLORS = {
    "4-Seam Fastball": (220, 60, 60),
    "Sinker": (196, 115, 230),
    "Cutter": (255, 255, 255),
    "Slider": (240, 145, 60),
    "Sweeper": (93, 46, 140),
    "Slurve": (135, 206, 235),
    "Curveball": (252, 237, 101),
    "Changeup": (110, 200, 110),
    "Split-Finger": (200, 200, 200),
    "Knuckleball": (224, 122, 148),
    "Knuckle Curve": (0, 255, 228)
}
DEFAULT_PITCH_COLOR = (170, 170, 170)

def get_pitch_abbreviation(pitch_name: str) -> str:
    """
    Returns the abbreviation for a given pitch name.
    Falls back to None if pitch not found.
    """
    abbreviation = PITCH_ABBREVIATIONS.get(pitch_name)
    return abbreviation

def get_pitch_color(pitch_name: str) -> tuple:
    """
    Returns the fixed RGB color for a given pitch name.
    Falls back to DEFAULT_PITCH_COLOR if pitch not found.
    """
    return PITCH_COLORS.get(pitch_name, DEFAULT_PITCH_COLOR)

if __name__ == "__main__":
    print(get_pitch_abbreviation("4-Seam Fastball")) 