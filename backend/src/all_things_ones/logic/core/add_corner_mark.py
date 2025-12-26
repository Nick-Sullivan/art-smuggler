import math

import numpy as np


def add_corner_mark(
    image: np.ndarray,
    segment_index: int,
    total_segments: int,
    size: int = 50,
    margin: int = 5,
    opacity: float = 0.8,
    border_width: int = 1,
) -> np.ndarray:
    marked_img = add_bottom_right_circle_mark(
        image,
        segment_index,
        total_segments,
        size,
        margin,
        opacity,
        border_width,
    )
    marked_img = add_top_left_square_mark(
        marked_img,
        segment_index,
        total_segments,
        size,
        margin,
        opacity,
        border_width,
    )
    return marked_img


def add_bottom_right_circle_mark(
    image: np.ndarray,
    segment_index: int,
    total_segments: int,
    circle_size: int = 50,
    margin: int = 5,
    opacity: float = 0.8,
    border_width: int = 1,
) -> np.ndarray:
    marked_image = image.copy()

    height, width = image.shape[:2]

    # Calculate position (bottom right with margin)
    center_x = width - circle_size // 2 - margin
    center_y = height - circle_size // 2 - margin

    # Calculate start and end angles for this segment
    angle_per_segment = 2 * math.pi / total_segments
    start_angle = segment_index * angle_per_segment
    end_angle = (segment_index + 1) * angle_per_segment

    # Create the segment mask
    radius = circle_size // 2

    for y in range(max(0, center_y - radius), min(height, center_y + radius + 1)):
        for x in range(max(0, center_x - radius), min(width, center_x + radius + 1)):
            # Calculate distance from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx * dx + dy * dy)

            # Check if point is within circle
            if distance <= radius:
                # Check if point is on the border
                if distance > radius - border_width:
                    # Black border
                    color = np.array([0.0, 0.0, 0.0]) if len(image.shape) == 3 else 0.0
                else:
                    # Calculate angle from center
                    angle = math.atan2(dy, dx)
                    # Normalize angle to 0-2π
                    if angle < 0:
                        angle += 2 * math.pi

                    # Check if angle is within this segment (black) or outside (white)
                    if start_angle <= angle < end_angle:
                        # Black segment
                        color = (
                            np.array([0.0, 0.0, 0.0]) if len(image.shape) == 3 else 0.0
                        )
                    else:
                        # White rest of circle
                        color = (
                            np.array([1.0, 1.0, 1.0]) if len(image.shape) == 3 else 1.0
                        )

                # Blend with original image
                marked_image[y, x] = (
                    opacity * color + (1 - opacity) * marked_image[y, x]
                )

    return marked_image


def add_top_left_square_mark(
    image: np.ndarray,
    segment_index: int,
    total_segments: int,
    square_size: int = 50,
    margin: int = 5,
    opacity: float = 0.8,
    border_width: int = 1,
) -> np.ndarray:
    marked_image = image.copy()

    height, width = image.shape[:2]

    # Add square in top left corner
    square_start_x = margin
    square_start_y = margin
    square_end_x = margin + square_size
    square_end_y = margin + square_size

    # Calculate center of square for angle calculations
    center_x = square_start_x + square_size // 2
    center_y = square_start_y + square_size // 2

    # Calculate start and end angles for this segment
    angle_per_segment = 2 * math.pi / total_segments
    start_angle = segment_index * angle_per_segment
    end_angle = (segment_index + 1) * angle_per_segment

    for y in range(max(0, square_start_y), min(height, square_end_y)):
        for x in range(max(0, square_start_x), min(width, square_end_x)):
            # Check if point is on the border
            if (
                x < square_start_x + border_width
                or x >= square_end_x - border_width
                or y < square_start_y + border_width
                or y >= square_end_y - border_width
            ):
                # Black border
                color = np.array([0.0, 0.0, 0.0]) if len(image.shape) == 3 else 0.0
            else:
                # Calculate angle from center
                dx = x - center_x
                dy = y - center_y
                angle = math.atan2(dy, dx)
                # Normalize angle to 0-2π
                if angle < 0:
                    angle += 2 * math.pi

                # Check if angle is within this segment (black) or outside (white)
                if start_angle <= angle < end_angle:
                    # Black segment
                    color = np.array([0.0, 0.0, 0.0]) if len(image.shape) == 3 else 0.0
                else:
                    # White rest of square
                    color = np.array([1.0, 1.0, 1.0]) if len(image.shape) == 3 else 1.0

            # Blend with original image
            marked_image[y, x] = opacity * color + (1 - opacity) * marked_image[y, x]

    return marked_image
