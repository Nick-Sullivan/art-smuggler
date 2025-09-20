import cProfile
import pstats
import time

import numpy as np

from all_things_ones.core.adjust_image_brightness import adjust_image_brightness
from all_things_ones.core.brighten_image import brighten_image
from all_things_ones.core.combine_images import combine_images
from all_things_ones.core.resize_image import resize_image
from all_things_ones.files.clear_files import clear_files
from all_things_ones.files.load_image import load_image
from all_things_ones.files.save_image import SaveType, save_image
from all_things_ones.shatter.shatter_image_with_cache import shatter_image_with_cache

target_file = "data/input/target/london.png"
seed_folder = "data/input/seed/005_london"
seed = 1
seed_suffix = "2"
num_images = 4
num_pieces = 500
img_size = 2000


def main():
    # Crack the image into different images
    start_time = time.time()

    clear_files()
    target_img = load_image(target_file)
    target_img = resize_image(target_img, (img_size, img_size, 3))
    fragment_pos = shatter_image_with_cache(
        target_img,
        num_pieces=num_pieces,
        num_images=num_images,
        seed=seed,
        background_color=1,
    )
    for i, piece in enumerate(fragment_pos):
        save_image(piece, f"shattered_piece_{i:02d}.png", image_type=SaveType.SPLIT)

    # Fill in the partial images using AI
    # (manual for now, then put in input/seed)
    target_img = adjust_image_brightness(target_img, min_=0.2, max_=0.8)

    # Load up the AI images
    ai_imgs = []
    for i in range(num_images):
        ai_img = load_image(
            f"{seed_folder}/shattered_piece_{i:02d}_gen_{seed_suffix}.jpg"
        )
        ai_img = resize_image(ai_img, target_img.shape)
        save_image(
            ai_img,
            "ai_img_before.png",
            image_type=SaveType.DEBUG,
        )
        ai_img = brighten_image(ai_img, min_brightness=0.4)
        save_image(
            ai_img,
            "ai_img_after.png",
            image_type=SaveType.DEBUG,
        )
        ai_imgs.append(ai_img)

    # Make a copy of the AI image to be edited
    output_imgs = []
    for img in [ai_imgs[0], ai_imgs[1], ai_imgs[2], ai_imgs[3]]:
        output_img = np.copy(img)
        output_imgs.append(output_img)

    # Incrementally adjust each image to get closer to the target
    iteration = 0
    needs_iteration = True
    diff_indicator_history = []
    while needs_iteration:
        iteration += 1
        needs_iteration = False
        combined = combine_images(output_imgs)
        save_image(
            combined,
            f"output_image_iteration_{iteration}_combined.png",
            image_type=SaveType.DEBUG,
        )
        # for img_i, output_img in enumerate(output_imgs):
        #     save_image(
        #         output_img,
        #         f"output_image_iteration_{iteration}_image_{img_i}.png",
        #         image_type=SaveType.DEBUG,
        #     )

        tolerance = 0.05
        min_increment = 0.01
        img_diff = target_img - combined
        diff_indicator = np.round(np.abs(img_diff).mean(), 3)
        diff_indicator_history.append(diff_indicator)
        if len(diff_indicator_history) >= 11 and all(
            x == diff_indicator_history[-1] for x in diff_indicator_history[-11:]
        ):
            print("No improvement in last 11 iterations, stopping")
            break
        print(
            f"Iteration {iteration}, diff: {diff_indicator: .3f}, time: {time.time() - start_time:.2f}s"
        )
        start_time = time.time()
        img_diff_pos = img_diff.clip(min=0)
        img_diff_neg = img_diff.clip(max=0)
        fragments_pos = shatter_image_with_cache(
            img_diff_pos,
            num_pieces=num_pieces,
            num_images=num_images,
            seed=iteration // 5,
            background_color=0,
        )
        fragments_neg = shatter_image_with_cache(
            img_diff_neg,
            num_pieces=num_pieces,
            num_images=num_images,
            seed=100 * (iteration // 5),
            background_color=1,
        )

        # Option 1: fragment by fragment
        for i in range(num_images):
            fragment_pos = fragments_pos[i]
            fragment_neg = fragments_neg[i]
            # too dark
            pos_indices = np.where(fragment_pos > tolerance)
            if len(pos_indices[0]) > 0:
                needs_iteration = True
                increment = np.maximum(
                    min_increment, np.abs(fragment_pos[pos_indices]) / 2
                )
                output_imgs[i][pos_indices] += increment
                output_imgs[i] = np.clip(output_imgs[i], 0, 1)
            # too bright
            neg_indices = np.where(fragment_neg < -tolerance)
            if len(neg_indices[0]) > 0:
                needs_iteration = True
                decrement = np.maximum(
                    min_increment, np.abs(fragment_neg[neg_indices]) / 2
                )
                output_imgs[i][neg_indices] -= decrement
                output_imgs[i] = np.clip(output_imgs[i], 0, 1)

    combined = combine_images(output_imgs)
    save_image(
        combined,
        "output_combined.png",
        image_type=SaveType.SPLIT,
    )
    for img_i, output_img in enumerate(output_imgs):
        save_image(
            output_img,
            f"output_image_{img_i}.png",
            image_type=SaveType.SPLIT,
        )
    print("FINISHED")


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    profiler.dump_stats("profile_results.prof")
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)

    # 404 sec
    # 390 sec with np vector
    # 50 sec with scipy
    # 48 sec
    # Then run snakeviz profile_results.prof --server --port 8080 --hostname 0.0.0.0
    # Then open http://localhost:8080/snakeviz/profile_results.prof
