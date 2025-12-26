import numpy as np


def combine_images(images: list[np.ndarray]) -> np.ndarray:
    """
    Combine images according to light.

    Say you stack:
        Cyan: R=0, G=1, B=1
        Magenta: R=1, G=0, B=1
        Resulting transmission:
        R = 0 × 1 = 0
        G = 1 × 0 = 0
        B = 1 × 1 = 1
        So the final light that passes through is pure blue → RGB: (0, 0, 255)
    """
    if not images:
        raise ValueError("No images to combine")
    return np.prod(images, axis=0)
