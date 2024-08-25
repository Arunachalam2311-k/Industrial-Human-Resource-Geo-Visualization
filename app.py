# import librarys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page configuration to wide layout
st.set_page_config(layout="wide")

# Set the title of the application
st.title("Industrial Human Resource Geo-Visualization")

# Create a horizontal menu in the main content
selected = option_menu("Menu",["Home", "Overview", "Explore"],
                       icons=["house", "graph-up-arrow", "bar-chart-line"],
                       menu_icon="menu-button-wide",
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px",
                                            "--hover-color": "#FF5A5F"},
                               "nav-link-selected": {"background-color": "#FF5A5F"}})

# Load dataset
df= pd.read_csv("D:/demo/compained_saved.csv")  # Adjust path as needed

# -------------------------------------------------------------------------------------------------------------------------------------

# Home Page
if selected == "Home":
    # st.title("Industrial Human Resource Geo-Visualization")
    
    # Create two columns
    col1, col2 = st.columns(2)

    # Content for the first column
    with col1:
        st.subheader("About the Dataset:")
        st.write("Our dataset comprises state-wise counts of main and marginal workers across diverse industries, including manufacturing, construction, retail, and more.")
        st.write("Explore the dynamic landscape of India's workforce with our Industrial Human Resource Geo-Visualization project.")
        st.write("Gain insights into employment trends, industry distributions, and economic patterns to drive informed decision-making and policy formulation.")
        
    # Content for the second column
    with col2:
        st.subheader("About the Project:")
        st.write("Our project aims to:")
        st.markdown("""
        - Update and refine the industrial classification data of main and marginal workers.
        - Provide accurate and relevant information for policy-making and employment planning.
        - Empower stakeholders with actionable insights to foster economic growth and development.
        """)

        st.subheader("Key Features:")
        st.markdown("""
        - **Data Exploration:** Dive deep into state-wise industrial classification data.
        - **Visualization:** Interactive charts and maps for intuitive data exploration.
        - **Insights and Analysis:** Extract actionable insights to support policy-making and resource management.
        """)
# -------------------------------------------------------------------------------------------------------------------------------------

# Overview Page
elif selected == "Overview":

    # Select box for type of worker
    worker_type = st.selectbox('Select Worker Type', ['Main Workers', 'Marginal Workers'])

    # Column mapping
    if worker_type == 'Main Workers':
        column_total = 'Main Workers - Total -  Persons'
        column_rural = 'Main Workers - Rural -  Persons'
        column_urban = 'Main Workers - Urban -  Persons'
    else:
        column_total = 'Marginal Workers - Total -  Persons'
        column_rural = 'Marginal Workers - Rural -  Persons'
        column_urban = 'Marginal Workers - Urban -  Persons'

    # Strip any extra spaces from column names
    df.columns = [col.strip() for col in df.columns]

    # Print DataFrame columns for debugging
    print("DataFrame Columns:", df.columns)

    # Scatter Plot
    fig1 = px.scatter(df, x=column_total, y=column_rural, title=f'{worker_type} - Total vs Rural')
    st.plotly_chart(fig1)

    fig2 = px.scatter(df, x=column_total, y=column_urban, title=f'{worker_type} - Total vs Urban')
    st.plotly_chart(fig2)

    # Box Plot for Top 10 NIC Names
    top_10_nic_names = df['NIC Name'].value_counts().head(10).index
    top_10_df = df[df['NIC Name'].isin(top_10_nic_names)]

    fig3 = px.box(top_10_df, x='NIC Name', y=column_total, title=f'{worker_type} by Top 10 NIC Names')
    st.plotly_chart(fig3)

    # Count plot for a categorical column
    st.subheader(f"Distribution of {worker_type} by India/States")
    sns.set_palette("bright")
    fig, ax = plt.subplots()
    sns.countplot(x='India/States', data=df, ax=ax)
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # Plot: Relationship between Rural/Urban and Total Persons
    st.subheader(f'Relationship between {worker_type} - Rural/Urban - Persons and {worker_type} - Total - Persons')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df[f'{worker_type} - Rural -  Persons'], df[f'{worker_type} - Total -  Persons'], label='Rural', alpha=0.5)
    ax.scatter(df[f'{worker_type} - Urban -  Persons'], df[f'{worker_type} - Total -  Persons'], label='Urban', alpha=0.5)
    ax.set_xlabel(f'{worker_type} - Rural - Persons / {worker_type} - Urban - Persons')
    ax.set_ylabel(f'{worker_type} - Total - Persons')
    ax.set_title(f'Relationship between {worker_type} - Rural/Urban - Persons and {worker_type} - Total - Persons')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# ---------------------------------------------------------------------------------------------------------------
# Explore Page
elif selected == "Explore":

   # Fetch GeoJSON data for India's states
    @st.cache_resource
    def fetch_geojson():
        geojson_url = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
        response = requests.get(geojson_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch GeoJSON data")

    # Main Streamlit App
    def main():
        st.title("India Map Visualization")

        # Fetch GeoJSON data
        geojson_data = fetch_geojson()

        # Extract state names from GeoJSON data
        geojson_state_names = set(feature['properties']['NAME_1'] for feature in geojson_data['features'])

        # State names from DataFrame
        dataframe_state_names = set(df['India/States'])

        # Select box for type of worker
        worker_type = st.selectbox('Select Worker Type', ['Main Workers', 'Marginal Workers'], key="worker_type_selectbox")

        # Select box for sex
        sex_type = st.selectbox('Select Sex', ['Males', 'Females'], key="sex_type_selectbox")

        # Select box for area
        area_type = st.selectbox('Select Area', ['Rural', 'Urban'], key="area_type_selectbox")

        # Determine the column based on selected worker type, sex, and area
        column_name = f'{worker_type} - {area_type} - {sex_type}'

        # Plotly Choropleth map
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=df['India/States'],
            featureidkey="properties.NAME_1",
            z=df[column_name],
            colorscale='Viridis',
            zmin=df[column_name].min(),
            zmax=df[column_name].max(),
            marker_opacity=0.7,
            marker_line_width=0,
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=3,
            mapbox_center={"lat": 20.5937, "lon": 78.9629},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            title=f"{worker_type} ({sex_type}, {area_type}) Population Across Indian States",
            title_x=0.5
        )

        # Display the map
        st.plotly_chart(fig)

    # Call the main function
    if __name__ == "__main__":
        main()

