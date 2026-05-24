import streamlit as st
import pandas as pd

SHEET_NAME = "Ward Data Collecting Sheet"

st.set_page_config(page_title="Ward Daily Report", layout="wide")
st.title("Ward Daily Report")

col1, col2 = st.columns([1, 2])

with col1:
    query_date = st.date_input("Query Date")

with col2:
    uploaded_file = st.file_uploader("Upload Ward Excel File", type=["xlsx", "xls"])

if uploaded_file and query_date:
    query_date_str = str(query_date)

    try:
        xl = pd.ExcelFile(uploaded_file)

        if SHEET_NAME not in xl.sheet_names:
            st.error(
                f"Sheet '{SHEET_NAME}' not found. Available sheets: {xl.sheet_names}"
            )
            st.stop()

        df = xl.parse(SHEET_NAME)
        df = df.dropna(axis=1, how="all")

        # Normalize date columns
        df["Date of Admission"] = pd.to_datetime(
            df["Date of Admission"], errors="coerce"
        )
        df["DATE  OF DISCHARGE"] = pd.to_datetime(
            df["DATE  OF DISCHARGE"], errors="coerce"
        )

        query_dt = pd.to_datetime(query_date_str)

        # --- Discharge counts ---
        dis_df = df[
            (df["DATE  OF DISCHARGE"].dt.normalize() == query_dt)
            & (df["Status Of Discharge"] == "Cured")
        ]
        dama_df = df[
            (df["DATE  OF DISCHARGE"].dt.normalize() == query_dt)
            & (df["Status Of Discharge"] == "DAMA")
        ]
        transfered_df = df[
            (df["DATE  OF DISCHARGE"].dt.normalize() == query_dt)
            & (df["Status Of Discharge"] == "Transferred")
        ]

        dis_count = dis_df.shape[0]
        dama_count = dama_df.shape[0]
        transfered_count = transfered_df.shape[0]
        total_discharge_count = dis_count + dama_count + transfered_count

        admitted_df = df[df["Date of Admission"].dt.normalize() == query_dt]
        admitted_count = admitted_df.shape[0]

        # --- Occupied beds ---
        occ_df = df[
            (df["Date of Admission"].dt.normalize() <= query_dt)
            & (
                df["DATE  OF DISCHARGE"].isna()
                | (df["DATE  OF DISCHARGE"].dt.normalize() >= query_dt)
            )
        ]
        ob_agg_df = (
            occ_df.groupby("Sepciality").size().reset_index(name="Occupied Beds")
        )

        remaining_df = occ_df[occ_df["Date of Admission"].dt.normalize() < query_dt]
        remaining_count = remaining_df.shape[0]

        # --- Display ---
        st.divider()
        st.subheader(f"Summary for {query_date_str}")

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("New Admissions", admitted_count)
        m2.metric("Remaining from Past Days", remaining_count)
        m3.metric("Total Discharges", total_discharge_count)
        m4.metric("Discharged (Cured)", dis_count)
        m5.metric("DAMA", dama_count)
        m6.metric("Transferred", transfered_count)

        st.divider()
        st.subheader("Occupied Beds by Speciality")

        if ob_agg_df.empty:
            st.info("No occupied beds found for this date.")
        else:
            total = ob_agg_df["Occupied Beds"].sum()
            ob_agg_df_display = pd.concat(
                [
                    ob_agg_df,
                    pd.DataFrame([{"Sepciality": "**Total**", "Occupied Beds": total}]),
                ],
                ignore_index=True,
            )
            st.dataframe(ob_agg_df_display, use_container_width=True, hide_index=True)

            with st.expander("Raw records — Occupied Beds"):
                st.dataframe(occ_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Discharge Records")

        discharge_tabs = st.tabs(["Cured", "DAMA", "Transferred", "All Discharges"])
        with discharge_tabs[0]:
            if dis_df.empty:
                st.info("No cured discharges on this date.")
            else:
                st.dataframe(dis_df, use_container_width=True, hide_index=True)
        with discharge_tabs[1]:
            if dama_df.empty:
                st.info("No DAMA discharges on this date.")
            else:
                st.dataframe(dama_df, use_container_width=True, hide_index=True)
        with discharge_tabs[2]:
            if transfered_df.empty:
                st.info("No transfers on this date.")
            else:
                st.dataframe(transfered_df, use_container_width=True, hide_index=True)
        with discharge_tabs[3]:
            all_dis_df = pd.concat([dis_df, dama_df, transfered_df], ignore_index=True)
            if all_dis_df.empty:
                st.info("No discharges on this date.")
            else:
                st.dataframe(all_dis_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info(
        "Please select a query date and upload the Excel file to generate the report."
    )
