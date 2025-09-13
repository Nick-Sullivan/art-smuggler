import numpy as np


def create_paired_image(primary: np.ndarray, target: np.ndarray) -> np.ndarray:
    height, width, channels = target.shape
    secondary = np.zeros((height, width, channels), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            for c in range(channels):
                primary_value = primary[y, x, c]
                target_value = target[y, x, c]
                if primary_value == 0:
                    secondary[y, x, c] = 0
                else:
                    secondary[y, x, c] = 255 * (target_value / primary_value)
    return secondary
