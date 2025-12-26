import { BrowserRouter, Route, Routes } from "react-router-dom";
import ImageProcessor from "../ImageProcessor";
import ProjectorEffect from "../ProjectorEffect";
import "./styles.css";

function App() {
  return (
    <BrowserRouter basename="/art-smuggler">
      <Routes>
        <Route path="/" element={<ImageProcessor />} />
        <Route path="/projector" element={<ProjectorEffect />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
