import { DraggableImage } from "../hooks/useDraggable";

export function renderBlendedCanvas(
  canvas: HTMLCanvasElement,
  images: DraggableImage[],
  container: HTMLElement,
  bgColor: string
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

  ctx.fillStyle = bgColor;
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
