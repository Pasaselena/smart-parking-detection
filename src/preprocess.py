import cv2

def to_gray(frame):
    """Renkli kareyi gri tonlamaya çevirir."""
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray  

def blur(gray):
    """Gri resmi bulaniklastirarak kucuk gurultuleri yok eder."""
    blurred=cv2.GaussianBlur(gray,(5,5),0)
    return blurred

def threshold(blurred):
    """Detayları beyaz, düz alanları siyah yapar."""
    binary = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
    return binary 

def process_frame(frame):
    """uc istasyonu sırayla çalıştırır: gri -> bulanik -> siyah-beyaz"""
    gray= to_gray(frame)
    blurred=blur(gray)
    binary = threshold(blurred)
    return binary