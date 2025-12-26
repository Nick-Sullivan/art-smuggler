import numpy as np


def trim_colour_to_fit(image: np.ndarray, target: np.ndarray) -> np.ndarray:
    height, width, channels = target.shape
    for y in range(height):
        for x in range(width):
            for c in range(channels):
                if image[y, x, c] < target[y, x, c]:
                    image[y, x, c] = target[y, x, c]
