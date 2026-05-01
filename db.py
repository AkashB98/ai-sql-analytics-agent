from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "marketing_analytics.db"
CSV_PATH = DATA_DIR / "synthetic_marketing_data.csv"

ROWS = [
    ["2026-01-01", "Google Ads", "Search - Growth Plan", "NovaPay", 120000, 9600, 1320, 420, 18000, 61500],
    ["2026-01-01", "Meta Ads", "Lookalike - New Users", "BrightLoan", 180000, 7200, 760, 190, 14500, 24200],
    ["2026-01-01", "Email", "Lifecycle - Warm Leads", "NovaPay", 52000, 10400, 2180, 840, 1900, 89800],
    ["2026-01-01", "TikTok Ads", "Short Form Education", "BrightLoan", 210000, 8400, 690, 130, 9800, 14900],
    ["2026-01-01", "Affiliate", "Partner Marketplace", "OrbitCard", 90000, 5400, 980, 350, 8500, 40250],
    ["2026-02-01", "Google Ads", "Search - Growth Plan", "NovaPay", 135000, 11475, 1600, 510, 20250, 77000],
    ["2026-02-01", "Meta Ads", "Lookalike - New Users", "BrightLoan", 200000, 8600, 930, 240, 16200, 31100],
    ["2026-02-01", "Email", "Lifecycle - Warm Leads", "NovaPay", 61000, 12810, 2660, 1010, 2100, 112000],
    ["2026-02-01", "TikTok Ads", "Short Form Education", "BrightLoan", 230000, 10120, 860, 165, 11200, 19800],
    ["2026-02-01", "Affiliate", "Partner Marketplace", "OrbitCard", 98000, 6174, 1110, 410, 9400, 48000],
    ["2026-03-01", "Google Ads", "Search - Growth Plan", "NovaPay", 150000, 12900, 1800, 590, 22500, 91500],
    ["2026-03-01", "Meta Ads", "Lookalike - New Users", "BrightLoan", 220000, 9900, 1020, 280, 18100, 37600],
    ["2026-03-01", "Email", "Lifecycle - Warm Leads", "NovaPay", 68000, 14280, 2880, 1130, 2400, 128500],
    ["2026-03-01", "TikTok Ads", "Short Form Education", "BrightLoan", 250000, 11250, 950, 185, 12800, 22800],
    ["2026-03-01", "Affiliate", "Partner Marketplace", "OrbitCard", 105000, 6825, 1240, 470, 10100, 56800],
    ["2026-04-01", "Google Ads", "Search - Growth Plan", "NovaPay", 170000, 14450, 2050, 690, 25500, 108200],
    ["2026-04-01", "Meta Ads", "Lookalike - New Users", "BrightLoan", 245000, 11270, 1200, 330, 20400, 44900],
    ["2026-04-01", "Email", "Lifecycle - Warm Leads", "NovaPay", 74000, 15910, 3200, 1260, 2700, 147600],
    ["2026-04-01", "TikTok Ads", "Short Form Education", "BrightLoan", 278000, 12510, 1060, 215, 14500, 27400],
    ["2026-04-01", "Affiliate", "Partner Marketplace", "OrbitCard", 112000, 7504, 1390, 530, 11200, 65700],
]

COLUMNS = [
    "date", "channel", "campaign", "product", "impressions", "clicks",
    "leads", "customers", "spend", "revenue"
]

def create_database():
    DATA_DIR.mkdir(exist_ok=True)
    df = pd.DataFrame(ROWS, columns=COLUMNS)
    df.to_csv(CSV_PATH, index=False)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("marketing_performance", conn, if_exists="replace", index=False)
        conn.execute("""
            CREATE VIEW IF NOT EXISTS channel_summary AS
            SELECT
                channel,
                SUM(impressions) AS impressions,
                SUM(clicks) AS clicks,
                SUM(leads) AS leads,
                SUM(customers) AS customers,
                SUM(spend) AS spend,
                SUM(revenue) AS revenue,
                ROUND(1.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 4) AS ctr,
                ROUND(1.0 * SUM(leads) / NULLIF(SUM(clicks), 0), 4) AS lead_rate,
                ROUND(1.0 * SUM(customers) / NULLIF(SUM(leads), 0), 4) AS conversion_rate,
                ROUND(1.0 * SUM(spend) / NULLIF(SUM(customers), 0), 2) AS cac,
                ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
            FROM marketing_performance
            GROUP BY channel
        """)
        conn.commit()

    print(f"Database created at: {DB_PATH}")
    print(f"CSV created at: {CSV_PATH}")

if __name__ == "__main__":
    create_database()
