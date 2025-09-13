import numpy as np

from ..files.save_image import SaveType, save_image
from .brighten_image import brighten_image
from .create_image import create_image
from .create_paired_image import create_paired_image
from .darken_image import darken_image
from .trim_colour_to_fit import trim_colour_to_fit


def split_image(target: np.ndarray, seed: np.ndarray = None) -> list[np.ndarray]:
    height, width, channels = target.shape

    save_image(target, "00_target.png", image_type=SaveType.DEBUG)

    # Darken input image to ensure we can create patterns that multiply to it
    target = darken_image(target, max_brightness=0.7)
    save_image(target, "01_dark.png", image_type=SaveType.DEBUG)

    # Create a random pattern as primary
    if seed is not None:
        primary = seed
    else:
        primary = create_image(height, width)

    # Brighten seed image to ensure it has enough brightness to create the target
    save_image(primary, "02_primary.png", image_type=SaveType.DEBUG)
    primary = brighten_image(primary, min_brightness=0.1)
    save_image(primary, "03_primary_bright.png", image_type=SaveType.DEBUG)

    # Adjust primary to fit in boundaries
    trim_colour_to_fit(primary, target)
    save_image(primary, "04_trimmed.png", image_type=SaveType.DEBUG)

    # Create secondary so it can produce the target image
    secondary = create_paired_image(primary, target)
    save_image(secondary, "05_pair.png", image_type=SaveType.DEBUG)

    # Iterate with smoothing and patterns

    #
    # output_images = create_patterns(height, width, num_images)
    # adjust_values_to_target(output_images, target_image)

    return [primary, secondary]
