import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# Load data
Finaldf = pd.read_csv("Finaldf.csv")
Finaldf1 = pd.read_csv("Finaldf_Original.csv")

# Page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("West Africa ODA Dashboard (2000–2020)")
st.sidebar.markdown("---")
section = st.sidebar.radio("Navigation", ["AID Landscape", "Healthcare Indicators", "Education Indicators", "Aid Effectiveness Ratios"])

year = st.sidebar.slider("Select Year", 2000, 2020, 2019, key='aid_year')


# ------------------------------
# AID LANDSCAPE TAB (Start)
# ------------------------------
if section == "AID Landscape":
    st.markdown('<div class="aid-landscape-section">', unsafe_allow_html=True)

    total_oda = Finaldf[Finaldf['Sector'] == 'All sectors']['Sector_ODA_Millions'].sum()
    top_donor = Finaldf[Finaldf['Sector'] == 'All sectors'].groupby('Donor')['Sector_ODA_Millions'].sum().idxmax()
    top_country = Finaldf.groupby('Country')['oda_per_capita_usd'].mean().idxmax()
    top_sector = (Finaldf[Finaldf['Sector'] != 'All sectors'].groupby('Sector')['Sector_ODA_Millions'].sum().idxmax())

    #st.markdown("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ODA (2000-2020)", f"${total_oda/1e3:.1f}B")
    col2.metric("Top Donor(2000-2020)", top_donor)
    col3.metric("Highest ODA per Capita (2000-2020)", top_country)
    col4.metric("Top Sector (2000-2020)", top_sector)

    st.markdown("<hr style='margin-top: 0rem; margin-bottom: 0.5rem;'>", unsafe_allow_html=True)

    map_data = Finaldf[(Finaldf['Year'] == year) & (Finaldf['Sector'] == 'All sectors')]

    col_map, col_pie = st.columns((5,5))
    with col_map:
        st.markdown("<h5 style='margin-bottom: -1.5rem;'>ODA per Capita by Country</h5>", unsafe_allow_html=True)
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
        st.markdown("<h5 style='margin-bottom: -1.5rem;'>ODA by Sector</h5>", unsafe_allow_html=True)
        selected_sectors = ['Agriculture, forestry, fishing', 'Education', 'Health','Water supply & sanitation',
                            'Government and civil society']
        sector_data = Finaldf[(Finaldf['Year'] == year) & Finaldf['Sector'].isin(selected_sectors)]
        sector_sum = sector_data.groupby('Sector')['Sector_ODA_Millions'].sum()
        fig_pie = px.pie(sector_sum, values=sector_sum.values, names=sector_sum.index,
                         color_discrete_sequence=px.colors.sequential.Blues)
        fig_pie.update_layout(height=200, margin=dict(t=0, b=0, l=4, r=6), legend=dict(orientation="v", y=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    col_donor, col_channel = st.columns((6,5))
    with col_donor:
         st.markdown("<h5 style='margin-bottom: -2.2rem;'>Top Donors</h5>", unsafe_allow_html=True)
         donor_data = map_data.groupby('Donor')['Sector_ODA_Millions'].sum().nlargest(10).reset_index()
         fig_donor = px.bar(donor_data, x='Donor', y='Sector_ODA_Millions')
         fig_donor.update_layout(height=250, margin=dict(t=0, b=0, l=3, r=5))
         st.plotly_chart(fig_donor, use_container_width=True)
    
    with col_channel:
        st.markdown("<h5 style='margin-bottom: -2.2rem;'>ODA by Channel</h5>", unsafe_allow_html=True)
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
            fig_channel.update_layout(height=250,margin=dict(t=0, b=5, l=5, r=0),legend=dict(orientation="v", y=0.5))
            st.plotly_chart(fig_channel, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# HEALTHCARE INDICATORS TAB
# ------------------------------

elif section == "Healthcare Indicators":
    st.markdown('<div class="healthcare-section">', unsafe_allow_html=True)
    country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()), key='health_country')
    col1, col2 = st.columns((5,5))
    with col1:
        st.markdown("<h5 style='margin-bottom: -1.8rem;'>Reproductive Health ODA vs Maternal Mortality</h5>", unsafe_allow_html=True)
        healthcare_data = Finaldf[(Finaldf['Country'] == country) & (Finaldf['Sector'] == 'Reproductive health care')]
        healthcare_data = healthcare_data.groupby('Year').agg({
        'Sector_ODA_Millions': 'sum',
        'Maternal_Mortality': 'mean'
         }).reset_index()
        
        fig_health = px.line(healthcare_data, x='Year', y='Sector_ODA_Millions', labels={'Sector_ODA_Millions': 'Reproductive Health ODA (Millions)'})
        fig_health.add_scatter(x=healthcare_data['Year'], y=healthcare_data['Maternal_Mortality'],
                           name='Maternal Mortality', yaxis='y2')
        fig_health.update_layout(
        yaxis2=dict(title='Maternal Mortality per 1000', overlaying='y', side='right', range=[0, healthcare_data['Maternal_Mortality'].max() * 2]),
        height=270, margin=dict(t=0, b=0, l=0, r=3),legend=dict(orientation="h", y=-0.2))
 
        yaxis=dict(title='Reproductive ODA (Millions)',range=[0, healthcare_data['Sector_ODA_Millions'].max() * 4])
        
        st.plotly_chart(fig_health, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        

    with col2:
        st.markdown("<h5 style='margin-bottom: -1.9rem;'>Malaria Control ODA vs Malaria Rate</h5>", unsafe_allow_html=True)
        malaria_data = Finaldf[(Finaldf['Country'] == country) &(Finaldf['Sector'] == 'Malaria control')
        ].groupby('Year').agg({'Sector_ODA_Millions': 'sum','Malaria_RATE_PER_1000_N': 'mean'}).reset_index()
        fig_malaria = px.line(malaria_data, x='Year', y='Sector_ODA_Millions',
                          labels={'Sector_ODA_Millions': 'Malaria Control ODA (Millions)'})
        fig_malaria.add_scatter(x=malaria_data['Year'],
                            y=malaria_data['Malaria_RATE_PER_1000_N'],
                            name='Malaria Rate (per 1,000)',
                            yaxis='y2')
        fig_malaria.update_layout(height=270, margin=dict(t=0, b=0, l=0, r=10),legend=dict(orientation="h", y=-0.2),
        yaxis2=dict(title='Malaria Rate (per 1,000)', overlaying='y', side='right'))

        yaxis2=dict(title='Malaria Rate (per 1000)',overlaying='y',side='right',range=[0,1200])
        
        yaxis=dict(title='Malaria Control ODA (Millions)',range=[0, malaria_data['Sector_ODA_Millions'].max() * 3])
        
        st.plotly_chart(fig_malaria, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    

    col_sanitation, col_nurishment = st.columns((5,5))
    with col_sanitation:
        st.markdown("<h5 style='margin-bottom: -1.4rem;'>Water & Sanitation ODA vs Basic Sanitation Usage</h5>", unsafe_allow_html=True)
        sanitation_data = Finaldf[(Finaldf['Country'] == country) & (Finaldf['Sector'] == 'Water supply & sanitation')].groupby('Year').agg({
        'Sector_ODA_Millions': 'sum','Population_using_basic_sanitation%': 'mean'}).reset_index()

        fig_sanitation = px.line(sanitation_data,x='Year',y='Sector_ODA_Millions',labels={'Sector_ODA_Millions': 'Water & Sanitation ODA (Millions)'})
        fig_sanitation.add_scatter(x=sanitation_data['Year'], y=sanitation_data['Population_using_basic_sanitation%'],name='Population using basic sanitation (%)',
        yaxis='y2')
        fig_sanitation.update_layout(height=260, margin=dict(t=10, b=10, l=0, r=10),legend=dict(orientation="h", y=-0.3),
        #yaxis2=dict(title='Population using basic sanitation(%)',overlaying='y',side='right'))

        yaxis2=dict(title='Population using basic sanitation(%)',overlaying='y',side='right',range=[0, sanitation_data['Population_using_basic_sanitation%'].max() * 2]))
        
        yaxis=dict(title='Water & Sanitation ODA (Millions)',range=[0, sanitation_data['Sector_ODA_Millions'].max() * 2])


        st.plotly_chart(fig_sanitation, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_nurishment:
        st.markdown("<h5 style='margin-bottom: -1.8rem;'>Basic Nutrition ODA vs Undernourishment</h5>", unsafe_allow_html=True)
        Nourishment_data = Finaldf[(Finaldf['Country'] == country) & (Finaldf['Sector'] == 'Basic nutrition')].groupby('Year').agg({
        'Sector_ODA_Millions': 'sum','Undernourishment': 'mean'}).reset_index()

        fig_Nourishment = px.line(Nourishment_data,x='Year',y='Sector_ODA_Millions',labels={'Sector_ODA_Millions': 'Basic Nutrition ODA (Millions)'})
        fig_Nourishment.add_scatter(x=Nourishment_data['Year'], y=Nourishment_data['Undernourishment'],name='Population Undernourished(%)',
        yaxis='y2')
        fig_Nourishment.update_layout(height=270, margin=dict(t=0, b=10, l=0, r=0),legend=dict(orientation="h", y=-0.3),
        yaxis2=dict(title='Undernourishment',overlaying='y',side='right',range=[0, Nourishment_data['Undernourishment'].max() * 2]))
        
        yaxis=dict(title='Basic Nutrition ODA (Millions)',range=[0, Nourishment_data['Sector_ODA_Millions'].max() * 2])


        st.plotly_chart(fig_Nourishment, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

     

# ------------------------------
# EDUCATION INDICATORS TAB
# ------------------------------
elif section == "Education Indicators":
    st.markdown('<div class="education-section">', unsafe_allow_html=True)
    country = st.selectbox("Select Country", sorted(Finaldf['Country'].unique()), key='health_country')
    col_Primary, col_Lit = st.columns((5,5))
    with col_Primary:
        st.markdown("<h5 style='margin-bottom: -1.8rem;'>Primary Education ODA vs Primary Completion</h5>", unsafe_allow_html=True)
        primary_data = Finaldf1[(Finaldf1['Country'] == country) & (Finaldf1['Sector'] == 'Primary education') & (Finaldf1['Year'].between(2000, 2019))]
        primary_data = primary_data[(primary_data['Sector_ODA_Millions'] != 0) & (primary_data['Primary_Completion'] != 0)].dropna()
        primary_data = primary_data.groupby('Year').agg({'Sector_ODA_Millions': 'sum','Primary_Completion': 'mean'}).reset_index()
        
        fig_primary = px.line(primary_data, x='Year', y='Sector_ODA_Millions', labels={'Sector_ODA_Millions': 'Primary Education ODA (Millions)'})
        fig_primary.add_scatter(x=primary_data['Year'], y=primary_data['Primary_Completion'],
                           name='Primary Completion Rate', yaxis='y2')
        fig_primary.update_layout(
        yaxis2=dict(title='Primary Completion Rate', overlaying='y', side='right', range=[0, primary_data['Primary_Completion'].max() * 2]),
        height=270, margin=dict(t=0, b=0, l=0, r=3),legend=dict(orientation="h", y=-0.2))
 
        yaxis=dict(title='Primary Education ODA (Millions)',range=[0, primary_data['Sector_ODA_Millions'].max() * 2])
        
        st.plotly_chart(fig_primary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        

    with col_Lit:
        st.markdown("<h5 style='margin-bottom: -1.8rem;'>Basic Education ODA vs Total Literacy</h5>", unsafe_allow_html=True)
        Lit_data = Finaldf1[(Finaldf1['Country'] == country) & (Finaldf1['Sector'] == 'Education') & (Finaldf1['Year'].between(2000, 2019))]
        Lit_data = Lit_data[(Lit_data['Sector_ODA_Millions'] != 0) & (Lit_data['Total_Literacy'] != 0)].dropna()
        Lit_data = Lit_data.groupby('Year').agg({'Sector_ODA_Millions': 'sum','Total_Literacy': 'mean'}).reset_index()
        
        fig_lit = px.line(Lit_data, x='Year', y='Sector_ODA_Millions', labels={'Sector_ODA_Millions': 'Basic Education ODA (Millions)'})
        fig_lit.add_scatter(x=Lit_data['Year'], y=Lit_data['Total_Literacy'],
                           name='Total Literacy', yaxis='y2')
        fig_lit.update_layout(
        yaxis2=dict(title='Total Literacy', overlaying='y', side='right', range=[0, Lit_data['Total_Literacy'].max() * 2]),
        height=270, margin=dict(t=0, b=0, l=0, r=3),legend=dict(orientation="h", y=-0.2))
 
        yaxis=dict(title='Basic Education ODA (Millions)',range=[0, Lit_data['Sector_ODA_Millions'].max() * 2])
        
        st.plotly_chart(fig_lit, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_male, col_female = st.columns((5,5))
    with col_male:
        st.markdown("<h5 style='margin-bottom: -1.4rem;'>Literacy-Male </h5>", unsafe_allow_html=True)
        male_data= Finaldf1[(Finaldf1['Country'] == country) & (Finaldf1['Year'].between(2000, 2019))]
        male_data = male_data.dropna(subset=['Literacy_Male'])
        male_data = male_data.groupby('Year')['Literacy_Male'].mean().reset_index()
       
        
        fig_male = px.bar(male_data,x='Year',y='Literacy_Male',
        height=300,color_discrete_sequence=['#ff7f0e'])
        fig_male.update_layout(margin=dict(t=20, b=30, l=40, r=10))
        st.plotly_chart(fig_male, use_container_width=True)
        
    with col_female:
        st.markdown("<h5 style='margin-bottom: -1.4rem;'> Literacy-Female </h5>", unsafe_allow_html=True)
        fem_data= Finaldf1[(Finaldf1['Country'] == country) &(Finaldf1['Year'].between(2000, 2019))]
        fem_data = fem_data.dropna(subset=['Literacy_Female'])
        fem_data = fem_data.groupby('Year')['Literacy_Female'].mean().reset_index()
        
        fig_female = px.bar(fem_data,x='Year',y='Literacy_Female',
        height=300,color_discrete_sequence=['#ff7f0e'])
        fig_female.update_layout(margin=dict(t=20, b=30, l=40, r=10))
        st.plotly_chart(fig_female, use_container_width=True) 
        st.markdown('</div>', unsafe_allow_html=True)





# ------------------------------
# AID EFFECTIVENESS RATIOS TAB
# ------------------------------
elif section == "Aid Effectiveness Ratios":
    st.markdown('<div class="corruption-section">', unsafe_allow_html=True)
    st.markdown("## 🌍 Aid Effectiveness Ratios (2005–2019)")

    indicator_options = {
        "Maternal Mortality (↓)": {"sector": "Reproductive health care", "indicator": "Maternal_Mortality", "better": "lower"},
        "Primary Completion (↑)": {"sector": "Primary education", "indicator": "Primary_Completion", "better": "higher"},
        "Undernourishment (↓)": {"sector": "Basic nutrition", "indicator": "Undernourishment", "better": "lower"},
        "Sanitation Access (↑)": {"sector": "Water supply & sanitation", "indicator": "Population_using_basic_sanitation%", "better": "higher"},
        "School Enrolment Gender Parity Index (GPI) (↑)": {"sector": "Primary education", "indicator": "School_Enroll_GPI", "better": "higher"}
    }

    selected_label = st.selectbox("Select Aid Effectiveness Indicator", list(indicator_options.keys()))
    selected = indicator_options[selected_label]
    sector = selected["sector"]
    indicator = selected["indicator"]
    better = selected["better"]

    df = Finaldf[(Finaldf['Sector'] == sector) & (Finaldf['Year'].isin([2005, 2019]))].copy()
    results = []

    for country in df['Country'].unique():
        d = df[df['Country'] == country]
        if d['Year'].nunique() < 2:
            continue
        try:
            v1 = d[d['Year'] == 2005][indicator].mean()
            v2 = d[d['Year'] == 2019][indicator].mean()
            oda1 = d[d['Year'] == 2005]['Sector_ODA_Millions'].sum()
            oda2 = d[d['Year'] == 2019]['Sector_ODA_Millions'].sum()
            if oda2 - oda1 == 0:
                continue
            aer = (v2 - v1) / (oda2 - oda1)
            results.append({"Country": country, "AER": round(aer, 4)})
        except:
            continue

    aer_df = pd.DataFrame(results)

    if aer_df.empty:
        st.warning("⚠️ No data available for selected indicator.")
    else:
        top = aer_df.sort_values(by="AER", ascending=(better == "lower")).iloc[0]
        worst = aer_df.sort_values(by="AER", ascending=(better == "lower")).iloc[-1]

        col1, col2 = st.columns(2)
        col1.metric("Top Country (Best AER)", f"{top['Country']}", f"AER: {top['AER']}")
        col2.metric("Worst Country (Lowest AER)", f"{worst['Country']}", f"AER: {worst['AER']}")

        fig = px.choropleth(
            aer_df,
            locations="Country",
            locationmode="country names",
            color="AER",
            color_continuous_scale="RdBu_r",
            scope="africa",
            title=f"Aid Effectiveness Ratio: {selected_label} (2005–2019)",
            labels={"AER": "Aid Effectiveness Ratio"},
        )
        fig.update_geos(lonaxis_range=[-20, 10], lataxis_range=[-5, 20])
        fig.update_layout(height=550, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
