import asyncio
import os

from patchright.async_api import Browser, BrowserContext, Page, async_playwright

from leonardo_ui_interactor.core.types import GenerationSettings, PromptSettings


class LeonardoUIInteractor:
    browser: Browser
    context: BrowserContext
    page: Page

    def __init__(self, headless: bool = False):
        self.session_file = "data/session/session.json"
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        if os.path.exists(self.session_file):
            self.context = await self.browser.new_context(
                storage_state=self.session_file
            )
        else:
            self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def authenticate(self):
        await self.page.goto("https://app.leonardo.ai/image-generation")
        current_url = self.page.url
        if "app.leonardo.ai/auth" in current_url:
            print("Authentication required. Please log in manually...")
            print("The script will wait for you to complete the login process.")
            while "app.leonardo.ai/auth" in self.page.url:
                await asyncio.sleep(2)
            print("Login detected! Saving session state...")
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            await self.context.storage_state(path=self.session_file)
            print(f"Session saved to {self.session_file}")

    async def setup_generation_settings(self, settings: GenerationSettings):
        await self.page.click('button:has-text("Let\'s Go!")')
        await self.page.click('button:has-text("No thanks")')
        await self.page.click('p:has-text("Model")')
        await self.page.click(f'[aria-label="{settings.model}"][role="article"]')
        await self.page.click('p:has-text("Model")')
        await self.page.click(
            f'[data-tracking-id="generation_mode_{settings.generation_mode.lower()}_button"]'
        )
        await self.page.click(f'button:has-text("{settings.aspect_ratio}")')
        await self.page.click(f'button:has-text("{settings.size}")')
        await self.page.click(
            f'#number-of-images button:has-text("{settings.number_of_images}")'
        )

    async def setup_prompt(self, settings: PromptSettings):
        await self.page.fill("#prompt-textarea", settings.prompt)
        ref_settings = settings.reference_image_settings
        if ref_settings:
            await self.page.click(
                '[data-tracking-id="generation_add_image_guidance_element"]'
            )
            await self.page.click(f'button:has-text("{ref_settings.type}")')
            # TODO add some kind of wait
            await self.page.set_input_files(
                'input[type="file"]',
                ref_settings.image_path,
            )
            await self.page.click('[data-slot="prompt-thumbnails"]')
            await self.page.click(
                f'label:has(input[name="image-guidance"][value="{ref_settings.guidance_strength}"])'
            )

    async def generate_images(self) -> int:
        await self.page.click('button[aria-label="Generate"]')
        # TODO a better wait
        await asyncio.sleep(10)
        table = self.page.locator('[class="relative mt-4 flex flex-col gap-4"]')
        first_element = table.locator('[data-index="0"]')
        images = first_element.locator('img[data-nimg="1"]')
        return await images.count()

    async def download_images(self, output_dir: str, base_filename: str) -> list[str]:
        os.makedirs(output_dir, exist_ok=True)
        table = self.page.locator('[class="relative mt-4 flex flex-col gap-4"]')
        first_element = table.locator('[data-index="0"]')
        images = first_element.locator('img[data-nimg="1"]')
        image_count = await images.count()
        downloaded_files = []
        for i in range(image_count):
            print(f"Downloading image {i + 1} of {image_count}")
            image = images.nth(i)
            image_src = await image.get_attribute("src")
            response = await self.page.request.get(image_src)
            filename = f"{base_filename}_gen_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(await response.body())
            downloaded_files.append(filepath)
        return downloaded_files

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()
