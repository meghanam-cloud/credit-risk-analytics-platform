
import os
import getpass

import pandas as pd
import psycopg
import streamlit as st


# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Credit Risk Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("Credit Risk Analytics Dashboard")
st.caption("Monthly mortgage performance and delinquency monitoring")


# --------------------------------------------------
# 2. Database connection
# --------------------------------------------------
@st.cache_resource
def get_connection():
    password = os.getenv("PGPASSWORD")

    if not password:
        password = getpass.getpass(
            "PostgreSQL password: "
        )
    return psycopg.connect(
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5432")),
    dbname=os.getenv("PGDATABASE", "credit_risk_db"),
    user=os.getenv("PGUSER", "postgres"),
    password=password,
    )



# --------------------------------------------------
# 3. Load monthly analytics
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_monthly_summary():
    query = """
        SELECT
            reporting_month,
            total_records,
            delinquent_30_plus,
            delinquent_60_plus,
            delinquent_90_plus
        FROM analytics.monthly_delinquency_summary
        ORDER BY reporting_month;
    """

    with get_connection().cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            description.name
            for description in cursor.description
        ]

    return pd.DataFrame(rows, columns=columns)


try:
    df = load_monthly_summary()
except Exception as exc:
    st.error(
        "Could not load the analytics data. "
        "Check that PostgreSQL is running and the "
        "analytics tables exist."
    )
    st.exception(exc)
    st.stop()


if df.empty:
    st.warning("No monthly analytics data was found.")
    st.stop()


# --------------------------------------------------
# 4. Calculate delinquency rates
# --------------------------------------------------
df["reporting_month"] = pd.to_datetime(df["reporting_month"])

for count_column, rate_column in [
    ("delinquent_30_plus", "rate_30_plus"),
    ("delinquent_60_plus", "rate_60_plus"),
    ("delinquent_90_plus", "rate_90_plus"),
]:
    df[rate_column] = (
        df[count_column] / df["total_records"] * 100
    )


# --------------------------------------------------
# 5. Date filters
# --------------------------------------------------
st.sidebar.header("Dashboard Filters")

min_month = df["reporting_month"].min().date()
max_month = df["reporting_month"].max().date()

