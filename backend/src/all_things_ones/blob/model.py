from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class Blob:
    id: int
    size: int
    centroid: Tuple[float, float]  # (x, y)
    bbox: Tuple[float, float, float, float]  # (x, y, width, height)
    mean_color: np.ndarray
    mask: np.ndarray
