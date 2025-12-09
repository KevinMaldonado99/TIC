import GaugeComponent from "react-gauge-component";

export default function Gauge({ value, clase }) {

  const benignColor = "#1E90FF";
  const benignLight = "#3AA0FF";

  const ransomColor = "#B100FF";
  const ransomLight = "#B100FF";

  const baseColor = clase === "Trojan" ? ransomColor : benignColor;
  const lightColor = clase === "Trojan" ? ransomLight : benignLight;

  return (
    <div className={`gauge-wrapper ${clase === "Trojan" ? "gauge-trojan" : "gauge-benign"}`}>
      <GaugeComponent
        value={value}
        minValue={0}
        maxValue={100}
        type="semicircle"
        arc={{
          colorArray: [baseColor, lightColor],
          subArcs: [{ limit: 100, color: baseColor }],
          padding: 0.09,
          width: 0.15
        }}
        pointer={{
          color: baseColor,
          length: 0.7,
          width: 8
        }}
        labels={{
          valueLabel: {
            formatTextValue: (val) => `${val.toFixed(2)}%`,
            style: { fontSize: "32px", fontWeight: "bold", fill: "#ffffff" }
          },
          tickLabels: {
            type: "inner",
            defaultTickValueConfig: {
              format: (val) => `${val}%`,
              style: { fill: "#ffffff", fontSize: "12px" }
            }
          }
        }}
        style={{ width: "350px", margin: "0 auto" }}
      />
    </div>
  );
}
