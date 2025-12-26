import base64
from typing import AsyncGenerator

import numpy as np
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from all_things_ones.logic.conversion import load_image_from_bytes, save_image_to_bytes
from all_things_ones.logic.core import combine_layers_by_transparency, resize_image
from all_things_ones.logic.events import (
    create_complete_message,
    create_error_message,
    create_image_message,
    create_status_message,
)
from all_things_ones.logic.inpainting import inpaint
from all_things_ones.logic.segmentation import segment_by_frequency
from all_things_ones.repository.files import SaveType, save_image

router = APIRouter()


@router.post("/process-image")
async def process_image(
    target_file: UploadFile = File(..., description="Target image to process"),
    num_images: int = Form(4, description="Number of output images"),
    img_size: int = Form(2000, description="Output image size (square)"),
):
    target_bytes = await target_file.read()
    return StreamingResponse(
        process_with_sse(target_bytes, num_images, img_size),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def process_with_sse(
    target_bytes: bytes,
    num_images: int,
    img_size: int,
) -> AsyncGenerator[str, None]:
    try:
        yield create_status_message("Loading image...")
        target_img = load_image_from_bytes(target_bytes)
        save_image(target_img, "target_img.png", image_type=SaveType.DEBUG)

        target_img = resize_image(target_img, (img_size, img_size, 3))
        save_image(target_img, "target_img_resized.png", image_type=SaveType.DEBUG)
        yield create_status_message(f"Image loaded with shape {target_img.shape}")

        yield create_status_message("Creating canvases")
        canvases = [
            np.zeros((img_size, img_size, 4), dtype=np.float32)
            for _ in range(num_images)
        ]

        yield create_status_message("Segmenting image by frequency")

        trans_images = []
        for trans_img in segment_by_frequency(
            target_img, canvases, num_images, img_size
        ):
            trans_images.append(trans_img)
            index = len(trans_images) - 1
            image_bytes = save_image_to_bytes(canvases[index], format="PNG")
            img_base64 = base64.b64encode(image_bytes).decode("utf-8")
            yield create_image_message(img_base64, index=index)

        yield create_status_message("Inpainting images")
        for i, layer in enumerate(
            inpaint(canvases, trans_images, num_images, img_size)
        ):
            image_bytes = save_image_to_bytes(layer, format="PNG")
            img_base64 = base64.b64encode(image_bytes).decode("utf-8")
            yield create_image_message(img_base64, index=i)

        combined = combine_layers_by_transparency(canvases)
        save_image(combined, "combined_image.png", image_type=SaveType.DEBUG)

        yield create_complete_message("Processing complete")

    except Exception as e:
        print(e)
        yield create_error_message(str(e))
