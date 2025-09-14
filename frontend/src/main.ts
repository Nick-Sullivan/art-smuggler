import { renderBlendedCanvas } from "./blending/renderBlendedImage.js";
import { DragHandler } from "./interaction/dragHandler.js";
import { DraggableImage } from "./types.js";
import { loadImageData } from "./utils/loadImageData.js";

class ProjectorEffect {
  private images: DraggableImage[] = [];
  private container: HTMLElement;
  private blendCanvas: HTMLCanvasElement;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId)!;
    this.blendCanvas = this.setupCanvas();
    this.setupCenterButton();
    this.init().catch(console.error);
  }

  private async init(): Promise<void> {
    await this.setupImages();
    new DragHandler(this.images, () => this.updateCanvas());
    this.updateCanvas();
  }

  private setupCenterButton(): void {
    const button = document.getElementById("center-images-btn");
    if (button) {
      button.addEventListener("click", () => this.centerAllImages());
    }
  }

  private setupCanvas(): HTMLCanvasElement {
    const canvas = document.createElement("canvas");
    canvas.style.position = "absolute";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = "10";
    this.container.appendChild(canvas);
    return canvas;
  }

  private async setupImages(): Promise<void> {
    const imageElements = this.container.querySelectorAll(".draggable-image");
    const containerWidth = this.container.clientWidth;
    const containerHeight = this.container.clientHeight;

    for (let index = 0; index < imageElements.length; index++) {
      const img = imageElements[index] as HTMLElement;

      const maxX = containerWidth - 350; // 350 is image width
      const maxY = containerHeight - 350; // 350 is image height
      const spacingX = Math.min(
        300,
        maxX / Math.max(1, imageElements.length - 1)
      );
      const spacingY = Math.min(
        150,
        maxY / Math.max(1, imageElements.length - 1)
      );

      const draggableImage: DraggableImage = {
        element: img,
        isDragging: false,
        startX: 0,
        startY: 0,
        currentX: Math.min(index * spacingX, maxX),
        currentY: Math.min(50 + index * spacingY, maxY),
        imageData: null,
        canvas: document.createElement("canvas"),
      };

      img.style.position = "absolute";
      img.style.left = `${draggableImage.currentX}px`;
      img.style.top = `${draggableImage.currentY}px`;
      img.style.cursor = "grab";
      await loadImageData(draggableImage);
      this.images.push(draggableImage);
    }
  }

  private centerAllImages(): void {
    const containerRect = this.container.getBoundingClientRect();
    const centerX = containerRect.width / 2 - 175; // 175 is half of image width (350px)
    const centerY = containerRect.height / 2 - 175; // 175 is half of image height (350px)

    this.images.forEach((draggableImage) => {
      draggableImage.currentX = centerX;
      draggableImage.currentY = centerY;
      draggableImage.element.style.left = `${centerX}px`;
      draggableImage.element.style.top = `${centerY}px`;
    });

    this.updateCanvas();
  }

  private updateCanvas(): void {
    renderBlendedCanvas(this.blendCanvas, this.images, this.container);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new ProjectorEffect("projector-container");
});
