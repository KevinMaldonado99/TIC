document.addEventListener("DOMContentLoaded", function() {
    const gauge = document.getElementById("gaugeChart");
    if (!gauge) return;

    const confianza = parseFloat(gauge.dataset.confianza || 0);
    const clase = gauge.dataset.clase || "";

    // Color según la clase dominante
    let color;
    if (clase === "Ransomware") color = "#d73a49";
    else if (clase === "Trojan") color = "#f39c12";
    else color = "#4CAF50";  // Benign

    // Plugin para mostrar el texto centrado dentro del gauge
    const centerTextPlugin = {
        id: "centerText",
        afterDraw(chart) {
            const { ctx, chartArea: { width, height } } = chart;
            ctx.save();
            ctx.font = "bold 30px 'Segoe UI', sans-serif";
            ctx.fillStyle = "#e6e6e6";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(confianza.toFixed(2) + "%", width / 2, height / 1.5);
            ctx.restore();
        }
    };

    // Crear el gráfico tipo semicírculo
    new Chart(gauge, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [confianza, 100 - confianza],
                backgroundColor: [color, "#2f3542"],
                borderWidth: 0
            }]
        },
        options: {
            rotation: -90,
            circumference: 180,
            cutout: "70%",
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            }
        },
        plugins: [centerTextPlugin]
    });
});
