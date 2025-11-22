import { DraggableImage } from "../types.js";

export function renderBlendedCanvas(
  canvas: HTMLCanvasElement,
  images: DraggableImage[],
  container: HTMLElement
): void {
  if (images.length === 0) {
    canvas.style.display = "none";
    return;
  }
  canvas.style.display = "block";
  canvas.style.left = "0px";
  canvas.style.top = "0px";
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  const ctx = canvas.getContext("2d")!;

  const bgColor = window.getComputedStyle(container).backgroundColor;
  ctx.fillStyle = bgColor || "white";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.globalCompositeOperation = "multiply";
  for (const image of images) {
    const imageRect = image.element.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const x = imageRect.left - containerRect.left;
    const y = imageRect.top - containerRect.top;
    const width = imageRect.width;
    const height = imageRect.height;
    ctx.drawImage(image.canvas, x, y, width, height);
  }
}
