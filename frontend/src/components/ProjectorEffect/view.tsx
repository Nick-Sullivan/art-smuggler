import { ProjectorEffectViewModel } from "./model";
import "./styles.css";

interface ProjectorEffectProps {
  viewModel: ProjectorEffectViewModel;
}

export function ProjectorEffectView({ viewModel }: ProjectorEffectProps) {
  const handleDownload = async () => {
    // Create a temporary canvas to combine the images
    const tempCanvas = document.createElement("canvas");
    const ctx = tempCanvas.getContext("2d");
    if (!ctx) return;

    // Load all images
    const imageElements = await Promise.all(
      viewModel.imageUrls.map((url) => {
        return new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = url;
        });
      })
    );

    // Set canvas size to match the images
    const firstImg = imageElements[0];
    tempCanvas.width = firstImg.width;
    tempCanvas.height = firstImg.height;

    // Draw all images on top of each other (combined)
    imageElements.forEach((img) => {
      ctx.drawImage(img, 0, 0);
    });

    // Download the combined image
    const dataURL = tempCanvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.href = dataURL;
    link.download = `combined-images-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="projector-header">
        <h1>Interactive Projector</h1>
        <button onClick={viewModel.handleStackImages}>Stack Images</button>
        <button onClick={handleDownload}>Download Combined Image</button>
        <button onClick={viewModel.handleToggleMode}>
          Mode:{" "}
          {viewModel.currentMode.charAt(0).toUpperCase() +
            viewModel.currentMode.slice(1)}
        </button>
        <button onClick={viewModel.handleToggleBackground}>
          Background: {viewModel.isBackgroundBlack ? "Black" : "White"}
        </button>
      </div>

      <div
        ref={viewModel.containerRef}
        className="projector-container"
        style={{
          backgroundColor: viewModel.isBackgroundBlack ? "#000000" : "#ffffff",
        }}
      >
        <canvas ref={viewModel.canvasRef} className="projector-canvas" />
        {viewModel.imageUrls.map((url, index) => (
          <div
            key={index}
            id={`image-${index}`}
            className="draggable-image"
            style={{
              backgroundImage: `url(${url})`,
            }}
          />
        ))}
      </div>
    </>
  );
}
