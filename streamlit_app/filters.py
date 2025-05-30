import streamlit as st
import pandas as pd
from typing import List, Tuple

def display_sidebar(data: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp, List[str], List[str], List[str]]:
    # Inject custom CSS for multiselect dropdowns
    st.markdown(
        """
        <style>
        /* Style for selected items in multiselect */
        .stMultiSelect > div > div > div [aria-selected="true"] {
            background-color: rgba(72, 209, 204, 0.2); /* Sea Green-Blue color with transparency */
            color: white; /* White text for better readability */
        }

        /* Style for selected items in multiselect */
        .stMultiSelect > div > div > div [aria-selected="true"]:nth-child(odd) {
            background-color: rgba(32, 178, 170, 0.2); /* Different shade for odd items */
        }

        /* Hover effect for selected items */
        .stMultiSelect > div > div > div:hover {
            background-color: rgba(0, 139, 139, 0.2); /* Darker Green-Blue when hovered */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.header("Filters")
    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['send_date'].min().date())).tz_localize("UTC")
    last_date = pd.Timestamp(st.sidebar.date_input("End date", data['send_date'].max().date())).tz_localize("UTC")
    positions = sorted(data['position_group'].unique())
    selected_positions = st.sidebar.multiselect("Department", positions, positions)
    selected_templates = st.sidebar.multiselect("Select Template", data['template_name'].unique())
    selected_statuses = st.sidebar.multiselect("Select Status", data['status'].unique())
    email_reported = st.sidebar.selectbox("Email Reported", options=["Both", "Reported", "Not Reported"], index=0)
    return start_date, last_date, selected_positions, selected_templates, selected_statuses, email_reported

def filter_data(
    data: pd.DataFrame, 
    start_date: pd.Timestamp, 
    last_date: pd.Timestamp, 
    positions: List[str], 
    templates: List[str], 
    statuses: List[str],
    email_reported: bool
) -> pd.DataFrame:
    filtered = data[(data['send_date'] >= start_date) & (data['send_date'] < (last_date + pd.Timedelta(days=1)))].copy()
    filtered = filtered[filtered['position_group'].isin(positions)] if positions else filtered
    filtered = filtered[filtered['template_name'].isin(templates)] if templates else filtered
    filtered = filtered[filtered['status'].isin(statuses)] if statuses else filtered
    if email_reported == "Reported":
        filtered = filtered[filtered['reported'] == True]
    elif email_reported == "Not Reported":
        filtered = filtered[filtered['reported'] == False]
    # If "Both" is selected, no need to filter

    return filtered
