import streamlit as st
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine
import os
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium
import itertools

# Set up the SQLAlchemy connection
db_username = os.getenv('Db_USER')
db_password = os.getenv('Db_PASSWORD')
engine = create_engine(f'mysql+mysqlconnector://{db_username}:{db_password}@localhost/crimeview360(1)')

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "Navigation", 
        ["Crime Overview", "Crime Insights", "District Crime Breakdown", "Crime Location Analysis", "FAQs"],
        icons=["house", "bar-chart", "clipboard", "graph-up", "question-circle"],
        menu_icon="cast", 
        default_index=0
    )

# Crime Overview Page
if selected == "Crime Overview":
    st.title("Crime Overview")

    # KPIs
    st.header("Key Metrics")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Total Incidents", "2520")
    kpi_col2.metric("Open Cases", "1300", "-2%")
    kpi_col3.metric("Resolved Cases", "1220", "+1.5%")

    # Map Highlighting Chicago
    st.header("Crime Map: Chicago")
    m = folium.Map(location=[41.8781, -87.6298], zoom_start=11)
    folium.Marker([41.8781, -87.6298], tooltip="Chicago", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=400)

# Crime Insights Page
elif selected == "Crime Insights":
    st.title("Crime Insights Dashboard")

    # KPIs (Summary Metrics)
    st.header("Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Total Incidents", "2520")
    col2.metric("Open Cases", "1300", "-2%")

    # Crime Insights - Top 10 Locations (Bar Chart)
    st.header("Crime Insights by Location")
    main_col1, main_col2 = st.columns([2, 1])  # Adjust proportions for larger and smaller columns

    # Top 10 Locations (Bar Chart)
    query = "SELECT location FROM location"
    data = pd.read_sql(query, engine)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    # Set background color for the figure and axes
    fig.patch.set_facecolor('#F1F8ED')  # Figure background color
    ax1.set_facecolor('#F1F8ED')  # Axis background color

    top_locations = data['location'].value_counts().head(10)
    fig1, ax1 = plt.subplots(figsize=(8, 6))  # Adjust size
    colors = list(itertools.islice(itertools.cycle(["#381704", "#BA261A", "#701421", "#BA261A"]), len(top_locations)))
    top_locations.plot(kind='barh', color=colors, ax=ax1)
    ax1.set_title("Top 10 Locations with Most Incidents", fontsize=16, fontweight='bold')
    ax1.set_xlabel("Number of Incidents", fontsize=15)
    ax1.set_ylabel("Locations", fontsize=15)
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig1)

    # Left Column: Incident Categories (Pie Chart)
    with main_col1:
        query3 = "SELECT id,type FROM crime"
        data3 = pd.read_sql(query3, engine)

        if 'Type' in data3.columns:
            incident_categories = data3['Type'].value_counts()
        elif 'type' in data3.columns:
            incident_categories = data3['type'].value_counts()

        fig3, ax3 = plt.subplots(figsize=(8, 6))  # Larger figure size
        incident_categories.head(10).plot(
            kind='pie',
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors,
            textprops={'fontsize': 10},
            ax=ax3
        )
        ax3.set_title("Crime Incident Categories", fontsize=16, fontweight='bold')
        ax3.set_ylabel("")
        st.pyplot(fig3)

    # Right Column: Count of Arrests (Bar Chart) and Day-wise Crime Rates (Line Chart)
    with main_col2:
        # Count of Arrests
        query2 = "SELECT * FROM incident"
        data2 = pd.read_sql(query2, engine)

        arrest_counts = data2['Arrest'].value_counts()
        fig2, ax2 = plt.subplots(figsize=(6, 4))  # Adjust size
        arrest_counts.plot(kind='bar', color=['#103C61', '#3180C5'], ax=ax2)
        ax2.set_title("Number of Arrests by Status", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Arrest Status", fontsize=12)
        ax2.set_ylabel("Count", fontsize=12)
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels(['Wanted', 'Arrested'], rotation=0)
        st.pyplot(fig2)

        # Day-wise Crime Rates (Line Chart)
        query4 = "SELECT Date FROM incident"
        data4 = pd.read_sql(query4, engine)

        if 'Date' in data4.columns:
            data4['Date'] = pd.to_datetime(data4['Date'])
            may_data = data4[data4['Date'].dt.month == 5]
            daywise_crime = may_data.groupby(may_data['Date'].dt.day).size()
        elif 'date' in data4.columns:
            data4['date'] = pd.to_datetime(data4['date'])
            may_data = data4[data4['date'].dt.month == 5]
            daywise_crime = may_data.groupby(may_data['date'].dt.day).size()

        fig4, ax4 = plt.subplots(figsize=(6, 5))  # Adjust size
        ax4.plot(daywise_crime.index, daywise_crime.values, marker='o', color='blue')
        ax4.set_title("Day-wise Crime Rates in May", fontsize=14, fontweight='bold') 
        ax4.set_xlabel("Day of the Month", fontsize=12)
        ax4.set_ylabel("Number of Crimes", fontsize=12)
        ax4.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig4)

