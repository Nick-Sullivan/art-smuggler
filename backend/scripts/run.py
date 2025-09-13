import numpy as np

from all_things_ones.core.brighten_image import brighten_image
from all_things_ones.core.combine_images import combine_images
from all_things_ones.core.darken_image import darken_image
from all_things_ones.core.resize_image import resize_image
from all_things_ones.core.shatter_image import shatter_image
from all_things_ones.files.clear_files import clear_files
from all_things_ones.files.load_image import load_image
from all_things_ones.files.save_image import SaveType, save_image

target_file = "data/input/target/cats0250.png"
seed_folder = "data/input/seed"
seed = 1
num_images = 4
num_pieces = 500


def main():
    # Crack the image into different images

    clear_files()
    target_img = load_image(target_file)
    target_img = darken_image(target_img, max_brightness=0.4)
    fragment_pos = shatter_image(
        target_img,
        num_pieces=num_pieces,
        num_images=num_images,
        seed=seed,
        background_color=0.3,
    )
    for i, piece in enumerate(fragment_pos):
        save_image(piece, f"shattered_piece_{i:02d}.png", image_type=SaveType.SPLIT)

    # Fill in the partial images using AI
    # (manual for now, then put in input/seed)

    # Load up the AI images
    suffix = "4"
    ai_imgs = []
    for i in range(num_images):
        ai_img = load_image(f"data/input/seed/seed_piece_{i:02d} ({suffix}).jpg")
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
    # dreamer = DeepDream()
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
        for img_i, output_img in enumerate(output_imgs):
            save_image(
                output_img,
                f"output_image_iteration_{iteration}_image_{img_i}.png",
                image_type=SaveType.DEBUG,
            )

        tolerance = 0.05
        min_increment = 0.01
        img_diff = target_img - combined
        diff_indicator = np.round(np.abs(img_diff).mean(), 3)
        diff_indicator_history.append(diff_indicator)
        if len(diff_indicator_history) >= 6 and all(
            x == diff_indicator_history[-1] for x in diff_indicator_history[-6:]
        ):
            print("No improvement in last 5 iterations, stopping")
            break
        print(f"Iteration {iteration}, diff indicator: {diff_indicator}")
        img_diff_pos = img_diff.clip(min=0)
        img_diff_neg = img_diff.clip(max=0)
        fragments_pos = shatter_image(
            img_diff_pos,
            num_pieces=num_pieces,
            num_images=num_images,
            seed=iteration // 5,
            background_color=0,
        )
        fragments_neg = shatter_image(
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

        # Option 2: pixel by pixel
        # for color in range(3):
        #     for row in range(target_img.shape[0]):
        #         for col in range(target_img.shape[1]):
        #             # combined_pixel = combined[row, col, color]
        #             # target_pixel = target_img[row, col, color]
        #             # diff = target_pixel - combined_pixel
        #             diff = img_diff[row, col, color]
        #             increment = max(min_increment, abs(diff) / 2)
        #             # too dark
        #             if diff > tolerance:
        #                 needs_iteration = True
        #                 # pick an image to give it to
        #                 pool = [
        #                     i
        #                     for i in range(num_images)
        #                     if output_imgs[i][row, col, color] < 1.0
        #                 ]
        #                 if len(pool) == 0:
        #                     print(
        #                         "Hit max brightness, make target darker, or ai brighter"
        #                     )
        #                     return
        #                 img_i = np.random.choice(pool)
        #                 val = output_imgs[img_i][row, col, color]
        #                 output_imgs[img_i][row, col, color] = min(1, val + increment)
        #             # too bright
        #             elif diff < -tolerance:
        #                 needs_iteration = True
        #                 pool = [
        #                     i
        #                     for i in range(num_images)
        #                     if output_imgs[i][row, col, color] > 0.0
        #                 ]
        #                 if len(pool) == 0:
        #                     print("Hit min brightness")
        #                 img_i = np.random.choice(pool)
        #                 val = output_imgs[img_i][row, col, color]
        #                 output_imgs[img_i][row, col, color] = max(0, val - increment)

        # # Apply deep dream
        # for i in range(num_images):
        #     output_imgs[i] = dreamer.apply_deep_dream(
        #         output_imgs[i], iterations=100, lr=0.01
        #     )
        #     output_imgs[i] = np.clip(output_imgs[i], 0, 1)
        #     save_image(
        #         output_imgs[i],
        #         f"output_image_iteration_{iteration}_image_{i}_deepdream.png",
        #         image_type=SaveType.DEBUG,
        #     )

    combined = combine_images(output_imgs)
    save_image(
        combined,
        f"output_image_iteration_{iteration + 1}_combined.png",
        image_type=SaveType.DEBUG,
    )
    for img_i, output_img in enumerate(output_imgs):
        save_image(
            output_img,
            f"output_image_iteration_{iteration + 1}_image_{img_i}.png",
            image_type=SaveType.DEBUG,
        )
    print("FINISHED")

    # For each image, take the diff and
    # seeds = load_images(seed_folder)
    # for seed in seeds:
    #     clear_files()
    #     img = load_image(target_file)
    #     seed = resize_image(seed, img.shape)
    #     images = split_image(img, seed=seed)
    #     for i, img in enumerate(images):
    #         save_image(img, f"cat_{i + 1}.png", image_type=SaveType.SPLIT)

    #     combined = combine_images(images)
    #     save_image(combined, "combined.png", image_type=SaveType.RECOMBINED)
    #     subprocess.run(["code", "--wait", "data/output/split/cat_2.png"])


if __name__ == "__main__":
    main()
