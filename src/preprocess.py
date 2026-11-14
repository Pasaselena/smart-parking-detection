import cv2

def to_gray(frame):
    """Renkli kareyi gri tonlamaya çevirir."""
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray  

def blur(gray):
    """Gri resmi bulaniklastirarak kucuk gurultuleri yok eder."""
    blurred=cv2.GaussianBlur(gray,(5,5),0)
    return blurred