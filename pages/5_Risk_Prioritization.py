import plotly.express as px
import streamlit as st

from utils import (
    PRIORITY_ORDER,
    RISK_ORDER,
    active_case_mask,
    case_table,
    create_page_navigation,
    create_sidebar,
    initialize_page,
    load_data,
    plotly_layout,
)


initialize_page("Risk Prioritization")

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Risk Prioritization")

st.title("Risk Prioritization")
st.caption(
    "Use rule-based delay risk to focus attention on cases most likely to miss intake, clearance, scheduling, or first-visit targets."
)

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

active_df = filtered_df[active_case_mask(filtered_df)].copy()
high_risk_active = int((active_df["delay_risk"] == "High").sum())
urgent_cases = int((active_df["priority_level"] == "Urgent").sum())
pending_clearance = int((active_df["financial_clearance_status"] != "Cleared").sum())
pending_schedule = int(active_df["appointment_scheduled_date"].isna().sum())

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("High-Risk Active", f"{high_risk_active:,}")
kpi_2.metric("Urgent Active", f"{urgent_cases:,}")
kpi_3.metric("Pending Clearance", f"{pending_clearance:,}")
kpi_4.metric("Pending Scheduling", f"{pending_schedule:,}")

left_col, right_col = st.columns(2)

with left_col:
    risk_service = (
        active_df.groupby(["service_line", "delay_risk"]).size().reset_index(name="cases")
    )
    fig = px.bar(
        risk_service,
        x="service_line",
        y="cases",
        color="delay_risk",
        labels={"service_line": "Service line", "cases": "Cases"},
        color_discrete_map={"High": "#dc2626", "Medium": "#ca8a04", "Low": "#16a34a"},
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    priority_risk = (
        active_df.groupby(["priority_level", "delay_risk"]).size().reset_index(name="cases")
    )
    fig = px.bar(
        priority_risk,
        x="priority_level",
        y="cases",
        color="delay_risk",
        labels={"priority_level": "Priority", "cases": "Cases"},
        color_discrete_map={"High": "#dc2626", "Medium": "#ca8a04", "Low": "#16a34a"},
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Prioritized Case Queue")
priority_queue = active_df.copy()
priority_queue["risk_sort"] = priority_queue["delay_risk"].map(RISK_ORDER)
priority_queue["priority_sort"] = priority_queue["priority_level"].map(PRIORITY_ORDER)
priority_queue = priority_queue.sort_values(
    ["risk_sort", "priority_sort", "referral_date"]
)

st.dataframe(
    case_table(
        priority_queue,
        [
            "case_id",
            "patient_country",
            "service_line",
            "coordinator",
            "priority_level",
            "delay_risk",
            "documentation_status",
            "financial_clearance_status",
            "scheduling_status",
            "days_since_referral",
            "next_action",
        ],
    ),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "Delay risk is calculated from operational rules in utils.py. It is intended for case prioritization, not clinical diagnosis."
)
