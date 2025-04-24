import cv2
import numpy as np
from PIL import Image

def calculate_sharpness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

def calculate_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness

def score_image(image):
    sharpness = calculate_sharpness(image)
    brightness = calculate_brightness(image)
    
    sharp_score = min(sharpness / 500.0 * 50, 50)
    bright_score = max(0, min((brightness - 50) / 200.0 * 50, 50))
    
    total_score = sharp_score + bright_score
    return total_score, sharpness, brightness