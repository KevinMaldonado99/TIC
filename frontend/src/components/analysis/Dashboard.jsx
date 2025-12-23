import "./dashboard.css";
import Gauge from "./Gauge";

export default function Dashboard({ data }) {
  const {
    clase_dominante,
    confianza,
    nivel_riesgo,
    file_hash,
    total_features,
    tiempo_analisis,
    dataset_version,
    top_features = [],
  } = data;

  const gaugeValue = confianza;

  // 🎨 PALETA FINAL
  const benignColor = "#6FA8FF";
  const ransomwareColor = "#7C89D6";

  const riskColors = {
    Bajo: "#5BC8B1",
    Medio: "#E6B35C",
    Alto: "#E55353",
  };

  return (
    <div className="dashboard-container">

      {/* =============================
          FILA 1 — GAUGE + FICHA TÉCNICA
      ============================== */}
      <div className="row-top">

        {/* PANEL GAUGE */}
        <div className="panel panel-gauge">
          <h2
            className={`section-title ${
              clase_dominante === "Ransomware"
                ? "Ransomware-title"
                : "benign-title"
            }`}
          >
            RESULTADO DEL ANÁLISIS
          </h2>

          <span
            className={`result-label ${
              clase_dominante === "Ransomware"
                ? "label-Ransomware"
                : "label-benign"
            }`}
          >
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
                    ? "linear-gradient(90deg, #0A1322 0%, #3A4A6A 50%, #E55353 100%)"
                    : nivel_riesgo === "Medio"
                    ? "linear-gradient(90deg, #0A1322 0%, #3A4A6A 50%, #E6B35C 100%)"
                    : "linear-gradient(90deg, #0A1322 0%, #3A4A6A 50%, #5BC8B1 100%)",
              }}
            ></div>
          </div>
        </div>

        {/* PANEL FICHA TÉCNICA (AHORA ARRIBA) */}
        <div className="panel panel-model">
          <h2
            className={`section-title ${
              clase_dominante === "Ransomware"
                ? "Ransomware-title"
                : "benign-title"
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
                <td>Modelo:</td>
                <td>{dataset_version}</td>
              </tr>
              <tr>
                <td>Tiempo:</td>
                <td>{tiempo_analisis} s</td>
              </tr>
              <tr>
                <td>Clasificación:</td>
                <td>
                  <span
                    style={{
                      color:
                        clase_dominante === "Ransomware"
                          ? ransomwareColor
                          : benignColor,
                      fontWeight: "bold",
                    }}
                  >
                    {clase_dominante}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* =============================
          FILA 2 — CARACTERÍSTICAS (ABAJO)
      ============================== */}
      <div className="row-bottom">
        <div className="panel panel-features centered-panel">
          <h2
            className={`section-title ${
              clase_dominante === "Ransomware"
                ? "Ransomware-title"
                : "benign-title"
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
                          ? ransomwareColor
                          : benignColor,
                    }}
                  ></div>
                </div>

                <span className="percent">{f.importancia}%</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

    </div>
  );
}
