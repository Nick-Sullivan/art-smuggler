import numpy as np

from all_things_ones.core import (
    resize_image,
)
from all_things_ones.files import SaveType, clear_files, load_image, save_image
from all_things_ones.inpainting import inpaint
from all_things_ones.segmentation import segment_by_frequency

target_file = "data/input/target/mish.png"
num_images = 4
num_pieces = 500
img_size = 2000


def main():
    # Split the image into different frequencies
    clear_files()
    target_img = load_image(target_file)
    target_img = resize_image(target_img, (img_size, img_size, 3))
    canvases = [
        np.zeros((img_size, img_size, 4), dtype=np.float32) for _ in range(num_images)
    ]
    trans_images = segment_by_frequency(target_img, canvases, num_images, img_size)
    for i, canvas in enumerate(canvases):
        save_image(canvas, f"canvas_{i}.png", image_type=SaveType.DEBUG)

    inpaint(canvases, trans_images, num_images, img_size)


if __name__ == "__main__":
    # profiler = cProfile.Profile()
    # profiler.enable()

    main()

    # profiler.disable()``
    # profiler.dump_stats("profile_results.prof")
    # stats = pstats.Stats(profiler)
    # stats.sort_stats("cumulative")
    # stats.print_stats(10)
    # Then run snakeviz profile_results.prof --server --port 8080 --hostname 0.0.0.0

    # Ctrl click trans mask
    # Select fill layer
    # Layer -> Raster Mask -> Hide selection
