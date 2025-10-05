from flask import Flask, render_template, request
import pandas as pd
import joblib
import os
from sklearn.metrics import classification_report

app = Flask(__name__)

# Cargar el modelo y el encoder una sola vez al iniciar la app
MODEL_PATH = "../app/models/RF UnderSampling/modelo_RF_Under.pkl"
ENCODER_PATH = "../app/models/RF UnderSampling/label_encoder_RF_Under.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Validar que se haya subido un archivo
    if "dataset" not in request.files:
        return "⚠️ No se ha subido ningún archivo CSV", 400

    file = request.files["dataset"]

    # Leer el CSV subido por el usuario
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error al leer el CSV: {e}"

    # Ver si el CSV tiene la columna Category (para evaluación)
    if "Category" in df.columns:
        X = df.drop("Category", axis=1)
        y_true = df["Category"]
    else:
        X = df
        y_true = None

    # Predicciones
    y_pred = model.predict(X)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    df["Predicción"] = y_pred_labels

    # Convertir resultados a tabla HTML
    results_table = df.head(50).to_html(classes="table table-striped", index=False)

    # Si hay etiquetas reales, mostrar métricas
    report = None
    if y_true is not None:
        y_true_enc = label_encoder.transform(y_true)
        report = classification_report(y_true_enc, y_pred, target_names=label_encoder.classes_)

    return render_template("index.html", results=results_table, report=report)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
