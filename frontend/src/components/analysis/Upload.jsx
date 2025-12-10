import { useState, useRef } from "react";
import axios from "axios";
import Dashboard from "./Dashboard";
import "./upload.css";

export default function Upload() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);   // ⭐ NUEVO
  const fileInputRef = useRef(null);

  // =============================
  // FUNCIÓN PRINCIPAL
  // =============================
  const handleFileSelection = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setErrorMsg(null); // limpiar error anterior
    sendToBackend(file);
  };

  // =============================
  // CLICK EN EL LOADER → ABRIR EXPLORADOR
  // =============================
  const triggerFilePicker = () => {
    if (!loading) fileInputRef.current.click();
  };

  // =============================
  // ENVIAR ARCHIVO AL BACKEND
  // =============================
  const sendToBackend = async (file) => {
    setLoading(true);
    setErrorMsg(null); // limpiar errores previos

    const formData = new FormData();
    formData.append("dataset", file);

    try {
      const res = await axios.post(
        "http://localhost:5000/api/predict",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      // Si el backend devolvió status=error igualmente cae en catch
      setResult(res.data);
    } catch (error) {
      console.error(error);

      // ⭐ Caso 1: error controlado del backend
      if (error.response && error.response.data && error.response.data.message) {
        setErrorMsg(error.response.data.message);
      }
      // ⭐ Caso 2: error de red / servidor
      else {
        setErrorMsg("Ocurrió un error inesperado procesando el archivo.");
      }
    }

    setLoading(false);
  };

  // =============================
  // UI PRINCIPAL
  // =============================
  return (
    <div className="upload-container">

      {/* MOSTRAR LOADER SI NO HAY RESULTADO */}
      {!result && (
        <>
          <h1 className="main-title">Clasificación de Ransomware vs Benigno</h1>

          <p className="upload-subtitle">
            Haz clic en el círculo para subir un archivo
          </p>

          {/* === LOADER INTERACTIVO === */}
          <div className="scan-loader" onClick={triggerFilePicker}>
            <div className="scan-inner-circle"></div>
            <div className="scan-outer-circle"></div>
            <div className="scan-arrow">↑</div>
          </div>

          {/* INPUT OCULTO */}
          <input
            type="file"
            accept=".csv"
            ref={fileInputRef}
            onChange={handleFileSelection}
            style={{ display: "none" }}
          />

          {/* DESCRIPCIÓN */}
          <p className="upload-description">
            Este analizador utiliza modelos avanzados de Machine Learning para identificar
            patrones asociados a malware tipo <b>Ransomware</b>.
            <br /><br />
            Al subir un archivo <b>.CSV</b>, el sistema procesará sus características,
            calculará el nivel de riesgo y mostrará un reporte técnico detallado.
            <br /><br />
            <span className="desc-small">
              Ningún archivo es almacenado. El análisis se ejecuta localmente.
            </span>
          </p>

          {/* LOADING */}
          {loading && <p className="loading">Analizando archivo...</p>}

          {/* ⭐ MENSAJE DE ERROR */}
          {errorMsg && (
            <div className="error-box">
              ⚠ {errorMsg}
            </div>
          )}
        </>
      )}

      {/* RESULTADOS */}
      {result && <Dashboard data={result} />}
    </div>
  );
}
