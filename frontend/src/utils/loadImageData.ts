import { DraggableImage } from "../hooks/useDraggable";

export async function loadImageData(
  draggableImage: DraggableImage
): Promise<void> {
  const bgImage = window.getComputedStyle(
    draggableImage.element
  ).backgroundImage;
  const urlMatch = bgImage.match(/url\(["']?([^"']+)["']?\)/);
  if (!urlMatch) {
    throw new Error("No background image URL found");
  }
  const imageUrl = urlMatch[1];
  try {
    const img = new Image();
    img.crossOrigin = "anonymous";

    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
      img.src = imageUrl;
    });
    // Get the actual display dimensions
    const rect = draggableImage.element.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    // Set canvas to match display size
    draggableImage.canvas.width = width;
    draggableImage.canvas.height = height;
    const ctx = draggableImage.canvas.getContext("2d")!;
    ctx.drawImage(img, 0, 0, width, height);
    draggableImage.imageData = ctx.getImageData(0, 0, width, height);
  } catch (error) {
    console.warn("Could not load image:", imageUrl);
    throw error;
  }
}
