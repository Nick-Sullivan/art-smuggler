import numpy as np


def create_image(height: int, width: int) -> np.ndarray:
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
