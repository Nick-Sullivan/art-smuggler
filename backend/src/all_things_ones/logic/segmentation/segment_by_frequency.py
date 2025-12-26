import numpy as np

from all_things_ones.logic.core import low_pass_filter
from all_things_ones.repository.files import SaveType, save_image


def segment_by_frequency(target_img, canvases, num_images: int, img_size: int):
    masks = [np.ones((img_size, img_size), dtype=np.bool) for _ in range(num_images)]

    sigma = 0
    sigma_increment = 1
    diff_threshold = 0.05
    mask_threshold = 100.0 / (num_images + 2)
    print(f"Mask threshold: {mask_threshold:.2f}%")
    prev_img = target_img

    for i in range(num_images - 1):
        cum_mask = ~np.any(np.array(masks[:i]), axis=0)
        mask_pct = 0
        prev_mask_pct = 0
        while mask_pct < mask_threshold:
            filtered_img = low_pass_filter(target_img, sigma=sigma)
            diff = filtered_img - prev_img
            mask = np.max(np.abs(diff), axis=2) >= diff_threshold
            mask &= cum_mask
            mask_pct = calculate_pct_masked(mask, img_size)
            print(f"Image {i} sigma {sigma} mask percentage: {mask_pct:.2f}%")
            delta = mask_pct - prev_mask_pct
            if delta < 1:
                sigma_increment += 1
            elif delta > 2:
                sigma_increment = max(1, sigma_increment - 1)
            sigma += sigma_increment
            prev_mask_pct = mask_pct
        masks[i] = mask
        prev_img = filtered_img
        save_image(filtered_img, f"filtered_{i}.png", image_type=SaveType.DEBUG)

    # Editing in place
    masks[-1] = ~np.any(np.array(masks[:-1]), axis=0)
    for i in range(num_images):
        canvases[i][masks[i], :3] = target_img[masks[i]]
        canvases[i][masks[i], 3] = 1.0

    # create a transparent image, that is black where trans_mask is true
    # Ctrl click the box of the mask layer (selects all), click the fill layer, Layer -> Raster Mask -> Hide selection
    trans_images = []
    for i in range(1, num_images - 1):
        mask = np.any(np.array(masks[:i]), axis=0)
        trans_img = np.ones((img_size, img_size, 4), dtype=np.float32)
        trans_img[~mask, 3] = 0
        trans_images.append(trans_img)
        save_image(trans_img, f"trans_mask_{i}.png", image_type=SaveType.DEBUG)
    return trans_images


def calculate_pct_transparent(canvas, img_size: int):
    return (canvas[:, :, 3] == 0).sum() / (img_size * img_size) * 100


def calculate_pct_masked(mask, img_size: int):
    return np.sum(mask) / (img_size * img_size) * 100
