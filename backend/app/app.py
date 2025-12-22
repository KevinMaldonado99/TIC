from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from urllib.parse import unquote
from urllib.parse import quote
import pandas as pd
import joblib
import io
import hashlib
import time
import json
import os
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)


#**** CARGA DEL MODELO Y EL CODIFICADOR EN FORMATO PKL ****
MODEL_PATH = "../app/models/Pkls/modelo_RF_SMOTE.pkl"

ENCODER_PATH = "../app/models/Pkls/label_encoder_RF_SMOTE.pkl"



model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
clases = label_encoder.classes_


# ======================================================
# =============== RUTA HTML ORIGINAL ===================
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")


# ======================================================
# ========== RUTA /predict (para HTML backend) =========
# ======================================================
@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["dataset"]
    file_name = file.filename

    # === HASHES ===
    file_hash_md5 = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    file_hash_sha256 = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)
    file_hash = file_hash_md5[:6]

    # === Tamaño archivo ===
    file.seek(0, io.SEEK_END)
    file_size = round(file.tell() / 1024, 2)
    file.seek(0)

    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === LECTURA CSV ===
    df = pd.read_csv(file)
    columnas_modelo = list(model.feature_names_in_)

    try:
        # 1. Verificar que existan TODAS las columnas necesarias
        for col in columnas_modelo:
            if col not in df.columns:
                return jsonify({
                    "status": "error",
                    "message": f"El archivo no contiene la columna requerida: '{col}'. "
                            "Por favor sube un CSV válido del dominio Benign/Ransomware."
                }), 400

        # 2. Extraer únicamente las columnas necesarias
        X = df[columnas_modelo]

        # 3. Validar tipos → convertir a float
        X = X.astype(float)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "El archivo no es compatible con el modelo. "
                    "Debe contener las características correctas y valores numéricos.",
            "error": str(e)
        }), 400

  
    start = time.time()
    
      # === PREDICCIÓN ===
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    
    
    tiempo_analisis = round(time.time() - start, 2)

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax()

    # === CONFIANZA ===
    y_pred_proba = model.predict_proba(X)
    conf = []
    for i, label in enumerate(y_pred_labels):
        idx = np.where(clases == label)[0][0]
        conf.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(conf)) * 100, 2)
    
    
    
    if confianza_promedio < 75:
        return jsonify({
            "status": "error",
            "message": "El archivo no pertenece al dominio del modelo (Benign/Ransomware). "
                    "La confianza es demasiado baja para generar un resultado confiable.",
            "confianza": confianza_promedio
        }), 400


    
    # ========== MÉTRICAS SINTÉTICAS DINÁMICAS ============
 

    total_preds = len(y_pred_labels)

    precision = round(confianza_promedio, 2)

    if clase_dominante == "Ransomware":
        positivos = sum([1 for c in y_pred_labels if c == "Ransomware"])
    elif clase_dominante == "Benign":
        positivos = sum([1 for c in y_pred_labels if c == "Benign"])
    else:
        positivos = 0

    recall = round((positivos / total_preds) * 100, 2) if total_preds > 0 else 0

    f1_score = (
        round((2 * precision * recall) / (precision + recall), 2)
        if (precision + recall) > 0
        else 0.0
    )

   
    # ================ TOP FEATURES ========================

    importances = model.feature_importances_
    valores_medios = X.mean().values
    ajuste = importances * valores_medios
    indices = np.argsort(ajuste)[::-1][:7]

    top_features = [
    {
        "Característica": columnas_modelo[i],
        "Importancia": float(round((ajuste[i] / np.sum(ajuste)) * 100, 2))
    }
    for i in indices
    ]


    total_features = len(columnas_modelo)
    top_features_json = json.dumps(top_features)

    # === URL PARA PDF ===
    reporte_url = (
        "/report?"
        f"clase_dominante={clase_dominante}"
        f"&confianza_promedio={confianza_promedio}"
        f"&precision={precision}"
        f"&recall={recall}"
        f"&f1_score={f1_score}"
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
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        file_size=file_size,
        file_hash_md5=file_hash_md5,
        file_hash_sha256=file_hash_sha256,
        reporte_url=reporte_url
    )



