import io

import numpy as np
from PIL import Image


def save_image_to_bytes(image: np.ndarray, format: str = "PNG") -> bytes:
    image_uint8 = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    pil_image = Image.fromarray(image_uint8)
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()
