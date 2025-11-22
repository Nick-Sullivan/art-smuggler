import numpy as np

from all_things_ones.blob import detect_blobs, tessellate_blob, visualise_blobs
from all_things_ones.core import (
    combine_images,
    low_pass_filter,
)
from all_things_ones.core.darken_image import darken_image_pct
from all_things_ones.files import SaveType, clear_files, load_image, save_image

target_file = "data/output/debug/orig_target_final.png"
num_images = 3
canvas_files = [f"data/output/debug/canvas_{i}.png" for i in range(num_images)]
img_size = 1000


def main():
    # Load the image
    # Create a diff
    #
    clear_files(["data/output/debug2"])
    banned_idx = 0
    max_brightness = 1.0
    target_img = load_image(target_file)
    blurred_img = low_pass_filter(target_img, sigma=10)
    canvases = [load_image(f) for f in canvas_files]
    combined_img = combine_images(canvases)
    diff = blurred_img - combined_img
    inc_target_img = combined_img.copy()
    save_image(blurred_img, "blurred_img_10.png", image_type=SaveType.DEBUG2)
    save_image(diff, "filter_diff.png", image_type=SaveType.DEBUG2)

    labels, blobs = detect_blobs(diff)
    num_blobs = len(blobs)
    blob_img = visualise_blobs(labels, blobs)
    save_image(blob_img, "blob_img_10.png", image_type=SaveType.DEBUG2)
    print(f"Detected {num_blobs} blobs")
    for i, blob in enumerate(blobs):
        print(f"Processing blob {i + 1}/{num_blobs}")

        inc_target_img[blob.mask] = blurred_img[blob.mask]
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
            # save_image(
            #     combined,
            #     f"combined_blob_{i:02d}_{j:02d}.png",
            #     image_type=SaveType.DEBUG2,
            # )
            img_diff = inc_target_img - combined
            next_idx_picked = False
            while not next_idx_picked:
                canvas_idx = canvas_idx + 1 if canvas_idx + 1 < len(canvases) else 0
                if canvas_idx == banned_idx:
                    continue
                next_idx_picked = True

            canvases[canvas_idx] += img_diff * 0.1
            # If we've hit lightness cap, darken the target image
            if canvases[canvas_idx].max() > 1.0:
                canvases[canvas_idx] = np.clip(canvases[canvas_idx], 0, 1)
                max_brightness *= 0.9
                inc_target_img = darken_image_pct(inc_target_img, 10)
                blurred_img = darken_image_pct(blurred_img, 10)
                target_img = darken_image_pct(target_img, 10)
                print("Darkening target image, max brightness now", max_brightness)
                continue

            # save_image(
            #     inc_target_img,
            #     f"target_img_{i:02d}_{j:02d}.png",
            #     image_type=SaveType.DEBUG2,
            # )
            diff_indicator = np.round(np.abs(img_diff).max(), 3)
            if diff_indicator < 0.01:
                done = True
                for k, canvas in enumerate(canvases):
                    save_image(
                        canvas,
                        f"canvas_{i:02d}_{k:02d}.png",
                        image_type=SaveType.DEBUG2,
                    )
            if j >= 100:
                done = True

        if i >= 43:
            break

    for i, canvas in enumerate(canvases):
        save_image(canvas, f"canvas_{i}.png", image_type=SaveType.DEBUG2)
    combined = combine_images(canvases)
    save_image(combined, "combined_final.png", image_type=SaveType.DEBUG2)
    save_image(inc_target_img, "target_img_final.png", image_type=SaveType.DEBUG2)
    save_image(blurred_img, "blurred_img_final.png", image_type=SaveType.DEBUG2)
    save_image(target_img, "orig_target_final.png", image_type=SaveType.DEBUG2)


if __name__ == "__main__":
    main()
