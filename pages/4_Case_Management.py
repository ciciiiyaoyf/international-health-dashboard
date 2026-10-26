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


initialize_page("Case Management")

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Case Management")

st.title("Case Management")
st.caption("Review coordinator workload, active case mix, and operational follow-up needs.")

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

workload_df = filtered_df.copy()
workload_df["is_active"] = active_case_mask(workload_df)
workload_df["is_high_risk"] = workload_df["delay_risk"] == "High"
workload_df["is_unscheduled_active"] = workload_df["is_active"] & workload_df[
    "appointment_scheduled_date"
].isna()

summary = (
    workload_df.groupby("coordinator")
    .agg(
        total_cases=("case_id", "count"),
        active_cases=("is_active", "sum"),
        high_risk_cases=("is_high_risk", "sum"),
        unscheduled_active=("is_unscheduled_active", "sum"),
        median_days_to_schedule=("days_to_schedule", "median"),
    )
    .reset_index()
    .sort_values("active_cases", ascending=False)
)

avg_active = summary["active_cases"].mean()
max_active = summary["active_cases"].max()
high_risk_total = summary["high_risk_cases"].sum()
unscheduled_total = summary["unscheduled_active"].sum()

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Avg Active per Coordinator", f"{avg_active:.1f}")
kpi_2.metric("Highest Active Load", f"{max_active:,}")
kpi_3.metric("High-Risk Active Cases", f"{high_risk_total:,}")
kpi_4.metric("Unscheduled Active Cases", f"{unscheduled_total:,}")

left_col, right_col = st.columns(2)

with left_col:
    fig = px.bar(
        summary,
        x="coordinator",
        y="active_cases",
        labels={"coordinator": "Coordinator", "active_cases": "Active cases"},
        color="high_risk_cases",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    status_mix = (
        workload_df[workload_df["is_active"]]
        .groupby(["coordinator", "case_status"])
        .size()
        .reset_index(name="cases")
    )
    fig = px.bar(
        status_mix,
        x="coordinator",
        y="cases",
        color="case_status",
        labels={"coordinator": "Coordinator", "cases": "Cases"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Coordinator Summary")
display_summary = summary.rename(
    columns={
        "coordinator": "Coordinator",
        "total_cases": "Total Cases",
        "active_cases": "Active Cases",
        "high_risk_cases": "High-Risk Cases",
        "unscheduled_active": "Unscheduled Active",
        "median_days_to_schedule": "Median Days to Schedule",
    }
)
display_summary = display_summary.fillna({"Median Days to Schedule": "N/A"})
st.dataframe(display_summary, use_container_width=True, hide_index=True)

st.markdown("### Follow-Up Worklist")
worklist = workload_df[
    workload_df["is_active"]
    & (
        (workload_df["delay_risk"] == "High")
        | workload_df["appointment_scheduled_date"].isna()
        | (workload_df["documentation_status"] != "Complete")
    )
].sort_values(["delay_risk", "referral_date"])

st.dataframe(case_table(worklist), use_container_width=True, hide_index=True)
