import os
import random

import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi


def main():
    # Fill white parts of all split images
    input_dir = "data/output/svg_split"
    output_dir = "data/output/svg_filled"

    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} not found. Please run split_svg.py first.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Process all PNG files in the split directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".png"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            print(f"Processing {filename}...")
            fill_with_tessellation(input_path, output_path)
            print(f"Saved filled image to {output_path}")

    print("\nFilling complete!")
    print(f"Filled images saved to {output_dir}/")


def generate_bright_colors(num_colors):
    """Generate bright, vibrant colors"""
    colors = []
    for _ in range(num_colors):
        # Generate bright colors by ensuring at least one RGB component is high
        color = [random.randint(0, 255) for _ in range(3)]
        # Ensure at least one component is bright (>200)
        if max(color) < 200:
            idx = random.randint(0, 2)
            color[idx] = random.randint(200, 255)
        colors.append(tuple(color))
    return colors


def fill_with_tessellation(input_path, output_path, white_threshold=250, density=0.001):
    """Fill white areas with random bright colors using Voronoi tessellation"""

    # Load the image
    image = Image.open(input_path)
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Create a mask for white pixels
    if len(img_array.shape) == 3:
        white_mask = np.all(img_array >= white_threshold, axis=2)
    else:
        white_mask = img_array >= white_threshold

    if not np.any(white_mask):
        print("No white pixels found to fill")
        image.save(output_path)
        return

    # Get white pixel coordinates
    white_coords = np.column_stack(np.where(white_mask))
    print(f"Found {len(white_coords)} white pixels to fill")

    # Generate random seed points within white areas
    num_seeds = max(10, int(len(white_coords) * density))
    print(f"Generating {num_seeds} tessellation seeds")

    # Sample random points from white pixels
    seed_indices = np.random.choice(
        len(white_coords), size=min(num_seeds, len(white_coords)), replace=False
    )
    seeds = white_coords[seed_indices]

    # Add boundary points to ensure complete tessellation
    boundary_seeds = [
        [0, 0],
        [0, width - 1],
        [height - 1, 0],
        [height - 1, width - 1],
        [height // 2, 0],
        [height // 2, width - 1],
        [0, width // 2],
        [height - 1, width // 2],
    ]
    seeds = np.vstack([seeds, boundary_seeds])

    # Generate bright colors for each seed
    colors = generate_bright_colors(len(seeds))

    print("Creating Voronoi tessellation...")
    # Create Voronoi diagram
    vor = Voronoi(seeds[:, [1, 0]])  # Note: Voronoi expects (x, y) format

    # Create filled image
    filled_array = img_array.copy()

    # For each white pixel, find which Voronoi region it belongs to
    print("Assigning colors to white pixels...")
    for i, white_coord in enumerate(white_coords):
        y, x = white_coord
        point = np.array([x, y])

        # Find nearest seed point
        distances = np.sum((seeds[:, [1, 0]] - point) ** 2, axis=1)
        nearest_seed_idx = np.argmin(distances)

        # Assign color
        filled_array[y, x] = colors[nearest_seed_idx]

        if i % 50000 == 0:
            print(f"  Processed {i}/{len(white_coords)} pixels")

    # Save the filled image
    filled_image = Image.fromarray(filled_array)
    filled_image.save(output_path)


def fill_with_hexagonal_tessellation(
    input_path, output_path, white_threshold=250, hex_size=50
):
    """Fill white areas with hexagonal tessellation"""

    # Load the image
    image = Image.open(input_path)
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Create a mask for white pixels
    if len(img_array.shape) == 3:
        white_mask = np.all(img_array >= white_threshold, axis=2)
    else:
        white_mask = img_array >= white_threshold

    if not np.any(white_mask):
        print("No white pixels found to fill")
        image.save(output_path)
        return

    print("Creating hexagonal tessellation...")

    # Create filled image
    filled_array = img_array.copy()

    # Generate hexagonal grid
    hex_height = hex_size * np.sqrt(3) / 2

    for row in range(0, height, int(hex_height)):
        for col in range(0, width, hex_size):
            # Offset every other row
            offset = (hex_size // 2) if (row // int(hex_height)) % 2 else 0
            hex_x = col + offset
            hex_y = row

            # Generate random bright color for this hexagon
            color = generate_bright_colors(1)[0]

            # Fill hexagon area
            for y in range(
                max(0, hex_y - hex_size // 2), min(height, hex_y + hex_size // 2)
            ):
                for x in range(
                    max(0, hex_x - hex_size // 2), min(width, hex_x + hex_size // 2)
                ):
                    if white_mask[y, x]:  # Only fill white pixels
                        # Check if point is within hexagon (simplified as circle)
                        if (x - hex_x) ** 2 + (y - hex_y) ** 2 <= (hex_size // 2) ** 2:
                            filled_array[y, x] = color

    # Save the filled image
    filled_image = Image.fromarray(filled_array)
    filled_image.save(output_path)


def fill_with_triangular_tessellation(
    input_path, output_path, white_threshold=250, triangle_size=40
):
    """Fill white areas with triangular tessellation"""

    # Load the image
    image = Image.open(input_path)
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Create a mask for white pixels
    if len(img_array.shape) == 3:
        white_mask = np.all(img_array >= white_threshold, axis=2)
    else:
        white_mask = img_array >= white_threshold

    if not np.any(white_mask):
        print("No white pixels found to fill")
        image.save(output_path)
        return

    print("Creating triangular tessellation...")

    # Create PIL image for drawing
    filled_image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(filled_image)

    # Generate triangular grid
    for row in range(0, height, triangle_size):
        for col in range(0, width, triangle_size):
            # Generate two triangles per square
            colors = generate_bright_colors(2)

            # Triangle 1: top-left
            triangle1 = [
                (col, row),
                (col + triangle_size, row),
                (col, row + triangle_size),
            ]

            # Triangle 2: bottom-right
            triangle2 = [
                (col + triangle_size, row),
                (col + triangle_size, row + triangle_size),
                (col, row + triangle_size),
            ]

            # Create mask for each triangle and only fill white areas
            for triangle, color in [(triangle1, colors[0]), (triangle2, colors[1])]:
                # Create temporary image to get triangle mask
                temp_img = Image.new("L", (width, height), 0)
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.polygon(triangle, fill=255)
                triangle_mask = np.array(temp_img) > 0

                # Only fill where both triangle and white mask are true
                fill_mask = triangle_mask & white_mask
                if np.any(fill_mask):
                    filled_array = np.array(filled_image)
                    filled_array[fill_mask] = color
                    filled_image = Image.fromarray(filled_array)
                    draw = ImageDraw.Draw(filled_image)

    filled_image.save(output_path)


if __name__ == "__main__":
    main()
