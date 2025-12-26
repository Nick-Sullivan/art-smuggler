export interface ImageProcessorViewModel {
  formData: ImageFormData;
  healthResponse: string;
  processResponse: ProcessMessage[];
  isProcessing: boolean;
  isComplete: boolean;
  resultImageUrls: Record<number, string>;
  handleHealthCheck: () => Promise<void>;
  handleFileChange: (file: File | null) => void;
  handleInputChange: (id: string, value: number) => void;
  handleSubmit: () => Promise<void>;
  handleViewInProjector: () => void;
}

export interface ProcessMessage {
  message: string;
  timestamp: string;
}

export interface ImageFormData {
  targetFile: File | null;
  numImages: number;
  numPieces: number;
  imgSize: number;
  seed: number;
  maxIterations: number;
  tolerance: number;
  minBrightness: number;
}

export interface ProcessImageParams {
  targetFile: File;
  numImages: number;
  numPieces: number;
  imgSize: number;
  seed: number;
  maxIterations: number;
  tolerance: number;
  minBrightness: number;
}

export const DEFAULT_FORM_DATA: ImageFormData = {
  targetFile: null,
  numImages: 4,
  numPieces: 500,
  imgSize: 2000,
  seed: 1,
  maxIterations: 100,
  tolerance: 0.05,
  minBrightness: 0.4,
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
