# International Health Operations Dashboard

This Streamlit dashboard models the operational workflow of an International Health department using a patient case dataset. It was designed as a hospital administration analytics project to show how data can be used to monitor international patient flow from referral intake through documentation, financial clearance, appointment scheduling, patient navigation, coordinator workload, and case prioritization.

## Project Objective

The goal of this project is to make International Health operations more visible and measurable by helping teams:

- monitor active case volume and workflow stage distribution
- identify bottlenecks in documentation, records collection, financial clearance, and scheduling
- track interpreter needs, visa-support needs, and other navigation requirements
- evaluate coordinator workload and active case mix
- prioritize cases with elevated delay risk

## Dashboard Sections

### 1. Case Overview
Tracks active cases, completed or closed cases, country mix, service line demand, and recent referrals.

### 2. Intake and Documents
Monitors intake completion, medical records receipt, documentation status, and open follow-up work.

### 3. Scheduling and Navigation
Reviews scheduling progress, first-visit timing, interpreter needs, visa support, and navigation requests.

### 4. Case Management
Evaluates coordinator workload, active case mix, and cases requiring operational follow-up.

### 5. Risk Prioritization
Flags cases with elevated delay risk based on intake, documentation, clearance, and scheduling rules.

## Dataset

The app uses a synthetic Excel workbook:

`data/international_patient_cases.xlsx`

The workbook contains a `Cases` sheet with **72 synthetic case records and 24 source fields**. All case records and coordinator labels are demonstration data, not real patient information.

Derived fields are created in `utils.py`, including:

- `days_to_intake_complete`
- `days_to_records_received`
- `days_to_financial_clearance`
- `days_to_schedule`
- `days_to_first_visit`
- `delay_risk`

## Key Business Insight

This dashboard is designed to show that the main operational challenge in international patient services is often not referral intake itself, but the conversion of active cases into scheduling-ready and visit-complete cases. In this project, documentation follow-up, records readiness, scheduling coordination, and navigation support emerge as the main workflow constraints.

## Tools Used

- Python
- Streamlit
- Pandas
- Plotly
- Excel workbook

## Setup

1. Navigate to the project folder.
2. Install dependencies using the command that works on your machine.

### Option 1

```powershell
python -m pip install -r requirements.txt
```

### Option 2

```powershell
py -m pip install -r requirements.txt
```

3. Run the dashboard:

### Option 1

```powershell
python -m streamlit run app.py
```

### Option 2

```powershell
py -m streamlit run app.py
```

## Notes

The risk prioritization logic is rule-based and operational; it is not a clinical decision tool.

The home screen and five analysis pages use the same workbook and filters. Elapsed-time metrics are measured from referral dates; open-case age is anchored to the latest event date in the sample workbook rather than today's date.

## License and Attribution

The included MIT license and original copyright notice for Sajjad Ahmadi are preserved in `LICENSE.txt`.
