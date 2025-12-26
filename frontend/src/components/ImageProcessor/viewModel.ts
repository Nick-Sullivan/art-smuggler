import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { handleSSEStream } from "../../utils/parseServerSentEvents";
import {
  DEFAULT_FORM_DATA,
  ImageFormData,
  ImageProcessorViewModel,
  MAX_FILE_SIZE,
  ProcessMessage,
} from "./model";

export function useImageProcessorViewModel(): ImageProcessorViewModel {
  const [formData, setFormData] = useState<ImageFormData>(DEFAULT_FORM_DATA);
  const [healthResponse, setHealthResponse] = useState("");
  const [processResponse, setProcessResponse] = useState<ProcessMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [resultImageUrls, setResultImageUrls] = useState<
    Record<number, string>
  >({});
  const navigate = useNavigate();

  const handleHealthCheck = async () => {
    setHealthResponse("Loading...");
    try {
      const res = await fetch("http://localhost:8000/health");
      const data = await res.text();
      setHealthResponse(`Status: ${res.status}\n\n${data}`);
    } catch (error) {
      setHealthResponse(`Error: ${(error as Error).message}`);
    }
  };

  const handleFileChange = (file: File | null) => {
    if (!file) {
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      alert(
        `File size exceeds ${
          MAX_FILE_SIZE / (1024 * 1024)
        }MB limit. Selected file is ${(file.size / (1024 * 1024)).toFixed(
          2
        )}MB.`
      );
      return;
    }

    setFormData({ ...formData, targetFile: file });
  };

  const handleInputChange = (id: string, value: number) => {
    setFormData({
      ...formData,
      [id]: value,
    });
  };

  const handleSubmit = async () => {
    if (!formData.targetFile) {
      alert("Error: Please select a file");
      return;
    }

    setIsProcessing(true);
    setIsComplete(false);
    setProcessResponse([]);
    setResultImageUrls({});

    try {
      const formDataToSend = new FormData();
      formDataToSend.append("target_file", formData.targetFile);
      formDataToSend.append("num_images", formData.numImages.toString());
      formDataToSend.append("num_pieces", formData.numPieces.toString());
      formDataToSend.append("img_size", formData.imgSize.toString());
      formDataToSend.append("seed", formData.seed.toString());
      formDataToSend.append(
        "max_iterations",
        formData.maxIterations.toString()
      );
      formDataToSend.append("tolerance", formData.tolerance.toString());
      formDataToSend.append(
        "min_brightness",
        formData.minBrightness.toString()
      );

      const res = await fetch("http://localhost:8000/process-image", {
        method: "POST",
        body: formDataToSend,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      await handleSSEStream(res, (type, data) => {
        switch (type) {
          case "status":
            setProcessResponse((prev) => [
              ...prev,
              {
                message: data.message,
                timestamp: data.timestamp,
              },
            ]);
            break;

          case "image":
            const url = `data:image/png;base64,${data.image}`;
            setResultImageUrls((prev) => ({
              ...prev,
              [data.index]: url,
            }));
            setProcessResponse((prev) => [
              ...prev,
              {
                message: `Image ${data.index + 1} updated.`,
                timestamp: new Date().toISOString(),
              },
            ]);
            break;

          case "complete":
            setProcessResponse((prev) => [
              ...prev,
              {
                message: "Finished.",
                timestamp: new Date().toISOString(),
              },
            ]);
            setIsComplete(true);
            break;

          case "error":
            throw new Error(data.error);

          default:
            console.log("Unknown event type:", type, data);
        }
      });
    } catch (error) {
      setProcessResponse([
        {
          message: `Error: ${(error as Error).message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleViewInProjector = () => {
    const imageUrls = Object.values(resultImageUrls);
    navigate("/projector", { state: { imageUrls } });
  };

  return {
    formData,
    healthResponse,
    processResponse,
    isProcessing,
    isComplete,
    resultImageUrls,
    handleHealthCheck,
    handleFileChange,
    handleInputChange,
    handleSubmit,
    handleViewInProjector,
  };
}
