import os

import numpy as np
from PIL import Image


def main():
    # Recombine the 3 split images
    recombine_images()

    print("\nRecombined image saved to data/output/recombined/")


def recombine_images():
    """Recombine the 3 split images back into one image"""

    # Create output directory
    os.makedirs("data/output/recombined", exist_ok=True)

    # Load the 3 split images
    print("Loading split images...")
    image_paths = [
        "data/output/split/image_1.png",
        "data/output/split/image_2.png",
        "data/output/split/image_3.png",
    ]

    # Check if all images exist
    for path in image_paths:
        if not os.path.exists(path):
            print(f"Error: {path} not found!")
            return

    # Load images
    images = []
    for path in image_paths:
        img = Image.open(path)
        print(f"Loaded {path}: {img.size}")
        images.append(img)

    # All images should be the same size
    width, height = images[0].size

    # Verify all images are the same size
    for i, img in enumerate(images):
        if img.size != (width, height):
            print(f"Error: Image {i + 1} has different size: {img.size}")
            return

    print(f"Combining images of size: {width} x {height}")

    # Create output image
    combined = Image.new("RGB", (width, height), "white")

    # Convert images to numpy arrays for easier manipulation
    img_arrays = [np.array(img) for img in images]
    combined_array = np.array(combined)

    print("Recombining pixels...")

    # Method 1: Simple overlay - non-white pixels from each image
    for img_array in img_arrays:
        # Create mask for non-white pixels
        mask = ~np.all(img_array == [255, 255, 255], axis=2)

        # Copy non-white pixels to combined image
        combined_array[mask] = img_array[mask]

    # Convert back to PIL Image and save
    result = Image.fromarray(combined_array)
    save_path = "data/output/recombined/recombined_overlay.png"
    result.save(save_path)
    print(f"Overlay method saved to: {save_path}")

    # Method 2: Alpha blending - blend all 3 images equally
    print("Creating alpha blend version...")
    combined_blend = np.zeros_like(img_arrays[0], dtype=np.float64)

    for img_array in img_arrays:
        combined_blend += img_array.astype(np.float64) / 3.0

    # Convert back to uint8
    combined_blend = np.clip(combined_blend, 0, 255).astype(np.uint8)
    result_blend = Image.fromarray(combined_blend)
    save_path_blend = "data/output/recombined/recombined_blend.png"
    result_blend.save(save_path_blend)
    print(f"Blend method saved to: {save_path_blend}")

    # Method 3: Priority overlay - later images have priority
    print("Creating priority overlay version...")
    combined_priority = np.array(images[0])  # Start with image 1

    for img_array in img_arrays[1:]:
        # Create mask for non-white pixels
        mask = ~np.all(img_array == [255, 255, 255], axis=2)

        # Overlay non-white pixels (later images have priority)
        combined_priority[mask] = img_array[mask]

    result_priority = Image.fromarray(combined_priority)
    save_path_priority = "data/output/recombined/recombined_priority.png"
    result_priority.save(save_path_priority)
    print(f"Priority method saved to: {save_path_priority}")


if __name__ == "__main__":
    main()
