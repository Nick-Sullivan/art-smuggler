import io

import numpy as np
from PIL import Image


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Load image from bytes and convert to float32 numpy array"""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Convert to numpy array
    image_array = np.array(image).astype(np.float32) / 255.0

    # Convert RGB to BGR for OpenCV compatibility
    image_bgr = image_array[:, :, ::-1]

    return image_bgr
