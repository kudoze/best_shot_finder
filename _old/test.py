import cv2
from analyzer import score_image

img = cv2.imread("testbild.jpg")  # Lege testbild.jpg in denselben Ordner
score, sharpness, brightness = score_image(img)

print(f"Score: {score:.2f}")
print(f"Schärfe: {sharpness:.2f}")
print(f"Helligkeit: {brightness:.2f}")