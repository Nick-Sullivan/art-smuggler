import random

import numpy as np
from scipy.spatial import cKDTree


def shatter_image(
    target: np.ndarray,
    num_pieces: int = 15,
    num_images: int = 2,
    seed: int = None,
    background_color: float = 0.6,
) -> list[np.ndarray]:
    """
    Split image into irregular pieces like a shattered windshield, then distribute across multiple images.
    """
    pieces = shatter_into_pieces(target, num_pieces=num_pieces, seed=seed)
    height, width, channels = target.shape

    # Distribute pieces across images
    distributed_images = [[] for _ in range(num_images)]

    # Strategy: distribute pieces as evenly as possible
    for i, piece in enumerate(pieces):
        target_image = i % num_images
        distributed_images[target_image].append(piece)

    # Create composite images
    composite_images = []
    for pieces_list in distributed_images:
        if not pieces_list:
            continue

        # Create composite by combining all pieces for this image
        composite = np.full(
            (height, width, channels), background_color, dtype=target.dtype
        )

        for piece in pieces_list:
            # Where piece has alpha > 0, use the piece's color
            alpha_mask = piece[:, :, -1] > 0
            composite[alpha_mask] = piece[alpha_mask, :channels]

        composite_images.append(composite)

    return composite_images


def shatter_into_pieces(
    target: np.ndarray,
    num_pieces: int = 15,
    seed: int = None,
) -> list[np.ndarray]:
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

    # Only use the first num_pieces points (no boundary points for speed)
    points = np.array(points[:num_pieces])

    # Use KDTree for extremely fast nearest neighbor lookup
    tree = cKDTree(points)

    # Process in chunks to avoid memory issues
    chunk_size = 1000000  # Process 1M pixels at a time
    region_map = np.zeros((height, width), dtype=np.int32)

    total_pixels = height * width

    for start_idx in range(0, total_pixels, chunk_size):
        end_idx = min(start_idx + chunk_size, total_pixels)
        chunk_length = end_idx - start_idx

        # Convert flat indices to 2D coordinates for this chunk
        flat_indices = np.arange(start_idx, end_idx)
        y_coords = flat_indices // width
        x_coords = flat_indices % width

        # Create coordinate pairs for this chunk
        chunk_coords = np.column_stack([x_coords, y_coords])

        # Query KDTree for nearest points (much faster than manual distance calc)
        _, closest_indices = tree.query(chunk_coords)

        # Convert back to 2D coordinates and assign
        chunk_y = y_coords
        chunk_x = x_coords
        region_map[chunk_y, chunk_x] = closest_indices

    # Create all pieces
    all_pieces = []
    for piece_idx in range(num_pieces):
        # Create mask for this piece
        mask = region_map == piece_idx

        # Skip empty pieces
        if not np.any(mask):
            continue

        # Create piece with alpha channel
        piece = np.zeros((height, width, channels + 1), dtype=target.dtype)
        piece[mask, :channels] = target[mask]
        piece[mask, channels] = 1.0  # Alpha channel

        all_pieces.append(piece)

    return all_pieces