# District Crime Breakdown Page
elif selected == "District Crime Breakdown":
    st.title("Crime Breakdown in Specific Districts") 

    # Select a District
    district_query = "SELECT DISTINCT District FROM location"
    district_data = pd.read_sql(district_query, engine)
    district_options = district_data['District'].dropna().unique()

    selected_district = st.selectbox("Select a District:", district_options)

    # Get crime data for the selected district
    district_crime_query = f"""
    SELECT c.Type, COUNT(*) as count 
    FROM incident i
    JOIN location l ON i.Location_ID = l.ID
    JOIN crime c ON i.Crime_ID = c.ID
    WHERE l.District = '{selected_district}'
    GROUP BY c.Type
    """
    district_crime_data = pd.read_sql(district_crime_query, engine)

    if not district_crime_data.empty:
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        counts = district_crime_data['count']
        labels = district_crime_data['Type']

        # Create pie chart with a legend
        wedges, texts, autotexts = ax3.pie(
            counts,
            labels=None,  # Exclude labels from pie chart
            autopct='%1.1f%%',
            startangle=90,
            colors = plt.cm.Set3.colors,
            textprops={'fontsize': 8, 'color': 'black'},  # Percentages in black
        )

        # Add a legend to the right of the chart
        ax3.legend(
            wedges,
            labels,
            title="Crime Types",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=10
        )

        ax3.set_title(f"Crimes in District {selected_district}", fontsize=20, fontweight='bold')
        ax3.set_ylabel("")
        st.pyplot(fig3)
    else:
        st.write("No crime data available for the selected district.")

    location_query = f"SELECT DISTINCT location FROM location WHERE District = '{selected_district}'"
    location_data = pd.read_sql(location_query, engine)
    location_options = location_data['location'].dropna().unique()

    selected_location = st.selectbox("Select a Location in this District:", location_options, key="location_in_district")

    # Get crime data for the selected district and location
    district_location_crime_query = f"""
    SELECT c.Type, COUNT(*) as count 
    FROM incident i
    JOIN location l ON i.Location_ID = l.ID
    JOIN crime c ON i.Crime_ID = c.ID
    WHERE l.District = '{selected_district}' AND l.location = '{selected_location}'
    GROUP BY c.Type
    """
    district_location_crime_data = pd.read_sql(district_location_crime_query, engine)

    if not district_location_crime_data.empty:
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        counts = district_location_crime_data['count']
        labels = district_location_crime_data['Type']

        # Create pie chart with a legend
        wedges, texts, autotexts = ax3.pie(
            counts,
            labels=None,  # Exclude labels from pie chart
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Paired.colors,
            textprops={'fontsize': 8, 'color': 'black'},  # Percentages in black
        )

        # Add a legend to the right of the chart
        ax3.legend(
            wedges,
            labels,
            title="Crime Types",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=10
        )

        ax3.set_title(f"Crimes in Location {selected_location}, District {selected_district}", fontsize=20, fontweight='bold')
        ax3.set_ylabel("")
        st.pyplot(fig3)
    else:
        st.write(f"No crime data available for the location: {selected_location} in District {selected_district}.")

