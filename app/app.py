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
from lime.lime_tabular import LimeTabularExplainer

# ⚙️ Evitar advertencias y usar backend sin GUI
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# -------------------------
# Rutas del modelo y encoder
# -------------------------
MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_Under.pkl"
ENCODER_PATH = "../app/models/RF UnderSampling/label_encoder_RF_Under.pkl"

# Cargar modelo y encoder
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
    file_hash = hashlib.md5(file.read()).hexdigest()[:6]
    file.seek(0)

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error al leer el CSV: {e}"

    if "Category" in df.columns:
        return "⚠️ Este CSV contiene la columna 'Category'. Sube únicamente archivos sin etiquetas para detección real.", 400

    start_time = time.time()
    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------
    # Alinear columnas con el modelo
    # -------------------------
    columnas_modelo = model.feature_names_in_
    X = pd.DataFrame(columns=columnas_modelo)
    for col in columnas_modelo:
        X[col] = df[col] if col in df.columns else 0
    X = X[columnas_modelo]

    # -------------------------
    # Predicciones globales
    # -------------------------
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    df["Predicción"] = y_pred_labels

    tiempo_analisis = round(time.time() - start_time, 2)

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax()
    porcentaje_dominante = porcentajes.max()

    # -------------------------
    # Gráfico de distribución
    # -------------------------
    plt.figure(figsize=(5, 4))
    sns.barplot(x=pred_counts.index, y=pred_counts.values, palette="Set2")
    plt.title("Distribución de Predicciones por Clase")
    plt.ylabel("Cantidad de muestras")
    plt.xlabel("Clase Predicha")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    dist_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # -------------------------
    # Calcular confianza promedio
    # -------------------------
    y_pred_proba = model.predict_proba(X)
    confidencias = []
    for i, pred_label in enumerate(y_pred_labels):
        idx = list(clases).index(pred_label)
        confidencias.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(confidencias)) * 100, 2)

    # -------------------------
    # 🧠 LIME - Explicación local
    # -------------------------
    try:
        explainer = LimeTabularExplainer(
            X.values,
            feature_names=columnas_modelo,
            class_names=clases,
            discretize_continuous=True
        )

        # Tomar una muestra representativa (por ejemplo, la primera del CSV)
        muestra = X.iloc[0].values
        exp = explainer.explain_instance(
            muestra,
            model.predict_proba,
            num_features=5,
            top_labels=1
        )

        # Extraer características más influyentes de esa explicación
        lime_exp = exp.as_list(label=list(clases).index(y_pred_labels[0]))
        top_features = []
        for nombre, valor in lime_exp:
            top_features.append({
                "Característica": nombre,
                "Importancia": abs(valor)
            })

        # Normalizar a porcentaje
        total = sum([f["Importancia"] for f in top_features])
        for f in top_features:
            f["Importancia"] = round(f["Importancia"] / total * 100, 2)

        print(f"✅ LIME generado correctamente para la muestra dominante ({clase_dominante})")

    except Exception as e:
        top_features = [{'Característica': 'Error en LIME', 'Importancia': 0.0}]
        print(f"Error al calcular LIME: {e}")

    # -------------------------
    # Renderizado final
    # -------------------------
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
        file_hash=file_hash
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
