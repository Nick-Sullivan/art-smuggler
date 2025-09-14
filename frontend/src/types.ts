export interface DraggableImage {
  element: HTMLElement;
  isDragging: boolean;
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
  imageData: ImageData | null;
  canvas: HTMLCanvasElement;
}
