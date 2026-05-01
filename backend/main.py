from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np
import subprocess
import threading
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
import logging
import math
import sys

# ======================================================
# 1. FASTAPI SETUP
# ======================================================

app = FastAPI(title="Smart Home Energy API (Frozen Evaluation)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)

# ======================================================
# 2. PROJECT PATHS
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# DEFAULT_ML_CSV   = PROJECT_ROOT / "ml_control_log.csv"
# DEFAULT_RULE_CSV = PROJECT_ROOT / "control_log.csv"
DEFAULT_ML_CSV   = PROJECT_ROOT / "ml_control_log.csv"
DEFAULT_RULE_CSV = PROJECT_ROOT / "rule_eval_log.csv"
INTERVAL_FILE = PROJECT_ROOT / "log_interval.txt"
COMFORT_FILE  = PROJECT_ROOT / "comfort_mode.txt"

EVAL_LIMIT = 10000  # 🔒 fixed evaluation window

# ======================================================
# 3. ML AGENT PROCESS MANAGEMENT
# ======================================================

ml_process = None

@app.post("/api/start-ml")
def start_ml_agent():
    global ml_process

    if ml_process and ml_process.poll() is None:
        return {"status": "already_running"}

    cmd = [
        sys.executable,
        "-m",
        "agents.ml_main_control_agent.ml_main_control_agent",
        "--verbose"
    ]

    def run_agent():
        global ml_process
        ml_process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=None,
            stderr=None,
            text=True
        )

    threading.Thread(target=run_agent, daemon=True).start()
    return {"status": "started"}


@app.post("/api/stop-ml")
def stop_ml_agent():
    global ml_process

    if ml_process and ml_process.poll() is None:
        ml_process.terminate()
        ml_process = None
        return {"status": "stopped"}

    return {"status": "not_running"}

# ======================================================
# 4. CSV HELPERS
# ======================================================

def read_csv_safe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            on_bad_lines="skip"
        )
    except:
        return pd.DataFrame()


def sanitize(value: Any):
    try:
        if isinstance(value, np.generic):
            value = value.item()

        if value is None:
            return None

        s = str(value).strip()
        if s == "":
            return None

        if s.lower() in ("true", "false"):
            return s.lower() == "true"

        try:
            f = float(s)
            if not math.isnan(f) and not math.isinf(f):
                return f
        except:
            pass

        return s
    except:
        return None


def df_to_json(df: pd.DataFrame):
    if df.empty:
        return []

    cols = df.columns.tolist()
    return [
        {col: sanitize(v) for col, v in zip(cols, row)}
        for row in df.itertuples(index=False, name=None)
    ]

# ======================================================
# 5. METRICS COMPUTATION
# ======================================================

def compute_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    df = df.copy()

    df["house_overall_kw"]  = pd.to_numeric(df.get("house_overall_kw"), errors="coerce")
    df["price_eur_per_kwh"] = pd.to_numeric(df.get("price_eur_per_kwh"), errors="coerce")

    df["occupied"]    = df.get("occupied").astype(str).str.lower() == "true"
    df["action"]      = df.get("action", "").astype(str)
    df["price_level"] = df.get("price_level", "").astype(str)

    # ---------------- ENERGY ----------------
    avg_consumption  = df["house_overall_kw"].mean()
    peak_consumption = df["house_overall_kw"].max()

    high_load_pct = (
        (df["house_overall_kw"] > 2.5).sum() / len(df) * 100
        if len(df) > 0 else 0
    )

    occupied_shutdown_pct = (
        df[
            (df["occupied"]) &
            (df["action"].str.lower().str.contains("turn off"))
        ].shape[0]
        / max(1, df[df["occupied"]].shape[0]) * 100
    )

    action_diversity = df["action"].nunique()

    by_price_level = (
        df.groupby("price_level")["house_overall_kw"]
        .mean()
        .dropna()
        .to_dict()
    )

    # ---------------- COST ----------------
    df["cost"] = df["house_overall_kw"] * df["price_eur_per_kwh"]

    avg_cost   = df["cost"].mean()
    total_cost = df["cost"].sum()

    return {
        "avg_consumption": round(avg_consumption, 3),
        "peak_consumption": round(peak_consumption, 3),
        "high_load_pct": round(high_load_pct, 2),
        "occupied_shutdown_pct": round(occupied_shutdown_pct, 2),
        "action_diversity": int(action_diversity),
        "avg_cost": round(avg_cost, 6),
        "total_cost": round(total_cost, 4),
        "by_price_level": {k: round(v, 3) for k, v in by_price_level.items()},
    }

