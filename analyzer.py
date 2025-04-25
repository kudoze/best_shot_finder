import cv2
import numpy as np
from skimage.color import rgb2lab
from skimage import img_as_float
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_sharpness(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        sharpness = float(cv2.Laplacian(small, cv2.CV_64F).var() / 1000)
        logger.info(f"Sharpness for {image_path}: {sharpness}")
        return sharpness
    except Exception as e:
        raise ValueError(f"Error in calculate_sharpness: {str(e)}")

def calculate_noise(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        img_f = img_as_float(small)
        noise = float(np.std(img_f) * 100)
        logger.info(f"Noise for {image_path}: {noise}")
        return noise
    except Exception as e:
        raise ValueError(f"Error in calculate_noise: {str(e)}")

def calculate_brightness(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        brightness = float(np.mean(hsv[:, :, 2]) / 255 * 100)
        logger.info(f"Brightness for {image_path}: {brightness}")
        return brightness
    except Exception as e:
        raise ValueError(f"Error in calculate_brightness: {str(e)}")

def calculate_contrast(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        contrast = float(np.std(small) / 255 * 100)
        logger.info(f"Contrast for {image_path}: {contrast}")
        return contrast
    except Exception as e:
        raise ValueError(f"Error in calculate_contrast: {str(e)}")

def calculate_saturation(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        lab = rgb2lab(small)
        chroma = np.sqrt(lab[:, :, 1]**2 + lab[:, :, 2]**2)
        saturation = float(np.mean(chroma) / 180 * 100)
        logger.info(f"Saturation for {image_path}: {saturation}")
        return saturation
    except Exception as e:
        raise ValueError(f"Error in calculate_saturation: {str(e)}")

def calculate_composition(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not load image")
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        edges = cv2.Canny(small, 100, 200)
        h, w = edges.shape
        third_h, third_w = h // 3, w // 3
        score = 0
        for i in range(2):
            h_start = (i + 1) * third_h - third_h // 4
            h_end = (i + 1) * third_h + third_h // 4
            w_start = (i + 1) * third_w - third_w // 4
            w_end = (i + 1) * third_w + third_w // 4
            score += np.sum(edges[h_start:h_end, :]) + np.sum(edges[:, w_start:w_end])
        total_edges = np.sum(edges)
        if total_edges == 0:
            composition = 0.0
        else:
            # Normalisiere relativ zur maximal möglichen Kanten-Summe in den Dritteln
            max_possible_score = total_edges * 4  # Maximal 4 Bereiche (2 horizontal, 2 vertikal)
            composition = float(np.clip((score / max_possible_score) * 100, 0, 100))
        logger.info(f"Composition for {image_path}: {composition} (score={score}, total_edges={total_edges})")
        return composition
    except Exception as e:
        raise ValueError(f"Error in calculate_composition: {str(e)}")

def composite_score(metrics, weights=None):
    try:
        if weights is None:
            weights = {
                "sharpness": 0.25,
                "noise": -0.2,
                "brightness": 0.2,
                "contrast": 0.2,
                "saturation": 0.15,
                "composition": 0.2
            }
        noise_score = max(0, 100 - metrics["noise"])
        score = (
            metrics["sharpness"] * weights["sharpness"] +
            noise_score * (-weights["noise"]) +
            metrics["brightness"] * weights["brightness"] +
            metrics["contrast"] * weights["contrast"] +
            metrics["saturation"] * weights["saturation"] +
            metrics["composition"] * weights["composition"]
        )
        composite = float(np.clip(score / 2, 0, 100))
        logger.info(f"Composite score: {composite} (metrics={metrics}, weights={weights})")
        return composite
    except Exception as e:
        raise ValueError(f"Error in composite_score: {str(e)}")