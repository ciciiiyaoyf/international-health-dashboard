import plotly.express as px
import streamlit as st

from utils import (
    case_table,
    create_page_navigation,
    create_sidebar,
    format_days,
    format_percent,
    initialize_page,
    load_data,
    plotly_layout,
)


initialize_page("Scheduling and Navigation")

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Scheduling and Navigation")

st.title("Scheduling and Navigation")
st.caption("Follow appointment scheduling, first-visit timing, interpreter needs, visa support, and navigation support.")

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

scheduled_rate = filtered_df["appointment_scheduled_date"].notna().mean() * 100
median_first_visit = filtered_df["days_to_first_visit"].dropna().median()
interpreter_cases = int((filtered_df["interpreter_required"] == "Yes").sum())
visa_cases = int((filtered_df["visa_support_required"] == "Yes").sum())

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Scheduled Rate", format_percent(scheduled_rate))
kpi_2.metric("Median Days to First Visit", format_days(median_first_visit))
kpi_3.metric("Interpreter Needed", f"{interpreter_cases:,}")
kpi_4.metric("Visa Support Needed", f"{visa_cases:,}")

left_col, right_col = st.columns(2)

with left_col:
    schedule_counts = (
        filtered_df["scheduling_status"]
        .value_counts()
        .rename_axis("scheduling_status")
        .reset_index(name="cases")
    )
    fig = px.bar(
        schedule_counts,
        x="scheduling_status",
        y="cases",
        labels={"scheduling_status": "Scheduling status", "cases": "Cases"},
        color="scheduling_status",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    navigation_counts = (
        filtered_df["navigation_need"]
        .value_counts()
        .rename_axis("navigation_need")
        .reset_index(name="cases")
    )
    fig = px.bar(
        navigation_counts,
        x="cases",
        y="navigation_need",
        orientation="h",
        labels={"navigation_need": "Navigation need", "cases": "Cases"},
        color="cases",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Upcoming and Scheduled Visits")
scheduled_cases = filtered_df[
    filtered_df["appointment_scheduled_date"].notna()
].sort_values("first_visit_date")

st.dataframe(
    case_table(
        scheduled_cases,
        [
            "case_id",
            "patient_country",
            "service_line",
            "coordinator",
            "appointment_scheduled_date",
            "first_visit_date",
            "navigation_status",
            "navigation_need",
            "delay_risk",
        ],
    ),
    use_container_width=True,
    hide_index=True,
)
