import GaugeComponent from "react-gauge-component";

export default function Gauge({ value, clase }) {

  // 🎨 Paleta Multiclase
  const classPalette = {
    Ransomware: {
      base: "#E55353",      // rojo
      light: "#F5A3A3",
      wrapper: "gauge-Ransomware"
    },
    Trojan: {
      base: "#FF9900",      // naranja
      light: "#FFD199",
      wrapper: "gauge-Trojan"
    },
    Benign: {
      base: "#5BC8B1",      // verde
      light: "#A5E4D8",
      wrapper: "gauge-Benign"
    }
  };

  const current = classPalette[clase] || classPalette["Benign"];

  return (
    <div className={`gauge-wrapper ${current.wrapper}`}>
      <GaugeComponent
        value={value}
        minValue={0}
        maxValue={100}
        type="semicircle"

        arc={{
          width: 0.15,
          padding: 0.02,
          colorArray: [current.light, current.base],
          subArcs: [
            { limit: value, color: current.base },
            { limit: 100, color: "rgba(255,255,255,0.15)" }
          ],
        }}

        pointer={{
          color: current.base,
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
