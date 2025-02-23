import streamlit as st
import plotly.express as px
import pandas as pd
from typing import List
from .kpi_calculations import calculate_kpis_abs, calculate_kpis_rel

def display_kpi_and_funnel(data: pd.DataFrame, kpis: List[float], kpi_names: List[str]):
    """
    Displays KPI metrics in the left column (1-column wide)
    and the funnel chart in the right column (4-columns wide).
    """
    # Insert whitespace
    st.write("")

    # Display the header for KPI Metrics
    st.header("KPI Metrics")
    st.write("")

    # Create layout with 2 columns (1:4 ratio)
    col1, col2, col3 = st.columns([1, 0.5, 4])

    # KPI Metrics in the left column
    with col1:
        st.markdown(
            """
            <style>
            .kpi-card {
                background-color: #A5DBC2;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 1px;
                margin-bottom: 1px;
                text-align: center;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            }
            .kpi-card h1 {
                font-size: 1.2rem;
                margin: 0;
                color: #333;
            }
            .kpi-card p {
                font-size: 1.2rem;
                font-weight: bold;
                margin: 0;
                color: #555;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Render each KPI as a card
        for kpi_name, kpi_value in zip(kpi_names, kpis):
            st.markdown(
                f"""
                <div class="kpi-card">
                    <h1>{kpi_value}</h1>
                    <p>{kpi_name}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Funnel Chart in the right column
    with col3:
        # Calculate KPIs for funnel chart
        abs_values = calculate_kpis_abs(data)
        rel_values = calculate_kpis_rel(data)

        # Prepare the data for the funnel chart
        funnel_data = {
            "Status": [
                "Sent Emails",
                "Opened Emails",
                "Clicked Links",
                "Submitted Data",
                "Reported Emails"
            ],
            "Count": abs_values,
            "Percentage": rel_values
        }

        # Create a DataFrame and sort by 'Percentage' in descending order
        funnel_df = pd.DataFrame(funnel_data).sort_values("Percentage")
        funnel_df["Status"] = pd.Categorical(
            funnel_df["Status"],
            categories=funnel_df["Status"][::-1],  # Reverse the order
            ordered=True
        )

        # Create the funnel chart
        fig_funnel = px.funnel(
            funnel_df,
            x="Percentage",  # The size of the funnel sections
            y="Status",  # The labels for the sections
            title="Phishing Campaign Funnel Chart",
            color="Status",  # Optional: adds color to the sections
            color_discrete_sequence=px.colors.sequential.Darkmint,
            height=500
        )

        # Remove the legend and adjust the layout
        fig_funnel.update_layout(
            showlegend=False,  # Remove the legend
            title={
                "text": "Phishing Campaign Funnel Chart",  # Title text
                "x": 0.55,  # Center the title (horizontal alignment)
                "xanchor": "center",  # Anchor the title to the center
                "yanchor": "top"  # Anchor the title to the top
            },
            font=dict(
                size=16,  # General font size for the chart
                family="Arial, sans-serif"  # Optional: Set font family
            ),
            xaxis=dict(
                title=dict(font=dict(size=16)),  # Font size for x-axis title
                tickfont=dict(size=12)  # Font size for x-axis ticks
            ),
            yaxis=dict(
                title=dict(font=dict(size=16)),  # Font size for y-axis title
                tickfont=dict(size=12)  # Font size for y-axis ticks
            )
        )
        
        # Add percentage sign to the labels
        fig_funnel.update_traces(
            texttemplate="%{x}%",  # Add '%' to the data labels
            textposition="inside",  # Place labels inside the funnel sections
            textfont=dict(
                size=16,  # Increase font size for data labels
                color="black"  # Optional: Change label color
            )
        )

        # Display the funnel chart
        st.plotly_chart(fig_funnel, use_container_width=True)

    # Insert whitespace
    st.write("")
    st.write("")

    # Insert a line break for better spacing
    st.divider()

def display_position_analysis(data: pd.DataFrame):
    """
    Display analysis of phishing campaign data by position.
    Includes bar charts and pie charts for position-based insights.
    """
    # Insert whitespace
    st.write("")

    st.header("Department Analysis")

    # Insert whitespace
    st.write("")
    st.write("")

    

    # Create layout with 2 columns
    col1, col2 = st.columns(2)

    # Group data by position and calculate metrics
    filtered_position_counts = data["position_group"].value_counts().reset_index()
    filtered_position_counts.columns = ["Position", "Count"]

    # Bar chart for positions
    with col1:
        fig_position_bar = px.bar(
            filtered_position_counts,
            x="Position",
            y="Count",
            title=f"Percentage per Department",
            color="Position",
            color_discrete_sequence=px.colors.sequential.Bluyl[-5:],
            height=450
        )
        # Update layout to remove the legend and center the title
        fig_position_bar.update_layout(
            showlegend=False,  # Remove the legend
            title={
                "text": f"Distribution by Department",  # Title text
                "x": 0.5,  # Center the title (horizontal alignment)
                "xanchor": "center",  # Anchor the title to the center
                "yanchor": "top"  # Anchor the title to the top
            }
        )
        st.plotly_chart(fig_position_bar, use_container_width=True)

    # Pie chart for positions
    with col2:
        fig_position_pie = px.pie(
            filtered_position_counts,
            names="Position",
            values="Count",
            title=f"Percentage per Department",
            color_discrete_sequence=px.colors.sequential.Bluyl[-6:],
            height=450
        )
        # Update layout to remove the legend and center the title
        fig_position_pie.update_layout(
            showlegend=False,  # Remove the legend
            title={
                "text": f"Distribution by Department",  # Title text
                "x": 0.5,  # Center the title (horizontal alignment)
                "xanchor": "center",  # Anchor the title to the center
                "yanchor": "top"  # Anchor the title to the top
            }
        )
        # Add data labels to display the count and percentage
        fig_position_pie.update_traces(
            textinfo="label+percent",  # Add both label and percentage
            textposition="outside",  # Place the labels inside the pie slices
            hoverinfo="label+value+percent"  # Display value, label, and percentage on hover
        )
        st.plotly_chart(fig_position_pie, use_container_width=True)

def calculate_kpis_table(data: pd.DataFrame, status_order: List[str]):
    """
    Calculate the KPIs (absolute counts) per position and return a DataFrame.
    """
    # Define KPI logic for the given statuses
    kpi_mapping = {
        "Email Sent": ["Email Sent", "Email Opened", "Clicked Link", "Submitted Data", "Email Reported"],
        "Email Opened": ["Email Opened", "Clicked Link", "Submitted Data"],
        "Clicked Link": ["Clicked Link", "Submitted Data"],
        "Submitted Data": ["Submitted Data"],
    }
    
    # Initialize an empty dictionary to store counts
    kpis_by_position = {}

    # Loop through each position
    for position, group in data.groupby("position_group"):
        kpis_by_position[position] = {}
        for status, related_statuses in kpi_mapping.items():
            # Count rows where the status matches the related statuses
            kpis_by_position[position][status] = len(group[group["status"].isin(related_statuses)])

        # Add count of reported emails
        kpis_by_position[position]["Email Reported"] = len(group[group["reported"] == True])

    # Convert the dictionary to a DataFrame
    kpis_df = pd.DataFrame.from_dict(kpis_by_position, orient="index").reindex(columns=status_order, fill_value=0)
    
    # Sort the DataFrame by "Emails Sent" column in descending order
    kpis_df = kpis_df.sort_values(by="Email Sent", ascending=False)

    # Convert DataFrame to HTML with centered alignment
    kpis_df_html = kpis_df.style.set_table_styles(
        [
            {"selector": "th", "props": [("text-align", "left"), ("font-weight", "bold")]},
            {"selector": "td", "props": [("text-align", "center")]}
        ]
    ).to_html()

    # Clean up trailing whitespace
    kpis_df_html = kpis_df_html.strip()

    # Insert whitespace
    for i in range(4):
        st.write("")

    # Display the table
    st.write("")
    st.markdown(
        f"""
        <div style="text-align: left; padding: 10px;">
            <h5 style="margin-bottom: 40px;">Absolute KPIs per Department</h5>
            <div style="display: flex; justify-content: left; overflow-x: auto;">
                {kpis_df_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

def display_personal_data(data: pd.DataFrame):
    """
    Display information per employee and return a DataFrame.

    Parameters:
    data (pd.DataFrame): DataFrame containing employee data to display."""
    if data.empty:
        st.write("No data available to display.")
        return
    # Define the columns to display and their order
    columns_to_display = ["position", "first_name", "last_name", "email","campaign_id", "template_name", "status", "send_date", "modified_date", "reported"]
    # Filter and reorder the columns
    new_data = data[columns_to_display]
    # Set the index to start from 1
    new_data.index += 1

    # Display the DataFrame in a scrollable format with limited height
    st.write("")
    st.divider()
    st.write("")
    st.write("### Details")
    st.write("")
    # Convert DataFrame to CSV string
    filtered_csv_data = new_data.to_csv(index=False)
    # Download button
    st.download_button(label="Download Selected Data as CSV", data=filtered_csv_data, file_name="filtered_results.csv", mime="text/csv")
    st.write("")
    # Show dataframe
    st.dataframe(new_data, height=400)  # shows apr. 10 rows
    st.write("")