# Crime Location Analysis Page
elif selected == "Crime Location Analysis":
    st.title("Crime Analysis in Specific Locations")

    # Select a Location
    location_query = "SELECT DISTINCT location FROM location"
    location_data = pd.read_sql(location_query, engine)
    location_options = location_data['location'].dropna().unique()

    selected_location = st.selectbox("Select a Location:", location_options, key="location")

    # Get crime data for the selected location
    location_crime_query = f"""
    SELECT c.type AS crime_type, COUNT(*) AS count
    FROM incident i
    JOIN location l ON i.Location_ID = l.ID
    JOIN crime c ON i.Crime_ID = c.ID
    WHERE l.location = '{selected_location}'
    GROUP BY c.type
    ORDER BY count DESC
    """
    location_crime_data = pd.read_sql(location_crime_query, engine)

    if not location_crime_data.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        # Set background color for the figure and axes
        fig.patch.set_facecolor('#F1F8ED')  # Figure background color
        ax.set_facecolor('#F1F8ED')  # Axis background color

        ax.bar(location_crime_data['crime_type'], location_crime_data['count'], color='darkred')
        ax.set_title(f"Crimes in {selected_location}", fontsize=16, fontweight='bold')
        ax.set_xlabel("Crime Type", fontsize=14)
        ax.set_ylabel("Number of Crimes", fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        st.pyplot(fig)
    else:
        st.write(f"No crime data available for the location: {selected_location}.")

# Add "FAQs" to Sidebar Navigation


# FAQ Page
if selected == "FAQs":
    st.title("Frequently Asked Questions")
    st.write("Select a question from the dropdown to view the answer.")

    # Dropdown for FAQs
    faqs = [
        "What are the most common crime types in each district?",
        "What is the average number of incidents per community area for each crime type?",
        "What is the distribution of incidents across different years for each crime type?"
    ]
    selected_question = st.selectbox("Select a Question:", faqs)

    # Execute queries based on the selected question
    if selected_question == "What are the most common crime types in each district?":
        query = """
        WITH CrimeCounts AS (
            SELECT 
                l.District,
                c.Type,
                COUNT(*) AS TotalIncidents
            FROM Incident AS i
            JOIN Location AS l ON i.Location_ID = l.ID
            JOIN Crime AS c ON i.Crime_ID = c.ID
            GROUP BY 
                l.District,
                c.Type
        ),
        MostCommonCrimes AS (
            SELECT 
                District,
                Type,
                TotalIncidents,
                RANK() OVER (PARTITION BY District ORDER BY TotalIncidents DESC) AS Ranks
            FROM CrimeCounts
        )
        SELECT 
            District,
            Type AS MostCommonCrime,
            TotalIncidents
        FROM MostCommonCrimes
        WHERE Ranks = 1
        ORDER BY District;
        """
        result = pd.read_sql(query, engine)
        st.subheader("Most Common Crime Types in Each District")
        st.dataframe(result)

    elif selected_question == "What is the average number of incidents per community area for each crime type?":
        query = """
        SELECT 
            c.Type,
            l.Community_area,
            COUNT(DISTINCT i.ID) AS TotalIncidents,
            COUNT(DISTINCT l.ID) AS TotalCommunityAreas,
            CAST(COUNT(DISTINCT i.ID) AS REAL) / COUNT(DISTINCT l.ID) AS AvgIncidentsPerCommunityArea
        FROM Incident AS i
        JOIN Location AS l ON i.Location_ID = l.ID
        JOIN Crime AS c ON i.Crime_ID = c.ID
        GROUP BY 
            c.Type,
            l.Community_area
        ORDER BY 
            c.Type,
            AvgIncidentsPerCommunityArea DESC;
        """
        result = pd.read_sql(query, engine)
        st.subheader("Average Number of Incidents Per Community Area for Each Crime Type")
        st.dataframe(result)

    elif selected_question == "What is the distribution of incidents across different years for each crime type?":
        query = """
        SELECT
            i.Year,
            c.Type,
            COUNT(*) AS TotalIncidents
        FROM Incident AS i
        JOIN Crime AS c ON i.Crime_ID = c.ID
        GROUP BY
            i.Year,
            c.Type
        ORDER BY
            i.Year,
            c.Type;
        """
        result = pd.read_sql(query, engine)
        st.subheader("Distribution of Incidents Across Different Years for Each Crime Type")
        st.dataframe(result)


# Dispose of the engine connection
engine.dispose()
