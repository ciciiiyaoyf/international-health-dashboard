import plotly.express as px
import streamlit as st

from utils import (
    active_case_mask,
    case_table,
    create_page_navigation,
    create_sidebar,
    initialize_page,
    load_data,
    plotly_layout,
)


initialize_page("Case Overview")

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Case Overview")

st.title("Case Overview")
st.caption("Monitor referral volume, case status, country mix, and clinical service demand.")

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

active_cases = int(active_case_mask(filtered_df).sum())
closed_cases = len(filtered_df) - active_cases
country_count = filtered_df["patient_country"].nunique()
high_risk = int((filtered_df["delay_risk"] == "High").sum())

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Active Cases", f"{active_cases:,}")
kpi_2.metric("Completed or Closed", f"{closed_cases:,}")
kpi_3.metric("Countries Represented", f"{country_count:,}")
kpi_4.metric("High-Risk Cases", f"{high_risk:,}")

left_col, right_col = st.columns(2)

with left_col:
    country_counts = (
        filtered_df["patient_country"]
        .value_counts()
        .head(10)
        .rename_axis("patient_country")
        .reset_index(name="cases")
    )
    fig = px.bar(
        country_counts,
        x="cases",
        y="patient_country",
        orientation="h",
        labels={"patient_country": "Country", "cases": "Cases"},
        color="cases",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    service_counts = (
        filtered_df["service_line"]
        .value_counts()
        .rename_axis("service_line")
        .reset_index(name="cases")
    )
    fig = px.pie(
        service_counts,
        names="service_line",
        values="cases",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Recent Referrals")
recent_cases = filtered_df.sort_values("referral_date", ascending=False).head(15)
st.dataframe(case_table(recent_cases), use_container_width=True, hide_index=True)
