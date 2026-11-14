import cv2

def to_gray(frame):
    """Renkli kareyi gri tonlamaya çevirir."""
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray  