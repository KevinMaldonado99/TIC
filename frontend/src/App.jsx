import DarkVeil from "./components/backgrounds/DarkVeil";
import Upload from "./components/analysis/Upload";
import "./App.css";

export default function App() {
  return (
    <div className="app-container">
      {/* Fondo animado */}
      <DarkVeil />

      {/* Contenido frontal */}
      <div className="app-content">
        <Upload />
      </div>
    </div>
  );
}
