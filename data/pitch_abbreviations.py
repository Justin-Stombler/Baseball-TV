##pitch abbreviations
from data.team_abbreviations import get_team_abbreviation


PITCH_ABBREVIATIONS = {
    "4-Seam Fastball": "4FB",
    "Changeup": "CHG",
    "Curveball": "CRV",
    "Cutter": "CUT",
    "Knuckleball": "KN",
    "Sinker": "SNK",
    "Slider": "SLD",
    "Slurve": "SLV",
    "Split-Finger": "SPL",
    "Sweeper": "SWP",
}

def get_pitch_abbreviation(pitch_name: str) -> str:
    """
    Returns the abbreviation for a given pitch name.
    Falls back to None if pitch not found.
    """
    abbreviation = PITCH_ABBREVIATIONS.get(pitch_name)
    return abbreviation

if __name__ == "__main__":
    print(get_pitch_abbreviation("4-Seam Fastball")) 