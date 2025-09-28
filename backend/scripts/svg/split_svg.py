import os

import numpy as np
from PIL import Image, ImageDraw
from svgpathtools import svg2paths


def main():
    # Create round-robin split
    split_svg_into_images(4)

    print("\nRound-robin split complete!")
    print("Images saved to data/output/split/")


def split_svg_into_images(num_images):
    """Split SVG shapes into separate images using round-robin distribution"""

    # Create output directory
    os.makedirs("data/output/split", exist_ok=True)

    # Load paths and attributes
    print("Loading SVG file...")
    paths, attributes = svg2paths("data/input/target/file.svg")

    total_shapes = len(paths)
    print(f"Total shapes in SVG: {total_shapes}")

    # Filter out empty/invalid paths first
    valid_paths_attrs = []
    for path, attr in zip(paths, attributes):
        if path and len(path) > 0 and path.length() > 0:
            valid_paths_attrs.append((path, attr))

    print(f"Valid shapes after filtering: {len(valid_paths_attrs)}")

    # Calculate overall bounding box for consistent scaling
    print("Calculating overall bounding box...")
    all_bboxes = [path.bbox() for path, _ in valid_paths_attrs]
    min_x = min(bbox[0] for bbox in all_bboxes)
    max_x = max(bbox[1] for bbox in all_bboxes)
    min_y = min(bbox[2] for bbox in all_bboxes)
    max_y = max(bbox[3] for bbox in all_bboxes)

    # Calculate image dimensions and scaling
    width = max_x - min_x
    height = max_y - min_y
    image_size = 2000  # Target image size in pixels
    scale = image_size / max(width, height)

    img_width = int(width * scale)
    img_height = int(height * scale)

    print(f"Image dimensions: {img_width} x {img_height}")

    # Distribute shapes evenly using round-robin
    groups = [[] for _ in range(num_images)]
    for i, (path, attr) in enumerate(valid_paths_attrs):
        groups[i % num_images].append((path, attr))

    print(f"Group sizes: {[len(group) for group in groups]}")

    # Create 3 separate images
    for i, group in enumerate(groups):
        print(f"\n--- Creating image {i + 1} with {len(group)} shapes ---")

        # Create blank image
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        print(f"Drawing {len(group)} shapes...")
        shapes_drawn = 0
        for j, (path, attr) in enumerate(group):
            # Get colors from SVG attributes
            stroke_color = parse_color(attr.get("stroke", "black"))
            fill_color = parse_color(attr.get("fill", "none"))
            stroke_width = max(1, int(float(attr.get("stroke-width", 1)) * scale))

            # Draw the path
            if draw_path_improved(
                draw,
                path,
                min_x,
                min_y,
                scale,
                stroke_color=stroke_color,
                fill_color=fill_color,
                stroke_width=stroke_width,
            ):
                shapes_drawn += 1

            if j % 500 == 0:
                print(
                    f"  Processed {j}/{len(group)} shapes, successfully drawn: {shapes_drawn}"
                )

        # Save the image
        save_path = f"data/output/split/image_{i + 1}.png"
        image.save(save_path)

        print(f"Split image {i + 1} saved to {save_path}")
        print(f"Successfully drew {shapes_drawn}/{len(group)} shapes")


def parse_color(color_str):
    """Parse SVG color string to RGB tuple"""
    if color_str == "none" or color_str is None or color_str == "":
        return None
    if color_str.startswith("#"):
        hex_color = color_str.lstrip("#")
        if len(hex_color) == 6:
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        elif len(hex_color) == 3:
            return tuple(int(hex_color[i] * 2, 16) for i in range(3))
    return None


def draw_path_improved(
    draw,
    path,
    min_x,
    min_y,
    scale,
    stroke_color=None,
    fill_color=None,
    stroke_width=1,
):
    """Draw an SVG path using PIL ImageDraw with better sampling"""

    # Calculate appropriate number of sample points based on path length
    path_length = path.length()
    num_points = min(5000, max(100, int(path_length * scale / 5)))

    t_values = np.linspace(0, 1, num_points)

    points = []
    for t in t_values:
        point = path.point(t)
        # Convert SVG coordinates to image coordinates
        x = (point.real - min_x) * scale
        y = (point.imag - min_y) * scale

        # Only include points within image bounds
        # if 0 <= x < draw.im.size[0] and 0 <= y < draw.im.size[1]:
        points.append((x, y))

    if len(points) < 2:
        return False

    # Point filtering
    if len(points) > 2:
        filtered_points = [points[0]]
        for i in range(1, len(points)):
            dx = points[i][0] - filtered_points[-1][0]
            dy = points[i][1] - filtered_points[-1][1]
            if dx * dx + dy * dy > 0.1:  # Much smaller threshold
                filtered_points.append(points[i])
        points = filtered_points

    if len(points) < 2:
        return False

    if fill_color is None:
        raise Exception("Fill color cannot be None")

    # Close path for filling
    if points[0] != points[-1]:
        points.append(points[0])
    draw.polygon(points, fill=fill_color)

    if stroke_color is not None:
        for i in range(len(points) - 1):
            draw.line(
                [points[i], points[i + 1]],
                fill=stroke_color,
                width=stroke_width,
            )

    return True


if __name__ == "__main__":
    main()
