import os
os.environ["STREAMLIT_CONFIG_DIR"] = os.path.join(os.getcwd(), ".streamlit")
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
Finaldf = pd.read_csv("Finaldf.csv")

# Page configuration
st.set_page_config(layout="centered", page_title="ODA Dashboard", page_icon="📊")
st.title("\U0001F4CA West Africa ODA Dashboard (2000–2020)")

# Sidebar navigation
section = st.sidebar.radio("Navigation", ["AID Landscape", "Healthcare Indicators", "Education Indicators", "Corruption Indicators"])

# Shared interactive widgets
year = st.slider("Year", 2000, 2020, 2019, key='year')
country = st.selectbox("Country", sorted(Finaldf['Country'].unique()), key='country')

# ------------------------------
# AID LANDSCAPE TAB
# ------------------------------
if section == "AID Landscape":
    total_oda = Finaldf[Finaldf['Sector'] == 'All sectors']['Sector_ODA_Millions'].sum()
    top_donor = Finaldf[Finaldf['Sector'] == 'All sectors'].groupby('Donor')['Sector_ODA_Millions'].sum().idxmax()
    top_country = Finaldf.groupby('Country')['oda_per_capita_usd'].mean().idxmax()
    top_sector = Finaldf.groupby('Sector')['Sector_ODA_Millions'].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("\U0001F4B0 Total ODA", f"${total_oda/1e3:.1f}B")
    col2.metric("\U0001F30D Top Donor", top_donor)
    col3.metric("\U0001F4C8 Highest ODA per Capita", top_country)
    col4.metric("\U0001F3E7 Top Sector", top_sector)

    st.markdown("---")
    st.markdown("### \U0001F30D ODA Map and Top Donors")
    col5, col6 = st.columns([1, 1])
    with col5:
        map_data = Finaldf[(Finaldf['Year'] == year) & (Finaldf['Sector'] == 'All sectors')]
        fig_map = px.scatter_geo(
            map_data,
            locations="Country",
            locationmode="country names",
            size="oda_per_capita_usd",
            color="oda_per_capita_usd",
            color_continuous_scale="Blues",
            range_color=(0, map_data["oda_per_capita_usd"].max()),
            hover_name="Country",
            scope="africa",
            projection="natural earth"
        )
        fig_map.update_geos(lonaxis_range=[-20, 10], lataxis_range=[-5, 20])
        fig_map.update_layout(height=300, width=400)
        st.plotly_chart(fig_map, use_container_width=False)

    with col6:
        donor_data = map_data.groupby('Donor')['Sector_ODA_Millions'].sum().nlargest(10).reset_index()
        fig_donor = px.bar(donor_data, x='Donor', y='Sector_ODA_Millions', title=f"Top 10 Donors in {year}")
        fig_donor.update_layout(height=300, width=400)
        st.plotly_chart(fig_donor, use_container_width=False)

    st.markdown("### \U0001F967 ODA by Sector")
    selected_sectors = ['Agriculture', 'Education', 'Health',
                        'Water supply and sanitation - large systems',
                        'Conflict, peace and security',
                        'Economic infrastructure and services']
    sector_data = Finaldf[(Finaldf['Year'] == year) & Finaldf['Sector'].isin(selected_sectors)]
    sector_sum = sector_data.groupby('Sector')['Sector_ODA_Millions'].sum()
    fig_pie = px.pie(sector_sum, values=sector_sum.values, names=sector_sum.index,
                     title=f"ODA by Sector in {year}", color_discrete_sequence=px.colors.sequential.Blues)
    fig_pie.update_layout(height=300, width=400)
    st.plotly_chart(fig_pie, use_container_width=False)

# ------------------------------
# HEALTHCARE INDICATORS TAB
# ------------------------------
elif section == "Healthcare Indicators":
    st.subheader("\U0001F489 Maternal Mortality and Health ODA")
    healthcare_data = Finaldf[(Finaldf['Country'] == country) & (Finaldf['Sector'] == 'Reproductive health care')]
    healthcare_data = healthcare_data.groupby('Year').agg({
        'Sector_ODA_Millions': 'sum',
        'Maternal_Mortality': 'mean'
    }).reset_index()

    fig_health = px.line(healthcare_data, x='Year', y='Sector_ODA_Millions', labels={'Sector_ODA_Millions': 'ODA (Millions)'})
    fig_health.add_scatter(x=healthcare_data['Year'], y=healthcare_data['Maternal_Mortality'],
                           name='Maternal Mortality', yaxis='y2')
    fig_health.update_layout(
        yaxis2=dict(title='Maternal Mortality', overlaying='y', side='right'),
        title=f"Reproductive Health ODA and Maternal Mortality in {country}",
        height=400
    )
    st.plotly_chart(fig_health, use_container_width=True)

# ------------------------------
# EDUCATION INDICATORS TAB
# ------------------------------
elif section == "Education Indicators":
    st.subheader("\U0001F4D6 Education ODA vs Literacy Rate")
    edu_data = Finaldf[(Finaldf['Country'] == country) & (Finaldf['Sector'] == 'Education')]
    edu_data = edu_data[edu_data['Total_Literacy'] > 0].groupby('Year').agg({
        'Sector_ODA_Millions': 'sum',
        'Total_Literacy': 'mean'
    }).reset_index()

    fig_edu = px.line(edu_data, x='Year', y='Sector_ODA_Millions', labels={'Sector_ODA_Millions': 'ODA (Millions)'})
    fig_edu.add_scatter(x=edu_data['Year'], y=edu_data['Total_Literacy'], name='Literacy Rate (%)', yaxis='y2')
    fig_edu.update_layout(
        yaxis2=dict(title='Literacy Rate (%)', overlaying='y', side='right'),
        title=f"Education ODA and Literacy Rate in {country}",
        height=400
    )
    st.plotly_chart(fig_edu, use_container_width=True)

# ------------------------------
# CORRUPTION INDICATORS TAB
# ------------------------------
elif section == "Corruption Indicators":
    st.subheader("\U0001F50E Placeholder: Corruption and ODA")
    st.info("Add charts related to ODA vs CPI, governance, or anti-corruption indicators here.")


