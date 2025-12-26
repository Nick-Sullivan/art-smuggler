import cv2
import numpy as np


def load_input_image(file_name: str) -> np.ndarray:
    return load_image(f"data/input/{file_name}")


def load_seed_image(file_name: str) -> np.ndarray:
    return load_image(f"data/seed/{file_name}")


def load_image(file_path: str) -> np.ndarray:
    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    assert image is not None, f"Failed to load image: {file_path}"
    return image.astype(np.float32) / 255.0
