import "./dashboard.css";
import Gauge from "./Gauge";

export default function Dashboard({ data }) {
  const {
    clase_dominante,
    confianza,
    precision,
    recall,
    f1_score,
    nivel_riesgo,

    // PANEL 3 — ARCHIVO
    file_name,
    file_size,
    fecha_analisis,
    hash_md5,
    hash_sha256,

    // PANEL 4 — MODELO
    file_hash,
    total_features,
    tiempo_analisis,
    dataset_version,
    environment,
    libraries,

    top_features = [],
    reporte_url, // ← AGREGADO
  } = data;

  const gaugeValue = confianza;

  const benignColor = "#1E90FF";
  const trojanColor = "#B100FF";

  // 🔒 Riesgo forzado por clase (regla final)
  const riesgoFinal = clase_dominante === "Trojan" ? "Alto" : "Bajo";

  const riesgoColor = clase_dominante === "Trojan" ? "#ff4d4d" : "#64ebe5";

  return (
    <div className="dashboard-container">
      {/* === GRID 2 × 2 REAL === */}
      <div className="grid-2x2">
        {/* PANEL 1 */}

        <div className="panel panel-gauge">
          <h2
            className={`section-title ${
              clase_dominante === "Trojan" ? "trojan-title" : "benign-title"
            }`}
          >
            RESULTADO DEL ANÁLISIS
          </h2>

          <span
            className={`result-label ${
              clase_dominante === "Trojan" ? "label-trojan" : "label-benign"
            }`}
          >
            {clase_dominante}
          </span>

          <Gauge value={gaugeValue} clase={clase_dominante} />

          {/*<p className="confidence-text">Confianza promedio del modelo</p>

            <div className="metrics-grid">
            <div className="metric-card">
              <p>Precisión</p>
              <h3>{precision?.toFixed(2)}%</h3>
            </div>
            <div className="metric-card">
              <p>Recall</p>
              <h3>{recall?.toFixed(2)}%</h3>
            </div>
            <div className="metric-card">
              <p>F1-Score</p>
              <h3>{f1_score?.toFixed(2)}%</h3>
            </div>
          </div>*/}

          <p className="risk-label">
            <b>Nivel de Riesgo:</b>{" "}
            <span style={{ color: riesgoColor }}>{riesgoFinal}</span>
          </p>

          <div className="risk-bar">
            <div
              className="risk-fill"
              style={{
                width: `${gaugeValue}%`,
                background:
                  clase_dominante === "Trojan"
                    ? "linear-gradient(90deg, #000000 0%, #bfbfbf 45%, #B100FF 100%)"
                    : "linear-gradient(90deg, #000000 0%, #bfbfbf 45%, #64EBE5 100%)",
              }}
            ></div>
          </div>
        </div>

        {/* PANEL 2 — FEATURES */}
        <div className="panel panel-features">
          <h2
            className={`section-title ${
              clase_dominante === "Trojan" ? "trojan-title" : "benign-title"
            }`}
          >
            TOP CARACTERÍSTICAS INFLUYENTES
          </h2>

          <ul className="features-list">
            {top_features.map((f, i) => (
              <li key={i} className="feature-item">
                <span>{f.caracteristica}</span>

                <div className="bar-bg">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${f.importancia}%`,
                      background:
                        clase_dominante === "Trojan"
                          ? trojanColor
                          : benignColor,
                    }}
                  ></div>
                </div>

                <span className="percent">{f.importancia}%</span>
              </li>
            ))}
          </ul>
        </div>

        {/* PANEL 3 — ARCHIVO */}
        <div className="panel panel-file">
          <h2
            className={`section-title ${
              clase_dominante === "Trojan" ? "trojan-title" : "benign-title"
            }`}
          >
            INFORMACIÓN TÉCNICA DEL ARCHIVO ANALIZADO
          </h2>

          <table className="info-table clean-table">
            <tbody>
              <tr>
                <td>Archivo:</td>
                <td>{file_name}</td>
              </tr>
              <tr>
                <td>Tipo:</td>
                <td>text/csv</td>
              </tr>
              <tr>
                <td>Tamaño:</td>
                <td>{file_size} KB</td>
              </tr>
              <tr>
                <td>Fecha:</td>
                <td>{fecha_analisis}</td>
              </tr>
              <tr>
                <td>Hash MD5:</td>
                <td>{hash_md5}</td>
              </tr>
              <tr>
                <td>Hash SHA256:</td>
                <td>{hash_sha256}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* PANEL 4 — MODELO */}
        <div className="panel panel-model">
          <h2
            className={`section-title ${
              clase_dominante === "Trojan" ? "trojan-title" : "benign-title"
            }`}
          >
            FICHA TÉCNICA DEL ANÁLISIS Y DEL MODELO
          </h2>

          <table className="info-table clean-table">
            <tbody>
              <tr>
                <td>ID análisis:</td>
                <td>{file_hash}</td>
              </tr>
              <tr>
                <td>Total características:</td>
                <td>{total_features}</td>
              </tr>
              <tr>
                <td>Dataset:</td>
                <td>{dataset_version}</td>
              </tr>
              <tr>
                <td>Tiempo:</td>
                <td>{tiempo_analisis} s</td>
              </tr>
              <tr>
                <td>Modelo:</td>
                <td>RandomForest</td>
              </tr>

              <tr>
                <td>Clasificación:</td>
                <td>
                  {clase_dominante === "Trojan" && (
                    <span style={{ color: "#ff4d4d", fontWeight: "bold" }}>
                      Trojan
                    </span>
                  )}
                  {clase_dominante === "Benign" && (
                    <span style={{ color: "#00cc66", fontWeight: "bold" }}>
                      Benign
                    </span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* =======================================
          BOTÓN PDF (NUEVO)
      ======================================= */}
      {reporte_url && (
        <div className="pdf-container">
          <button
            className="pdf-button"
            style={{
              backgroundColor:
                clase_dominante === "Trojan" ? trojanColor : benignColor,
              boxShadow:
                clase_dominante === "Trojan"
                  ? "0 0 18px rgba(177, 0, 255, 0.7)"
                  : "0 0 18px rgba(30, 144, 255, 0.7)",
            }}
            onClick={() => {
              // Fuerza que sea solo ruta relativa
              const relativeUrl = reporte_url.startsWith("/report")
                ? reporte_url
                : new URL(reporte_url).pathname + new URL(reporte_url).search;

              // Abre con tu backend en Render
              window.open(
                `${import.meta.env.VITE_API_URL}${relativeUrl}`,
                "_blank",
              );
            }}
          >
            🖨️ Generar Reporte PDF
          </button>
        </div>
      )}
    </div>
  );
}
