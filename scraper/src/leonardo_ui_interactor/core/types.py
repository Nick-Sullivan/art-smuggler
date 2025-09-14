from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationSettings:
    model: str = "Phoenix 1.0"
    generation_mode: str = "Fast"
    aspect_ratio: str = "1:1"
    size: str = "Small"
    number_of_images: int = 4


@dataclass
class ReferenceImageSettings:
    image_path: str
    type: str = "Content Reference"
    guidance_strength: str = "High"


@dataclass
class PromptSettings:
    prompt: str
    reference_image_settings: Optional[ReferenceImageSettings]
