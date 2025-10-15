from flask import Flask, render_template, request
import pandas as pd
import joblib
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from datetime import datetime
import time
import numpy as np
import warnings

# ⚙️ Evitar advertencias y forzar backend sin GUI (soluciona el error)
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use('Agg')  # ✅ Backend sin interfaz gráfica
import matplotlib.pyplot as plt

app = Flask(__name__)

# -------------------------
# Rutas de modelo y encoder
# -------------------------
MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_Under.pkl"
ENCODER_PATH = "../app/models/RF UnderSampling/label_encoder_RF_Under.pkl"

# Cargar modelo y encoder
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "dataset" not in request.files:
        return "⚠️ No se ha subido ningún archivo CSV", 400

    file = request.files["dataset"]
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error al leer el CSV: {e}"

    # -------------------------
    # Iniciar temporizador
    # -------------------------
    start_time = time.time()
    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Separar etiquetas si existen
    if "Category" in df.columns:
        X = df.drop("Category", axis=1)
        y_true = df["Category"]
    else:
        X = df
        y_true = None

    # -------------------------
    # Predicciones
    # -------------------------
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    df["Predicción"] = y_pred_labels

    # Calcular tiempo de análisis
    tiempo_analisis = round(time.time() - start_time, 2)

    # -------------------------
    # Distribución de clases
    # -------------------------
    pred_counts = pd.Series(y_pred_labels).value_counts()
    total = pred_counts.sum()
    porcentajes = (pred_counts / total * 100).round(2)

    # Gráfico de distribución
    plt.figure(figsize=(5, 4))
    sns.barplot(x=pred_counts.index, y=pred_counts.values, palette="Set2", legend=False)
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
    clases = label_encoder.classes_
    confidencias = []

    for i, pred_label in enumerate(y_pred_labels):
        #idx = list(clases).tolist().index(pred_label)
        idx = list(clases).index(pred_label)
        confidencias.append(y_pred_proba[i][idx])

    confianza_promedio = round(float(pd.Series(confidencias).mean()) * 100, 2)

    # -------------------------
    # Clase dominante (mayoría)
    # -------------------------
    clase_dominante = porcentajes.idxmax()
    porcentaje_dominante = porcentajes.max()

    # -------------------------
    # Métricas si hay etiqueta real
    # -------------------------
    report, cm_image, roc_image, prob_image = None, None, None, None

    if y_true is not None:
        y_true_enc = label_encoder.transform(y_true)
        report_dict = classification_report(
            y_true_enc, y_pred, target_names=label_encoder.classes_, output_dict=True
        )

        # Métricas macro promedio
        precision = round(report_dict["macro avg"]["precision"] * 100, 1)
        recall = round(report_dict["macro avg"]["recall"] * 100, 1)
        f1_score = round(report_dict["macro avg"]["f1-score"] * 100, 1)

        # También el texto completo del reporte
        report = classification_report(
            y_true_enc, y_pred, target_names=label_encoder.classes_
        )
    else:
        precision = recall = f1_score = None

        # Matriz de confusión
        plt.figure(figsize=(5, 4))
        cm = pd.crosstab(y_true_enc, y_pred, rownames=['Real'], colnames=['Predicho'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title("Matriz de Confusión")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        cm_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        # Curva ROC
        y_true_bin = label_binarize(y_true_enc, classes=[0, 1, 2])
        y_pred_prob = model.predict_proba(X)
        fpr, tpr, roc_auc = {}, {}, {}
        for i, clase in enumerate(label_encoder.classes_):
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_prob[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
        plt.figure(figsize=(6, 5))
        for i, clase in enumerate(label_encoder.classes_):
            plt.plot(fpr[i], tpr[i], label=f"{clase} (AUC={roc_auc[i]:.2f})")
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Curva ROC por clase")
        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        roc_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

    # -------------------------
    # Tabla resumen
    # -------------------------
    results_table = df.head(10).to_html(classes="table table-striped", index=False)

    # -------------------------
    # Renderizado final
    # -------------------------
    return render_template(
        "index.html",
        results=results_table,
        report=report,
        cm_image=cm_image,
        roc_image=roc_image,
        dist_image=dist_image,
        fecha_analisis=fecha_analisis,
        tiempo_analisis=tiempo_analisis,
        porcentajes=porcentajes.to_dict(),
        clase_dominante=clase_dominante,
        porcentaje_dominante=porcentaje_dominante,
        confianza_promedio=confianza_promedio,
        precision=precision,
        recall=recall,
        f1_score=f1_score

    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
