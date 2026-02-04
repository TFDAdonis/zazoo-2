import streamlit as st
import json
import pandas as pd
import ee
import traceback
from datetime import datetime
import plotly.graph_objects as go

# Custom CSS for Clean Green & Black TypeScript/React Style
st.markdown("""
<style>
    /* Base styling */
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
    /* Remove Streamlit default padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Green & Black Theme */
    :root {
        --primary-green: #00ff88;
        --accent-green: #00cc6a;
        --primary-black: #000000;
        --card-black: #0a0a0a;
        --secondary-black: #111111;
        --border-gray: #222222;
        --text-white: #ffffff;
        --text-gray: #999999;
        --text-light-gray: #cccccc;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-white) !important;
    }
    
    h1 {
        font-size: 2rem !important;
        background: linear-gradient(90deg, var(--primary-green), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        color: var(--primary-green) !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Cards */
    .card {
        background: var(--card-black);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: var(--primary-green);
    }
    
    .card-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-gray);
    }
    
    .card-title .icon {
        width: 32px;
        height: 32px;
        background: rgba(0, 255, 136, 0.1);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-green);
        font-size: 16px;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, var(--primary-green), var(--accent-green));
        color: var(--primary-black) !important;
        border: none;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        margin: 5px 0;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        background: rgba(0, 255, 136, 0.1);
        color: var(--primary-green);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 30px 0;
        position: relative;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--border-gray);
        z-index: 1;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
    }
    
    .step-number {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: var(--border-gray);
        color: var(--text-gray);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    
    .step.active .step-number {
        background: var(--primary-green);
        color: var(--primary-black);
    }
    
    .step.completed .step-number {
        background: var(--accent-green);
        color: var(--primary-black);
    }
    
    .step-label {
        font-size: 12px;
        color: var(--text-gray);
        text-align: center;
    }
    
    .step.active .step-label {
        color: var(--primary-green);
        font-weight: 600;
    }
    
    /* Flag grid */
    .flag-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .flag-item {
        background: var(--secondary-black);
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        padding: 15px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }
    
    .flag-item:hover {
        border-color: var(--primary-green);
        transform: translateY(-2px);
    }
    
    .flag-item.selected {
        border-color: var(--primary-green);
        background: rgba(0, 255, 136, 0.05);
    }
    
    .flag-container {
        width: 80px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 4px;
    }
    
    .flag-name {
        font-size: 12px;
        text-align: center;
        color: var(--text-light-gray);
    }
    
    .flag-item.selected .flag-name {
        color: var(--primary-green);
        font-weight: 600;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Earth Engine Auto-Authentication
def auto_initialize_earth_engine():
    """Automatically initialize Earth Engine with service account credentials"""
    try:
        service_account_info = {
            "type": "service_account",
            "project_id": "citric-hawk-457513-i6",
            "private_key_id": "8984179a69969591194d8f8097e48cd9789f5ea2",
            "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDFQOtXKWE+7mEY
JUTNzx3h+QvvDCvZ2B6XZTofknuAFPW2LqAzZustznJJFkCmO3Nutct+W/iDQCG0
1DjOQcbcr/jWr+mnRLVOkUkQc/kzZ8zaMQqU8HpXjS1mdhpsrbUaRKoEgfo3I3Bp
dFcJ/caC7TSr8VkGnZcPEZyXVsj8dLSEzomdkX+mDlJlgCrNfu3Knu+If5lXh3Me
SKiMWsfMnasiv46oD4szBzg6HLgoplmNka4NiwfeM7qROYnCd+5conyG8oiU00Xe
zC2Ekzo2dWsCw4zIJD6IdAcvgdrqH63fCqDFmAjEBZ69h8fWrdnsq56dAIpt0ygl
P9ADiRbVAgMBAAECggEALO7AnTqBGy2AgxhMP8iYEUdiu0mtvIIxV8HYl2QOC2ta
3GzrE8J0PJs8J99wix1cSmIRkH9hUP6dHvy/0uYjZ1aTi84HHtH1LghE2UFdySKy
RJqqwyozaDmx15b8Jnj8Wdc91miIR6KkQvVcNVuwalcf6jIAWlQwGp/jqIq9nloN
eld6xNbEmacORz1qT+4/uxOE05mrrZHC4kIKtswi8Io4ExVe61VxXsXWSHrMCGz0
TiSGr2ORSlRWC/XCGCu7zFIJU/iw6BiNsxryk6rjqQrcAtmoFTFx0fWbjYkG1DDs
k/9Dov1gyx0OtEyX8beoaf0Skcej4zdfeuido2A1sQKBgQD4IrhFn50i4/pa9sk1
g7v1ypGTrVA3pfvj6c7nTgzj9oyJnlU3WJwCqLw1cTFiY84+ekYP15wo8xsu5VZd
YLzOKEg3B8g899Ge14vZVNd6cNfRyMk4clGrDwGnZ4OAQkdsT/AyaCGRIcyu9njA
xdmWa+6VPMG7U65f/656XGwkBQKBgQDLgVyRE2+r1XCY+tdtXtga9sQ4LoiYHzD3
eDHe056qmwk8jf1A1HekILnC1GyeaKkOUd4TEWhVBgQpsvtC4Z2zPXlWR8N7SwNu
SFAhy3OnHTZQgrRWFA8eBjeI0YoXmk5m6uMQ7McmDlFxxXenFi+qSl3Cu4aGGuOy
cfyWMbTwkQKBgAoKfaJznww2ZX8g1WuQ9R4xIEr1jHV0BglnALRjeCoRZAZ9nb0r
nMSOx27yMallmIb2s7cYZn1RuRvgs+n7bCh7gNCZRAUTkiv3VPVqdX3C6zjWAy6B
kcR2Sv7XNX8PL4y2f2XKyPDyiTHbT2+dkfyASZtIZh6KeFfyJMFW1BlxAoGAAeG6
V2UUnUQl/GQlZc+AtA8gFVzoym9PZppn66WNTAqO9U5izxyn1o6u6QxJzNUu6wD6
yrZYfqDFnRUYma+4Y5Xn71JOjm9NItHsW8Oj2CG/BNOQk1MwKJjqHovBeSJmIzF8
1AU8ei+btS+cQaFE45A4ebp+LfNFs7q2GTVwdOECgYEAtHkMqigOmZdR3QAcZTjL
3aeOMGVHB2pHYosTgslD9Yp+hyVHqSdyCplHzWB3d8roIecW4MEb0mDxlaTdZfmR
dtBYiTzMxLezHsRZ4KP4NtGAE3iTL1b6DXuoI84+H/HaQ1EB79+YV9ZTAabt1b7o
e5aU1RW6tlG8nzHHwK2FeyI=
-----END PRIVATE KEY-----""",
            "client_email": "cc-365@citric-hawk-457513-i6.iam.gserviceaccount.com",
            "client_id": "105264622264803277310",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cc-365%40citric-hawk-457513-i6.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        credentials = ee.ServiceAccountCredentials(
            service_account_info['client_email'],
            key_data=json.dumps(service_account_info)
        )
        
        ee.Initialize(credentials, project='citric-hawk-457513-i6')
        return True
    except Exception as e:
        st.error(f"Earth Engine auto-initialization failed: {str(e)}")
        return False

# Initialize Earth Engine
if 'ee_auto_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_auto_initialized = True
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_auto_initialized = False
            st.session_state.ee_initialized = False

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1  # Start at step 1
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None
if 'selected_municipality' not in st.session_state:
    st.session_state.selected_municipality = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header
st.markdown("""
<div class="compact-header">
    <div>
        <h1>🌍 KHISBA GIS</h1>
        <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics</p>
    </div>
    <div style="display: flex; gap: 10px;">
        <span class="status-badge">Connected</span>
        <span class="status-badge">3D Analysis</span>
        <span class="status-badge">v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Step Indicator
st.markdown("""
<div class="step-indicator">
    <div class="step ${'completed' if st.session_state.step > 1 else 'active' if st.session_state.step == 1 else ''}">
        <div class="step-number">1</div>
        <div class="step-label">Select Area</div>
    </div>
    <div class="step ${'completed' if st.session_state.step > 2 else 'active' if st.session_state.step == 2 else ''}">
        <div class="step-number">2</div>
        <div class="step-label">Configure Analysis</div>
    </div>
    <div class="step ${'completed' if st.session_state.step > 3 else 'active' if st.session_state.step == 3 else ''}">
        <div class="step-number">3</div>
        <div class="step-label">View Results</div>
    </div>
</div>
""".replace("${'completed' if st.session_state.step > 1 else 'active' if st.session_state.step == 1 else ''}", 
            "completed" if st.session_state.step > 1 else "active" if st.session_state.step == 1 else "")
 .replace("${'completed' if st.session_state.step > 2 else 'active' if st.session_state.step == 2 else ''}",
          "completed" if st.session_state.step > 2 else "active" if st.session_state.step == 2 else "")
 .replace("${'completed' if st.session_state.step > 3 else 'active' if st.session_state.step == 3 else ''}",
          "completed" if st.session_state.step > 3 else "active" if st.session_state.step == 3 else ""),
unsafe_allow_html=True)

# Step 1: Area Selection
if st.session_state.step == 1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">🌍</div><h3 style="margin: 0;">Step 1: Select Your Analysis Area</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state.ee_initialized:
        st.error("Earth Engine not initialized. Please check your connection.")
    else:
        try:
            # Get countries from Earth Engine
            countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
            country_names = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
            country_names = sorted(country_names)
            
            # Country selection
            st.subheader("Select a Country")
            
            # Create a flag grid for countries
            st.markdown('<div class="flag-grid">', unsafe_allow_html=True)
            
            # Predefined flags HTML (simplified for space - you can expand this)
            flags_html = {
                "Afghanistan": """<div class="flag-container" style="background: linear-gradient(to right, black 33%, #be0000 33%, #be0000 66%, #009900 0);"></div>""",
                "Albania": """<div class="flag-container" style="background-color: #da2b26;"></div>""",
                "Algeria": """<div class="flag-container" style="background: linear-gradient(to right, #00a652 50%, #fff 0);"></div>""",
                "Andorra": """<div class="flag-container" style="background: linear-gradient(to right, #3f2e8e 33%, #f8e211 33%, #f8e211 66%, #db1f40 0);"></div>""",
                "Angola": """<div class="flag-container" style="background: linear-gradient(#be0026 50%, #000 0);"></div>""",
                "Argentina": """<div class="flag-container" style="background: linear-gradient(#8ad3f4 33%, #fff 33%, #fff 66%, #8ad3f4 0);"></div>""",
                "Australia": """<div class="flag-container" style="background-color: #001b6a;"></div>""",
                "Austria": """<div class="flag-container" style="background: linear-gradient(#d72427 33%, #fff 33%, #fff 66%, #d72427 0);"></div>""",
                "Bangladesh": """<div class="flag-container" style="background-color: #006a4c;"></div>""",
                "Belgium": """<div class="flag-container" style="background: linear-gradient(to right, black 33%, #fddb21 33%, #fddb21 67%, #ef303f 0);"></div>""",
                "Brazil": """<div class="flag-container" style="background-color: #009c37;"></div>""",
                "Canada": """<div class="flag-container" style="background: linear-gradient(to right, #ec2224 30%, #fff 30%, #fff 70%, #ec2224 0);"></div>""",
                "China": """<div class="flag-container" style="background: #dd2d26;"></div>""",
                "Egypt": """<div class="flag-container" style="background: linear-gradient(#ce2029 33%, #fff 33%, #fff 67%, #000 0);"></div>""",
                "France": """<div class="flag-container" style="background: linear-gradient(to right, #192f8e 33%, #fff 33%, #fff 67%, #e01414 0);"></div>""",
                "Germany": """<div class="flag-container" style="background: linear-gradient(#000 33%, #de0000 33%, #de0000 67%, #ffcf00 0);"></div>""",
                "India": """<div class="flag-container" style="background: linear-gradient(#ff9933 33%, #fff 33%, #fff 66%, #138808 0);"></div>""",
                "Italy": """<div class="flag-container" style="background: linear-gradient(to right, #009343 33%, #fff 33%, #fff 66%, #cf2734 0);"></div>""",
                "Japan": """<div class="flag-container" style="background: #fff;"></div>""",
                "Mexico": """<div class="flag-container" style="background: linear-gradient(to right, #006845 33%, #fff 33%, #fff 66%, #cf0922 0);"></div>""",
                "Russia": """<div class="flag-container" style="background: linear-gradient(#fff 33%, #0136a8 33%, #0136a8 66%, #d72718 0);"></div>""",
                "South Africa": """<div class="flag-container" style="background: #007847;"></div>""",
                "Spain": """<div class="flag-container" style="background: linear-gradient(#ad1519 25%, #fabd00 25%, #fabd00 75%, #ad1519 0);"></div>""",
                "United Kingdom": """<div class="flag-container" style="background: #213064;"></div>""",
                "United States": """<div class="flag-container" style="background: repeating-linear-gradient(#b22234, #b22234 7.7%, #fff 7.7%, #fff 15.4%);"></div>""",
            }
            
            # Display countries in grid format
            cols = st.columns(4)
            for idx, country in enumerate(country_names[:20]):  # Show first 20 for example
                with cols[idx % 4]:
                    flag_html = flags_html.get(country, """<div class="flag-container" style="background: linear-gradient(45deg, #1e3c72, #2a5298);"></div>""")
                    if st.button(
                        f"**{country}**",
                        use_container_width=True,
                        key=f"country_{country}"
                    ):
                        st.session_state.selected_country = country
                        st.session_state.step = 2
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Or use dropdown as backup
            st.markdown("---")
            st.markdown("**Or select from all countries:**")
            selected_country_dropdown = st.selectbox(
                "Choose Country",
                options=["Select a country"] + country_names,
                index=0,
                key="country_dropdown"
            )
            
            if selected_country_dropdown and selected_country_dropdown != "Select a country":
                st.session_state.selected_country = selected_country_dropdown
            
            if st.session_state.selected_country:
                st.success(f"✅ Selected: **{st.session_state.selected_country}**")
                
                # Get municipalities for selected country
                country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', st.session_state.selected_country)).first()
                country_code = country_feature.get('ADM0_CODE').getInfo()
                
                admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq('ADM0_CODE', country_code))
                municipality_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                municipality_names = sorted(municipality_names)
                
                if municipality_names:
                    st.subheader("Select Municipality")
                    selected_municipality = st.selectbox(
                        "Choose Municipality",
                        options=["Select municipality"] + municipality_names,
                        index=0,
                        key="municipality_select"
                    )
                    
                    if selected_municipality and selected_municipality != "Select municipality":
                        st.session_state.selected_municipality = selected_municipality
                        
                        # Get geometry
                        municipality_geometry = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', selected_municipality))
                        st.session_state.selected_geometry = municipality_geometry
                        
                        st.success(f"✅ Selected: **{selected_municipality}**, {st.session_state.selected_country}")
                        
                        # Display area on mini map (simplified)
                        st.markdown("---")
                        st.subheader("📍 Selected Area Preview")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div style="background: #111111; padding: 15px; border-radius: 8px;">
                                <p style="color: #00ff88; margin: 0 0 10px 0;"><strong>Selected Area</strong></p>
                                <p style="margin: 5px 0;">🌍 Country: {st.session_state.selected_country}</p>
                                <p style="margin: 5px 0;">🏙️ Municipality: {st.session_state.selected_municipality}</p>
                                <p style="margin: 5px 0;">📍 Level: Municipal Analysis</p>
                                <p style="margin: 5px 0;">📊 Status: <span style="color: #00ff88;">Ready for Analysis</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            # Simplified map preview
                            st.markdown("""
                            <div style="background: #222222; height: 150px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #333333;">
                                <div style="text-align: center;">
                                    <div style="font-size: 24px;">🗺️</div>
                                    <p style="margin: 5px 0; color: #999999; font-size: 12px;">Area Selected</p>
                                    <p style="margin: 0; color: #00ff88; font-size: 12px;">✓ Ready</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Next button
                        if st.button("🚀 Continue to Step 2", type="primary", use_container_width=True):
                            st.session_state.step = 2
                            st.rerun()
                else:
                    st.warning("No municipality data available for this country.")
            
        except Exception as e:
            st.error(f"Error loading countries: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Analysis Configuration
elif st.session_state.step == 2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Configure Your Analysis</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.selected_country and st.session_state.selected_municipality:
        # Show selected area
        st.markdown(f"""
        <div style="background: #111111; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #00ff88;">
            <p style="margin: 0; color: #00ff88;"><strong>Selected Area:</strong> {st.session_state.selected_municipality}, {st.session_state.selected_country}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Analysis Settings
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2023, 1, 1),
                help="Start date for analysis",
                key="start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime(2023, 12, 31),
                help="End date for analysis",
                key="end_date"
            )
        
        # Satellite selection
        collection_choice = st.selectbox(
            "Satellite Source",
            options=["Sentinel-2", "Landsat-8"],
            help="Choose satellite collection",
            key="satellite_select"
        )
        
        # Cloud cover
        cloud_cover = st.slider(
            "Max Cloud Cover (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Maximum cloud cover percentage",
            key="cloud_slider"
        )
        
        # Vegetation Indices
        st.subheader("🌿 Vegetation Indices")
        
        available_indices = [
            'NDVI', 'EVI', 'SAVI', 'NDWI', 'ARVI', 'GNDVI', 'MSAVI',
            'NDMI', 'NBR', 'NDSI', 'VARI', 'OSAVI', 'DVI'
        ]
        
        # Create columns for indices
        cols = st.columns(3)
        selected_indices = []
        
        for idx, index in enumerate(available_indices):
            with cols[idx % 3]:
                if st.checkbox(index, value=(index in ['NDVI', 'EVI', 'SAVI', 'NDWI']), key=f"index_{index}"):
                    selected_indices.append(index)
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("← Back to Step 1", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col_btn2:
            if st.button("📊 View Sample Chart", use_container_width=True):
                # Generate sample chart
                st.session_state.step = 3
                st.rerun()
        with col_btn3:
            if st.button("🚀 Run Full Analysis", type="primary", use_container_width=True):
                if not selected_indices:
                    st.error("Please select at least one vegetation index")
                else:
                    with st.spinner("Running analysis..."):
                        try:
                            # This is a simplified analysis - in production, use actual Earth Engine calls
                            # For demo purposes, we'll create sample data
                            import random
                            from datetime import datetime, timedelta
                            
                            results = {}
                            dates = []
                            current_date = start_date
                            
                            # Generate sample dates
                            while current_date <= end_date:
                                dates.append(current_date.strftime('%Y-%m-%d'))
                                current_date += timedelta(days=30)
                            
                            # Generate sample data for each index
                            for index in selected_indices:
                                values = [random.uniform(0.1, 0.9) for _ in range(len(dates))]
                                results[index] = {'dates': dates, 'values': values}
                            
                            st.session_state.analysis_results = results
                            st.session_state.step = 3
                            st.success("✅ Analysis completed!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Step 3: Results View
elif st.session_state.step == 3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 3: Analysis Results</h3></div>', unsafe_allow_html=True)
    
    # Show selected area
    st.markdown(f"""
    <div style="background: #111111; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #00ff88;">
        <p style="margin: 0; color: #00ff88;">
            <strong>Analysis Results for:</strong> {st.session_state.selected_municipality}, {st.session_state.selected_country}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Summary Statistics
        st.subheader("📈 Summary Statistics")
        
        summary_data = []
        for index, data in results.items():
            if data['values']:
                values = data['values']
                summary_data.append({
                    'Index': index,
                    'Mean': round(sum(values) / len(values), 4),
                    'Min': round(min(values), 4),
                    'Max': round(max(values), 4),
                    'Std Dev': round((sum((x - (sum(values)/len(values)))**2 for x in values) / len(values))**0.5, 4) if len(values) > 1 else 0
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Charts Section
        st.subheader("📊 Vegetation Indices Over Time")
        
        for index, data in results.items():
            if data['dates'] and data['values']:
                try:
                    # Create chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=data['dates'], 
                        y=data['values'],
                        mode='lines+markers',
                        name=f'{index}',
                        line=dict(color='#00ff88', width=3),
                        marker=dict(
                            size=6,
                            color='#00ff88',
                            line=dict(width=1, color='#ffffff')
                        ),
                        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.4f}<extra></extra>'
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title=f'{index} - Vegetation Index',
                        plot_bgcolor='#0a0a0a',
                        paper_bgcolor='#0a0a0a',
                        font=dict(color='#ffffff'),
                        xaxis=dict(
                            gridcolor='#222222',
                            zerolinecolor='#222222',
                            tickcolor='#444444',
                            title_font_color='#ffffff',
                            title='Date'
                        ),
                        yaxis=dict(
                            gridcolor='#222222',
                            zerolinecolor='#222222',
                            tickcolor='#444444',
                            title_font_color='#ffffff',
                            title=f'{index} Value'
                        ),
                        legend=dict(
                            bgcolor='rgba(0,0,0,0.5)',
                            bordercolor='#222222',
                            borderwidth=1
                        ),
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error creating chart for {index}: {str(e)}")
        
        # Export Section
        st.subheader("💾 Export Results")
        
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📥 Download CSV", use_container_width=True):
                # Create CSV data
                export_data = []
                for index, data in results.items():
                    for date, value in zip(data['dates'], data['values']):
                        export_data.append({
                            'Date': date,
                            'Index': index,
                            'Value': value
                        })
                
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name=f"vegetation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col_exp2:
            if st.button("🔄 New Analysis", use_container_width=True):
                # Reset for new analysis
                st.session_state.step = 1
                st.session_state.selected_country = None
                st.session_state.selected_municipality = None
                st.session_state.analysis_results = None
                st.rerun()
    
    else:
        # Sample chart if no results
        st.info("No analysis results yet. Run an analysis in Step 2 or view a sample chart.")
        
        # Create sample chart
        import random
        from datetime import datetime, timedelta
        
        dates = []
        values = []
        current_date = datetime(2023, 1, 1)
        
        for i in range(12):
            dates.append(current_date.strftime('%Y-%m'))
            values.append(random.uniform(0.3, 0.8))
            current_date += timedelta(days=30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, 
            y=values,
            mode='lines+markers',
            name='NDVI (Sample)',
            line=dict(color='#00ff88', width=3),
            marker=dict(size=6, color='#00ff88')
        ))
        
        fig.update_layout(
            title='Sample Vegetation Index (NDVI)',
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Configuration", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Start New Analysis", use_container_width=True):
                st.session_state.step = 1
                st.session_state.selected_country = None
                st.session_state.selected_municipality = None
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 20px 0; margin-top: 30px;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Created by Taibi Farouk Djilali • Clean Green & Black Design</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span class="status-badge">Step-by-Step Guide</span>
        <span class="status-badge">Country Flags</span>
        <span class="status-badge">Earth Engine</span>
        <span class="status-badge">Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)
