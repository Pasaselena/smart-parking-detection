"""Play the video and draw the saved parking spots on every frame.

Week 1: only shows the spots (no detection yet).
Later weeks will add pre-processing and FREE / FULL decisions here.

Usage:
    python main.py
    python main.py --source my_video.mp4 --loop
    python main.py --snapshot outputs/week1.png   # save one frame, no window
"""

import argparse
import time
from pathlib import Path

import cv2

from src import config
from src.spots import draw_spots, load_spots
from src.video_source import get_first_frame, get_fps, open_source, read_frames
from src.preprocess import process_frame

WINDOW = "Smart Parking"


def save_snapshot(source, spots, out_path):
    frame = get_first_frame(source)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), draw_spots(frame, spots))
    print(f"Snapshot saved to {out_path}")


def run(source, spots, loop):
    cap = open_source(source)
    delay_ms = int(1000 / get_fps(cap))   # play at the video's real speed
    prev = time.time()

    for frame in read_frames(cap, loop=loop):
        output = draw_spots(frame, spots)

        # Measured processing speed (FPS) - becomes important on Raspberry Pi
        now = time.time()
        fps = 1.0 / max(now - prev, 1e-6)
        prev = now
        cv2.putText(output, f"Spots: {len(spots)}  FPS: {fps:.0f}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_TEXT, 2)

        cv2.imshow(WINDOW, output)
        key = cv2.waitKey(delay_ms) & 0xFF
        if key in (ord("q"), 27): 
            break
        if key == ord("p"):        # pause until any key
            cv2.waitKey(0)
        cv2.imshow("Processed", process_frame(frame))
    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Smart Parking viewer")
    parser.add_argument("--source", default=str(config.DEFAULT_VIDEO),
                        help="video file or camera index")
    parser.add_argument("--spots", default=str(config.DEFAULT_SPOTS_FILE),
                        help="parking spots JSON")
    parser.add_argument("--loop", action="store_true",
                        help="restart the video when it ends")
    parser.add_argument("--snapshot", metavar="PNG",
                        help="save the first frame with spots and exit")
    args = parser.parse_args()

    spots = load_spots(args.spots)
    print(f"Loaded {len(spots)} parking spots.")

    if args.snapshot:
        save_snapshot(args.source, spots, args.snapshot)
    else:
        run(args.source, spots, args.loop)


if __name__ == "__main__":
    main()
