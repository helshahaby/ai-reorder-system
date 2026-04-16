#Copy this Python into Snowsight → Streamlit → + New Streamlit App. It is mobile-responsive.

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(page_title="Reorder System", layout="wide")
st.title("📦 AI Predictive Reorder System")

session = get_active_session()

@st.cache_data(ttl=60)
def load_alerts():
    return session.sql(
        "SELECT * FROM REORDER_ALERTS ORDER BY SUPPLY_RISK_SCORE"
    ).to_pandas()

df = load_alerts()

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Items to reorder",  len(df[df.REORDER_STATUS=="REORDER NOW"]))
col2.metric("Items to monitor",  len(df[df.REORDER_STATUS=="MONITOR"]))
col3.metric("Avg risk score",    round(df.SUPPLY_RISK_SCORE.mean(), 2))

st.divider()

# Filter
status_filter = st.selectbox("Filter by status",
    ["All", "REORDER NOW", "MONITOR"])
if status_filter != "All":
    df = df[df.REORDER_STATUS == status_filter]

# Table
st.dataframe(df[["PRODUCT_NAME","CURRENT_STOCK","REORDER_POINT",
                  "REORDER_STATUS","SUPPLY_RISK_SCORE","EXTRACTED_DELAY",
                  "LAST_REFRESHED"]],
             use_container_width=True)

# Approve reorders
st.subheader("Approve reorders")
selected = st.multiselect("Select products to reorder",
    df[df.REORDER_STATUS=="REORDER NOW"]["PRODUCT_NAME"].tolist())
if st.button("✅ Approve selected") and selected:
    st.success(f"Reorder approved for: {', '.join(selected)}")
    # In production: INSERT into APPROVED_ORDERS table
