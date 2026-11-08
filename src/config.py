"""Project-wide settings in one place."""

from pathlib import Path

# Folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Default files
DEFAULT_VIDEO = DATA_DIR / "sample_parking.mp4"
DEFAULT_SPOTS_FILE = DATA_DIR / "parking_spots.json"

# Drawing (OpenCV uses BGR, not RGB)
COLOR_SPOT = (255, 200, 0)      # light blue - saved parking spots
COLOR_DRAFT = (0, 255, 255)     # yellow - spot currently being drawn
COLOR_TEXT = (255, 255, 255)    # white
LINE_THICKNESS = 2

# Each parking spot is defined by exactly 4 corner points
POINTS_PER_SPOT = 4
