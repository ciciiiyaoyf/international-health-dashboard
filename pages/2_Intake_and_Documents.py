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


initialize_page("Intake and Documents")

df = load_data()
filtered_df = create_sidebar(df)
create_page_navigation("Intake and Documents")

st.title("Intake and Documents")
st.caption("Track intake completion, medical records receipt, and documentation gaps.")

if filtered_df.empty:
    st.info("No cases match the current filters.")
    st.stop()

intake_rate = filtered_df["intake_completed_date"].notna().mean() * 100
records_rate = filtered_df["records_received_date"].notna().mean() * 100
median_intake_days = filtered_df["days_to_intake_complete"].dropna().median()
median_records_days = filtered_df["days_to_records_received"].dropna().median()

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("Intake Completion Rate", format_percent(intake_rate))
kpi_2.metric("Records Received Rate", format_percent(records_rate))
kpi_3.metric("Median Days to Intake", format_days(median_intake_days))
kpi_4.metric("Median Days to Records", format_days(median_records_days))

left_col, right_col = st.columns(2)

with left_col:
    doc_counts = (
        filtered_df["documentation_status"]
        .value_counts()
        .rename_axis("documentation_status")
        .reset_index(name="cases")
    )
    fig = px.bar(
        doc_counts,
        x="documentation_status",
        y="cases",
        labels={"documentation_status": "Documentation status", "cases": "Cases"},
        color="documentation_status",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

with right_col:
    language_counts = (
        filtered_df["preferred_language"]
        .value_counts()
        .rename_axis("preferred_language")
        .reset_index(name="cases")
    )
    fig = px.bar(
        language_counts,
        x="cases",
        y="preferred_language",
        orientation="h",
        labels={"preferred_language": "Language", "cases": "Cases"},
        color="cases",
        color_continuous_scale="Greens",
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True)

st.markdown("### Open Documentation Follow-Up")
pending_docs = filtered_df[filtered_df["documentation_status"] != "Complete"].sort_values(
    ["delay_risk", "referral_date"]
)
st.dataframe(
    case_table(
        pending_docs,
        [
            "case_id",
            "patient_country",
            "preferred_language",
            "coordinator",
            "documentation_status",
            "delay_risk",
            "referral_date",
            "next_action",
        ],
    ),
    use_container_width=True,
    hide_index=True,
)
