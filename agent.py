from dataclasses import dataclass

@dataclass
class QueryPlan:
    question_type: str
    sql: str
    chart_type: str
    explanation: str

def plan_query(question: str) -> QueryPlan:
    q = question.lower().strip()

    if "roas" in q or "return" in q:
        return QueryPlan(
            question_type="highest_roas",
            sql="""
                SELECT
                    channel,
                    SUM(spend) AS spend,
                    SUM(revenue) AS revenue,
                    ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
                FROM marketing_performance
                GROUP BY channel
                ORDER BY roas DESC
            """,
            chart_type="bar",
            explanation="Ranks channels by return on ad spend."
        )

    if "cac" in q or "acquisition" in q:
        return QueryPlan(
            question_type="lowest_cac",
            sql="""
                SELECT
                    channel,
                    SUM(customers) AS customers,
                    SUM(spend) AS spend,
                    ROUND(1.0 * SUM(spend) / NULLIF(SUM(customers), 0), 2) AS cac
                FROM marketing_performance
                GROUP BY channel
                ORDER BY cac ASC
            """,
            chart_type="bar",
            explanation="Ranks channels by customer acquisition cost."
        )

    if "campaign" in q and ("revenue" in q or "best" in q or "top" in q):
        return QueryPlan(
            question_type="top_campaign_revenue",
            sql="""
                SELECT
                    campaign,
                    channel,
                    SUM(revenue) AS revenue,
                    SUM(spend) AS spend,
                    ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
                FROM marketing_performance
                GROUP BY campaign, channel
                ORDER BY revenue DESC
            """,
            chart_type="bar",
            explanation="Finds campaigns that generated the most revenue."
        )

    if "product" in q or "customers" in q:
        return QueryPlan(
            question_type="product_customers",
            sql="""
                SELECT
                    product,
                    SUM(customers) AS customers,
                    SUM(revenue) AS revenue,
                    ROUND(1.0 * SUM(revenue) / NULLIF(SUM(customers), 0), 2) AS revenue_per_customer
                FROM marketing_performance
                GROUP BY product
                ORDER BY customers DESC
            """,
            chart_type="bar",
            explanation="Compares products by customer volume and revenue."
        )

    if "monthly" in q or "trend" in q or "over time" in q:
        return QueryPlan(
            question_type="monthly_revenue_trend",
            sql="""
                SELECT
                    date,
                    SUM(spend) AS spend,
                    SUM(revenue) AS revenue,
                    SUM(customers) AS customers,
                    ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
                FROM marketing_performance
                GROUP BY date
                ORDER BY date
            """,
            chart_type="line",
            explanation="Shows how spend, revenue, customers, and ROAS changed over time."
        )

    if "funnel" in q or "leak" in q or "drop" in q:
        return QueryPlan(
            question_type="funnel",
            sql="""
                SELECT
                    SUM(impressions) AS impressions,
                    SUM(clicks) AS clicks,
                    SUM(leads) AS leads,
                    SUM(customers) AS customers,
                    ROUND(1.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 4) AS ctr,
                    ROUND(1.0 * SUM(leads) / NULLIF(SUM(clicks), 0), 4) AS lead_rate,
                    ROUND(1.0 * SUM(customers) / NULLIF(SUM(leads), 0), 4) AS conversion_rate
                FROM marketing_performance
            """,
            chart_type="funnel",
            explanation="Analyzes conversion between funnel stages."
        )

    if "scale" in q or "budget" in q:
        return QueryPlan(
            question_type="budget_recommendation",
            sql="""
                SELECT
                    channel,
                    SUM(spend) AS spend,
                    SUM(revenue) AS revenue,
                    SUM(customers) AS customers,
                    ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas,
                    ROUND(1.0 * SUM(spend) / NULLIF(SUM(customers), 0), 2) AS cac
                FROM marketing_performance
                GROUP BY channel
                ORDER BY roas DESC, cac ASC
            """,
            chart_type="bar",
            explanation="Identifies channels that are efficient enough to consider scaling."
        )

    return QueryPlan(
        question_type="overview",
        sql="""
            SELECT
                channel,
                SUM(impressions) AS impressions,
                SUM(clicks) AS clicks,
                SUM(leads) AS leads,
                SUM(customers) AS customers,
                SUM(spend) AS spend,
                SUM(revenue) AS revenue,
                ROUND(1.0 * SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas,
                ROUND(1.0 * SUM(spend) / NULLIF(SUM(customers), 0), 2) AS cac
            FROM marketing_performance
            GROUP BY channel
            ORDER BY revenue DESC
        """,
        chart_type="bar",
        explanation="Default overview of channel performance."
    )

def create_answer(question_type: str, rows: list[dict]) -> str:
    if not rows:
        return "No rows returned."

    top = rows[0]

    if question_type == "highest_roas":
        return f"The strongest ROAS is from {top['channel']} at {top['roas']}x."
    if question_type == "lowest_cac":
        return f"The lowest CAC is from {top['channel']} at ${top['cac']} per customer."
    if question_type == "top_campaign_revenue":
        return f"The top campaign by revenue is {top['campaign']} from {top['channel']}, generating ${top['revenue']:,.0f}."
    if question_type == "product_customers":
        return f"{top['product']} has the most customers with {top['customers']:,.0f} customers."
    if question_type == "monthly_revenue_trend":
        return "Monthly trend returned. Review the chart to compare spend, revenue, customers, and ROAS over time."
    if question_type == "funnel":
        rates = {
            "Impression → Click": top["ctr"],
            "Click → Lead": top["lead_rate"],
            "Lead → Customer": top["conversion_rate"],
        }
        weakest = min(rates, key=rates.get)
        return f"The biggest funnel leak appears to be {weakest}, with a conversion rate of {rates[weakest]:.1%}."
    if question_type == "budget_recommendation":
        return f"Consider scaling {top['channel']} because it has ROAS of {top['roas']}x and CAC of ${top['cac']}."

    return f"The top result is {top}."
