from pathlib import Path
import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.agent import plan_query, create_answer

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "marketing_analytics.db"

app = FastAPI(
    title="AI SQL Analytics Agent",
    description="Plain-English analytics questions converted into safe SQL over synthetic marketing data.",
    version="1.0.0"
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "project": "AI SQL Analytics Agent",
        "database_exists": DB_PATH.exists()
    }

@app.get("/schema")
def get_schema():
    return {
        "table": "marketing_performance",
        "columns": [
            "date", "channel", "campaign", "product", "impressions",
            "clicks", "leads", "customers", "spend", "revenue"
        ]
    }

@app.post("/ask")
def ask_question(payload: QuestionRequest):
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Database not found. Run: python3 backend/db.py"
        )

    plan = plan_query(payload.question)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(plan.sql, conn)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    rows = df.to_dict(orient="records")
    answer = create_answer(plan.question_type, rows)

    return {
        "question": payload.question,
        "answer": answer,
        "sql": " ".join(plan.sql.split()),
        "chart_type": plan.chart_type,
        "explanation": plan.explanation,
        "rows": rows
    }
