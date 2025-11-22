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
    max_brightness = 1.0
    banned_idx = 0
    clear_files()
    target_img = load_image(target_file)
    target_img = resize_image(target_img, (img_size, img_size, 3))
    blurred_img = low_pass_filter(target_img, sigma=80)
    save_image(blurred_img, f"blurred_img_{80:02d}.png", image_type=SaveType.DEBUG)

    inc_target_img = np.ones((img_size, img_size, 3), dtype=np.float32)
    canvases = [
        np.ones((img_size, img_size, 3), dtype=np.float32) for _ in range(num_images)
    ]

    labels, blobs = detect_blobs(blurred_img)
    num_blobs = len(blobs)
    blob_img = visualise_blobs(labels, blobs)
    save_image(blob_img, "blob_img.png", image_type=SaveType.DEBUG)

    print(f"Detected {num_blobs} blobs")
    for i, blob in enumerate(blobs):
        if i < 0:
            continue
        print(f"Processing blob {i + 1}/{num_blobs}")

        # Place the blob onto the incremental target
        inc_target_img[blob.mask] = blurred_img[blob.mask]
        # save_image(
        #     inc_target_img,
        #     f"target_img_{i:02d}.png",
        #     image_type=SaveType.DEBUG,
        # )

        # Tessellate the blob
        tessellations = tessellate_blob(blob, blurred_img, num_blobs=2)
        # Apply to all canvases
        for j, (colors, rotated_y, rotated_x) in enumerate(tessellations):
            for idx in range(len(canvases)):
                ratio = 0.6 if j == 0 else 0.1
                canvases[idx][rotated_y, rotated_x] = (
                    canvases[idx][rotated_y, rotated_x] * (1 - ratio) + colors * ratio
                )

        # # Work out which canvas makes bright pixels darker, or dark pixels brighter
        # scores = []
        # for idx in range(0, len(canvases)):
        #     potential_img = canvases[idx].copy()
        #     for colors, rotated_y, rotated_x in tessellations:
        #         potential_img[rotated_y, rotated_x] = colors
        #     img_diff = potential_img - canvases[idx]

        #     # Create a score thats good if its making dark pixels brighter, or bright pixels darker
        #     mask_brighter = img_diff > 0
        #     mask_darker = img_diff < 0
        #     score_brighter = -np.sum(potential_img[mask_brighter])
        #     score_darker = np.sum(potential_img[mask_darker])
        #     score = score_brighter + score_darker
        #     scores.append(
        #         {"canvas_idx": idx, "score": score, "potential_img": potential_img}
        #     )
        # best_canvas = min(scores, key=lambda x: x["score"])
        # canvas_idx = best_canvas["canvas_idx"]
        # print("Applying blob to canvas ", canvas_idx)
        # # Apply the tessellation to the chosen canvas
        # canvases[canvas_idx] = best_canvas["potential_img"]

        # for j, (colors, rotated_y, rotated_x) in enumerate(tessellations):
        #     ratio = 0.7 if j == 0 else 0.3
        #     canvases[0][rotated_y, rotated_x] = (
        #         canvases[0][rotated_y, rotated_x] * (1 - ratio) + colors * ratio
        #     )

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
            #     image_type=SaveType.DEBUG,
            # )
            img_diff = inc_target_img - combined
            next_idx_picked = False
            while not next_idx_picked:
                canvas_idx = canvas_idx + 1 if canvas_idx + 1 < len(canvases) else 0
                if canvas_idx == banned_idx:
                    continue
                next_idx_picked = True
            # # Work out which canvas makes bright pixels darker, or dark pixels brighter
            # mask_brighter = img_diff > 0
            # mask_darker = img_diff < 0
            # best_score = -float("inf")
            # canvas_idx = 1
            # for idx in range(1, len(canvases)):
            #     # Create a score thats good if its making dark pixels brighter, or bright pixels darker
            #     potential = canvases[idx] + img_diff
            #     score_brighter = -np.sum(potential[mask_brighter])
            #     score_darker = np.sum(potential[mask_darker])
            #     score = score_brighter + score_darker
            #     if score > best_score:
            #         best_score = score
            #         canvas_idx = idx

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
            #     image_type=SaveType.DEBUG,
            # )
            diff_indicator = np.round(np.abs(img_diff).max(), 3)
            if diff_indicator < 0.01:
                done = True
                # for k, canvas in enumerate(canvases):
                #     save_image(
                #         canvas, f"canvas_{i:02d}_{k:02d}.png", image_type=SaveType.DEBUG
                #     )
            if j >= 100:
                done = True

        if i >= 44:
            break

    for i, canvas in enumerate(canvases):
        save_image(canvas, f"canvas_{i}.png", image_type=SaveType.DEBUG)
    combined = combine_images(canvases)
    save_image(combined, "combined_final.png", image_type=SaveType.DEBUG)
    save_image(inc_target_img, "target_img_final.png", image_type=SaveType.DEBUG)
    save_image(blurred_img, "blurred_img_final.png", image_type=SaveType.DEBUG)
    save_image(target_img, "orig_target_final.png", image_type=SaveType.DEBUG)


if __name__ == "__main__":
    main()
