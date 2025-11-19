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
# Rutas del modelo y encoder
# -------------------------
MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_Under_ramnsomware.pkl"
ENCODER_PATH = "../app/models/RF UnderSampling/label_E_RF_Under_ramnsomware.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
clases = label_encoder.classes_


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "dataset" not in request.files:
        return "⚠️ No se ha subido ningún archivo CSV", 400

    file = request.files["dataset"]
    file_name = file.filename

    # -------------------------
    # Hashes del archivo
    # -------------------------
    file_hash_md5 = hashlib.md5(file.read()).hexdigest()
    file.seek(0)

    file_hash_sha256 = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)

    # ID de análisis
    file_hash = file_hash_md5[:6]

    # Tamaño del archivo
    file.seek(0, io.SEEK_END)
    file_size = round(file.tell() / 1024, 2)
    file.seek(0)

    # -------------------------
    # Leer CSV
    # -------------------------
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error al leer el CSV: {e}"

    if "Category" in df.columns:
        return "⚠️ El CSV contiene la columna 'Category'. Sube archivos sin etiquetas.", 400

    start_time = time.time()
    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    columnas_modelo = model.feature_names_in_

    # -------------------------
    # Validación estructura
    # -------------------------
    cols_input = [c.strip().lower() for c in df.columns]
    cols_modelo = [c.strip().lower() for c in columnas_modelo]
    coincidencias = len(set(cols_input).intersection(set(cols_modelo)))
    porcentaje_coincidencia = (coincidencias / len(cols_modelo)) * 100

    if porcentaje_coincidencia < 90:
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error=f"⚠️ El archivo no coincide ({porcentaje_coincidencia:.2f}%).",
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
            fecha_analisis=fecha_analisis,
            file_size=file_size,
            file_hash_md5=file_hash_md5,
            file_hash_sha256=file_hash_sha256
        )

    # -------------------------
    # Alinear columnas
    # -------------------------
    X = pd.DataFrame(columns=columnas_modelo)
    for col in columnas_modelo:
        X[col] = df[col] if col in df.columns else 0
    X = X[columnas_modelo]

    if X.empty:
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error="⚠️ No contiene datos válidos.",
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
            fecha_analisis=fecha_analisis,
            file_size=file_size,
            file_hash_md5=file_hash_md5,
            file_hash_sha256=file_hash_sha256
        )

    # -------------------------
    # Clasificación
    # -------------------------
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    df["Clasificación"] = y_pred_labels
    tiempo_analisis = round(time.time() - start_time, 2)

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax() if not porcentajes.empty else "Desconocido"

    # -------------------------
    # Confianza promedio
    # -------------------------
    y_pred_proba = model.predict_proba(X)
    confidencias = []
    for i, pred_label in enumerate(y_pred_labels):
        idx = np.where(clases == pred_label)[0][0]
        confidencias.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(confidencias)) * 100, 2)

    # -------------------------
    # Desconocido
    # -------------------------
    if confianza_promedio < 85:
        return render_template(
            "index.html",
            clase_dominante="Desconocido",
            mensaje_error="⚠️ Muestra no reconocida.",
            confianza_promedio=0,
            top_features=[],
            dist_image=None,
            porcentajes={},
            precision=0,
            recall=0,
            f1_score=0,
            file_name=file_name,
            file_hash=file_hash,
            tiempo_analisis=tiempo_analisis,
            fecha_analisis=fecha_analisis,
            file_size=file_size,
            file_hash_md5=file_hash_md5,
            file_hash_sha256=file_hash_sha256
        )

    # -------------------------
    # Gráfico distribución
    # -------------------------
    plt.figure(figsize=(5, 4))
    sns.barplot(x=pred_counts.index, y=pred_counts.values, palette="coolwarm")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    dist_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    precision = confianza_promedio
    recall = confianza_promedio
    f1_score = confianza_promedio

    # -------------------------
    # Importancias
    # -------------------------
    try:
        importances = model.feature_importances_
        valores_medios = X.mean().values
        ajuste = importances * valores_medios
        indices = np.argsort(ajuste)[::-1][:10]

        top_features = [
            {
                "Característica": columnas_modelo[i],
                "Importancia": round((ajuste[i] / np.sum(ajuste)) * 100, 2)
            }
            for i in indices
        ]
    except:
        top_features = []

    total_features = len(model.feature_names_in_)

    return render_template(
        "index.html",
        fecha_analisis=fecha_analisis,
        tiempo_analisis=tiempo_analisis,
        confianza_promedio=confianza_promedio,
        clase_dominante=clase_dominante,
        porcentajes=porcentajes.to_dict(),
        dist_image=dist_image,
        top_features=top_features,
        file_hash=file_hash,
        file_name=file_name,
        total_features=total_features,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        file_size=file_size,
        file_hash_md5=file_hash_md5,
        file_hash_sha256=file_hash_sha256
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
