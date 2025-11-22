from pathlib import Path

from all_things_ones.core import add_corner_mark
from all_things_ones.files import SaveType, load_image, save_image

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

    for i, file in enumerate(files):
        img = load_image(folder / file)
        marked_img = add_corner_mark(
            img,
            segment_index=i,
            total_segments=len(files),
            size=CIRCLE_SIZE,
            margin=MARGIN,
            opacity=OPACITY,
        )
        output_path = file.replace("image_", "image_marked_")
        save_image(marked_img, output_path, image_type=SaveType.SPLIT)


if __name__ == "__main__":
    main()
