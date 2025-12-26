export interface ProjectorEffectViewModel {
  currentMode: BlendMode;
  isBackgroundBlack: boolean;
  imageUrls: string[];
  containerRef: React.RefObject<HTMLDivElement>;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  handleStackImages: () => void;
  handleToggleMode: () => void;
  handleToggleBackground: () => void;
}

export type BlendMode = "stack" | "project";

export const DEFAULT_MODE: BlendMode = "stack";
export const DEFAULT_BACKGROUND_BLACK = false;
