"""Parking spot (ROI) storage and drawing.

A parking spot is a polygon with 4 corners: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].
All spots are stored in a JSON file so they only need to be selected once
(the camera is fixed, so the spots never move).
"""

import json
from pathlib import Path

import cv2
import numpy as np

from src import config


def save_spots(spots, path=config.DEFAULT_SPOTS_FILE):
    """Save the list of spots to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "spots": [
            {"id": i + 1, "points": [[int(x), int(y)] for x, y in pts]}
            for i, pts in enumerate(spots)
        ]
    }
    path.write_text(json.dumps(data, indent=2))


def load_spots(path=config.DEFAULT_SPOTS_FILE):
    """Load spots from JSON. Returns a list of 4-point lists."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No spots file at {path}. Run select_spots.py first."
        )
    data = json.loads(path.read_text())
    spots = [s["points"] for s in data["spots"]]
    for i, pts in enumerate(spots, start=1):
        if len(pts) != config.POINTS_PER_SPOT:
            raise ValueError(f"Spot {i} has {len(pts)} points, expected 4.")
    return spots


def spot_center(points):
    """Middle point of a polygon - used to place the spot number."""
    pts = np.array(points)
    return int(pts[:, 0].mean()), int(pts[:, 1].mean())


def draw_spots(frame, spots, color=config.COLOR_SPOT):
    """Draw every spot as a closed polygon with its number in the middle.

    Returns a new image; the original frame is not modified.
    """
    output = frame.copy()
    for i, pts in enumerate(spots, start=1):
        polygon = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(output, [polygon], isClosed=True,
                      color=color, thickness=config.LINE_THICKNESS)
        cx, cy = spot_center(pts)
        cv2.putText(output, str(i), (cx - 8, cy + 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_TEXT, 2)
    return output


def crop_spot(frame, points):
    """Cut one spot out of the frame (needed from Week 3 on).

    Returns the bounding-box crop and a mask where pixels inside the
    polygon are 255 and outside are 0.
    """
    pts = np.array(points, dtype=np.int32)
    x, y, w, h = cv2.boundingRect(pts)
    crop = frame[y:y + h, x:x + w]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [pts - [x, y]], 255)
    return crop, mask
