from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import json
import os
import pandas as pd

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

# ----- Backtest configuration -----
FILE_PATH = "Updated_Dataset_with_Signals_Ranked.csv"
INITIAL_INVEST = 50_000
CONTRIB_AMOUNT = 3_000
CONTRIB_FREQ = 22
MANUAL_EXIT_DATE = pd.Timestamp("2024-06-27")
HOLD_DAYS = 25

def load_prices(fp: str) -> pd.DataFrame:
    df = pd.read_csv(fp)
    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Price", "Open"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce"
        )
    return df.sort_values("Date")

df_sorted = load_prices(os.path.join(base_dir, FILE_PATH))
date_index = df_sorted["Date"].unique()


def run_backtest(df: pd.DataFrame):
    cash, contrib_ctr = INITIAL_INVEST, 0
    portfolio, trades, equity_curve = [], [], []
    trade_history = []

    for i, curr_date in enumerate(date_index):
        contrib_ctr += 1
        if contrib_ctr == CONTRIB_FREQ:
            cash += CONTRIB_AMOUNT
            contrib_ctr = 0

        if curr_date == MANUAL_EXIT_DATE:
            for pos in portfolio[:]:
                px = df.loc[(df["Company"] == pos["company"]) & (df["Date"] == curr_date), "Price"]
                if px.empty:
                    continue
                px = px.iloc[0]
                profit = (px - pos["buy_price"]) * pos["shares_bought"]
                cash += pos["shares_bought"] * px
                trades.append(profit > 0)
                trade_history.append(
                    dict(company=pos["company"], date=curr_date, action="sell", price=px)
                )
            portfolio.clear()

        todays_rows = df[df["Date"] == curr_date]
        for _, row in todays_rows.iterrows():
            if row["30 Day Buy Signal"] == 1 and cash > 0 and i + 1 < len(date_index):
                nxt = df[(df["Company"] == row["Company"]) & (df["Date"] == date_index[i + 1])]
                if nxt.empty:
                    continue
                next_open = nxt.iloc[0]["Open"]
                qty = (cash * 0.30) / next_open
                if qty >= 1:
                    invest = qty * next_open
                    cash -= invest
                    buy_date = date_index[i + 1]
                    sell_date = date_index[i + HOLD_DAYS] if i + HOLD_DAYS < len(date_index) else None
                    portfolio.append(
                        dict(
                            company=row["Company"],
                            buy_date=buy_date,
                            sell_date=sell_date,
                            shares_bought=qty,
                            buy_price=next_open,
                        )
                    )
                    trade_history.append(
                        dict(company=row["Company"], date=buy_date, action="buy", price=next_open)
                    )

        for pos in portfolio[:]:
            if pos["sell_date"] is not None and curr_date == pos["sell_date"]:
                px = df.loc[(df["Company"] == pos["company"]) & (df["Date"] == pos["sell_date"]), "Price"]
                if px.empty:
                    continue
                px = px.iloc[0]
                profit = (px - pos["buy_price"]) * pos["shares_bought"]
                cash += pos["shares_bought"] * px
                trades.append(profit > 0)
                trade_history.append(
                    dict(company=pos["company"], date=curr_date, action="sell", price=px)
                )
                portfolio.remove(pos)

        pv = 0
        for pos in portfolio:
            cur_px = df.loc[(df["Company"] == pos["company"]) & (df["Date"] == curr_date), "Price"]
            if not cur_px.empty:
                pv += pos["shares_bought"] * cur_px.iloc[0]
        equity_curve.append(cash + pv)

    total_contrib = INITIAL_INVEST + CONTRIB_AMOUNT * (len(date_index) // CONTRIB_FREQ)
    final_val = equity_curve[-1]
    roi = (final_val - total_contrib) / total_contrib * 100
    win_rate = (sum(trades) / len(trades) * 100) if trades else 0

    last_date = date_index[-1]
    rows = []
    for pos in portfolio:
        last_px = df.loc[(df["Company"] == pos["company"]) & (df["Date"] == last_date), "Price"]
        if last_px.empty:
            continue
        last_px = last_px.iloc[0]
        pl_val = (last_px - pos["buy_price"]) * pos["shares_bought"]
        pl_pct = (last_px - pos["buy_price"]) / pos["buy_price"] * 100
        if pos["sell_date"] is not None:
            days_remaining = (pos["sell_date"] - last_date).days
        else:
            days_held = (last_date - pos["buy_date"]).days
            days_remaining = HOLD_DAYS - days_held
        rows.append(
            {
                "company": pos["company"],
                "shares": round(pos["shares_bought"], 2),
                "buy_date": f"{pos['buy_date'].month}/{pos['buy_date'].day}/{pos['buy_date'].year}",
                "buy_price": round(pos["buy_price"], 2),
                "current_price": round(last_px, 2),
                "pl_val": round(pl_val, 2),
                "pl_pct": round(pl_pct, 2),
                "days_remaining": days_remaining,
            }
        )
    open_df = pd.DataFrame(rows)

    trades_df = pd.DataFrame(trade_history)
    return {
        "equity_curve": [
            {"date": d.strftime("%Y-%m-%d"), "value": v} for d, v in zip(date_index, equity_curve)
        ],
        "final_value": round(final_val, 2),
        "roi": round(roi, 2),
        "win_rate": round(win_rate, 2),
        "open_positions": open_df.to_dict(orient="records"),
        "trades": trades_df.to_dict(orient="records"),
    }


backtest_results = run_backtest(df_sorted)
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


@app.get("/backtest")
async def get_backtest():
    """Return precomputed backtest results."""
    return backtest_results


# Serve the HTML and other static assets in the project directory
app.mount("/", StaticFiles(directory=".", html=True), name="static")
