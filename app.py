import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI SQL Analytics Agent",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI SQL Analytics Agent")
st.caption("Ask business questions in English. The agent creates safe SQL, runs it, and returns answers from synthetic marketing data.")

with st.sidebar:
    st.header("System")
    st.markdown("**Frontend:** Streamlit")
    st.markdown("**Backend:** FastAPI")
    st.markdown("**Database:** SQLite")
    st.markdown("**AI Layer:** Rule-based SQL planner")

    if st.button("Check API"):
        try:
            res = requests.get(f"{API_URL}/", timeout=5)
            st.success(res.json())
        except Exception as exc:
            st.error(f"API not reachable: {exc}")

example_questions = [
    "Which channel has the highest ROAS?",
    "Which channel has the lowest CAC?",
    "Which campaign generated the most revenue?",
    "Where is the funnel leaking?",
    "Which product has the most customers?",
    "Show monthly revenue trend",
    "Which channel should we scale?"
]

question = st.selectbox("Try an example", example_questions)
custom_question = st.text_input("Or ask your own question", placeholder="Example: Which channel should we scale?")

final_question = custom_question if custom_question else question

if st.button("Ask Agent", type="primary"):
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": final_question},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
    except Exception as exc:
        st.error(f"Request failed. Make sure the FastAPI server is running. Error: {exc}")
        st.stop()

    st.subheader("Answer")
    st.success(result["answer"])

    st.subheader("Generated SQL")
    st.code(result["sql"], language="sql")

    st.subheader("Why this query was chosen")
    st.write(result["explanation"])

    rows = result["rows"]
    df = pd.DataFrame(rows)

    if df.empty:
        st.warning("No results returned.")
        st.stop()

    st.subheader("Result Table")
    st.dataframe(df, use_container_width=True)

    st.subheader("Visualization")
    chart_type = result["chart_type"]

    if chart_type == "line" and "date" in df.columns:
        fig = px.line(df, x="date", y=[c for c in ["spend", "revenue", "customers", "roas"] if c in df.columns])
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "funnel":
        row = df.iloc[0]
        funnel_df = pd.DataFrame({
            "stage": ["Impressions", "Clicks", "Leads", "Customers"],
            "count": [row["impressions"], row["clicks"], row["leads"], row["customers"]]
        })
        fig = px.funnel(funnel_df, x="count", y="stage")
        st.plotly_chart(fig, use_container_width=True)

    else:
        x_col = "channel" if "channel" in df.columns else ("campaign" if "campaign" in df.columns else df.columns[0])
        y_candidates = ["roas", "cac", "revenue", "customers", "spend"]
        y_col = next((col for col in y_candidates if col in df.columns), df.columns[-1])
        fig = px.bar(df, x=x_col, y=y_col, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
