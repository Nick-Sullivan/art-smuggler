import io

import cv2
import numpy as np
from PIL import Image


def save_image_to_bytes(image: np.ndarray, format: str = "PNG") -> bytes:
    image_uint8 = (image * 255).astype(np.uint8)
    image_rgba = cv2.cvtColor(image_uint8, cv2.COLOR_BGRA2RGBA)
    pil_image = Image.fromarray(image_rgba, mode="RGBA")
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()
