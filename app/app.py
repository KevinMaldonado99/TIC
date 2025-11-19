from flask import Flask, render_template, request
import pandas as pd
import joblib
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import warnings
import hashlib
import numpy as np

warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# -------------------------
# Rutas del modelo y encoder (Ransomware vs Benign)
# -------------------------
MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_Under_ramnsomware.pkl"

ENCODER_PATH = "../app/models/RF UnderSampling/label_E_RF_Under_ramnsomware.pkl"

#MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_OVER.pkl"
#ENCODER_PATH = "../app/models/RF UnderSampling/label_encoder_RF_OVER.pkl"

# Cargar modelo y encoder
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
clases = label_encoder.classes_  # ['Benign', 'Ransomware']


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "dataset" not in request.files:
        return "⚠️ No se ha subido ningún archivo CSV", 400

    file = request.files["dataset"]
    file_name = file.filename
    file_hash = hashlib.md5(file.read()).hexdigest()[:6]
    file.seek(0)

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error al leer el CSV: {e}"

    if "Category" in df.columns:
        return "⚠️ Este CSV contiene la columna 'Category'. Sube únicamente archivos sin etiquetas.", 400

    start_time = time.time()
    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    columnas_modelo = model.feature_names_in_

    # -------------------------
    # 1️⃣ Validar estructura del archivo
    # -------------------------
    cols_input = [c.strip().lower() for c in df.columns]
    cols_modelo = [c.strip().lower() for c in columnas_modelo]
    coincidencias = len(set(cols_input).intersection(set(cols_modelo)))
    porcentaje_coincidencia = (coincidencias / len(cols_modelo)) * 100

    if porcentaje_coincidencia < 90:
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error=f"⚠️ El archivo no coincide con las características esperadas ({porcentaje_coincidencia:.2f}% de coincidencia).",
            confianza_promedio=0,
            top_features=[],
            dist_image=None,
            porcentajes={},
            precision=0,
            recall=0,
            f1_score=0,
            file_name=file_name,
            file_hash=file_hash,
            tiempo_analisis=0,
            fecha_analisis=fecha_analisis
        )

    # -------------------------
    # 2️⃣ Alinear columnas
    # -------------------------
    X = pd.DataFrame(columns=columnas_modelo)
    for col in columnas_modelo:
        X[col] = df[col] if col in df.columns else 0
    X = X[columnas_modelo]

    if X.empty or len(X) == 0 or X.isna().all().all():
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error="⚠️ El archivo no contiene datos válidos o no se reconocen características para clasificar.",
            confianza_promedio=0,
            top_features=[],
            dist_image=None,
            porcentajes={},
            precision=0,
            recall=0,
            f1_score=0,
            file_name=file_name,
            file_hash=file_hash,
            tiempo_analisis=0,
            fecha_analisis=fecha_analisis
        )

    # -------------------------
    # 3️⃣ Clasificación
    # -------------------------
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    df["Clasificación"] = y_pred_labels
    tiempo_analisis = round(time.time() - start_time, 2)

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax() if not porcentajes.empty else "Desconocido"
    porcentaje_dominante = porcentajes.max() if not porcentajes.empty else 0

    # -------------------------
    # 4️⃣ Confianza promedio
    # -------------------------
    y_pred_proba = model.predict_proba(X)
    confidencias = []
    for i, pred_label in enumerate(y_pred_labels):
        idx = np.where(clases == pred_label)[0][0]
        confidencias.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(confidencias)) * 100, 2)

    # -------------------------
    # 5️⃣ Detección de desconocidos
    # -------------------------
    UMBRAL_DESCONOCIDO = 85
    if confianza_promedio < UMBRAL_DESCONOCIDO or pred_counts.sum() == 0:
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error="⚠️ La muestra no coincide con las características conocidas por el modelo (ni Ransomware ni Benigno).",
            confianza_promedio=0.0,
            top_features=[],
            dist_image=None,
            porcentajes={},
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            file_name=file_name,
            file_hash=file_hash,
            tiempo_analisis=tiempo_analisis,
            fecha_analisis=fecha_analisis
        )

    # -------------------------
    # 6️⃣ Gráfico distribución
    # -------------------------
    plt.figure(figsize=(5, 4))
    sns.barplot(x=pred_counts.index, y=pred_counts.values, palette="coolwarm")
    plt.title("Distribución de Clasificaciones (Ransomware vs Benign)")
    plt.ylabel("Cantidad de muestras")
    plt.xlabel("Clase Predicha")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    dist_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # --- Métricas dinámicas según la clase dominante ---
    precision = round(confianza_promedio, 2)
    total_preds = len(y_pred_labels)

    if clase_dominante == "Ransomware":
        positivos = sum([1 for c in y_pred_labels if c == "Ransomware"])
        recall = round((positivos / total_preds) * 100, 2)
    elif clase_dominante == "Benign":
        positivos = sum([1 for c in y_pred_labels if c == "Benign"])
        recall = round((positivos / total_preds) * 100, 2)
    else:
        recall = 0.0

    f1_score = round((2 * precision * recall) / (precision + recall), 2) if (precision + recall) > 0 else 0.0

    # -------------------------
    # 7️⃣ Características influyentes (ponderadas por la muestra)
    # -------------------------
    try:
        importances = model.feature_importances_
        valores_medios = X.mean().values  # promedio por característica en la muestra
        ajuste = importances * valores_medios  # ponderación dinámica

        # Top 5 características más relevantes en esta muestra
        indices = np.argsort(ajuste)[::-1][:15]
        top_features = []
        for i in indices:
            top_features.append({
                "Característica": columnas_modelo[i],
                "Importancia": round((ajuste[i] / np.sum(ajuste)) * 100, 2)
            })
        
    except Exception as e:
        top_features = [{'Característica': 'Error al calcular importancias', 'Importancia': 0.0}]
        print(f"Error al calcular Feature Importances: {e}")

    # -------------------------
    # 8️⃣ Render final
    # -------------------------
    total_features = len(model.feature_names_in_)

    return render_template(
        "index.html",
        fecha_analisis=fecha_analisis,
        tiempo_analisis=tiempo_analisis,
        confianza_promedio=confianza_promedio,
        clase_dominante=clase_dominante,
        porcentaje_dominante=porcentaje_dominante,
        porcentajes=porcentajes.to_dict(),
        dist_image=dist_image,
        top_features=top_features,
        file_hash=file_hash,
        file_name=file_name,
        total_features=total_features,
        precision=precision,
        recall=recall,
        f1_score=f1_score
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
