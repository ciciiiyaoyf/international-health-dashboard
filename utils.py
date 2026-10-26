from pathlib import Path
import base64

import pandas as pd
import streamlit as st


DATA_PATH = Path("data") / "international_patient_cases.xlsx"

DATE_COLUMNS = [
    "referral_date",
    "intake_started_date",
    "intake_completed_date",
    "records_received_date",
    "financial_clearance_date",
    "appointment_scheduled_date",
    "first_visit_date",
]

COMPLETED_STATUSES = {"First Visit Complete", "Closed"}

RISK_ORDER = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_ORDER = {"Urgent": 0, "High": 1, "Routine": 2}

PAGE_LINKS = [
    ("Home", "/"),
    ("Case Overview", "/Case_Overview"),
    ("Intake and Documents", "/Intake_and_Documents"),
    ("Scheduling and Navigation", "/Scheduling_and_Navigation"),
    ("Case Management", "/Case_Management"),
    ("Risk Prioritization", "/Risk_Prioritization"),
]

CASE_TABLE_COLUMNS = [
    "case_id",
    "patient_country",
    "service_line",
    "coordinator",
    "case_status",
    "priority_level",
    "delay_risk",
    "referral_date",
    "next_action",
]

COLUMN_LABELS = {
    "case_id": "Case ID",
    "patient_country": "Country",
    "region": "Region",
    "preferred_language": "Language",
    "coordinator": "Coordinator",
    "service_line": "Service Line",
    "case_status": "Case Status",
    "priority_level": "Priority",
    "delay_risk": "Delay Risk",
    "referral_date": "Referral Date",
    "documentation_status": "Documentation Status",
    "financial_clearance_status": "Financial Clearance",
    "scheduling_status": "Scheduling Status",
    "navigation_status": "Navigation Status",
    "navigation_need": "Navigation Need",
    "intake_completed_date": "Intake Completed",
    "records_received_date": "Records Received",
    "financial_clearance_date": "Financial Cleared",
    "appointment_scheduled_date": "Appointment Scheduled",
    "first_visit_date": "First Visit",
    "days_to_intake_complete": "Days to Intake",
    "days_to_records_received": "Days to Records",
    "days_to_financial_clearance": "Days to Clearance",
    "days_to_schedule": "Days to Schedule",
    "days_to_first_visit": "Days to First Visit",
    "next_action": "Next Action",
}


def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def initialize_page(page_title="International Health Operations Dashboard"):
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        page_icon="assets/images/logo.png",
        initial_sidebar_state="expanded",
    )

    css_path = Path("assets") / "styles.css"
    if css_path.exists():
        with open(css_path) as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH, sheet_name="Cases")
    df.columns = [column.strip() for column in df.columns]

    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    df["case_id"] = df["case_id"].astype(str)
    df["estimated_deposit_usd"] = pd.to_numeric(
        df["estimated_deposit_usd"], errors="coerce"
    )

    as_of_date = df[DATE_COLUMNS].max().max()
    df["days_since_referral"] = (as_of_date - df["referral_date"]).dt.days

    df["days_to_intake_complete"] = (
        df["intake_completed_date"] - df["referral_date"]
    ).dt.days
    df["days_to_records_received"] = (
        df["records_received_date"] - df["referral_date"]
    ).dt.days
    df["days_to_financial_clearance"] = (
        df["financial_clearance_date"] - df["referral_date"]
    ).dt.days
    df["days_to_schedule"] = (
        df["appointment_scheduled_date"] - df["referral_date"]
    ).dt.days
    df["days_to_first_visit"] = (df["first_visit_date"] - df["referral_date"]).dt.days

    df["delay_risk"] = df.apply(assign_delay_risk, axis=1)

    return df


def assign_delay_risk(row):
    if row["case_status"] in COMPLETED_STATUSES:
        return "Low"

    unscheduled = pd.isna(row["appointment_scheduled_date"])
    intake_open = row["documentation_status"] != "Complete"
    clearance_open = row["financial_clearance_status"] != "Cleared"
    days_open = row["days_since_referral"]

    if row["priority_level"] == "Urgent" and unscheduled:
        return "High"
    if intake_open and days_open > 10:
        return "High"
    if clearance_open and days_open > 14:
        return "High"
    if unscheduled and days_open > 21:
        return "High"
    if row["days_to_schedule"] > 21 or row["days_to_first_visit"] > 35:
        return "High"

    if intake_open and days_open > 5:
        return "Medium"
    if clearance_open and days_open > 7:
        return "Medium"
    if unscheduled and days_open > 10:
        return "Medium"
    if row["days_to_schedule"] > 14 or row["days_to_first_visit"] > 28:
        return "Medium"

    return "Low"


def active_case_mask(df):
    return ~df["case_status"].isin(COMPLETED_STATUSES)


def create_sidebar(df):
    logo_path = Path("assets") / "images" / "logo.png"
    if logo_path.exists():
        st.sidebar.markdown(
            f"""
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{img_to_base64(logo_path)}" width="36">
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        "<div class='sidebar-title'>International Health Operations</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Filters")

    min_date = df["referral_date"].min().date()
    max_date = df["referral_date"].max().date()
    selected_range = st.sidebar.date_input(
        "Referral date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date = pd.Timestamp(selected_range[0])
        end_date = pd.Timestamp(selected_range[1])
    else:
        start_date = pd.Timestamp(min_date)
        end_date = pd.Timestamp(max_date)

    filtered_df = df[
        (df["referral_date"] >= start_date) & (df["referral_date"] <= end_date)
    ].copy()

    filtered_df = apply_multiselect_filter(
        filtered_df,
        "case_status",
        "Case status",
    )
    filtered_df = apply_multiselect_filter(
        filtered_df,
        "coordinator",
        "Coordinator",
    )
    filtered_df = apply_multiselect_filter(
        filtered_df,
        "service_line",
        "Service line",
    )
    filtered_df = apply_multiselect_filter(
        filtered_df,
        "delay_risk",
        "Delay risk",
    )

    st.sidebar.caption(f"{len(filtered_df):,} cases in current view")
    return filtered_df


def apply_multiselect_filter(df, column, label):
    options = sorted(df[column].dropna().unique().tolist())
    selected = st.sidebar.multiselect(label, options=options, default=[])
    if selected:
        return df[df[column].isin(selected)].copy()
    return df


def create_page_navigation(active_page):
    links = []
    for label, href in PAGE_LINKS:
        active = "true" if label == active_page else "false"
        links.append(
            f"<a target='_self' href='{href}' class='nav-link' data-active='{active}'>{label}</a>"
        )

    st.markdown(
        f"<nav class='top-nav'>{''.join(links)}</nav>",
        unsafe_allow_html=True,
    )


def format_days(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.0f} days"


def format_percent(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def case_table(df, columns=None):
    selected_columns = columns or CASE_TABLE_COLUMNS
    available_columns = [column for column in selected_columns if column in df.columns]
    table = df[available_columns].copy()

    for column in table.columns:
        if column.endswith("_date") or column == "referral_date":
            table[column] = table[column].dt.strftime("%Y-%m-%d").fillna("")

    return table.rename(columns=COLUMN_LABELS)


def plotly_layout(fig, height=360):
    fig.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 45, "b": 30},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
    )
    return fig
