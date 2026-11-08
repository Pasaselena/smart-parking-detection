"""Create a simple synthetic parking-lot video for testing.

It draws a top-down car park with 7 bays. Cars arrive and leave over time,
and the brightness changes slowly (like clouds) so the later weeks have
something realistic to deal with.

Usage (from the project root):
    python scripts/make_sample_video.py
It writes data/sample_parking.mp4 and data/parking_spots.json.
Replace both with your own video + select_spots.py when you have real footage.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import config  # noqa: E402
from src.spots import save_spots  # noqa: E402

WIDTH, HEIGHT = 960, 540
FPS = 25
SECONDS = 12
BAY_W, BAY_H = 110, 200
TOP = 170
LEFT = 70
GAP = 10  # space between bays


def bay_rect(i):
    x1 = LEFT + i * (BAY_W + GAP)
    return x1, TOP, x1 + BAY_W, TOP + BAY_H


def draw_background(rng):
    # Asphalt: grey with a little random noise (texture)
    img = np.full((HEIGHT, WIDTH, 3), 85, dtype=np.uint8)
    noise = rng.integers(-12, 12, size=(HEIGHT, WIDTH, 1))
    img = np.clip(img.astype(int) + noise, 0, 255).astype(np.uint8)
    for i in range(7):
        x1, y1, x2, y2 = bay_rect(i)
        cv2.rectangle(img, (x1, y1), (x2, y2), (235, 235, 235), 3)
    cv2.putText(img, "SAMPLE PARKING LOT", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 230, 230), 2)
    return img


def draw_car(img, i, color):
    x1, y1, x2, y2 = bay_rect(i)
    cx1, cy1, cx2, cy2 = x1 + 18, y1 + 20, x2 - 18, y2 - 20
    cv2.rectangle(img, (cx1, cy1), (cx2, cy2), color, -1)               # body
    cv2.rectangle(img, (cx1 + 8, cy1 + 25), (cx2 - 8, cy1 + 60),
                  (40, 40, 40), -1)                                     # windscreen
    cv2.rectangle(img, (cx1 + 8, cy2 - 45), (cx2 - 8, cy2 - 15),
                  (40, 40, 40), -1)                                     # rear window
    cv2.rectangle(img, (cx1, cy1), (cx2, cy2), (20, 20, 20), 2)         # outline


def main():
    rng = np.random.default_rng(42)
    background = draw_background(rng)
    car_colors = [(40, 40, 200), (200, 120, 30), (30, 160, 30),
                  (180, 180, 180), (20, 20, 20), (0, 200, 220), (150, 50, 150)]

    # For each bay: (time it becomes occupied, time it becomes free) in seconds
    schedule = [(0, 7), (3, 99), (0, 99), (-1, -1), (5, 10), (0, 4), (8, 99)]

    out_path = config.DEFAULT_VIDEO
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"),
                             FPS, (WIDTH, HEIGHT))

    total = FPS * SECONDS
    for f in range(total):
        t = f / FPS
        frame = background.copy()
        for i, (start, end) in enumerate(schedule):
            if start <= t < end:
                draw_car(frame, i, car_colors[i])
        # Slowly changing brightness (simulates clouds / sunlight)
        gain = 1.0 + 0.25 * np.sin(2 * np.pi * t / SECONDS)
        frame = cv2.convertScaleAbs(frame, alpha=gain, beta=0)
        writer.write(frame)
    writer.release()

    # Spot corners, clockwise from top-left, slightly inside the white lines
    spots = []
    for i in range(7):
        x1, y1, x2, y2 = bay_rect(i)
        spots.append([[x1 + 4, y1 + 4], [x2 - 4, y1 + 4],
                      [x2 - 4, y2 - 4], [x1 + 4, y2 - 4]])
    save_spots(spots, config.DEFAULT_SPOTS_FILE)

    print(f"Video: {out_path} ({total} frames)")
    print(f"Spots: {config.DEFAULT_SPOTS_FILE} ({len(spots)} spots)")


if __name__ == "__main__":
    main()
