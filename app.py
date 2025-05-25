import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
Finaldf = pd.read_csv("Finaldf.csv")

# Page configuration
st.set_page_config(layout="wide")
st.title("\U0001F4CA West Africa ODA Dashboard (2000–2020)")

# ------------------------------
# SUMMARY STATISTICS
# ------------------------------
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

# ------------------------------
# INTERACTIVE WIDGETS
# ------------------------------
year = st.slider("Select Year", 2000, 2020, 2019)
country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()))

# ------------------------------
# DATA FILTERING
# ------------------------------
map_data = Finaldf[(Finaldf['Year'] == year) & (Finaldf['Sector'] == 'All sectors')]

# ------------------------------
# ROW 1: MAP & DONORS
# ------------------------------
col5, col6 = st.columns(2)
with col5:
    st.subheader("\U0001F30D ODA per Capita Map")
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
        projection="natural earth",
        title=f"ODA per Capita in {year}"
    )
    fig_map.update_geos(lonaxis_range=[-20, 10], lataxis_range=[-5, 20])
    st.plotly_chart(fig_map, use_container_width=True)

with col6:
    st.subheader("\U0001F4CA Top 10 Donors")
    donor_data = map_data.groupby('Donor')['Sector_ODA_Millions'].sum().nlargest(10).reset_index()
    fig_donor = px.bar(donor_data, x='Donor', y='Sector_ODA_Millions', title=f"Top 10 Donors in {year}")
    st.plotly_chart(fig_donor, use_container_width=True)

# ------------------------------
# ROW 2: SECTOR PIE & EDUCATION
# ------------------------------
col7, col8 = st.columns(2)
with col7:
    st.subheader("\U0001F967 ODA by Sector")
    selected_sectors = ['Agriculture', 'Education', 'Health',
                        'Water supply and sanitation - large systems',
                        'Conflict, peace and security',
                        'Economic infrastructure and services']
    sector_data = Finaldf[(Finaldf['Year'] == year) & Finaldf['Sector'].isin(selected_sectors)]
    sector_sum = sector_data.groupby('Sector')['Sector_ODA_Millions'].sum()
    fig_pie = px.pie(sector_sum, values=sector_sum.values, names=sector_sum.index,
                     title=f"ODA by Sector in {year}", color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_pie, use_container_width=True)

with col8:
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

