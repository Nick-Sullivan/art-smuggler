from pathlib import Path

import numpy as np

from all_things_ones.core.add_corner_mark import add_corner_mark
from all_things_ones.files.load_image import load_image
from all_things_ones.files.save_image import SaveType, save_image

CIRCLE_SIZE = 250
MARGIN = 10
OPACITY = 0.8


def main():
    folder = Path("data/output/split")
    files = [
        "output_image_0.png",
        "output_image_1.png",
        "output_image_2.png",
        "output_image_3.png",
    ]

    sample_img = load_image(folder / files[0])
    white_img = np.ones_like(sample_img)
    base_img = add_corner_mark(
        white_img,
        segment_index=0,
        total_segments=len(files) + 1,
        circle_size=CIRCLE_SIZE,
        margin=MARGIN,
        opacity=OPACITY,
    )

    save_image(base_img, "output_image_marked_base.png", image_type=SaveType.SPLIT)
    for i, file in enumerate(files):
        img = load_image(folder / file)
        marked_img = add_corner_mark(
            img,
            segment_index=i + 1,
            total_segments=len(files) + 1,
            circle_size=CIRCLE_SIZE,
            margin=MARGIN,
            opacity=OPACITY,
        )
        output_path = file.replace("image_", "image_marked_")
        save_image(marked_img, output_path, image_type=SaveType.SPLIT)


if __name__ == "__main__":
    main()
