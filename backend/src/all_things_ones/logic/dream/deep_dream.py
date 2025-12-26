from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


class DeepDream:
    def __init__(
        self, model_name: str = "vgg19", layer_name: str = "features.28"
    ) -> None:
        self.device: torch.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # Load pre-trained model
        if model_name == "vgg19":
            self.model: nn.Module = models.vgg19(pretrained=True).features
        elif model_name == "inception":
            self.model: nn.Module = models.inception_v3(pretrained=True)

        self.model.eval()
        self.model.to(self.device)
        self.layer_name: str = layer_name

        # Normalization for ImageNet
        self.normalize: transforms.Normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )

    def get_activations(self, x: torch.Tensor) -> Optional[torch.Tensor]:
        """Extract activations from specified layer"""
        activations: list[torch.Tensor] = []

        def hook(
            module: nn.Module, input: tuple[torch.Tensor, ...], output: torch.Tensor
        ) -> None:
            activations.append(output)

        # Register hook
        for name, layer in self.model.named_modules():
            if name == self.layer_name:
                layer.register_forward_hook(hook)
                break

        self.model(x)
        return activations[0] if activations else None

    def dream_step(self, image: torch.Tensor, lr: float = 0.01) -> torch.Tensor:
        """Single optimization step"""
        image.requires_grad_(True)

        # Forward pass
        activations: Optional[torch.Tensor] = self.get_activations(image)
        if activations is None:
            return image

        # Maximize activations (dream objective)
        loss: torch.Tensor = -activations.norm()

        # Backward pass
        loss.backward()

        # Update image
        with torch.no_grad():
            image += lr * image.grad
            image.grad.zero_()

        return image

    def apply_deep_dream(
        self, img_array: np.ndarray, iterations: int = 20, lr: float = 0.01
    ) -> np.ndarray:
        """Apply Deep Dream to numpy image array"""
        # Convert numpy to PIL to tensor
        if img_array.max() <= 1.0:
            img_array = (img_array * 255).astype(np.uint8)

        pil_img: Image.Image = Image.fromarray(img_array)

        # Transform to tensor
        transform: transforms.Compose = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
            ]
        )

        img_tensor: torch.Tensor = transform(pil_img).unsqueeze(0).to(self.device)
        img_tensor = self.normalize(img_tensor)

        # Apply Deep Dream
        for i in range(iterations):
            img_tensor = self.dream_step(img_tensor, lr)

        # Convert back to numpy - detach from computation graph first
        img_tensor = img_tensor.squeeze(0).cpu().detach()

        # Denormalize
        mean: torch.Tensor = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std: torch.Tensor = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        img_tensor = img_tensor * std + mean

        # Convert to numpy and resize back
        img_np: np.ndarray = img_tensor.permute(1, 2, 0).clamp(0, 1).numpy()

        # Resize back to original size
        pil_result: Image.Image = Image.fromarray((img_np * 255).astype(np.uint8))
        pil_result = pil_result.resize((img_array.shape[1], img_array.shape[0]))

        result_array: np.ndarray = np.array(pil_result).astype(np.float32) / 255.0

        return result_array
