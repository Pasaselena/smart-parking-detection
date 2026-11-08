"""Interactive tool to mark parking spots with the mouse.

Usage:
    python select_spots.py                      # uses data/sample_parking.mp4
    python select_spots.py --source my_video.mp4
    python select_spots.py --source 0           # webcam

Controls:
    Left click  : add a corner (4 corners = 1 spot, clockwise is easiest)
    u           : undo the last corner
    d           : delete the last finished spot
    s           : save to JSON
    q / Esc     : quit (asks you to save first if there are unsaved changes)
"""

import argparse

import cv2
import numpy as np

from src import config
from src.spots import draw_spots, load_spots, save_spots
from src.video_source import get_first_frame

WINDOW = "Select parking spots"


class SpotSelector:
    def __init__(self, frame, spots=None):
        self.frame = frame
        self.spots = spots or []    # finished spots (each has 4 points)
        self.current = []           # corners of the spot being drawn
        self.unsaved = False

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current.append([x, y])
            if len(self.current) == config.POINTS_PER_SPOT:
                self.spots.append(self.current)
                self.current = []
                self.unsaved = True
                print(f"Spot {len(self.spots)} added.")

    def render(self):
        img = draw_spots(self.frame, self.spots)
        # Spot in progress: dots + open lines
        for p in self.current:
            cv2.circle(img, tuple(p), 4, config.COLOR_DRAFT, -1)
        if len(self.current) > 1:
            pts = np.array(self.current, dtype=np.int32)
            cv2.polylines(img, [pts], False, config.COLOR_DRAFT, 1)

        info = f"Spots: {len(self.spots)} | click 4 corners | u undo  d delete  s save  q quit"
        cv2.rectangle(img, (0, 0), (img.shape[1], 28), (0, 0, 0), -1)
        cv2.putText(img, info, (8, 19), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, config.COLOR_TEXT, 1)
        return img


def main():
    parser = argparse.ArgumentParser(description="Mark parking spots.")
    parser.add_argument("--source", default=str(config.DEFAULT_VIDEO),
                        help="video file or camera index")
    parser.add_argument("--output", default=str(config.DEFAULT_SPOTS_FILE),
                        help="where to save the JSON")
    args = parser.parse_args()

    frame = get_first_frame(args.source)

    # Continue from an existing file if there is one
    try:
        spots = load_spots(args.output)
        print(f"Loaded {len(spots)} existing spots from {args.output}")
    except FileNotFoundError:
        spots = []

    selector = SpotSelector(frame, spots)
    cv2.namedWindow(WINDOW)
    cv2.setMouseCallback(WINDOW, selector.on_mouse)

    while True:
        cv2.imshow(WINDOW, selector.render())
        key = cv2.waitKey(20) & 0xFF

        if key == ord("u") and selector.current:
            selector.current.pop()
        elif key == ord("d") and selector.spots:
            selector.spots.pop()
            selector.unsaved = True
            print(f"Last spot deleted. {len(selector.spots)} left.")
        elif key == ord("s"):
            save_spots(selector.spots, args.output)
            selector.unsaved = False
            print(f"Saved {len(selector.spots)} spots to {args.output}")
        elif key in (ord("q"), 27):  # 27 = Esc
            if selector.unsaved:
                print("Unsaved changes! Press 's' to save or 'q' again to quit.")
                selector.unsaved = False
                continue
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
