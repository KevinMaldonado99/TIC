import { useState } from "react";
import axios from "axios";
import Dashboard from "./Dashboard";
import Dropzone from "./Dropzone";
import "./upload.css";

export default function Upload() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // =============================
  // ENVIAR ARCHIVO AL BACKEND
  // =============================
  const sendToBackend = async (file) => {
    if (!file) return;

    setLoading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append("dataset", file);

    try {
      const res = await axios.post(
        "http://localhost:5000/api/predict",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
    } catch (error) {
      console.error(error);

      setErrorMsg(
        error.response?.data?.message ||
        "Ocurrió un error inesperado procesando el archivo."
      );
    }

    setLoading(false);
  };

  // =============================
  // UI PRINCIPAL
  // =============================
  return (
    <div className="upload-container">

      {!result && (
        <>
          <h1 className="main-title">Clasificador de archivos Ransomware y benignos</h1>

          <p className="upload-subtitle">
            Haz clic o arrastra tu archivo en formato CSV.
          </p>

          {/* 🔹 TARJETA DRAG & DROP */}
          <Dropzone
            onFileSelected={sendToBackend}
            disabled={loading}
          />

          {/* 🔹 ESTADO DE PROCESO */}
          {loading && (
            <p className="loading">
              Analizando archivo…
            </p>
          )}

          {/* 🔹 MENSAJE DE ERROR */}
          {errorMsg && (
            <div className="error-box">
              ⚠ {errorMsg}
            </div>
          )}

          {/* 🔹 DESCRIPCIÓN */}
          <p className="upload-description">
            Este prototipo clasifica archivos para determinar si corresponden a
            <b> ransomware</b> o a <b>software benigno</b>.
            <br /><br />
            Al cargar el archivo, el sistema mostrará el resultado de la
            clasificación, el nivel de confianza asignado, las características
            que más influyeron en la decisión y un resumen técnico del análisis
            realizado.
          </p>
        </>
      )}

      {/* RESULTADOS */}
      {result && <Dashboard data={result} />}
    </div>
  );
}
