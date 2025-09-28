import os

import matplotlib.pyplot as plt
import numpy as np
from svgpathtools import svg2paths


def main():
    plt.switch_backend("Agg")
    os.makedirs("data/output/reassembled", exist_ok=True)

    # Create multiple reassembled versions with different numbers of shapes
    shape_counts = [10, 50, 100, 500, 1000, 2000, 5000, 10_000]

    print("Creating reassembled images with different numbers of shapes...")
    reassemble_iteratively(shape_counts)


def reassemble_iteratively(shape_counts):
    """Iteratively create reassembled images with different shape counts"""

    # Load paths and attributes once
    print("Loading SVG file...")
    paths, attributes = svg2paths("data/input/target/file.svg")

    total_shapes = len(paths)
    print(f"Total shapes in SVG: {total_shapes}")

    # Calculate overall bounding box once
    print("Calculating overall bounding box...")
    all_bboxes = [path.bbox() for path in paths]
    min_x = min(bbox[0] for bbox in all_bboxes)
    max_x = max(bbox[1] for bbox in all_bboxes)
    min_y = min(bbox[2] for bbox in all_bboxes)
    max_y = max(bbox[3] for bbox in all_bboxes)

    # Sort shape counts to build incrementally
    shape_counts = sorted(shape_counts)

    # Pre-process all shape data once
    print("Pre-processing shape data...")
    shape_data = []
    for i, (path, attr) in enumerate(zip(paths, attributes)):
        stroke_color = attr.get("stroke", "black")
        fill_color = attr.get("fill", "none")
        stroke_width = float(attr.get("stroke-width", 1))

        # Pre-calculate path coordinates
        num_points = 1000
        t_values = np.linspace(0, 1, num_points)
        x_coords = []
        y_coords = []

        for t in t_values:
            point = path.point(t)
            x_coords.append(point.real)
            y_coords.append(point.imag)

        shape_data.append(
            {
                "x_coords": x_coords,
                "y_coords": y_coords,
                "stroke_color": stroke_color,
                "fill_color": fill_color,
                "stroke_width": stroke_width,
            }
        )

        if i % 1000 == 0:
            print(f"  Pre-processed {i}/{total_shapes} shapes...")

    # Create images iteratively
    for n_shapes in shape_counts:
        print(f"\n--- Creating image with {n_shapes} shapes ---")
        n_shapes = min(n_shapes, total_shapes)

        # Create the reassembled image
        plt.figure(figsize=(12, 12))
        ax = plt.gca()

        print(f"Plotting {n_shapes} shapes...")
        for i in range(n_shapes):
            data = shape_data[i]

            # Handle color mapping
            stroke_color = data["stroke_color"]
            if stroke_color == "none":
                stroke_color = "black"

            # Plot the path outline
            ax.plot(
                data["x_coords"],
                data["y_coords"],
                color=stroke_color,
                linewidth=data["stroke_width"],
            )

            # If there's a fill color and it's not 'none', fill the shape
            if data["fill_color"] != "none" and len(data["x_coords"]) > 2:
                # Close the path for filling
                x_coords = data["x_coords"] + [data["x_coords"][0]]
                y_coords = data["y_coords"] + [data["y_coords"][0]]
                ax.fill(x_coords, y_coords, color=data["fill_color"], alpha=0.7)

            if i % 100 == 0:
                print(f"  Plotted {i}/{n_shapes} shapes...")

        # Set consistent axis limits
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
        ax.set_aspect("equal")

        # Remove axes and grid for clean image
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        plt.title(f"Reassembled Image - First {n_shapes} Shapes", fontsize=14, pad=20)

        # Save the reassembled image
        save_path = f"data/output/reassembled/first_{n_shapes}_shapes.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()

        print(f"Reassembled image saved to {save_path}")


def plot_path(path, ax=None, stroke_color="blue", fill_color="none", stroke_width=1):
    """Plot an SVG path using matplotlib with original colors"""
    if ax is None:
        ax = plt.gca()

    # Sample points along the path
    num_points = 1000
    t_values = np.linspace(0, 1, num_points)

    x_coords = []
    y_coords = []

    for t in t_values:
        point = path.point(t)
        x_coords.append(point.real)
        y_coords.append(point.imag)

    # Handle color mapping
    if stroke_color == "none":
        stroke_color = "black"

    # Plot the path outline
    ax.plot(x_coords, y_coords, color=stroke_color, linewidth=stroke_width)

    # If there's a fill color and it's not 'none', fill the shape
    if fill_color != "none" and len(x_coords) > 2:
        # Close the path for filling
        x_coords.append(x_coords[0])
        y_coords.append(y_coords[0])
        ax.fill(x_coords, y_coords, color=fill_color, alpha=0.7)

    return ax


if __name__ == "__main__":
    main()
