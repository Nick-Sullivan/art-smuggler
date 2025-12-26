import { FormEvent } from "react";
import { Link } from "react-router-dom";
import { ImageProcessorViewModel } from "./model";
import "./styles.css";

interface ImageProcessorProps {
  viewModel: ImageProcessorViewModel;
}

export function ImageProcessorView({ viewModel }: ImageProcessorProps) {
  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (!file) {
      return;
    }
    viewModel.handleFileChange(file);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    viewModel.handleInputChange(e.target.id, parseFloat(e.target.value));
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    viewModel.handleSubmit();
  };

  const hasResults = Object.keys(viewModel.resultImageUrls).length > 0;

  return (
    <div className="image-processor">
      <h1>
        <Link to="/projector">Interactive Projector</Link>
      </h1>

      <button className="health-btn" onClick={viewModel.handleHealthCheck}>
        Check Health
      </button>

      {viewModel.healthResponse && (
        <div className="response-display">{viewModel.healthResponse}</div>
      )}

      <h2>Process Image</h2>
      <form className="process-form" onSubmit={onSubmit}>
        <div className="form-group">
          <label htmlFor="targetFile">Target Image:</label>
          <input
            type="file"
            id="targetFile"
            accept="image/*"
            required
            onChange={onFileChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="numImages">Number of Images:</label>
          <input
            type="number"
            id="numImages"
            value={viewModel.formData.numImages}
            min="1"
            onChange={onInputChange}
          />
        </div>

        {/* <div className="form-group">
          <label htmlFor="imgSize">Image Size:</label>
          <input
            type="number"
            id="imgSize"
            value={viewModel.formData.imgSize}
            min="1"
            onChange={onInputChange}
          />
        </div> */}

        <button
          type="submit"
          className="submit-btn"
          disabled={viewModel.isProcessing}
        >
          {viewModel.isProcessing ? "Processing..." : "Process Image"}
        </button>
      </form>

      {viewModel.processResponse && (
        <div className="response-display">{viewModel.processResponse}</div>
      )}

      {viewModel.isComplete && (
        <button
          className="view-projector-btn"
          onClick={viewModel.handleViewInProjector}
        >
          View in Projector
        </button>
      )}

      {hasResults && (
        <div>
          {Object.entries(viewModel.resultImageUrls).map(([index, url]) => (
            <img
              key={index}
              src={url}
              alt={`Result ${index}`}
              className="result-image"
            />
          ))}
        </div>
      )}
    </div>
  );
}
