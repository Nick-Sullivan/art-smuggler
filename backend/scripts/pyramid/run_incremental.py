import cProfile
import pstats

import numpy as np

from all_things_ones.blob import detect_blobs, tessellate_blob, visualise_blobs
from all_things_ones.core import (
    combine_images,
    darken_image_pct,
    low_pass_filter,
    resize_image,
)
from all_things_ones.files import SaveType, clear_files, load_image, save_image

target_file = "data/input/target/cats_chair.png"
img_size = 1000
num_images = 3
max_brightness = 1


def main():
    # Load the image
    # Split it into X layers
    # Apply low pass filtering on each layer
    # For each layer:
    #  - Do blob detection
    #  - For each blob:
    #    - Grow: Put a larger blob onto a canvas
    #    - OR Tesselate: Duplicate and rotate the blog around the center
    #    - OR spatial split: Split into smaller blobs
    #    - OR colour split: Split into different colour channels
    #    - Then apply correction on the other canvas
    #
    clear_files()
    target_img = load_image(target_file)
    target_img = resize_image(target_img, (img_size, img_size, 3))
    canvases = [
        np.ones((img_size, img_size, 3), dtype=np.float32) for _ in range(num_images)
    ]

    sigma_values = [80, 40, 20, 15, 10, 6, 4, 2, 1, 0]
    for i, sigma in enumerate(sigma_values):
        target_img, canvases = apply_thing(
            target_img,
            canvases,
            sigma,
            exclude_zero_pixels=False,
        )


def apply_thing(
    target_img: np.ndarray,
    canvases: list[np.ndarray],
    sigma: int,
    exclude_zero_pixels: bool,
) -> tuple[np.ndarray, list[np.ndarray]]:
    prefix = f"{sigma:02d}_"
    global max_brightness
    banned_idx = 0
    blurred_img = low_pass_filter(target_img, sigma=sigma)

    combined_img = combine_images(canvases)
    inc_target_img = combined_img.copy()
    diff = blurred_img - combined_img
    # save_image(diff, f"{prefix}filter_diff.png", image_type=SaveType.DEBUG)
    diff_normalized = (diff - diff.min()) / (diff.max() - diff.min())
    save_image(diff_normalized, f"{prefix}filter_diff.png", image_type=SaveType.DEBUG)

    labels, blobs = detect_blobs(diff, exclude_zero_pixels=exclude_zero_pixels)
    num_blobs = len(blobs)
    blob_img = visualise_blobs(labels, blobs)
    save_image(blob_img, f"{prefix}blob_img.png", image_type=SaveType.DEBUG)

    for i, blob in enumerate(blobs):
        print(f"Processing blob {i + 1}/{num_blobs}")

        # Place the blob onto the incremental target
        inc_target_img[blob.mask] = blurred_img[blob.mask]

        # Tessellate the blob
        tessellations = tessellate_blob(blob, blurred_img, num_blobs=2)

        # Apply to all canvases
        for j, (colors, rotated_y, rotated_x) in enumerate(tessellations):
            for idx in range(len(canvases)):
                ratio = 0.6 if j == 0 else 0.1
                canvases[idx][rotated_y, rotated_x] = (
                    canvases[idx][rotated_y, rotated_x] * (1 - ratio) + colors * ratio
                )
        # Apply correction on the other canvas
        done = False
        j = 0
        canvas_idx = 0
        banned_idx = banned_idx + 1 if banned_idx + 1 < len(canvases) else 0
        while not done:
            j += 1
            combined = combine_images(canvases)
            img_diff = inc_target_img - combined
            next_idx_picked = False
            while not next_idx_picked:
                canvas_idx = canvas_idx + 1 if canvas_idx + 1 < len(canvases) else 0
                if canvas_idx == banned_idx:
                    continue
                next_idx_picked = True

            canvases[canvas_idx] += img_diff * 0.3
            # If we've hit lightness cap, darken the target image
            if canvases[canvas_idx].max() > 1.0:
                canvases[canvas_idx] = np.clip(canvases[canvas_idx], 0, 1)
                max_brightness *= 0.9
                inc_target_img = darken_image_pct(inc_target_img, 10)
                blurred_img = darken_image_pct(blurred_img, 10)
                target_img = darken_image_pct(target_img, 10)
                print("Darkening target image, max brightness now", max_brightness)
                continue

            diff_indicator = np.round(np.abs(img_diff).max(), 3)
            if diff_indicator < 0.01:
                done = True
            if j >= 100:
                done = True

    for i, canvas in enumerate(canvases):
        save_image(canvas, f"{prefix}canvas_{i}.png", image_type=SaveType.DEBUG)
    combined = combine_images(canvases)
    save_image(combined, f"{prefix}combined.png", image_type=SaveType.DEBUG)
    save_image(inc_target_img, f"{prefix}inc_target_img.png", image_type=SaveType.DEBUG)
    save_image(blurred_img, f"{prefix}blurred_img.png", image_type=SaveType.DEBUG)
    save_image(target_img, f"{prefix}target_img.png", image_type=SaveType.DEBUG)
    return target_img, canvases


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    profiler.dump_stats("profile_results.prof")
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)