# ======================================================
# 6. FROZEN COMPARISON LOGIC
# ======================================================

def get_comparison_metrics():

    rule_df = read_csv_safe(DEFAULT_RULE_CSV).tail(EVAL_LIMIT)
    ml_df   = read_csv_safe(DEFAULT_ML_CSV).tail(EVAL_LIMIT)

    if rule_df.empty or ml_df.empty:
        raise HTTPException(400, "Both rule and ML logs are required")

    rule_metrics = compute_metrics(rule_df)
    ml_metrics   = compute_metrics(ml_df)

    # -------- COST IMPROVEMENT --------
    rule_cost = rule_metrics.get("avg_cost", 0)
    ml_cost   = ml_metrics.get("avg_cost", 0)

    improvement = 0
    if rule_cost > 0:
        improvement = ((rule_cost - ml_cost) / rule_cost) * 100

    return {
        "evaluation_window_size": EVAL_LIMIT,
        "rule": rule_metrics,
        "ml": ml_metrics,
        "ml_cost_improvement_percent": round(improvement, 2)
    }

# ======================================================
# 7. API ROUTES
# ======================================================

@app.get("/")
def root():
    return HTMLResponse("<h3>Smart Home Backend Running (Frozen Evaluation)</h3>")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/current")
def api_current():

    if DEFAULT_ML_CSV.exists():
        df = read_csv_safe(DEFAULT_ML_CSV)
        if not df.empty:
            return {"source": "ml", "latest": df_to_json(df.tail(1))[0]}

    if DEFAULT_RULE_CSV.exists():
        df = read_csv_safe(DEFAULT_RULE_CSV)
        if not df.empty:
            return {"source": "rule", "latest": df_to_json(df.tail(1))[0]}

    raise HTTPException(404, "No logs available")


@app.get("/api/logs/ml")
def api_logs_ml(limit: Optional[int] = None):
    df = read_csv_safe(DEFAULT_ML_CSV)
    if limit:
        df = df.tail(limit)
    return {"rows": df_to_json(df)}


@app.get("/api/logs/rule")
def api_logs_rule(limit: Optional[int] = None):
    df = read_csv_safe(DEFAULT_RULE_CSV)
    if limit:
        df = df.tail(limit)
    return {"rows": df_to_json(df)}


@app.get("/api/compare")
def api_compare():
    return get_comparison_metrics()

# ======================================================
# 8. INTERVAL + COMFORT MODE
# ======================================================

@app.get("/api/get-log-interval")
def get_log_interval():
    try:
        if INTERVAL_FILE.exists():
            return {"interval": int(INTERVAL_FILE.read_text().strip())}
    except:
        pass
    return {"interval": 1}


@app.post("/api/set-log-interval")
def set_log_interval(seconds: int = Body(...)):
    seconds = max(1, int(seconds))
    INTERVAL_FILE.write_text(str(seconds))
    return {"status": "ok", "interval": seconds}


@app.get("/api/get-comfort-mode")
def get_comfort_mode():
    try:
        if COMFORT_FILE.exists():
            raw = COMFORT_FILE.read_text().strip().lower()
            return {"comfort_mode": raw in ("1", "true", "yes", "on")}
    except:
        pass
    return {"comfort_mode": False}


@app.post("/api/set-comfort-mode")
def set_comfort_mode(enabled: bool = Body(...)):
    try:
        COMFORT_FILE.write_text("1" if enabled else "0")
        return {"status": "ok", "comfort_mode": enabled}
    except:
        raise HTTPException(500, "Failed to set comfort mode")
