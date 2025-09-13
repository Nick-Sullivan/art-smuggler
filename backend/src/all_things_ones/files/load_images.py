import os

import cv2
import numpy as np


def load_images(folder: str) -> list[np.ndarray]:
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            filepath = os.path.join(folder, filename)
            images.append(cv2.imread(filepath))
    return images
