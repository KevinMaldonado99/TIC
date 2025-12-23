import GaugeComponent from "react-gauge-component";

export default function Gauge({ value, clase }) {

  // 🎨 PALETA FINAL (alineada al background)
  const benignColor = "#6FA8FF";      // azul frío
  const benignLight = "#A9C8FF";      // azul claro

  const ransomwareColor = "#7C89D6";  // violeta azulado
  const ransomwareLight = "#B4BCEB";  // violeta claro

  const baseColor =
    clase === "Ransomware" ? ransomwareColor : benignColor;

  const lightColor =
    clase === "Ransomware" ? ransomwareLight : benignLight;

  return (
    <div
      className={`gauge-wrapper ${
        clase === "Ransomware" ? "gauge-Ransomware" : "gauge-benign"
      }`}
    >
      <GaugeComponent
        value={value}
        minValue={0}
        maxValue={100}
        type="semicircle"

        arc={{
          width: 0.15,
          padding: 0.02,
          colorArray: [lightColor, baseColor],
          subArcs: [
            { limit: value, color: baseColor },
            { limit: 100, color: "rgba(255,255,255,0.15)" }
          ],
        }}

        pointer={{
          color: baseColor,
          length: 0.7,
          width: 8,
        }}

        labels={{
          valueLabel: {
            formatTextValue: (val) => `${val.toFixed(2)}%`,
            style: {
              fill: "#E6EAF0",
              fontSize: "32px",
              fontWeight: "bold",
            },
          },
          tickLabels: {
            type: "inner",
            defaultTickValueConfig: {
              format: (val) => `${val}%`,
              style: {
                fill: "#AAB4C3",
                fontSize: "12px",
              },
            },
          },
        }}

        style={{ width: "340px", margin: "0 auto" }}
      />
    </div>
  );
}
