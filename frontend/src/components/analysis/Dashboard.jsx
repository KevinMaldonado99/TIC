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
  const RansomwareColor = "#B100FF";

  const riskColors = {
    Bajo: "#64ebe5",
    Medio: "orange",
    Alto: "red",
  };

  return (
    <div className="dashboard-container">

  {/* =============================
       FILA 1 — PANEL GAUGE + PANEL FEATURES
  ============================== */}
  <div className="row-top">
    {/* PANEL 1 */}
    <div className="panel panel-gauge">
      <h2 className={`section-title ${clase_dominante === "Ransomware" ? "Ransomware-title" : "benign-title"}`}>
        RESULTADO DEL ANÁLISIS
      </h2>

      <span className={`result-label ${clase_dominante === "Ransomware" ? "label-Ransomware" : "label-benign"}`}>
        {clase_dominante}
      </span>

      <Gauge value={gaugeValue} clase={clase_dominante} />

      <p className="risk-label">
        <b>Nivel de Riesgo:</b>{" "}
        <span style={{ color: riskColors[nivel_riesgo] }}>
          {nivel_riesgo}
        </span>
      </p>

      <div className="risk-bar">
        <div
          className="risk-fill"
          style={{
            width: `${gaugeValue}%`,
            background:
              nivel_riesgo === "Alto"
                ? "linear-gradient(90deg, #000000 0%, #bbbbbb 40%, #B100FF 100%)"
                : "linear-gradient(90deg, #000000 0%, #e0e0e0 40%, #64ebe5 100%)",
          }}
        ></div>
      </div>
    </div>

    {/* PANEL 2 — FEATURES */}
    <div className="panel panel-features">
      <h2
        className={`section-title ${
          clase_dominante === "Ransomware" ? "Ransomware-title" : "benign-title"
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
                    clase_dominante === "Ransomware"
                      ? "#B100FF"
                      : "#1E90FF",
                }}
              ></div>
            </div>
            <span className="percent">{f.importancia}%</span>
          </li>
        ))}
      </ul>
    </div>
  </div>

  {/* =============================
       FILA 2 — SOLO PANEL DEL MODELO (CENTRADO)
  ============================== */}
  <div className="row-bottom">
    <div className="panel panel-model centered-panel">
      <h2
        className={`section-title ${
          clase_dominante === "Ransomware" ? "Ransomware-title" : "benign-title"
        }`}
      >
        FICHA TÉCNICA DEL ANÁLISIS Y DEL MODELO
      </h2>

      <table className="info-table clean-table centered-table">
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
            <td>SMOTE</td>
          </tr>

          <tr>
            <td>Clasificación:</td>
            <td>
              {clase_dominante === "Ransomware" ? (
                <span style={{ color: "#ff4d4d", fontWeight: "bold" }}>
                  Ransomware
                </span>
              ) : (
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

  {/* BOTÓN PDF */}
  {reporte_url && (
    <div className="pdf-container">
      <button
        className="pdf-button"
        style={{
          backgroundColor:
            clase_dominante === "Ransomware" ? "#B100FF" : "#1E90FF",
        }}
        onClick={() =>
          window.open(`http://localhost:5000${reporte_url}`, "_blank")
        }
      >
        🖨️ Generar Reporte PDF
      </button>
    </div>
  )}

</div>

  );
}
