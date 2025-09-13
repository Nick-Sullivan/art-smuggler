from enum import Enum

import cv2
import numpy as np


class SaveType(Enum):
    DEBUG = 1
    SPLIT = 2
    RECOMBINED = 3


def save_image(image: np.ndarray, path: str, image_type: SaveType) -> None:
    folder = (
        "debug"
        if image_type == SaveType.DEBUG
        else "split"
        if image_type == SaveType.SPLIT
        else "recombined"
    )
    path = f"data/output/{folder}/{path}"
    image = (image * 255).astype(np.uint8)
    cv2.imwrite(path, image)
