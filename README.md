# AI SQL Analytics Agent

A portfolio-ready AI-style analytics agent that converts plain-English business questions into safe SQL, runs them against a synthetic marketing database, and returns answers, charts, and explanations.

No API key is required. This MVP uses a rule-based query planner so it works immediately. A real LLM layer can be added later.

## What this project shows

- AI + real-world problem solving
- System design thinking beyond UI
- Data + backend + APIs
- Shipping ability with a usable local app
- AI-tool-ready architecture

## Architecture

```text
Streamlit Frontend
      ↓
FastAPI Backend
      ↓
Query Planner / Agent
      ↓
Safe SQL Generator
      ↓
SQLite Database
      ↓
Answer + Chart Data + Explanation
```

## Run locally

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 2. Create the database

```bash
python3 backend/db.py
```

### 3. Start the API

```bash
python3 -m uvicorn backend.main:app --reload
```

### 4. In a second terminal, start the UI

```bash
source .venv/bin/activate
python3 -m streamlit run frontend/app.py
```

## Try these questions

- Which channel has the highest ROAS?
- Which channel has the lowest CAC?
- Which campaign generated the most revenue?
- Where is the funnel leaking?
- Which product has the most customers?
- Show monthly revenue trend
- Which channel should we scale?

## Privacy note

This project uses fully synthetic company, campaign, and product names. No real employer, customer, or internal business data is included.

## Future improvements

- Add OpenAI/Claude natural-language-to-SQL
- Add SQL validation and permissions layer
- Add Snowflake or BigQuery connector
- Add authentication
- Deploy backend and frontend
