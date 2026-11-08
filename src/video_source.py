"""Reading frames from a video file or a live camera."""

import cv2


def open_source(source):
    """Open a video file or a camera.

    source: a file path (str / Path) or a camera index such as 0.
    A string made only of digits (e.g. "0") is treated as a camera index.
    """
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    elif not isinstance(source, int):
        source = str(source)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise IOError(f"Could not open video source: {source}")
    return cap


def get_first_frame(source):
    """Return only the first frame (used by the spot selector)."""
    cap = open_source(source)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise IOError(f"Could not read a frame from: {source}")
    return frame


def read_frames(cap, loop=False):
    """Yield frames one by one.

    If loop=True and the source is a video file, it restarts from the
    beginning when it reaches the end (handy for demos).
    """
    while True:
        ok, frame = cap.read()
        if not ok:
            if loop:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = cap.read()
                if not ok:
                    break
            else:
                break
        yield frame


def get_fps(cap, default=25.0):
    """Frames per second reported by the source (cameras sometimes report 0)."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    return fps if fps and fps > 0 else default
