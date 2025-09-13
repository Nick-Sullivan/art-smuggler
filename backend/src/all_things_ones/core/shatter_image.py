import random

import numpy as np


def shatter_image(
    target: np.ndarray,
    num_pieces: int = 15,
    num_images: int = 2,
    seed: int = None,
    background_color: float = 0.6,  # Changed to float for 0-1 range
) -> list[np.ndarray]:
    """
    Split image into irregular pieces like a shattered windshield, then distribute across multiple images.

    Args:
        target: Input image array (0-1 range)
        num_pieces: Number of shattered pieces to create
        num_images: Number of output images to distribute pieces across
        seed: Random seed for reproducible results
        background_color: Background color value (0-1 range)

    Returns:
        List of composite images, each containing some of the pieces
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    height, width, channels = target.shape

    # Generate random points for Voronoi diagram (impact points)
    points = []

    # Add some points near the center (main impact)
    center_x, center_y = width // 2, height // 2
    center_points = max(1, num_pieces // 4)

    for _ in range(center_points):
        x = center_x + np.random.normal(0, width * 0.1)
        y = center_y + np.random.normal(0, height * 0.1)
        points.append([x, y])

    # Add random scattered points
    scatter_points = num_pieces - len(points)

    for _ in range(scatter_points):
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, height)
        points.append([x, y])

    # Add boundary points to ensure full coverage
    margin = 50
    boundary_points = [
        [-margin, -margin],
        [width // 2, -margin],
        [width + margin, -margin],
        [-margin, height // 2],
        [width + margin, height // 2],
        [-margin, height + margin],
        [width // 2, height + margin],
        [width + margin, height + margin],
    ]
    points.extend(boundary_points)

    points = np.array(points)

    # Create coordinate arrays
    y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
    coords = np.column_stack([x_coords.ravel(), y_coords.ravel()])

    # Assign each pixel to closest Voronoi point (only consider first num_pieces points)
    distances = np.sqrt(
        ((coords[:, np.newaxis, :] - points[np.newaxis, :num_pieces, :]) ** 2).sum(
            axis=2
        )
    )
    closest_point = np.argmin(distances, axis=1)
    region_map = closest_point.reshape(height, width)

    # Create all pieces first
    all_pieces = []
    for piece_idx in range(num_pieces):
        # Create mask for this piece
        mask = region_map == piece_idx

        # Create piece with alpha channel (alpha still 0-1 range)
        piece = np.zeros((height, width, channels + 1), dtype=target.dtype)
        piece[mask, :channels] = target[mask]
        piece[mask, channels] = 1.0  # Alpha channel (1.0 for opaque)

        all_pieces.append((piece_idx, piece))

    # Distribute pieces across images
    distributed_images = [[] for _ in range(num_images)]

    # Strategy: distribute pieces as evenly as possible
    for i, (piece_idx, piece) in enumerate(all_pieces):
        target_image = i % num_images
        distributed_images[target_image].append(piece)

    # Create composite images
    composite_images = []
    for pieces in distributed_images:
        if not pieces:
            continue

        # Create composite by combining all pieces for this image
        composite = np.full(
            (height, width, channels), background_color, dtype=target.dtype
        )

        for piece in pieces:
            # Where piece has alpha > 0, use the piece's color
            alpha_mask = piece[:, :, -1] > 0
            composite[alpha_mask] = piece[alpha_mask, :channels]

        composite_images.append(composite)

    return composite_images
