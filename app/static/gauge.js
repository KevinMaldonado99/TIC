// Esperar a que todo el DOM cargue
document.addEventListener("DOMContentLoaded", function() {

    /* ────────────────────────────────────────────────
       🎯 1. CONFIGURACIÓN DEL GRÁFICO GAUGE
    ──────────────────────────────────────────────── */
    const gauge = document.getElementById("gaugeChart");
    if (gauge) {
        const confianza = parseFloat(gauge.dataset.confianza || 0);
        const clase = gauge.dataset.clase || "";

        // Color según la clase dominante
        let color;
        if (clase === "Ransomware") color = "#d73a49";       // Rojo intenso
        else if (clase === "Trojan") color = "#f39c12";      // Naranja
        else color = "#4CAF50";                              // Verde (Benigno)

        // Plugin para mostrar el texto centrado en el gauge
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

        // Crear el semicírculo Gauge con Chart.js
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
                rotation: -90,       // Inicia desde la parte superior
                circumference: 180,  // Semicírculo
                cutout: "70%",       // Tamaño del hueco interior
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                }
            },
            plugins: [centerTextPlugin]
        });
    }

    /* ────────────────────────────────────────────────
       ⚙️ 2. ANIMACIÓN DEL NIVEL DE RIESGO (BARRA)
    ──────────────────────────────────────────────── */
    document.querySelectorAll(".risk-gradient").forEach(el => {
        const width = el.dataset.width;
        if (width) {
            el.style.width = width + "%";
        }
    });

    /* ────────────────────────────────────────────────
       🧠 3. ANIMACIÓN DE LAS BARRAS LIME (CARACTERÍSTICAS)
    ──────────────────────────────────────────────── */
    document.querySelectorAll(".bar-fill").forEach(el => {
        const width = el.dataset.importance;
        if (width) {
            el.style.width = width + "%";
        }
    });
});
