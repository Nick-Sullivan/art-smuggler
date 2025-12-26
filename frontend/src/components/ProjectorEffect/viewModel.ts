import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { renderBlendedCanvas } from "../../blending/renderBlendedCanvas";
import { renderStackedCanvas } from "../../blending/renderStackedCanvas";
import image0 from "../../data/009_cats/canvas_filled_0.png";
import image1 from "../../data/009_cats/canvas_filled_1.png";
import image2 from "../../data/009_cats/canvas_filled_2.png";
import image3 from "../../data/009_cats/canvas_filled_3.png";
import { useDraggable } from "../../hooks/useDraggable";
import {
  BlendMode,
  DEFAULT_BACKGROUND_BLACK,
  DEFAULT_MODE,
  ProjectorEffectViewModel,
} from "./model";

export function useProjectorEffectViewModel(): ProjectorEffectViewModel {
  const containerRef = useRef<HTMLDivElement>(null!);
  const canvasRef = useRef<HTMLCanvasElement>(null!);
  const [currentMode, setCurrentMode] = useState<BlendMode>(DEFAULT_MODE);
  const [isBackgroundBlack, setIsBackgroundBlack] = useState(
    DEFAULT_BACKGROUND_BLACK
  );
  const location = useLocation();
  const defaultImageUrls = [image0, image1, image2, image3];
  const imageUrls = (location.state?.imageUrls as string[]) || defaultImageUrls;
  const imagesRef = useRef<any[]>([]);

  const renderCanvas = () => {
    if (
      !canvasRef.current ||
      !containerRef.current ||
      !imagesRef.current.length
    ) {
      return;
    }

    const bgColor = isBackgroundBlack ? "#000000" : "#ffffff";

    if (currentMode === "stack") {
      renderStackedCanvas(
        canvasRef.current,
        imagesRef.current,
        containerRef.current,
        bgColor
      );
    } else {
      renderBlendedCanvas(
        canvasRef.current,
        imagesRef.current,
        containerRef.current,
        bgColor
      );
    }
  };

  const images = useDraggable(containerRef, renderCanvas);
  imagesRef.current = images;

  const handleStackImages = () => {
    images.forEach((img) => {
      img.currentX = 0;
      img.currentY = 0;
      img.element.style.left = "0px";
      img.element.style.top = "0px";
    });
    renderCanvas();
  };

  const handleToggleMode = () => {
    setCurrentMode((prev) => (prev === "stack" ? "project" : "stack"));
  };

  const handleToggleBackground = () => {
    setIsBackgroundBlack((prev) => !prev);
  };

  useEffect(() => {
    renderCanvas();
  }, [currentMode, isBackgroundBlack, images]);

  return {
    currentMode,
    isBackgroundBlack,
    imageUrls,
    containerRef,
    canvasRef,
    handleStackImages,
    handleToggleMode,
    handleToggleBackground,
  };
}
