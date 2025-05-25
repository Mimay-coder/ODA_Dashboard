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
country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()), key='health_country')

# ------------------------------
# AID LANDSCAPE TAB (Start)
# ------------------------------
if section == "AID Landscape":
    st.markdown('<div class="aid-landscape-section">', unsafe_allow_html=True)

    total_oda = Finaldf[Finaldf['Sector'] == 'All sectors']['Sector_ODA_Millions'].sum()
    top_donor = Finaldf[Finaldf['Sector'] == 'All sectors'].groupby('Donor')['Sector_ODA_Millions'].sum().idxmax()
    top_country = Finaldf.groupby('Country')['oda_per_capita_usd'].mean().idxmax()
    top_sector = Finaldf.groupby('Sector')['Sector_ODA_Millions'].sum().idxmax()

    #st.markdown("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ODA", f"${total_oda/1e3:.1f}B")
    col2.metric("Top Donor", top_donor)
    col3.metric("Highest ODA per Capita", top_country)
    col4.metric("Top Sector", top_sector)

    st.markdown("---")

    map_data = Finaldf[(Finaldf['Year'] == year) & (Finaldf['Sector'] == 'All sectors')]

    col_map, col_pie = st.columns((5,5))
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
        fig_map.update_layout(height=300, margin=dict(t=10, b=0, l=10, r=10))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_pie:
        st.markdown("ODA by Sector")
        selected_sectors = ['Agriculture, forestry, fishing', 'Education', 'Health','Water supply & sanitation',
                            'Government and civil society','Economic infrastructure and services']
        sector_data = Finaldf[(Finaldf['Year'] == year) & Finaldf['Sector'].isin(selected_sectors)]
        sector_sum = sector_data.groupby('Sector')['Sector_ODA_Millions'].sum()
        fig_pie = px.pie(sector_sum, values=sector_sum.values, names=sector_sum.index,
                         color_discrete_sequence=px.colors.sequential.Blues)
        fig_pie.update_layout(height=200, margin=dict(t=0, b=0, l=4, r=6), legend=dict(orientation="v", y=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    col_donor, col_channel = st.columns((5,5))
    with col_donor:
         st.markdown("<h5 style='margin-bottom: -2.1rem;'>Top Donors</h5>", unsafe_allow_html=True)
         donor_data = map_data.groupby('Donor')['Sector_ODA_Millions'].sum().nlargest(10).reset_index()
         fig_donor = px.bar(donor_data, x='Donor', y='Sector_ODA_Millions')
         fig_donor.update_layout(height=220, margin=dict(t=0, b=0, l=3, r=3))
         st.plotly_chart(fig_donor, use_container_width=True)
    
    with col_channel:
        st.markdown("<h5 style='margin-bottom: -2.1rem;'>ODA by Channel</h5>", unsafe_allow_html=True)
        # Filter data for the selected year and non-null channel
        sector_filtered2 = Finaldf[
        (Finaldf['Year'] == year) &
        (Finaldf['Channel'].notnull())]
        
        if sector_filtered2.empty:
            st.warning(f"No data for year {year}")
        else:
            sector_sum = sector_filtered2.groupby('Channel')['Sector_ODA_Millions'].sum().reset_index()
            
            fig_channel = px.pie(sector_sum,names='Channel',values='Sector_ODA_Millions',hole=0.3,
                                 color_discrete_sequence=["#08306B", "#08519C", "#2171B5", "#4292C6", "#6BAED6",
                                                                              "#9ECAE1", "#C6DBEF", "#DEEBF7"])
            fig_channel.update_traces(texttemplate='%{percent:.1%}')
            fig_channel.update_layout(height=250,margin=dict(t=0, b=10, l=0, r=10),legend=dict(orientation="h", y=-0.3))
            st.plotly_chart(fig_channel, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# HEALTHCARE INDICATORS TAB
# ------------------------------
elif section == "Healthcare Indicators":
    st.markdown('<div class="healthcare-section">', unsafe_allow_html=True)
    col1, col2 = st.columns((5,5))
    with col1:
        st.markdown("<h5 style='margin-bottom: -2.1rem;'>Reproductive Health ODA vs Maternal Mortality</h5>", unsafe_allow_html=True)
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
        height=200, margin=dict(t=3, b=0, l=0, r=3)
        )
        st.plotly_chart(fig_health, use_container_width=True)

    with col2:
        st.markdown("<h5 style='margin-bottom: -1.5rem;'>Malaria Control ODA vs Malaria Rate</h5>", unsafe_allow_html=True)
        malaria_data = Finaldf[(Finaldf['Country'] == country) &(Finaldf['Sector'] == 'Malaria control')
        ].groupby('Year').agg({'Sector_ODA_Millions': 'sum','Malaria_RATE_PER_1000_N': 'mean'}).reset_index()
        fig_malaria = px.line(malaria_data, x='Year', y='Sector_ODA_Millions',
                          labels={'Sector_ODA_Millions': 'ODA (Millions)'})
        fig_malaria.add_scatter(x=malaria_data['Year'],
                            y=malaria_data['Malaria_RATE_PER_1000_N'],
                            name='Malaria Rate (per 1,000)',
                            yaxis='y2')
        fig_malaria.update_layout(height=250, margin=dict(t=10, b=20, l=10, r=10),legend=dict(orientation="h", y=-0.3),
        yaxis2=dict(title='Malaria Rate (per 1,000)', overlaying='y', side='right')
                                 )
        st.plotly_chart(fig_malaria, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# EDUCATION INDICATORS TAB
# ------------------------------
elif section == "Education Indicators":

    st.markdown('<div class="education-section">', unsafe_allow_html=True)

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

    st.markdown('<div class="corruption-section">', unsafe_allow_html=True)

    st.subheader("🔍 Placeholder: Corruption and ODA")
    st.info("Add charts related to ODA vs CPI, governance, or anti-corruption indicators here.")

    st.markdown('</div>', unsafe_allow_html=True)
