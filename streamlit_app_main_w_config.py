import csv
import io
import json
import streamlit as st
import pandas as pd
from typing import List, Tuple
from gophish import Gophish
from streamlit_app.data_loader import load_data
from streamlit_app.filters import display_sidebar, filter_data
from streamlit_app.kpi_calculations import calculate_kpis_abs
from streamlit_app.visualization import display_kpi_and_funnel, display_position_analysis, calculate_kpis_table
from streamlit_app.gophish_utils import GophishClient, CampaignDataProcessor


class StreamlitApp:
    """Manages the Streamlit app interface."""

    def __init__(self, results_csv: str, events_csv: str) -> None:
        self.results_csv = results_csv
        self.events_csv = events_csv

    def run(self) -> None:
        self._display_csv_download_buttons()

    def _display_csv_download_buttons(self) -> None:
        col1, col2 = st.columns([1, 5.5])
        with col1:
            with st.expander("Export CSV Files"):
                self._create_download_button("Download Results CSV", self.results_csv, "results.csv")
                self._create_download_button("Download Events CSV", self.events_csv, "events.csv")

    @staticmethod
    def _create_download_button(label: str, data: str, file_name: str) -> None:
        st.download_button(label=label, data=data, file_name=file_name, mime="text/csv")

class Dashboard:
    """Orchestrates the entire Streamlit dashboard logic."""

    @staticmethod
    def configure_page() -> None:
        st.set_page_config(
            page_title="Phishing Campaigns Dashboard",
            page_icon="mail.png",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        st.markdown("""
            <style>
            footer {visibility: hidden;} 
            .block-container { padding-top: 1rem; padding-bottom: 1rem; }
            </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _load_data(api_key: str, data_source: str) -> Tuple[str, str]:
        if data_source == "Real Campaign Data":
            client = GophishClient(api_key=api_key)
            campaigns = client.fetch_campaigns()
            processor = CampaignDataProcessor(campaigns)
            return processor.process_campaigns()
        else:
            with open("./generated_results/generated_results.csv", "r", encoding="utf-8") as file:
                generated_results_csv = file.read()
            with open("./generated_results/generated_events.csv", "r", encoding="utf-8") as file:
                generated_events_csv = file.read()
            return generated_results_csv, generated_events_csv

    def main(self) -> None:
        self.configure_page()
        with open("config.json", "r") as file:
            config = json.load(file)
            api_key = config["GOPHISH_API_KEY"]

        st.image("mail.png", width=60)
        st.title("Phishing Campaign Dashboard")
        st.write("")

        data_source = st.sidebar.radio(
            "### **Select Data Source:**",
            options=["Generated Campaign Data", "Real Campaign Data"],
            index=0
        )

        results_csv, events_csv = self._load_data(api_key, data_source)
        results_df = load_data(results_csv)
        results_df["send_date"] = pd.to_datetime(results_df["send_date"])
        results_df["modified_date"] = pd.to_datetime(results_df["modified_date"])

        start_date, last_date, selected_positions, selected_templates, selected_statuses, email_reported = display_sidebar(results_df)
        filtered_data = filter_data(results_df, start_date, last_date, selected_positions, selected_templates, selected_statuses, email_reported)

        kpis = calculate_kpis_abs(filtered_data)
        kpi_names = ["Sent Emails", "Opened Emails", "Clicked Links", "Submitted Data", "Reported Emails"]

        st.markdown("#### Download Campaign Results and Events Data")
        st.write("")

        app = StreamlitApp(results_csv, events_csv)
        app.run()

        st.write("")
        st.divider()
        st.write("")

        display_kpi_and_funnel(filtered_data, kpis, kpi_names)
        display_position_analysis(filtered_data)

        calculate_kpis_table(filtered_data, ["Email Sent", "Email Opened", "Clicked Link", "Submitted Data", "Email Reported"])

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.main()