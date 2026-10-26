import plotly.express as px
import streamlit as st

from utils import (
    RISK_ORDER,
    active_case_mask,
    case_table,
    create_page_navigation,
    create_sidebar,
    format_days,
    format_percent,
    initialize_page,
    load_data,
    plotly_layout,
)


initialize_page()

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Home")

st.title("International Health Operations Dashboard")
st.caption(
    "Operational view of international patient intake, documentation, financial clearance, scheduling, navigation, and coordinator workload."
)

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

total_cases = len(filtered_df)
active_cases = int(active_case_mask(filtered_df).sum())
intake_completion_rate = filtered_df["intake_completed_date"].notna().mean() * 100
median_days_to_schedule = filtered_df["days_to_schedule"].dropna().median()

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Total Cases", f"{total_cases:,}")
kpi_2.metric("Active Cases", f"{active_cases:,}")
kpi_3.metric("Intake Completion Rate", format_percent(intake_completion_rate))
kpi_4.metric("Median Days to Schedule", format_days(median_days_to_schedule))

st.markdown("### Operations Snapshot")
left_col, right_col = st.columns(2)

with left_col:
    status_counts = (
        filtered_df["case_status"]
        .value_counts()
        .rename_axis("case_status")
        .reset_index(name="cases")
    )
    fig = px.bar(
        status_counts,
        x="case_status",
        y="cases",
        labels={"case_status": "Case status", "cases": "Cases"},
        color="case_status",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    risk_counts = (
        filtered_df["delay_risk"]
        .value_counts()
        .rename_axis("delay_risk")
        .reset_index(name="cases")
    )
    risk_counts["sort_order"] = risk_counts["delay_risk"].map(RISK_ORDER)
    risk_counts = risk_counts.sort_values("sort_order")
    fig = px.bar(
        risk_counts,
        x="delay_risk",
        y="cases",
        labels={"delay_risk": "Delay risk", "cases": "Cases"},
        color="delay_risk",
        color_discrete_map={"High": "#dc2626", "Medium": "#ca8a04", "Low": "#16a34a"},
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Active Case Queue")
queue = filtered_df[active_case_mask(filtered_df)].copy()
queue["risk_sort"] = queue["delay_risk"].map(RISK_ORDER)
queue = queue.sort_values(["risk_sort", "priority_level", "referral_date"]).head(12)

st.dataframe(case_table(queue), use_container_width=True, hide_index=True)
