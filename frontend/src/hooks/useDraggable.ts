import { RefObject, useEffect, useRef, useState } from "react";
import { loadImageData } from "../utils/loadImageData";

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

export function useDraggable(
  containerRef: RefObject<HTMLDivElement>,
  onDragCallback: () => void
) {
  const [images, setImages] = useState<DraggableImage[]>([]);
  const imagesRef = useRef<DraggableImage[]>([]);
  const lastDraggedImageRef = useRef<DraggableImage | null>(null);
  const callbackRef = useRef(onDragCallback);

  callbackRef.current = onDragCallback;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleMouseDown = (e: MouseEvent, img: DraggableImage) => {
      img.isDragging = true;
      img.startX = e.clientX - img.currentX;
      img.startY = e.clientY - img.currentY;
      img.element.style.cursor = "grabbing";
      lastDraggedImageRef.current = img;
      e.preventDefault();
    };

    const handleMouseMove = (e: MouseEvent) => {
      imagesRef.current.forEach((img) => {
        if (img.isDragging) {
          img.currentX = e.clientX - img.startX;
          img.currentY = e.clientY - img.startY;
          img.element.style.left = `${img.currentX}px`;
          img.element.style.top = `${img.currentY}px`;
          callbackRef.current();
        }
      });
    };

    const handleMouseUp = () => {
      imagesRef.current.forEach((img) => {
        img.isDragging = false;
        img.element.style.cursor = "grab";
      });
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      const lastDraggedImage = lastDraggedImageRef.current;
      if (!lastDraggedImage) return;

      const nudgeAmount = 1;
      let moved = false;

      switch (e.key) {
        case "ArrowUp":
          lastDraggedImage.currentY -= nudgeAmount;
          moved = true;
          break;
        case "ArrowDown":
          lastDraggedImage.currentY += nudgeAmount;
          moved = true;
          break;
        case "ArrowLeft":
          lastDraggedImage.currentX -= nudgeAmount;
          moved = true;
          break;
        case "ArrowRight":
          lastDraggedImage.currentX += nudgeAmount;
          moved = true;
          break;
      }

      if (moved) {
        lastDraggedImage.element.style.left = `${lastDraggedImage.currentX}px`;
        lastDraggedImage.element.style.top = `${lastDraggedImage.currentY}px`;
        callbackRef.current();
        e.preventDefault();
      }
    };

    const setupImages = async () => {
      const imageElements = container.querySelectorAll(".draggable-image");
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
      const newImages: DraggableImage[] = [];

      for (let index = 0; index < imageElements.length; index++) {
        const img = imageElements[index] as HTMLElement;
        const maxX = containerWidth - 350;
        const maxY = containerHeight - 350;
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

        img.style.left = `${draggableImage.currentX}px`;
        img.style.top = `${draggableImage.currentY}px`;

        await loadImageData(draggableImage);
        img.addEventListener("mousedown", (e) =>
          handleMouseDown(e, draggableImage)
        );
        newImages.push(draggableImage);
      }

      imagesRef.current = newImages;
      setImages(newImages);
      callbackRef.current();
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    document.addEventListener("keydown", handleKeyDown);
    setupImages();

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return images;
}
