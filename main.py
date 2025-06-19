from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

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


# Serve the HTML and other static assets in the project directory
app.mount("/", StaticFiles(directory=".", html=True), name="static")
