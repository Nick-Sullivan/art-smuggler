import numpy as np
from scipy.ndimage import binary_dilation, rotate

from all_things_ones.files import SaveType, save_image


def inpaint(canvases, trans_images, num_images: int, img_size: int):
    seeds = generate_seeds(canvases, num_images)

    processed_layers = []
    for i in range(num_images):
        if i == num_images - 1:
            processed_layers.append(canvases[i])
            continue

        # Convert seed image to RGBA
        seed_with_alpha = np.zeros((img_size, img_size, 4), dtype=np.float32)
        seed_with_alpha[:, :, :3] = seeds[i]
        seed_with_alpha[:, :, 3] = 1.0

        if i > 0:
            trans_idx = i - 1
            # Where trans_mask has alpha>0 (opaque), make seed transparent (cut holes)
            mask_to_apply = trans_images[trans_idx][:, :, 3] > 0
            seed_with_alpha[mask_to_apply, 3] = 0.0
            save_image(
                seed_with_alpha, f"seed_with_holes_{i}.png", image_type=SaveType.DEBUG
            )

        # Overlay the canvas on top of the seed
        layer = np.copy(seed_with_alpha)
        canvas_mask = canvases[i][:, :, 3] > 0
        layer[canvas_mask] = canvases[i][canvas_mask]

        processed_layers.append(layer)

    for i, layer in enumerate(processed_layers):
        save_image(layer, f"canvas_filled_{i}.png", image_type=SaveType.DEBUG)

    # Combine all layers - stack them and use the topmost opaque pixel
    combined = np.zeros((img_size, img_size, 4), dtype=np.float32)

    for layer in processed_layers:
        # Where layer has alpha > 0, use it (later layers override earlier ones)
        layer_mask = layer[:, :, 3] > 0
        combined[layer_mask] = layer[layer_mask]

    # Create final RGB output (no alpha channel)
    final_output = combined[:, :, :3]
    save_image(final_output, "final_output.png", image_type=SaveType.DEBUG)

    return final_output


def generate_seeds(canvases: list[np.ndarray], num_images: int) -> list[np.ndarray]:
    """
    Generate camouflage seed patterns for each canvas.

    Args:
        canvases: List of canvas images (RGBA format)
        num_images: Number of images/canvases

    Returns:
        List of RGB seed patterns
    """
    seeds = []
    for i, canvas in enumerate(canvases):
        if i == num_images - 1:
            # Last canvas uses blank seed
            blank_seed = np.ones(
                (canvas.shape[0], canvas.shape[1], 3), dtype=np.float32
            )
            seeds.append(blank_seed)
            continue
        print(f"Generating camouflage pattern for canvas {i}...")
        np.random.seed(42 + i)

        # Choose technique based on canvas density
        technique = choose_camouflage_technique(canvas)
        print(f"  Using technique: {technique}")

        if technique == "blob_duplication":
            pattern = generate_camouflage_pattern(
                canvas, num_copies=40, min_blob_size=500
            )
        elif technique == "fractal":
            pattern = generate_fractal_pattern(canvas)
        elif technique == "texture_synthesis":
            pattern = generate_texture_synthesis(canvas, patch_size=50, num_patches=100)
        else:  # noise
            pattern = generate_organic_pattern(canvas, scale=150.0, detail=6)

        # Add additional obfuscation
        print("  Adding obfuscation layers...")
        pattern = add_false_patterns(pattern, canvas)

        save_image(pattern, f"generated_pattern_{i}.png", image_type=SaveType.DEBUG)
        seeds.append(pattern)

    return seeds


def choose_camouflage_technique(canvas: np.ndarray) -> str:
    """
    Choose the best camouflage technique based on canvas characteristics.
    """
    content_mask = canvas[:, :, 3] > 0
    density = np.sum(content_mask) / content_mask.size

    if density < 0.1:
        return "noise"  # Sparse canvas, use noise
    elif density < 0.3:
        return "blob_duplication"  # Medium density, duplicate elements
    else:
        return "texture_synthesis"  # Dense canvas, synthesize texture


