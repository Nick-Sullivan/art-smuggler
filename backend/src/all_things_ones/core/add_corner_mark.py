import math

import numpy as np


def add_corner_mark(
    image: np.ndarray,
    segment_index: int,
    total_segments: int,
    circle_size: int = 50,
    margin: int = 5,
    opacity: float = 0.8,
) -> np.ndarray:
    """
    Add a circular segment mark in the bottom right corner.
    The full circle is white with one black segment.

    Args:
        image: Input image
        segment_index: Which segment this is (0-based)
        total_segments: Total number of segments that make up the full circle
        circle_size: Diameter of the circle
        margin: Margin from edge
        opacity: Opacity of the segment
    """
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
                # Calculate angle from center
                angle = math.atan2(dy, dx)
                # Normalize angle to 0-2π
                if angle < 0:
                    angle += 2 * math.pi

                # Check if angle is within this segment (black) or outside (white)
                if start_angle <= angle < end_angle:
                    # Black segment
                    color = np.array([0.0, 0.0, 0.0]) if len(image.shape) == 3 else 0.0
                else:
                    # White rest of circle
                    color = np.array([1.0, 1.0, 1.0]) if len(image.shape) == 3 else 1.0

                # Blend with original image
                marked_image[y, x] = (
                    opacity * color + (1 - opacity) * marked_image[y, x]
                )

    return marked_image
