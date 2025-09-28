import { renderBlendedCanvas } from "./blending/renderBlendedImage.js";
import { DragHandler } from "./interaction/dragHandler.js";
import { DraggableImage } from "./types.js";
import { loadImageData } from "./utils/loadImageData.js";

import image0 from "./data/005_london/output_image_marked_0.png";
import image1 from "./data/005_london/output_image_marked_1.png";
import image2 from "./data/005_london/output_image_marked_2.png";
import image3 from "./data/005_london/output_image_marked_3.png";
import image4 from "./data/005_london/output_image_marked_base.png";

class ProjectorEffect {
  private imageUrls = [image0, image1, image2, image3, image4];
  private images: DraggableImage[] = [];
  private container: HTMLElement;
  private blendCanvas: HTMLCanvasElement;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId)!;
    this.blendCanvas = this.setupCanvas();
    this.setupStackButton();
    this.init().catch(console.error);
  }

  private async init(): Promise<void> {
    await this.setupImages();
    new DragHandler(this.images, () => this.updateCanvas());
    this.updateCanvas();
  }

  private setupStackButton(): void {
    const button = document.getElementById("center-images-btn");
    if (button) {
      button.addEventListener("click", () => this.stackImages());
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
      img.style.backgroundImage = `url(${this.imageUrls[index]})`;
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

  private stackImages(): void {
    this.images.forEach((draggableImage) => {
      draggableImage.currentX = 0;
      draggableImage.currentY = 0;
      draggableImage.element.style.left = `0px`;
      draggableImage.element.style.top = `0px`;
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
