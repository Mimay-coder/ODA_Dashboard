import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
Finaldf = pd.read_csv("Finaldf.csv")

# Page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("West Africa ODA Dashboard (2000–2020)")
st.sidebar.markdown("---")
section = st.sidebar.radio("Navigation", ["AID Landscape", "Healthcare Indicators", "Education Indicators", "Corruption Indicators"])

year = st.sidebar.slider("Select Year", 2000, 2020, 2019, key='aid_year')
#st.markdown("<style> .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 1rem; padding-right: 1rem;} </style>", unsafe_allow_html=True)


st.markdown('<div class="aid-landscape-section">', unsafe_allow_html=True)
# ------------------------------
# AID LANDSCAPE TAB (Start)
# ------------------------------
st.markdown('<div class="aid-landscape-section">', unsafe_allow_html=True)

if section == "AID Landscape":
    total_oda = Finaldf[Finaldf['Sector'] == 'All sectors']['Sector_ODA_Millions'].sum()
    top_donor = Finaldf[Finaldf['Sector'] == 'All sectors'].groupby('Donor')['Sector_ODA_Millions'].sum().idxmax()
    top_country = Finaldf.groupby('Country')['oda_per_capita_usd'].mean().idxmax()
    top_sector = Finaldf.groupby('Sector')['Sector_ODA_Millions'].sum().idxmax()

    st.markdown("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ODA", f"${total_oda/1e3:.1f}B")
    col2.metric("Top Donor", top_donor)
    col3.metric("Highest ODA per Capita", top_country)
    col4.metric("Top Sector", top_sector)

    st.markdown("---")

    
    map_data = Finaldf[(Finaldf['Year'] == year) & (Finaldf['Sector'] == 'All sectors')]

    col_map, col_donor = st.columns((7, 3))
    with col_map:
        st.markdown("ODA per Capita by Country")
        fig_map = px.choropleth(
            map_data,
            locations="Country",
            locationmode="country names",
            color="oda_per_capita_usd",
            color_continuous_scale="Blues",
            range_color=(0, map_data["oda_per_capita_usd"].max()),
            hover_name="Country",
            scope="africa",
            projection="natural earth",
        )
        fig_map.update_geos(lonaxis_range=[-20, 10], lataxis_range=[-5, 20])
        fig_map.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_donor:
        st.markdown("Top Donors")
        donor_data = map_data.groupby('Donor')['Sector_ODA_Millions'].sum().nlargest(10).reset_index()
        fig_donor = px.bar(donor_data, x='Donor', y='Sector_ODA_Millions', title=f"Top 10 Donors in {year}")
        fig_donor.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donor, use_container_width=True)

    st.markdown("ODA by Sector")
    selected_sectors = ['Agriculture', 'Education', 'Health',
                        'Water supply and sanitation - large systems',
                        'Conflict, peace and security',
                        'Economic infrastructure and services']
    sector_data = Finaldf[(Finaldf['Year'] == year) & Finaldf['Sector'].isin(selected_sectors)]
    sector_sum = sector_data.groupby('Sector')['Sector_ODA_Millions'].sum()
    fig_pie = px.pie(sector_sum, values=sector_sum.values, names=sector_sum.index,
                     title=f"ODA by Sector in {year}", color_discrete_sequence=px.colors.sequential.Blues)
    fig_pie.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)
    
st.markdown('</div>', unsafe_allow_html=True)
# ------------------------------
# HEALTHCARE INDICATORS TAB
# ------------------------------
elif section == "Healthcare Indicators":
    st.markdown('<div class="healthcare-section">', unsafe_allow_html=True)

    st.subheader("💉 Maternal Mortality and Health ODA")
    country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()), key='health_country')
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
        height=400, margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_health, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# EDUCATION INDICATORS TAB
# ------------------------------
elif section == "Education Indicators":

    st.markdown('<div class="Education-section">', unsafe_allow_html=True)

    st.subheader("📚 Education ODA vs Literacy Rate")
    country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()), key='edu_country')
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
        height=400, margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_edu, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# CORRUPTION INDICATORS TAB
# ------------------------------
elif section == "Corruption Indicators":

    st.markdown('<div class="Couruption-section">', unsafe_allow_html=True)

    st.subheader("🔍 Placeholder: Corruption and ODA")
    st.info("Add charts related to ODA vs CPI, governance, or anti-corruption indicators here.")

    st.markdown('</div>', unsafe_allow_html=True)
