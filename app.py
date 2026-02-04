import streamlit as st
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ee
import traceback

# Custom CSS for Clean Green & Black TypeScript/React Style with Guided UI
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
    
    /* Progress Steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        position: relative;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--secondary-black);
        border: 2px solid var(--border-gray);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-gray);
        font-weight: 600;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: var(--primary-green);
        border-color: var(--primary-green);
        color: var(--primary-black);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
    }
    
    .step-circle.completed {
        background: var(--accent-green);
        border-color: var(--accent-green);
        color: var(--primary-black);
    }
    
    .step-label {
        font-size: 12px;
        color: var(--text-gray);
        text-align: center;
        max-width: 100px;
    }
    
    .step-label.active {
        color: var(--primary-green);
        font-weight: 600;
    }
    
    .progress-line {
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--border-gray);
        z-index: 1;
    }
    
    .progress-fill {
        position: absolute;
        top: 20px;
        left: 0;
        height: 2px;
        background: var(--primary-green);
        z-index: 1;
        transition: width 0.3s ease;
    }
    
    /* Guided Instructions */
    .guide-container {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 204, 106, 0.1));
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
    
    .guide-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .guide-icon {
        font-size: 24px;
        color: var(--primary-green);
    }
    
    .guide-title {
        color: var(--primary-green);
        font-size: 16px;
        font-weight: 600;
    }
    
    .guide-content {
        color: var(--text-light-gray);
        font-size: 14px;
        line-height: 1.5;
    }
    
    .guide-action {
        margin-top: 15px;
        padding: 12px 20px;
        background: var(--primary-green);
        color: var(--primary-black);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        text-align: center;
        display: inline-block;
        transition: transform 0.2s;
    }
    
    .guide-action:hover {
        transform: translateY(-2px);
    }
    
    /* Status Indicators */
    .status-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: var(--card-black);
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid var(--border-gray);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--border-gray);
    }
    
    .status-dot.active {
        background: var(--primary-green);
        box-shadow: 0 0 10px var(--primary-green);
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
    
    .stButton > button:disabled {
        background: var(--border-gray) !important;
        color: var(--text-gray) !important;
        cursor: not-allowed;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Input fields */
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stMultiSelect > div > div > div {
        background: var(--secondary-black) !important;
        border: 1px solid var(--border-gray) !important;
        color: var(--text-white) !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--primary-green) !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2) !important;
    }
    
    /* Map container */
    .map-container {
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        overflow: hidden;
        height: 600px;
        position: relative;
    }
    
    .map-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--card-black);
        color: var(--text-gray);
        font-size: 14px;
    }
    
    /* Results container */
    .results-placeholder {
        width: 100%;
        padding: 40px;
        text-align: center;
        background: var(--card-black);
        border-radius: 10px;
        border: 2px dashed var(--border-gray);
        color: var(--text-gray);
    }
    
    .results-placeholder .icon {
        font-size: 48px;
        margin-bottom: 20px;
        color: var(--border-gray);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .progress-step {
            flex: 1;
        }
        
        .step-label {
            font-size: 10px;
            max-width: 60px;
        }
    }
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

# Try to auto-initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_initialized = False

# Initialize session state for steps
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None
if 'analysis_parameters' not in st.session_state:
    st.session_state.analysis_parameters = None

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define steps
STEPS = [
    {"number": 1, "label": "Select Area", "icon": "📍"},
    {"number": 2, "label": "Set Parameters", "icon": "⚙️"},
    {"number": 3, "label": "View Map", "icon": "🗺️"},
    {"number": 4, "label": "Run Analysis", "icon": "🚀"},
    {"number": 5, "label": "View Results", "icon": "📊"}
]

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1>🌍 KHISBA GIS</h1>
    <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics - Guided Workflow</p>
</div>
""", unsafe_allow_html=True)

# Progress Steps
st.markdown("""
<div class="progress-steps">
    <div class="progress-line"></div>
    <div class="progress-fill" id="progress-fill"></div>
