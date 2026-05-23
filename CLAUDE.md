# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Architecture

Single-file Streamlit app (`app.py`) that generates daily ward reports from hospital Excel files.

**Data flow:**
1. User selects a query date and uploads an Excel file
2. App parses the sheet named `"Ward Data Collecting Sheet"` using pandas/openpyxl
3. Date columns are normalized with `pd.to_datetime(..., errors="coerce")`
4. Four metrics are computed: admissions, discharges (cured/DAMA/transferred)
5. Occupied beds are aggregated by specialty and displayed as a dataframe

**Key column names in the Excel data** (exact strings — whitespace and typos matter):
- `"Date of Admission"` — admission date
- `"DATE  OF DISCHARGE"` — discharge date (two spaces)
- `"Status Of Discharge"` — values: `"Cured"`, `"DAMA"`, `"Transferred"`
- `"Sepciality"` — specialty column (intentional misspelling matching the source data)

Occupied beds logic: a patient occupies a bed on `query_dt` if `admission <= query_dt < discharge`.
