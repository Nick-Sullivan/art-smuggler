import numpy as np

from .brighten_image import brighten_image
from .create_image import create_image
from .create_paired_image import create_paired_image
from .darken_image import darken_image
from .trim_colour_to_fit import trim_colour_to_fit


def split_image(target: np.ndarray, seed: np.ndarray = None) -> list[np.ndarray]:
    height, width, channels = target.shape

    # Darken input image to ensure we can create patterns that multiply to it
    target = darken_image(target, max_brightness=0.7)

    # Create a random pattern as primary
    if seed is not None:
        primary = seed
    else:
        primary = create_image(height, width)

    # Brighten seed image to ensure it has enough brightness to create the target
    primary = brighten_image(primary, min_brightness=0.1)

    # Adjust primary to fit in boundaries
    trim_colour_to_fit(primary, target)

    # Create secondary so it can produce the target image
    secondary = create_paired_image(primary, target)

    # Iterate with smoothing and patterns
    return [primary, secondary]