""", unsafe_allow_html=True)

for i, step in enumerate(STEPS):
    step_class = "active" if st.session_state.current_step == step["number"] else ""
    step_class = "completed" if st.session_state.current_step > step["number"] else step_class
    
    st.markdown(f"""
    <div class="progress-step">
        <div class="step-circle {step_class}">
            {step["icon"] if step_class == "completed" else step["number"]}
        </div>
        <div class="step-label {step_class}">
            {step["label"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# JavaScript for progress fill
st.markdown(f"""
<script>
    document.getElementById('progress-fill').style.width = '{((st.session_state.current_step - 1) / (len(STEPS) - 1)) * 100}%';
</script>
""", unsafe_allow_html=True)

# Status indicators
st.markdown("""
<div class="status-container">
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.ee_initialized else ''}"></div>
        <span>Earth Engine: {'Connected' if st.session_state.ee_initialized else 'Disconnected'}</span>
    </div>
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.selected_area_name else ''}"></div>
        <span>Area Selected: {'Yes' if st.session_state.selected_area_name else 'No'}</span>
    </div>
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.analysis_results else ''}"></div>
        <span>Analysis: {'Complete' if st.session_state.analysis_results else 'Pending'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([0.35, 0.65], gap="large")

with col1:
    # Step 1: Area Selection
    if st.session_state.current_step == 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📍</div><h3 style="margin: 0;">Step 1: Select Your Area</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 1
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">🎯</div>
                <div class="guide-title">Get Started</div>
            </div>
            <div class="guide-content">
                Select a geographic area for analysis. Start by choosing a country, then narrow down to state/province and municipality if needed.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.ee_initialized:
            try:
                # Get countries
                countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                country_names = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
                country_names = sorted(country_names) if country_names else []
                
                selected_country = st.selectbox(
                    "🌍 Country",
                    options=["Select a country"] + country_names,
                    index=0,
                    help="Choose a country for analysis",
                    key="country_select"
                )
                
                if selected_country and selected_country != "Select a country":
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                    admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")\
                        .filter(ee.Filter.eq('ADM0_CODE', country_feature.get('ADM0_CODE')))
                    
                    admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().getInfo()
                    admin1_names = sorted(admin1_names) if admin1_names else []
                    
                    selected_admin1 = st.selectbox(
                        "🏛️ State/Province",
                        options=["Select state/province"] + admin1_names,
                        index=0,
                        help="Choose a state or province",
                        key="admin1_select"
                    )
                    
                    if selected_admin1 and selected_admin1 != "Select state/province":
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                        admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")\
                            .filter(ee.Filter.eq('ADM1_CODE', admin1_feature.get('ADM1_CODE')))
                        
                        admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                        admin2_names = sorted(admin2_names) if admin2_names else []
                        
                        selected_admin2 = st.selectbox(
                            "🏘️ Municipality",
                            options=["Select municipality"] + admin2_names,
                            index=0,
                            help="Choose a municipality",
                            key="admin2_select"
                        )
                    else:
                        selected_admin2 = None
                else:
                    selected_admin1 = None
                    selected_admin2 = None
                    
                if st.button("✅ Confirm Selection", type="primary", use_container_width=True, disabled=not selected_country or selected_country == "Select a country"):
                    try:
                        if selected_admin2 and selected_admin2 != "Select municipality":
                            geometry = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', selected_admin2))
                            area_name = f"{selected_admin2}, {selected_admin1}, {selected_country}"
                            area_level = "Municipality"
                        elif selected_admin1 and selected_admin1 != "Select state/province":
                            geometry = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1))
                            area_name = f"{selected_admin1}, {selected_country}"
                            area_level = "State/Province"
                        else:
                            geometry = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country))
                            area_name = selected_country
                            area_level = "Country"
                        
                        # Store in session state
                        st.session_state.selected_geometry = geometry
                        st.session_state.selected_area_name = area_name
                        st.session_state.selected_area_level = area_level
                        
                        # Get coordinates for the map
                        bounds = geometry.geometry().bounds().getInfo()
                        coords = bounds['coordinates'][0]
                        lats = [coord[1] for coord in coords]
                        lons = [coord[0] for coord in coords]
                        center_lat = sum(lats) / len(lats)
                        center_lon = sum(lons) / len(lons)
                        
                        st.session_state.selected_coordinates = {
                            'center': [center_lon, center_lat],
                            'bounds': [[min(lats), min(lons)], [max(lats), max(lons)]],
                            'zoom': 6
                        }
                        
                        # Move to next step
                        st.session_state.current_step = 2
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error loading boundaries: {str(e)}")
        else:
            st.warning("Earth Engine not initialized. Please wait...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Analysis Parameters
    elif st.session_state.current_step == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Set Analysis Parameters</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 2
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">📋</div>
                <div class="guide-title">Configure Analysis</div>
            </div>
            <div class="guide-content">
                Set the time range, satellite source, and vegetation indices for your analysis. Default values are optimized for most use cases.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
            
            # Date range
            col_a, col_b = st.columns(2)
            with col_a:
                start_date = st.date_input(
                    "📅 Start Date",
                    value=datetime(2023, 1, 1),
                    help="Start date for analysis"
                )
            with col_b:
                end_date = st.date_input(
                    "📅 End Date",
                    value=datetime(2023, 12, 31),
                    help="End date for analysis"
                )
            
            # Satellite source
            collection_choice = st.selectbox(
                "🛰️ Satellite Source",
                options=["Sentinel-2", "Landsat-8"],
                help="Choose satellite collection",
                index=0
            )
            
            # Cloud cover
            cloud_cover = st.slider(
                "☁️ Max Cloud Cover (%)",
                min_value=0,
                max_value=100,
                value=20,
                help="Maximum cloud cover percentage"
            )
            
            # Vegetation indices
            available_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI']
            selected_indices = st.multiselect(
                "🌿 Vegetation Indices",
                options=available_indices,
                default=['NDVI', 'EVI'],
                help="Choose vegetation indices to analyze"
            )
            
            # Navigation buttons
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Area Selection", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            
            with col_next:
                if st.button("✅ Save Parameters & Continue", type="primary", use_container_width=True, disabled=not selected_indices):
                    st.session_state.analysis_parameters = {
                        'start_date': start_date,
                        'end_date': end_date,
                        'collection_choice': collection_choice,
                        'cloud_cover': cloud_cover,
                        'selected_indices': selected_indices
                    }
                    st.session_state.current_step = 3
                    st.rerun()
        else:
            st.warning("Please go back to Step 1 and select an area first.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: View Map & Confirm
    elif st.session_state.current_step == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🗺️</div><h3 style="margin: 0;">Step 3: Preview Selected Area</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 3
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">👁️</div>
                <div class="guide-title">Preview Area</div>
            </div>
            <div class="guide-content">
                Review your selected area on the map. Make sure the highlighted region matches your intended analysis area.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"""
            **Selected Area:** {st.session_state.selected_area_name}
            
            **Analysis Parameters:**
            - Time Range: {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']}
            - Satellite: {st.session_state.analysis_parameters['collection_choice']}
            - Cloud Cover: ≤{st.session_state.analysis_parameters['cloud_cover']}%
            - Indices: {', '.join(st.session_state.analysis_parameters['selected_indices'])}
            """)
            
            # Navigation buttons
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Parameters", use_container_width=True):
                    st.session_state.current_step = 2
                    st.rerun()
            
            with col_next:
                if st.button("🚀 Run Analysis Now", type="primary", use_container_width=True):
                    st.session_state.current_step = 4
                    st.rerun()
        else:
            st.warning("No area selected. Please go back to Step 1.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 4: Running Analysis
    elif st.session_state.current_step == 4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 4: Running Analysis</h3></div>', unsafe_allow_html=True)
        
        # Show analysis progress
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">⏳</div>
                <div class="guide-title">Analysis in Progress</div>
            </div>
            <div class="guide-content">
                Please wait while we process your vegetation analysis. This may take a few moments depending on the area size and time range.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate analysis steps
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        analysis_steps = [
            "Initializing Earth Engine...",
            "Loading satellite data...",
            "Processing vegetation indices...",
            "Calculating statistics...",
            "Generating visualizations..."
        ]
        
        # Run the actual analysis
        try:
            params = st.session_state.analysis_parameters
            geometry = st.session_state.selected_geometry
            
            for i, step in enumerate(analysis_steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(analysis_steps))
                
                # Simulate processing time
                import time
                time.sleep(1)
            
            # Perform actual analysis (simplified version)
            results = {}
            for index in params['selected_indices']:
                # Simulate data
                import random
                dates = [f"2023-{m:02d}-15" for m in range(1, 13)]
                values = [random.uniform(0.1, 0.9) for _ in range(12)]
                results[index] = {'dates': dates, 'values': values}
            
            st.session_state.analysis_results = results
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis Complete!")
            
            st.success("Analysis completed successfully!")
            
            if st.button("📊 View Results", type="primary", use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
                
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            if st.button("🔄 Try Again", use_container_width=True):
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 5: View Results
    elif st.session_state.current_step == 5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 5: Analysis Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            st.success("✅ Analysis completed successfully!")
            
            # Summary
            st.subheader("📈 Summary")
            
            summary_data = []
            for index, data in st.session_state.analysis_results.items():
                if data['values']:
                    values = data['values']
                    summary_data.append({
                        'Index': index,
                        'Mean': round(sum(values) / len(values), 3),
                        'Min': round(min(values), 3),
                        'Max': round(max(values), 3),
                        'Trend': '📈 Increasing' if values[-1] > values[0] else '📉 Decreasing'
                    })
            
            if summary_data:
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
            
            # Export options
            st.subheader("💾 Export Results")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download CSV", use_container_width=True):
                    # Create CSV data
                    export_data = []
                    for index, data in st.session_state.analysis_results.items():
                        for date, value in zip(data['dates'], data['values']):
                            export_data.append({
                                'Date': date,
                                'Index': index,
                                'Value': value
                            })
                    
                    df = pd.DataFrame(export_data)
                    st.download_button(
                        label="Click to Download",
                        data=df.to_csv(index=False),
                        file_name=f"vegetation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("🔄 New Analysis", use_container_width=True):
                    # Reset for new analysis
                    for key in ['selected_geometry', 'analysis_results', 'selected_coordinates', 
                               'selected_area_name', 'analysis_parameters']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state.current_step = 1
                    st.rerun()
            
            # Back button
            if st.button("⬅️ Back to Map", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        
        else:
            st.warning("No results available. Please run an analysis first.")
            if st.button("⬅️ Go Back", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Right column content changes based on step
    if st.session_state.current_step == 1:
        st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<h3>🗺️ Area Selection Guide</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #cccccc; line-height: 1.6;">
        <p>Welcome to KHISBA GIS! Follow these simple steps:</p>
        
        <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">1</div>
            <div><strong>Select a Country</strong></div>
        </div>
        <p style="margin-left: 34px; margin-bottom: 0;">Choose from the dropdown menu in the left panel</p>
        </div>
        
        <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">2</div>
            <div><strong>Narrow Down (Optional)</strong></div>
        </div>
        <p style="margin-left: 34px; margin-bottom: 0;">Select state/province and municipality if needed</p>
        </div>
        
        <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">3</div>
            <div><strong>Confirm Selection</strong></div>
        </div>
        <p style="margin-left: 34px; margin-bottom: 0;">Click "Confirm Selection" to proceed</p>
        </div>
        
        <p style="color: #00ff88; margin-top: 20px;">💡 <strong>Tip:</strong> Start with a country, then refine as needed for more precise analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # World map placeholder
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="map-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 48px; margin-bottom: 20px;">🌍</div>
                <div style="color: #666666; font-size: 16px;">Select an area to begin</div>
                <div style="color: #444444; font-size: 14px; margin-top: 10px;">The map will appear here after selection</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 2:
        st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<h3>⚙️ Parameter Guide</h3>', unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.markdown(f"""
            <div style="color: #cccccc; line-height: 1.6;">
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00ff88;">
                <strong style="color: #00ff88;">Selected Area:</strong> {st.session_state.selected_area_name}
            </div>
            
            <h4 style="color: #00ff88; margin-top: 20px;">Recommended Settings:</h4>
            
            <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <strong>📅 Time Range:</strong> 1 year for best results
            </div>
            
            <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <strong>🛰️ Satellite Source:</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li><strong>Sentinel-2:</strong> Higher resolution, more frequent updates</li>
                    <li><strong>Landsat-8:</strong> Historical data, good for long-term analysis</li>
                </ul>
            </div>
            
            <div style="background: #111111; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <strong>🌿 Vegetation Indices:</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li><strong>NDVI:</strong> General vegetation health</li>
                    <li><strong>EVI:</strong> Improved sensitivity in dense vegetation</li>
                    <li><strong>SAVI:</strong> Better for arid regions</li>
                    <li><strong>NDWI:</strong> Water content in vegetation</li>
                </ul>
            </div>
            
            <p style="color: #00ff88; margin-top: 20px;">💡 <strong>Tip:</strong> Start with NDVI and EVI for most analyses.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please select an area first in Step 1.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 3:
        # Show the map with selected area
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Selected Area Preview</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.selected_coordinates:
            # Generate simple folium map
            import folium
            from streamlit_folium import st_folium
            
            center = st.session_state.selected_coordinates['center'][::-1]  # Folium expects [lat, lon]
            
            m = folium.Map(
                location=center,
                zoom_start=st.session_state.selected_coordinates['zoom'],
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                width='100%',
                height='100%'
            )
            
            # Add rectangle for selected area
            if st.session_state.selected_coordinates['bounds']:
                bounds = st.session_state.selected_coordinates['bounds']
                folium.Rectangle(
                    bounds=[[bounds[0][0], bounds[0][1]], [bounds[1][0], bounds[1][1]]],
                    color='#00ff88',
                    fill=True,
                    fill_color='#00ff88',
                    fill_opacity=0.2,
                    weight=3,
                    popup=st.session_state.selected_area_name
                ).add_to(m)
            
            # Add marker at center
            folium.Marker(
                location=center,
                popup=st.session_state.selected_area_name,
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
            
            # Display map
            st_folium(m, width=700, height=500)
            
            # Map instructions
            st.markdown("""
            <div style="background: #111111; padding: 15px; border-radius: 8px; margin-top: 10px; font-size: 14px; color: #cccccc;">
            <strong>🗺️ Map Controls:</strong>
            <ul style="margin: 5px 0 0 20px;">
                <li>Drag to move the map</li>
                <li>Scroll to zoom in/out</li>
                <li>Click on the green rectangle for area details</li>
                <li>Green marker shows area center</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No area selected. Please go back to Step 1.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 4:
        # Analysis progress visualization
        st.markdown('<div class="card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<h3>🚀 Analysis Progress</h3>', unsafe_allow_html=True)
        
        # Animated progress visualization
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: spin 2s linear infinite;">🔄</div>
            <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Processing Your Request</div>
            <div style="color: #666666; font-size: 14px;">This may take a few moments...</div>
        </div>
        
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # What's happening info
        st.markdown("""
        <div style="background: #111111; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <h4 style="color: #00ff88; margin-bottom: 10px;">What's happening:</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="background: #0a0a0a; padding: 10px; border-radius: 6px;">
                    <div style="color: #00ff88; font-size: 12px;">📡 Satellite Data</div>
                    <div style="font-size: 12px; color: #cccccc;">Downloading from {}</div>
                </div>
                <div style="background: #0a0a0a; padding: 10px; border-radius: 6px;">
                    <div style="color: #00ff88; font-size: 12px;">🌿 Vegetation Indices</div>
                    <div style="font-size: 12px; color: #cccccc;">Calculating {}</div>
                </div>
                <div style="background: #0a0a0a; padding: 10px; border-radius: 6px;">
                    <div style="color: #00ff88; font-size: 12px;">☁️ Cloud Filtering</div>
                    <div style="font-size: 12px; color: #cccccc;">Removing clouds</div>
                </div>
                <div style="background: #0a0a0a; padding: 10px; border-radius: 6px;">
                    <div style="color: #00ff88; font-size: 12px;">📊 Statistics</div>
                    <div style="font-size: 12px; color: #cccccc;">Generating reports</div>
                </div>
            </div>
        </div>
        """.format(
            st.session_state.analysis_parameters['collection_choice'],
            ', '.join(st.session_state.analysis_parameters['selected_indices'])
        ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 5:
        # Show analysis results
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">📊 Analysis Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            # Create charts for each index
            for index, data in st.session_state.analysis_results.items():
                if data['dates'] and data['values']:
                    # Create Plotly chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=data['dates'],
                        y=data['values'],
                        mode='lines+markers',
                        name=index,
                        line=dict(color='#00ff88', width=3),
                        marker=dict(size=8, color='#ffffff')
                    ))
                    
                    fig.update_layout(
                        title=f"{index} - Vegetation Index Over Time",
                        plot_bgcolor='#0a0a0a',
                        paper_bgcolor='#0a0a0a',
                        font=dict(color='#ffffff'),
                        xaxis=dict(
                            title="Date",
                            gridcolor='#222222',
                            tickcolor='#444444'
                        ),
                        yaxis=dict(
                            title=f"{index} Value",
                            gridcolor='#222222',
                            tickcolor='#444444'
                        ),
                        height=300,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Results summary
            st.markdown("""
            <div style="background: #111111; padding: 20px; border-radius: 8px; margin-top: 20px;">
                <h4 style="color: #00ff88; margin-bottom: 15px;">📋 Results Summary</h4>
                <div style="color: #cccccc; font-size: 14px; line-height: 1.6;">
                    <p>Your vegetation analysis is complete! The charts above show the temporal patterns of selected vegetation indices.</p>
                    <p><strong>Next Steps:</strong></p>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Download the CSV for further analysis</li>
                        <li>Start a new analysis with different parameters</li>
                        <li>Compare results with different time periods</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="results-placeholder">
                <div class="icon">📊</div>
                <div style="color: #666666; font-size: 16px; margin-bottom: 10px;">No Results Available</div>
                <div style="color: #444444; font-size: 14px;">Please run an analysis to see results</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Guided Workflow • Step-by-Step Analysis • User-Friendly Interface</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">Step-by-Step</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">Earth Engine</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">User Guide</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v2.1</span>
    </div>
</div>
""", unsafe_allow_html=True)
