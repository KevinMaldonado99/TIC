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
import json

warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

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

    # =======================
    # ARCHIVO
    # =======================
    file = request.files["dataset"]
    file_name = file.filename

    file_hash_md5 = hashlib.md5(file.read()).hexdigest()
    file.seek(0)

    file_hash_sha256 = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)

    file_hash = file_hash_md5[:6]

    file.seek(0, io.SEEK_END)
    file_size = round(file.tell() / 1024, 2)
    file.seek(0)

    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(file)

    columnas_modelo = model.feature_names_in_

    # =======================
    # ALINEAR COLUMNAS
    # =======================
    X = pd.DataFrame(columns=columnas_modelo)
    for col in columnas_modelo:
        X[col] = df[col] if col in df.columns else 0

    # =======================
    # PREDICCIÓN
    # =======================
    start = time.time()
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    tiempo_analisis = round(time.time() - start, 2)

    df["Clasificación"] = y_pred_labels

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax()

    # =======================
    # CONFIANZA
    # =======================
    y_pred_proba = model.predict_proba(X)
    conf = []
    for i, label in enumerate(y_pred_labels):
        idx = np.where(clases == label)[0][0]
        conf.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(conf)) * 100, 2)

    # =======================
    # TOP FEATURES
    # =======================
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

    total_features = len(model.feature_names_in_)
    top_features_json = json.dumps(top_features)

    # =======================
    # URL PARA REPORTE PDF
    # =======================
    reporte_url = (
        "/report?"
        f"clase_dominante={clase_dominante}"
        f"&confianza_promedio={confianza_promedio}"
        f"&precision={confianza_promedio}"
        f"&recall={confianza_promedio}"
        f"&f1_score={confianza_promedio}"
        f"&file_name={file_name}"
        f"&file_hash={file_hash}"
        f"&file_size={file_size}"
        f"&file_hash_md5={file_hash_md5}"
        f"&file_hash_sha256={file_hash_sha256}"
        f"&fecha_analisis={fecha_analisis}"
        f"&tiempo_analisis={tiempo_analisis}"
        f"&total_features={total_features}"
        f"&dataset_version=FeatureSet v2.3"
        f"&environment=Flask App v2.0 (Python 3.11)"
        f"&libraries=Scikit-Learn 1.4 | Pandas 2.2 | NumPy 1.26"
        f"&top_features={top_features_json}"
    )

    return render_template(
        "index.html",
        fecha_analisis=fecha_analisis,
        tiempo_analisis=tiempo_analisis,
        confianza_promedio=confianza_promedio,
        clase_dominante=clase_dominante,
        porcentajes=porcentajes.to_dict(),
        top_features=top_features,
        file_hash=file_hash,
        file_name=file_name,
        total_features=total_features,
        precision=confianza_promedio,
        recall=confianza_promedio,
        f1_score=confianza_promedio,
        file_size=file_size,
        file_hash_md5=file_hash_md5,
        file_hash_sha256=file_hash_sha256,
        reporte_url=reporte_url
    )


@app.route("/report")
def report():
    data = request.args.to_dict()
    data["top_features"] = json.loads(data["top_features"])
    return render_template("report.html", **data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
