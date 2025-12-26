import { ImageProcessorView } from "./view";
import { useImageProcessorViewModel } from "./viewModel";

export default function ImageProcessor() {
  const viewModel = useImageProcessorViewModel();
  return <ImageProcessorView viewModel={viewModel} />;
}
