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

  ctx.imageSmoothingEnabled = false;

  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.globalCompositeOperation = "multiply";

  for (const image of images) {
    const imageRect = image.element.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const x = Math.round(imageRect.left - containerRect.left);
    const y = Math.round(imageRect.top - containerRect.top);
    const width = Math.round(imageRect.width);
    const height = Math.round(imageRect.height);

    if (image.imageData) {
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = image.imageData.width;
      tempCanvas.height = image.imageData.height;
      const tempCtx = tempCanvas.getContext("2d")!;
      tempCtx.imageSmoothingEnabled = false;
      tempCtx.putImageData(image.imageData, 0, 0);
      ctx.drawImage(tempCanvas, x, y, width, height);
    } else {
      ctx.drawImage(image.canvas, x, y, width, height);
    }
  }
}