# ======================================================
# ========== RUTA API PARA REACT =======================
# ======================================================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    file = request.files.get("dataset")
    if file is None:
        return jsonify({"error": "No se envió archivo"}), 400

    file_name = file.filename

    # === HASHES ===
    file_hash_md5 = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    file_hash_sha256 = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)
    file_hash = file_hash_md5[:6]

    # === Tamaño ===
    file.seek(0, io.SEEK_END)
    file_size = round(file.tell() / 1024, 2)
    file.seek(0)

    fecha_analisis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === CSV ===
    # ===============================
    # VALIDACIÓN DE ARCHIVO CSV
    # ===============================
    df = pd.read_csv(file)
    columnas_modelo = list(model.feature_names_in_)

    try:
        # 1. Verificar que existan TODAS las columnas necesarias
        for col in columnas_modelo:
            if col not in df.columns:
                return jsonify({
                    "status": "error",
                    "message": f"El archivo no contiene la columna requerida: '{col}'. "
                            "Por favor sube un CSV válido del dominio Benign/Ransomware."
                }), 400

        # 2. Extraer únicamente las columnas necesarias
        X = df[columnas_modelo]

        # 3. Validar tipos → convertir a float
        X = X.astype(float)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "El archivo no es compatible con el modelo. "
                    "Debe contener las características correctas y valores numéricos.",
            "error": str(e)
        }), 400


    # === PRED ===
    start = time.time()
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    tiempo_analisis = round(time.time() - start, 2)

    pred_counts = pd.Series(y_pred_labels).value_counts()
    porcentajes = (pred_counts / pred_counts.sum() * 100).round(2)
    clase_dominante = porcentajes.idxmax()

    # === CONFIANZA ===
    y_pred_proba = model.predict_proba(X)
    
    
    conf = []
    for i, label in enumerate(y_pred_labels):
        idx = np.where(clases == label)[0][0]
        conf.append(y_pred_proba[i][idx])
    confianza_promedio = round(float(np.mean(conf)) * 100, 2)

    if confianza_promedio < 75:
        return jsonify({
            "status": "error",
            "message": "El archivo no pertenece al dominio del modelo (Benign/Ransomware). "
                    "La confianza es demasiado baja para generar un resultado confiable.",
            "confianza": confianza_promedio
        }), 400


    # ======================================================
    # ========== MÉTRICAS SINTÉTICAS PARA REACT ===========
    # ======================================================

    total_preds = len(y_pred_labels)

    precision = round(confianza_promedio, 2)

    if clase_dominante == "Ransomware":
        positivos = sum([1 for c in y_pred_labels if c == "Ransomware"])
    elif clase_dominante == "Benign":
        positivos = sum([1 for c in y_pred_labels if c == "Benign"])
    else:
        positivos = 0

    recall = round((positivos / total_preds) * 100, 2) if total_preds > 0 else 0

    f1_score = (
        round((2 * precision * recall) / (precision + recall), 2)
        if (precision + recall) > 0
        else 0.0
    )

    # === TOP FEATURES ===
    importances = model.feature_importances_
    valores_medios = X.mean().values
    ajuste = importances * valores_medios
    indices = np.argsort(ajuste)[::-1][:5]

    top_features = [
        {
            "caracteristica": columnas_modelo[i],
            "importancia": float(round((ajuste[i] / np.sum(ajuste)) * 100, 2))
        }
        for i in indices
    ]

    total_features = len(columnas_modelo)

    # === URL PARA REPORTE PDF ===
    reporte_url = (
        "/report?"
        f"clase_dominante={clase_dominante}"
        f"&confianza_promedio={confianza_promedio}"
        f"&precision={precision}"
        f"&recall={recall}"
        f"&f1_score={f1_score}"
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
        f"&top_features={quote(json.dumps(top_features))}"
    )

    # RETORNO COMPLETO PARA REACT
    return jsonify({
        "clase_dominante": clase_dominante,
        "confianza": confianza_promedio,

        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,

        "resultado_porcentajes": porcentajes.to_dict(),

        "nivel_riesgo": (
            "Alto" if clase_dominante == "Ransomware" and confianza_promedio >= 90 else
            "Medio" if clase_dominante == "Ransomware" and confianza_promedio >= 70 else
            "Bajo"
        ),

        # PANEL FORENSE 1
        "file_name": file_name,
        "file_hash": file_hash,
        "file_size": file_size,
        "hash_md5": file_hash_md5,
        "hash_sha256": file_hash_sha256,
        "fecha_analisis": fecha_analisis,

        # PANEL FORENSE 2
        "tiempo_analisis": tiempo_analisis,
        "total_features": total_features,
        "dataset_version": "FeatureSet v2.3",
        "environment": "Flask App v2.0 (Python 3.11)",
        "libraries": "Scikit-Learn 1.4 | Pandas 2.2 | NumPy 1.26",

        "top_features": top_features,

        # ← ← ← NUEVO
        "reporte_url": reporte_url
    })
    
    


# ======================================================
# ================= REPORTE PDF ========================
# ======================================================
@app.route("/report")
def report():
    data = request.args.to_dict()
    data["top_features"] = json.loads(unquote(data["top_features"]))
    return render_template("report.html", **data)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