def add_false_patterns(pattern: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    """
    Add fake geometric patterns and noise to further obfuscate the real content.
    """
    height, width = pattern.shape[:2]
    result = pattern.copy()

    # Get color palette from canvas
    content_mask = canvas[:, :, 3] > 0
    if np.any(content_mask):
        content_colors = canvas[content_mask, :3]
        mean_color = np.mean(content_colors, axis=0)
        std_color = np.std(content_colors, axis=0)
    else:
        mean_color = np.array([0.5, 0.5, 0.5])
        std_color = np.array([0.1, 0.1, 0.1])

    # Add random geometric shapes (circles, rectangles, lines)
    num_shapes = np.random.randint(10, 30)

    for _ in range(num_shapes):
        # Random color from canvas palette
        color = np.clip(mean_color + np.random.randn(3) * std_color, 0, 1)

        shape_type = np.random.choice(["circle", "rectangle", "line"])

        if shape_type == "circle":
            center_y = np.random.randint(0, height)
            center_x = np.random.randint(0, width)
            radius = np.random.randint(20, 100)

            y, x = np.ogrid[:height, :width]
            mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2

            # Blend circle
            alpha = 0.3
            for c in range(3):
                result[mask, c] = result[mask, c] * (1 - alpha) + color[c] * alpha

        elif shape_type == "rectangle":
            y1 = np.random.randint(0, height - 50)
            x1 = np.random.randint(0, width - 50)
            rect_h = np.random.randint(30, 150)
            rect_w = np.random.randint(30, 150)

            y2 = min(y1 + rect_h, height)
            x2 = min(x1 + rect_w, width)

            # Blend rectangle
            alpha = 0.3
            for c in range(3):
                result[y1:y2, x1:x2, c] = (
                    result[y1:y2, x1:x2, c] * (1 - alpha) + color[c] * alpha
                )

    # Add textured noise based on canvas colors
    noise_scale = generate_perlin_noise(height, width, scale=80, octaves=4)
    for c in range(3):
        color_noise = (noise_scale - 0.5) * std_color[c] * 2
        result[:, :, c] = np.clip(result[:, :, c] + color_noise * 0.2, 0, 1)

    return result


def generate_fractal_pattern(canvas: np.ndarray) -> np.ndarray:
    """
    Generate a fractal-like pattern that mimics the canvas at different scales.
    """
    height, width = canvas.shape[:2]
    pattern = np.zeros((height, width, 3), dtype=np.float32)

    # Sample colors from canvas
    content_mask = canvas[:, :, 3] > 0
    if np.any(content_mask):
        content_colors = canvas[content_mask, :3]
        sampled_colors = content_colors[
            np.random.choice(len(content_colors), min(50, len(content_colors)))
        ]
    else:
        sampled_colors = np.array([[0.5, 0.5, 0.5]])

    # Generate fractal noise at multiple scales
    scales = [200, 100, 50, 25]
    weights = [0.4, 0.3, 0.2, 0.1]

    for scale, weight in zip(scales, weights):
        noise = generate_perlin_noise(height, width, scale=scale, octaves=4)

        # Map noise to colors
        for i, color in enumerate(sampled_colors):
            lower = i / len(sampled_colors)
            upper = (i + 1) / len(sampled_colors)
            mask = (noise >= lower) & (noise < upper)

            for c in range(3):
                pattern[mask, c] += color[c] * weight

    pattern = np.clip(pattern, 0, 1)
    return pattern


def generate_texture_synthesis(
    canvas: np.ndarray, patch_size: int = 50, num_patches: int = 100
) -> np.ndarray:
    """
    Synthesize texture by extracting and recombining patches from the canvas.
    Similar to Image Quilting algorithm.
    """
    height, width = canvas.shape[:2]
    pattern = np.zeros((height, width, 3), dtype=np.float32)

    content_mask = canvas[:, :, 3] > 0

    if not np.any(content_mask):
        return generate_organic_pattern(canvas, scale=150.0, detail=6)

    # Find all valid patch locations in canvas
    valid_patches = []
    for y in range(0, height - patch_size, patch_size // 2):
        for x in range(0, width - patch_size, patch_size // 2):
            patch_mask = content_mask[y : y + patch_size, x : x + patch_size]
            if np.sum(patch_mask) > (
                patch_size * patch_size * 0.1
            ):  # At least 10% content
                patch_rgb = canvas[y : y + patch_size, x : x + patch_size, :3].copy()
                valid_patches.append((patch_rgb, patch_mask))

    if len(valid_patches) == 0:
        return generate_organic_pattern(canvas, scale=150.0, detail=6)

    print(f"    Found {len(valid_patches)} valid patches")

    # Fill pattern with patches
    for _ in range(num_patches):
        # Pick random patch
        patch_rgb, patch_mask = valid_patches[np.random.randint(len(valid_patches))]

        # Random position
        y = np.random.randint(0, height - patch_size)
        x = np.random.randint(0, width - patch_size)

        # Random transform
        if np.random.random() > 0.5:
            patch_rgb = np.fliplr(patch_rgb)
            patch_mask = np.fliplr(patch_mask)
        if np.random.random() > 0.5:
            patch_rgb = np.flipud(patch_rgb)
            patch_mask = np.flipud(patch_mask)

        # Rotate
        angle = np.random.choice([0, 90, 180, 270])
        if angle > 0:
            patch_rgb = rotate(patch_rgb, angle, reshape=False, axes=(0, 1), order=1)
            patch_mask = (
                rotate(patch_mask.astype(float), angle, reshape=False, order=0) > 0.5
            )

        # Slight color variation
        color_shift = (np.random.rand(3) - 0.5) * 0.15
        patch_rgb = np.clip(patch_rgb + color_shift, 0, 1)

        # Blend into pattern
        alpha = 0.7
        for c in range(3):
            pattern[y : y + patch_size, x : x + patch_size, c] = np.where(
                patch_mask,
                patch_rgb[:, :, c] * alpha
                + pattern[y : y + patch_size, x : x + patch_size, c] * (1 - alpha),
                pattern[y : y + patch_size, x : x + patch_size, c],
            )

    # Fill empty areas
    empty_mask = np.all(pattern == 0, axis=2)
    if np.any(empty_mask):
        background = generate_background_fill(canvas)
        pattern[empty_mask] = background[empty_mask]

    return pattern


def generate_camouflage_pattern(
    canvas: np.ndarray, num_copies: int = 25, min_blob_size: int = 500
) -> np.ndarray:
    """
    Generate a camouflage pattern by extracting and duplicating elements from the canvas.

    Args:
        canvas: The canvas to mimic (RGBA format)
        num_copies: Number of element copies to create
        min_blob_size: Minimum size of blobs to extract (in pixels)

    Returns:
        RGB image with duplicated and transformed canvas elements
    """
    height, width = canvas.shape[:2]
    pattern = np.zeros((height, width, 3), dtype=np.float32)

    # Extract connected components (blobs) from the canvas
    print("  Extracting canvas elements...")
    blobs = extract_canvas_blobs(canvas, min_blob_size=min_blob_size)

    print(f"  Found {len(blobs)} elements")

    if len(blobs) == 0:
        print("  No elements found, using noise pattern")
        return generate_organic_pattern(canvas, scale=150.0, detail=6)

    # Save debug info about blob sizes
    blob_sizes = [np.sum(blob[0]) for blob in blobs]
    print(
        f"  Blob sizes: min={min(blob_sizes)}, max={max(blob_sizes)}, avg={np.mean(blob_sizes):.0f}"
    )

    print(f"  Creating {num_copies} copies...")

    # Create copies of blobs with transformations
    for copy_idx in range(num_copies):
        # Pick a random blob (favor larger blobs)
        blob_weights = np.array([np.sum(blob[0]) for blob in blobs])
        blob_weights = blob_weights / blob_weights.sum()
        blob_idx = np.random.choice(len(blobs), p=blob_weights)

        blob_mask, blob_rgb, bbox = blobs[blob_idx]

        # Apply random transformations
        transformed_mask, transformed_rgb = apply_random_transform(blob_mask, blob_rgb)

        # Find a random position to place it
        blob_h, blob_w = transformed_mask.shape
        max_y = max(1, height - blob_h)
        max_x = max(1, width - blob_w)

        pos_y = np.random.randint(0, max_y)
        pos_x = np.random.randint(0, max_x)

        # Blend the blob into the pattern
        blend_blob_into_pattern(
            pattern, transformed_mask, transformed_rgb, pos_y, pos_x
        )

    # Fill any remaining empty space with subtle noise
    empty_mask = np.all(pattern == 0, axis=2)
    if np.any(empty_mask):
        background = generate_background_fill(canvas)
        pattern[empty_mask] = background[empty_mask]

    return pattern


def extract_canvas_blobs(canvas: np.ndarray, min_blob_size: int = 500) -> list:
    """
    Extract individual blobs/elements from the canvas using dilation to group nearby pixels.
    Returns list of (mask, rgb, bbox) tuples.
    """
    from scipy.ndimage import find_objects, label

    content_mask = canvas[:, :, 3] > 0

    if not np.any(content_mask):
        return []

    # Dilate to connect nearby pixels into larger blobs
    dilated_mask = binary_dilation(content_mask, iterations=10)

    # Label connected components
    labeled, num_features = label(dilated_mask)

    blobs = []
    slices = find_objects(labeled)

    max_blob_size = (canvas.shape[0] * canvas.shape[1]) / 3

    for i, slice_obj in enumerate(slices):
        if slice_obj is None:
            continue

        y_slice, x_slice = slice_obj

        # Get the dilated region mask
        dilated_region = labeled[y_slice, x_slice] == (i + 1)

        # Get the actual content within this region
        actual_content = content_mask[y_slice, x_slice] & dilated_region

        blob_size = np.sum(actual_content)

        # Only keep blobs that are reasonably sized
        if min_blob_size <= blob_size <= max_blob_size:
            # Extract RGB values for the actual content
            blob_rgb = np.zeros(
                (dilated_region.shape[0], dilated_region.shape[1], 3), dtype=np.float32
            )

            # Fill with canvas colors where content exists
            blob_rgb[actual_content] = canvas[y_slice, x_slice, :3][actual_content]

            # Use the dilated mask for shape but actual content for colors
            blobs.append((dilated_region, blob_rgb, (y_slice, x_slice)))

    return blobs


def apply_random_transform(blob_mask: np.ndarray, blob_rgb: np.ndarray):
    """
    Apply random transformations to a blob (rotation, flip, slight color variation).
    """
    # Random rotation
    angle = np.random.choice([0, 90, 180, 270])
    if angle > 0:
        blob_mask = rotate(blob_mask.astype(float), angle, reshape=True, order=0) > 0.5
        blob_rgb = rotate(blob_rgb, angle, reshape=True, axes=(0, 1), order=1)

    # Random flip
    if np.random.random() > 0.5:
        blob_mask = np.fliplr(blob_mask)
        blob_rgb = np.fliplr(blob_rgb)

    if np.random.random() > 0.5:
        blob_mask = np.flipud(blob_mask)
        blob_rgb = np.flipud(blob_rgb)

    # Slight color variation
    color_shift = (np.random.rand(3) - 0.5) * 0.2
    blob_rgb = np.clip(blob_rgb + color_shift, 0, 1)

    return blob_mask, blob_rgb


def blend_blob_into_pattern(
    pattern: np.ndarray,
    blob_mask: np.ndarray,
    blob_rgb: np.ndarray,
    pos_y: int,
    pos_x: int,
):
    """
    Blend a blob into the pattern at the specified position.
    """
    blob_h, blob_w = blob_mask.shape

    # Calculate actual region to paste (handle edges)
    end_y = min(pos_y + blob_h, pattern.shape[0])
    end_x = min(pos_x + blob_w, pattern.shape[1])
    actual_h = end_y - pos_y
    actual_w = end_x - pos_x

    if actual_h <= 0 or actual_w <= 0:
        return

    # Crop blob if needed
    blob_mask_crop = blob_mask[:actual_h, :actual_w]
    blob_rgb_crop = blob_rgb[:actual_h, :actual_w]

    # Only paste where blob_rgb has actual color (not black from padding)
    has_color = np.any(blob_rgb_crop > 0, axis=2) & blob_mask_crop

    # Blend with slight transparency
    alpha = 0.8
    pattern_region = pattern[pos_y:end_y, pos_x:end_x]

    for c in range(3):
        pattern_region[:, :, c] = np.where(
            has_color,
            blob_rgb_crop[:, :, c] * alpha + pattern_region[:, :, c] * (1 - alpha),
            pattern_region[:, :, c],
        )


def generate_background_fill(canvas: np.ndarray) -> np.ndarray:
    """
    Generate a subtle background fill based on canvas colors.
    """
    height, width = canvas.shape[:2]
    content_mask = canvas[:, :, 3] > 0
    content_colors = canvas[content_mask, :3]

    if len(content_colors) == 0:
        return np.full((height, width, 3), 0.5, dtype=np.float32)

    # Use mean color with some noise
    mean_color = np.mean(content_colors, axis=0)

    # Generate subtle noise
    noise = np.random.randn(height, width, 3) * 0.08
    background = np.clip(mean_color + noise, 0, 1)

    return background


def generate_organic_pattern(
    canvas: np.ndarray, scale: float = 80.0, detail: int = 6
) -> np.ndarray:
    """
    Generate an organic pattern using Perlin noise and canvas color sampling.
    Fallback for when no blobs are found.
    """
    height, width = canvas.shape[:2]
    sampled_colors = sample_colors_from_canvas(canvas, num_samples=30)

    print("  Generating noise layers...")
    noise_r = generate_perlin_noise(height, width, scale=scale, octaves=detail)
    noise_g = generate_perlin_noise(height, width, scale=scale * 1.2, octaves=detail)
    noise_b = generate_perlin_noise(height, width, scale=scale * 0.8, octaves=detail)
    color_selector = generate_perlin_noise(height, width, scale=scale * 2, octaves=4)

    print("  Mapping colors...")
    pattern = np.zeros((height, width, 3), dtype=np.float32)
    num_colors = len(sampled_colors)

    for i in range(num_colors):
        lower = i / num_colors
        upper = (i + 1) / num_colors
        mask = (color_selector >= lower) & (color_selector < upper)

        for c in range(3):
            base_color = sampled_colors[i, c]
            noise_val = [noise_r, noise_g, noise_b][c]
            variation = (noise_val - 0.5) * 0.3
            pattern[mask, c] = np.clip(base_color + variation[mask], 0, 1)

    fine_noise = generate_perlin_noise(height, width, scale=20, octaves=3)
    fine_noise = (fine_noise - 0.5) * 0.1
    pattern = np.clip(pattern + fine_noise[:, :, np.newaxis], 0, 1)

    return pattern


def sample_colors_from_canvas(canvas: np.ndarray, num_samples: int = 20) -> np.ndarray:
    """
    Sample representative colors from the canvas content.
    """
    content_mask = canvas[:, :, 3] > 0
    content_colors = canvas[content_mask, :3]

    if len(content_colors) == 0:
        return np.array([[0.5, 0.5, 0.5]])

    if len(content_colors) > num_samples:
        indices = np.random.choice(len(content_colors), num_samples, replace=False)
        sampled_colors = content_colors[indices]
    else:
        sampled_colors = content_colors

    return sampled_colors


def generate_perlin_noise(
    height: int, width: int, scale: float = 100.0, octaves: int = 6
) -> np.ndarray:
    """
    Generate 2D Perlin-like noise using multiple octaves of random noise.
    """
    noise = np.zeros((height, width))

    for octave in range(octaves):
        freq = 2**octave
        amp = 1.0 / (2**octave)

        grid_h = int(height / scale * freq) + 2
        grid_w = int(width / scale * freq) + 2
        grid = np.random.randn(grid_h, grid_w)

        from scipy.ndimage import zoom

        zoomed = zoom(grid, (height / grid_h, width / grid_w), order=1)
        noise += zoomed[:height, :width] * amp

    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return noise