date_range = st.sidebar.date_input(
    "Reporting period",
    value=(min_month, max_month),
    min_value=min_month,
    max_value=max_month,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = df[
        (df["reporting_month"].dt.date >= start_date)
        & (df["reporting_month"].dt.date <= end_date)
    ]
else:
    filtered = df.copy()


if filtered.empty:
    st.warning("No records are available for this date range.")
    st.stop()


# --------------------------------------------------
# 6. Portfolio KPI cards
# --------------------------------------------------
total_records = int(filtered["total_records"].sum())
total_30 = int(filtered["delinquent_30_plus"].sum())
total_60 = int(filtered["delinquent_60_plus"].sum())
total_90 = int(filtered["delinquent_90_plus"].sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Performance Records", f"{total_records:,}")
col2.metric(
    "30+ Delinquency Rate",
    f"{total_30 / total_records * 100:.2f}%"
    if total_records else "N/A",
)
col3.metric(
    "60+ Delinquency Rate",
    f"{total_60 / total_records * 100:.2f}%"
    if total_records else "N/A",
)
col4.metric(
    "90+ Delinquency Rate",
    f"{total_90 / total_records * 100:.2f}%"
    if total_records else "N/A",
)


# --------------------------------------------------
# 6.1 Latest-month business insights
# --------------------------------------------------
st.subheader("Latest Month Risk Insights")

monthly = filtered.sort_values("reporting_month")

if len(monthly) >= 2:
    latest = monthly.iloc[-1]
    previous = monthly.iloc[-2]

    latest_rate = latest["rate_30_plus"]
    previous_rate = previous["rate_30_plus"]

    change = latest_rate - previous_rate

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Latest Reporting Month",
        latest["reporting_month"].strftime("%B %Y"),
    )

    col2.metric(
        "Latest 30+ Delinquency Rate",
        f"{latest_rate:.2f}%",
        delta=f"{change:+.2f} percentage points",
        delta_color="inverse",
    )

    col3.metric(
        "Latest 90+ Delinquency Rate",
        f"{latest['rate_90_plus']:.2f}%",
    )

    if change > 0:
        st.warning(
            "The 30+ delinquency rate increased compared "
            "with the previous reporting month."
        )
    elif change < 0:
        st.success(
            "The 30+ delinquency rate decreased compared "
            "with the previous reporting month."
        )
    else:
        st.info(
            "The 30+ delinquency rate was unchanged "
            "compared with the previous reporting month."
        )
else:
    st.info(
        "Select at least two reporting months to compare trends."
    )




# --------------------------------------------------
# 6.2 Portfolio Breakdown
# --------------------------------------------------
st.subheader("Portfolio Breakdown")


@st.cache_data(ttl=300)
def load_portfolio_breakdowns():
    with get_connection().cursor() as cursor:
        # Loans grouped by purpose, with readable labels
        cursor.execute("""
            SELECT
                CASE
                    WHEN loan_purpose = 'N'
                        THEN 'Refinance - No Cash Out'
                    WHEN loan_purpose = 'P'
                        THEN 'Purchase'
                    WHEN loan_purpose = 'C'
                        THEN 'Refinance - Cash Out'
                    ELSE COALESCE(
                        NULLIF(BTRIM(loan_purpose), ''),
                        'Unknown'
                    )
                END AS loan_purpose,
                COUNT(*) AS loan_count
            FROM analytics.loan_origination
            GROUP BY 1
            ORDER BY loan_count DESC;
        """)
        purpose_rows = cursor.fetchall()

        # Loans grouped by property state
        cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(BTRIM(property_state), ''),
                    'Unknown'
                ) AS property_state,
                COUNT(*) AS loan_count
            FROM analytics.loan_origination
            GROUP BY 1
            ORDER BY loan_count DESC;
        """)
        state_rows = cursor.fetchall()

    return (
        pd.DataFrame(
            purpose_rows,
            columns=["Loan Purpose", "Loan Count"]
        ),
        pd.DataFrame(
            state_rows,
            columns=["Property State", "Loan Count"]
        ),
    )


try:
    purpose_df, state_df = load_portfolio_breakdowns()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Loans by Purpose")
        st.bar_chart(
            purpose_df.set_index("Loan Purpose"),
            y="Loan Count",
        )

    with col2:
        st.markdown("#### Loans by Property State")
        st.bar_chart(
            state_df.head(15).set_index("Property State"),
            y="Loan Count",
        )
        st.caption("Showing the 15 states with the most loans.")

except Exception:
    st.error(
        "Unable to load portfolio breakdowns. "
        "Check the Streamlit terminal for the error details."
    )




# --------------------------------------------------
# 7. Delinquency trend chart
# --------------------------------------------------
st.subheader("Monthly Delinquency Rates")

chart_data = filtered[
    [
        "reporting_month",
        "rate_30_plus",
        "rate_60_plus",
        "rate_90_plus",
    ]
].copy()

chart_data["Month"] = chart_data["reporting_month"]

chart_data = chart_data.set_index("Month")[
    ["rate_30_plus", "rate_60_plus", "rate_90_plus"]
].rename(
    columns={
        "rate_30_plus": "30+ days",
        "rate_60_plus": "60+ days",
        "rate_90_plus": "90+ days",
    }
)

st.line_chart(chart_data, y_label="Delinquency rate (%)")


# --------------------------------------------------
# 8. Monthly record counts
# --------------------------------------------------
st.subheader("Monthly Performance Records")

st.bar_chart(
    filtered.set_index("reporting_month")[
        ["total_records"]
    ],
    y_label="Records",
)


# --------------------------------------------------
# 9. Monthly detail table
# --------------------------------------------------
st.subheader("Monthly Risk Summary")

display_df = filtered[
    [
        "reporting_month",
        "total_records",
        "delinquent_30_plus",
        "rate_30_plus",
        "delinquent_60_plus",
        "rate_60_plus",
        "delinquent_90_plus",
        "rate_90_plus",
    ]
].copy()

display_df = display_df.rename(
    columns={
        "reporting_month": "Reporting Month",
        "total_records": "Performance Records",
        "delinquent_30_plus": "30+ Records",
        "rate_30_plus": "30+ Rate (%)",
        "delinquent_60_plus": "60+ Records",
        "rate_60_plus": "60+ Rate (%)",
        "delinquent_90_plus": "90+ Records",
        "rate_90_plus": "90+ Rate (%)",
    }
)

rate_columns = [
    "30+ Rate (%)",
    "60+ Rate (%)",
    "90+ Rate (%)",
]

display_df[rate_columns] = display_df[rate_columns].round(2)

display_df["Reporting Month"] = (
    display_df["Reporting Month"].dt.strftime("%b %Y")
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Rates are calculated as delinquent monthly performance "
    "records divided by all monthly performance records "
    "in the selected period. These are record-level rates, "
    "not unique-borrower rates or official portfolio default rates."
)
