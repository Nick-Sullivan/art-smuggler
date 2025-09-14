import { DraggableImage } from "../types.js";

export class DragHandler {
  private images: DraggableImage[];
  private lastDraggedImage: DraggableImage | null = null;
  private onDragCallback: () => void;

  constructor(images: DraggableImage[], onDragCallback: () => void) {
    this.images = images;
    this.onDragCallback = onDragCallback;
    this.addEventListeners();
  }

  private addEventListeners(): void {
    this.images.forEach((img) => {
      img.element.addEventListener("mousedown", (e) => this.startDrag(e, img));
    });
    document.addEventListener("mousemove", (e) => this.drag(e));
    document.addEventListener("mouseup", () => this.stopDrag());
    document.addEventListener("keydown", (e) => this.handleKeyPress(e));
  }

  private startDrag(e: MouseEvent, img: DraggableImage): void {
    img.isDragging = true;
    img.startX = e.clientX - img.currentX;
    img.startY = e.clientY - img.currentY;
    img.element.style.cursor = "grabbing";
    this.lastDraggedImage = img;
    e.preventDefault();
  }

  private drag(e: MouseEvent): void {
    this.images.forEach((img) => {
      if (img.isDragging) {
        img.currentX = e.clientX - img.startX;
        img.currentY = e.clientY - img.startY;
        img.element.style.left = `${img.currentX}px`;
        img.element.style.top = `${img.currentY}px`;
        this.onDragCallback();
      }
    });
  }

  private stopDrag(): void {
    this.images.forEach((img) => {
      img.isDragging = false;
      img.element.style.cursor = "grab";
    });
  }

  private handleKeyPress(e: KeyboardEvent): void {
    if (!this.lastDraggedImage) {
      return;
    }
    const nudgeAmount = 1;
    let moved = false;
    switch (e.key) {
      case "ArrowUp":
        this.lastDraggedImage.currentY -= nudgeAmount;
        moved = true;
        break;
      case "ArrowDown":
        this.lastDraggedImage.currentY += nudgeAmount;
        moved = true;
        break;
      case "ArrowLeft":
        this.lastDraggedImage.currentX -= nudgeAmount;
        moved = true;
        break;
      case "ArrowRight":
        this.lastDraggedImage.currentX += nudgeAmount;
        moved = true;
        break;
    }
    if (moved) {
      this.lastDraggedImage.element.style.left = `${this.lastDraggedImage.currentX}px`;
      this.lastDraggedImage.element.style.top = `${this.lastDraggedImage.currentY}px`;
      this.onDragCallback();
      e.preventDefault();
    }
  }

  public cleanup(): void {
    document.removeEventListener("mousemove", (e) => this.drag(e));
    document.removeEventListener("mouseup", () => this.stopDrag());
    document.removeEventListener("keydown", (e) => this.handleKeyPress(e));
  }
}
