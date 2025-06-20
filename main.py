from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import json
import os

app = FastAPI()

# Load dashboard data if available
base_dir = os.path.dirname(__file__)
metrics_info = {}
combos_info = {}
try:
    with open(os.path.join(base_dir, "metrics.json")) as f:
        metrics_info = json.load(f)
except FileNotFoundError:
    pass
try:
    with open(os.path.join(base_dir, "combos.json")) as f:
        combos_info = json.load(f)
except FileNotFoundError:
    pass

# Allow frontend JavaScript running on http://localhost:8000 to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use ["http://localhost:8000"] for tighter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChurnInput(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


@app.post("/predict")
async def predict_churn(data: ChurnInput):
    # TODO: Load your real model and pipeline here
    # Mock prediction and SHAP output
    probability = 0.72  # Dummy value
    contributions = {
        "Contract": 0.3,
        "Tenure": 0.2,
        "MonthlyCharges": 0.15,
        "InternetService": 0.07,
        "SeniorCitizen": 0.05,
    }
    return {"probability": probability, "contributions": contributions}


@app.get("/metrics")
async def get_metrics():
    """Return stored model performance metrics."""
    return metrics_info


@app.get("/dashboard")
async def dashboard_data():
    """Return data used by the churn dashboard."""
    return {
        "top_combos": combos_info.get("top_combos", []),
        "bottom_combos": combos_info.get("bottom_combos", []),
        "total_customers": combos_info.get("total_customers"),
        "churn_rate": combos_info.get("churn_rate"),
        "highest_rule": combos_info.get("highest_rule"),
    }


# Serve the HTML and other static assets in the project directory
app.mount("/", StaticFiles(directory=".", html=True), name="static")
