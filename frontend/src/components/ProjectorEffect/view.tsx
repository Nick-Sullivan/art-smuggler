import { ProjectorEffectViewModel } from "./model";
import "./styles.css";

interface ProjectorEffectProps {
  viewModel: ProjectorEffectViewModel;
}

export function ProjectorEffectView({ viewModel }: ProjectorEffectProps) {
  return (
    <>
      <div className="projector-header">
        <h1>Interactive Projector</h1>
        <button onClick={viewModel.handleStackImages}>Stack Images</button>
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
