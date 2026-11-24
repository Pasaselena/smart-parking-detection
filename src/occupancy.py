import cv2

from src.spots import crop_spot


def count_white(binary, points):
    """Bir park yerinin icindeki beyaz pikselleri sayar."""
    crop, mask = crop_spot(binary, points)
    inside = cv2.bitwise_and(crop, crop, mask=mask)
    return cv2.countNonZero(inside)