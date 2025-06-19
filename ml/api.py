from fastapi import FastAPI
import pandas as pd
import numpy as np
import joblib
from tensorflow import keras
import shap
import json

app = FastAPI()

model = keras.models.load_model('churn_model.h5')
preprocess = joblib.load('preprocess.pkl')
try:
    with open('metrics.json') as f:
        metrics_info = json.load(f)
except FileNotFoundError:
    metrics_info = {}

# SHAP explainer with simple background
dummy = np.zeros((1, model.input_shape[1]))
explainer = shap.KernelExplainer(model.predict, dummy)

@app.post('/predict')
def predict(features: dict):
    df = pd.DataFrame([features])
    processed = preprocess.transform(df)
    prob = float(model.predict(processed)[0][0])
    shap_vals = explainer.shap_values(processed)[0]
    names = preprocess.get_feature_names_out()
    top_idx = np.argsort(np.abs(shap_vals))[::-1][:5]
    contributions = {names[i]: float(shap_vals[i]) for i in top_idx}
    return {'probability': prob, 'contributions': contributions}

@app.get('/metrics')
def metrics():
    return metrics_info
