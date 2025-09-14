import asyncio

from leonardo_ui_interactor.core.types import (
    GenerationSettings,
    PromptSettings,
    ReferenceImageSettings,
)
from leonardo_ui_interactor.core.ui_interactor import LeonardoUIInteractor

img_references = [
    "shattered_piece_00",
    "shattered_piece_01",
    "shattered_piece_02",
    "shattered_piece_03",
]


async def main():
    for img_reference in img_references:
        async with LeonardoUIInteractor() as interactor:
            await interactor.authenticate()
            await interactor.setup_generation_settings(
                GenerationSettings(
                    model="Phoenix 1.0",
                    generation_mode="Fast",
                    aspect_ratio="1:1",
                    size="Small",
                    number_of_images=4,
                )
            )
            await interactor.setup_prompt(
                PromptSettings(
                    prompt="Create kaleidoscope of bright colors and tessellated shapes to hide the image, mimicking the shapes that are present in the image",
                    reference_image_settings=ReferenceImageSettings(
                        type="Content Reference",
                        guidance_strength="High",
                        image_path=f"data/input/files/{img_reference}.png",
                    ),
                )
            )
            num_images = await interactor.generate_images()
            assert num_images == 4
            await interactor.download_images("data/output", img_reference)

    print("DONE")


if __name__ == "__main__":
    asyncio.run(main())
