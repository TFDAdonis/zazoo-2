import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ee
import traceback
from io import StringIO

# Custom CSS for Clean Green & Black TypeScript/React Style
st.markdown("""
<style>
    /* Base styling */
    .stApp {
        background: #000000;
        color: #ffffff;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove Streamlit default padding */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
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
    
    /* Layout Container */
    .main-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin: 0 auto;
    }
    
    @media (min-width: 768px) {
        .main-container {
            flex-direction: row;
        }
    }
    
    .sidebar-container {
        flex: 0 0 320px;
        min-width: 0;
    }
    
    .content-container {
        flex: 1;
        min-width: 0;
    }
    
    /* Cards */
    .card {
        background: var(--card-black);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: var(--primary-green);
    }
    
    .card-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-gray);
    }
    
    .card-title .icon {
        width: 28px;
        height: 28px;
        background: rgba(0, 255, 136, 0.1);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-green);
        font-size: 14px;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, var(--primary-green), var(--accent-green));
        color: var(--primary-black) !important;
        border: none;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        margin: 4px 0;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stMultiSelect > div > div {
        background: var(--secondary-black) !important;
        border: 1px solid var(--border-gray) !important;
        color: var(--text-white) !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
        font-size: 13px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--primary-green) !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2) !important;
    }
    
    /* Map container */
    .map-container {
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        overflow: hidden;
        height: 500px;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        background: rgba(0, 255, 136, 0.1);
        color: var(--primary-green);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin: 2px;
    }
    
    /* View toggle */
    .view-toggle {
        display: flex;
        background: var(--card-black);
        border-radius: 6px;
        padding: 3px;
        border: 1px solid var(--border-gray);
        margin-bottom: 12px;
    }
    
    .view-option {
        flex: 1;
        padding: 6px 10px;
        text-align: center;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
        border-radius: 4px;
        transition: all 0.2s;
        color: var(--text-gray);
    }
    
    .view-option.active {
        background: var(--primary-green);
        color: var(--primary-black);
    }
    
    /* Charts */
    .js-plotly-plot .plotly {
        border-radius: 8px;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .sidebar-container, .content-container {
            flex: 1 0 100%;
        }
        
        .map-container {
            height: 400px;
        }
        
        .card {
            padding: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Earth Engine Auto-Authentication with Service Account
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

# Try to auto-initialize Earth Engine on app start
if 'ee_auto_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_auto_initialized = True
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_auto_initialized = False
            st.session_state.ee_initialized = False

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None
if 'selected_area_level' not in st.session_state:
    st.session_state.selected_area_level = None

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper Functions for Earth Engine
def get_admin_boundaries(level, country_code=None, admin1_code=None):
    """Get administrative boundaries from Earth Engine"""
    try:
        if level == 0:
            return ee.FeatureCollection("FAO/GAUL/2015/level0")
        elif level == 1:
            admin1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
            if country_code:
                return admin1.filter(ee.Filter.eq('ADM0_CODE', country_code))
            return admin1
        elif level == 2:
            admin2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
            if admin1_code:
                return admin2.filter(ee.Filter.eq('ADM1_CODE', admin1_code))
            elif country_code:
                return admin2.filter(ee.Filter.eq('ADM0_CODE', country_code))
            return admin2
    except Exception as e:
        st.error(f"Error loading boundaries: {str(e)}")
        return None

def get_boundary_names(feature_collection, level):
    """Extract boundary names from Earth Engine FeatureCollection"""
    try:
        if level == 0:
            names = feature_collection.aggregate_array('ADM0_NAME').distinct()
        elif level == 1:
            names = feature_collection.aggregate_array('ADM1_NAME').distinct()
        elif level == 2:
            names = feature_collection.aggregate_array('ADM2_NAME').distinct()
        else:
            return []
        
        names_list = names.getInfo()
        if names_list:
            return sorted(names_list)
        return []
        
    except Exception as e:
        st.error(f"Error extracting names: {str(e)}")
        return []

def get_geometry_coordinates(geometry):
    """Get center coordinates and bounds from geometry"""
    try:
        bounds = geometry.geometry().bounds().getInfo()
        coords = bounds['coordinates'][0]
        lats = [coord[1] for coord in coords]
        lons = [coord[0] for coord in coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)
        
        return {
            'center': [center_lon, center_lat],
            'bounds': [[min_lat, min_lon], [max_lat, max_lon]],
            'zoom': 6
        }
    except Exception as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return {'center': [0, 20], 'bounds': None, 'zoom': 2}

def simple_add_indices(image):
    """Simplified vegetation indices calculation"""
    # For Sentinel-2
    try:
        nir = image.select('B8')
        red = image.select('B4')
        green = image.select('B3')
        blue = image.select('B2')
        
        # Calculate basic indices
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        evi = nir.subtract(red).multiply(2.5).divide(
            nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
        ).rename('EVI')
        savi = nir.subtract(red).multiply(1.5).divide(
            nir.add(red).add(0.5)
        ).rename('SAVI')
        ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
        
        return image.addBands([ndvi, evi, savi, ndwi])
    except:
        # For Landsat
        nir = image.select('B5')
        red = image.select('B4')
        green = image.select('B3')
        blue = image.select('B2')
        
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        evi = nir.subtract(red).multiply(2.5).divide(
            nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
        ).rename('EVI')
        savi = nir.subtract(red).multiply(1.5).divide(
            nir.add(red).add(0.5)
        ).rename('SAVI')
        ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
        
        return image.addBands([ndvi, evi, savi, ndwi])

# Main Dashboard Layout
st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <h1 style="margin: 0;">🌍 KHISBA GIS</h1>
            <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="status-badge">Connected</span>
            <span class="status-badge">3D Mapbox Globe</span>
            <span class="status-badge">v2.0</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create main layout containers
col1, col2 = st.columns([1, 2], gap="medium")

# LEFT SIDEBAR - All controls
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">🌍</div><h3 style="margin: 0;">Area Selection</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.ee_initialized:
        try:
            # Get countries
            countries_fc = get_admin_boundaries(0)
            if countries_fc:
                country_names = get_boundary_names(countries_fc, 0)
                selected_country = st.selectbox(
                    "Country",
                    options=["Select a country"] + country_names,
                    index=0,
                    help="Choose a country for analysis",
                    key="country_select"
                )
                
                if selected_country and selected_country != "Select a country":
                    # Get country code
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                    
                    # Get admin1 regions for selected country
                    admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                    if admin1_fc:
                        admin1_names = get_boundary_names(admin1_fc, 1)
                        selected_admin1 = st.selectbox(
                            "State/Province",
                            options=["Select state/province"] + admin1_names,
                            index=0,
                            help="Choose a state or province",
                            key="admin1_select"
                        )
                        
                        if selected_admin1 and selected_admin1 != "Select state/province":
                            # Get admin1 code
                            admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                            
                            # Get admin2 regions for selected admin1
                            admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                            if admin2_fc:
                                admin2_names = get_boundary_names(admin2_fc, 2)
                                selected_admin2 = st.selectbox(
                                    "Municipality",
                                    options=["Select municipality"] + admin2_names,
                                    index=0,
                                    help="Choose a municipality",
                                    key="admin2_select"
                                )
                            else:
                                selected_admin2 = None
                        else:
                            selected_admin2 = None
                    else:
                        selected_admin1 = None
                        selected_admin2 = None
                else:
                    selected_admin1 = None
                    selected_admin2 = None
            else:
                st.error("Failed to load countries. Please check Earth Engine connection.")
                selected_country = None
                selected_admin1 = None
                selected_admin2 = None
                
        except Exception as e:
            st.error(f"Error loading boundaries: {str(e)}")
            selected_country = None
            selected_admin1 = None
            selected_admin2 = None
    else:
        st.warning("Earth Engine not initialized")
        selected_country = None
        selected_admin1 = None
        selected_admin2 = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update selected geometry when area is selected
    if selected_country and selected_country != "Select a country":
        try:
            # Determine geometry
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
            
            # Get coordinates for the map
            coords_info = get_geometry_coordinates(geometry)
            
            # Store in session state
            st.session_state.selected_geometry = geometry
            st.session_state.selected_coordinates = coords_info
            st.session_state.selected_area_name = area_name
            st.session_state.selected_area_level = area_level
            
            # Show selected area info
            st.markdown(f"""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 12px; border-radius: 8px; margin-top: 10px;">
                <div style="color: #00ff88; font-weight: 600; font-size: 13px;">📍 Selected Area</div>
                <div style="color: white; font-size: 14px; margin: 5px 0;">{area_name}</div>
                <div style="color: #999; font-size: 12px;">Level: {area_level}</div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error processing geometry: {str(e)}")
    
    # Analysis Parameters Card
    if selected_country and selected_country != "Select a country":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Analysis Settings</h3></div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2023, 1, 1),
                help="Start date for analysis",
                key="start_date"
            )
        with col_b:
            end_date = st.date_input(
                "End Date",
                value=datetime(2023, 12, 31),
                help="End date for analysis",
                key="end_date"
            )
        
        collection_choice = st.selectbox(
            "Satellite Source",
            options=["Sentinel-2", "Landsat-8"],
            help="Choose satellite collection",
            key="satellite_select"
        )
        
        cloud_cover = st.slider(
            "Max Cloud Cover (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Maximum cloud cover percentage",
            key="cloud_slider"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vegetation Indices Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🌿</div><h3 style="margin: 0;">Vegetation Indices</h3></div>', unsafe_allow_html=True)
        
        available_indices = [
            'NDVI', 'ARVI', 'ATSAVI', 'DVI', 'EVI', 'EVI2', 'GNDVI', 'MSAVI', 'MSI', 'MTVI', 'MTVI2',
            'NDTI', 'NDWI', 'OSAVI', 'RDVI', 'RI', 'RVI', 'SAVI', 'TVI', 'TSAVI', 'VARI', 'VIN', 'WDRVI',
            'GCVI', 'AWEI', 'MNDWI', 'WI', 'ANDWI', 'NDSI', 'nDDI', 'NBR', 'DBSI', 'SI', 'S3', 'BRI',
            'SSI', 'NDSI_Salinity', 'SRPI', 'MCARI', 'NDCI', 'PSSRb1', 'SIPI', 'PSRI', 'Chl_red_edge', 'MARI', 'NDMI'
        ]
        
        selected_indices = st.multiselect(
            "Select Indices",
            options=available_indices,
            default=['NDVI', 'EVI', 'SAVI', 'NDWI'],
            help="Choose vegetation indices to analyze",
            key="indices_select"
        )
        
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("Select All", use_container_width=True, key="select_all"):
                st.session_state.selected_indices_all = available_indices
                st.rerun()
        with col_d:
            if st.button("Clear All", use_container_width=True, key="clear_all"):
                st.session_state.selected_indices_all = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Run Analysis Button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True, key="run_analysis"):
            if not selected_indices:
                st.error("Please select at least one vegetation index")
            else:
                with st.spinner("Running analysis..."):
                    try:
                        # Define collection based on choice
                        if collection_choice == "Sentinel-2":
                            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                        else:
                            collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                        
                        # Filter collection
                        filtered_collection = (collection
                            .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                            .filterBounds(st.session_state.selected_geometry.geometry())
                            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                            .limit(50)  # Limit for performance
                        )
                        
                        # Apply vegetation indices
                        processed_collection = filtered_collection.map(simple_add_indices)
                        
                        # Calculate time series for selected indices
                        results = {}
                        for index in selected_indices:
                            try:
                                # Get time series for this index
                                def add_date_and_reduce(image):
                                    reduced = image.select(index).reduceRegion(
                                        reducer=ee.Reducer.mean(),
                                        geometry=st.session_state.selected_geometry.geometry(),
                                        scale=100,  # Lower resolution for speed
                                        maxPixels=1e8
                                    )
                                    return ee.Feature(None, reduced.set('date', image.date().format()))
                                
                                time_series = processed_collection.map(add_date_and_reduce)
                                
                                # Get results
                                time_series_list = time_series.getInfo()
                                
                                dates = []
                                values = []
                                
                                if 'features' in time_series_list:
                                    for feature in time_series_list['features']:
                                        props = feature['properties']
                                        if index in props and props[index] is not None and 'date' in props:
                                            dates.append(props['date'])
                                            values.append(props[index])
                                
                                results[index] = {'dates': dates, 'values': values}
                                
                            except Exception as e:
                                st.warning(f"Could not calculate {index}: {str(e)}")
                                results[index] = {'dates': [], 'values': []}
                        
                        st.session_state.analysis_results = results
                        st.success("✅ Analysis completed!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.error(f"Full error: {traceback.format_exc()}")

# MAIN CONTENT AREA - 3D Mapbox Globe with Selected Area Highlight
with col2:
    # 3D Mapbox Globe
    st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
    st.markdown('<div style="padding: 15px 15px 8px 15px;"><h3 style="margin: 0;">Interactive 3D Global Map</h3></div>', unsafe_allow_html=True)
    
    # Prepare coordinates for the map
    map_center = [0, 20]
    map_zoom = 2
    bounds_data = None
    
    if st.session_state.selected_coordinates:
        map_center = st.session_state.selected_coordinates['center']
        map_zoom = st.session_state.selected_coordinates['zoom']
        bounds_data = st.session_state.selected_coordinates['bounds']
    
    # Generate HTML for Mapbox interactive globe
    mapbox_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>KHISBA GIS - 3D Global Map</title>
      <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
      <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
      <style>
        body {{ 
          margin: 0; 
          padding: 0; 
          background: #000000;
          font-family: 'Inter', sans-serif;
        }}
        #map {{ 
          width: 100%; 
          height: 100%; 
          border-radius: 8px;
        }}
        .map-container {{
          width: 100%;
          height: 450px;
          position: relative;
        }}
        .selected-area-info {{
          position: absolute;
          top: 10px;
          left: 10px;
          background: rgba(10, 10, 10, 0.9);
          color: white;
          padding: 12px;
          border-radius: 8px;
          border: 1px solid #222222;
          max-width: 250px;
          z-index: 1000;
          font-size: 12px;
        }}
        .area-title {{
          color: #00ff88;
          font-weight: 600;
          margin-bottom: 8px;
          font-size: 13px;
        }}
      </style>
    </head>
    <body>
      <div class="map-container">
        <div id="map"></div>
        {f'''
        <div class="selected-area-info">
            <div class="area-title">📍 Selected Area</div>
            <div style="color: white; font-weight: 500;">{st.session_state.selected_area_name if st.session_state.selected_area_name else 'None'}</div>
            <div style="color: #999; margin-top: 5px;">Level: {st.session_state.selected_area_level if st.session_state.selected_area_level else 'None'}</div>
        </div>
        ''' if st.session_state.selected_area_name else ''}
      </div>
      
      <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';

        // Create a new map instance
        const map = new mapboxgl.Map({{
          container: 'map',
          style: 'mapbox://styles/mapbox/satellite-streets-v12',
          center: {map_center},
          zoom: {map_zoom},
          pitch: 45,
          bearing: 0
        }});

        // Add navigation controls
        map.addControl(new mapboxgl.NavigationControl());

        // Wait for map to load
        map.on('load', () => {{
          {f'''
          if ({bounds_data}) {{
            const bounds = {bounds_data};
            
            // Create a polygon for the selected area
            map.addSource('selected-area', {{
              'type': 'geojson',
              'data': {{
                'type': 'Feature',
                'geometry': {{
                  'type': 'Polygon',
                  'coordinates': [[
                    [bounds[0][1], bounds[0][0]],
                    [bounds[1][1], bounds[0][0]],
                    [bounds[1][1], bounds[1][0]],
                    [bounds[0][1], bounds[1][0]],
                    [bounds[0][1], bounds[0][0]]
                  ]]
                }}
              }}
            }});

            // Add the polygon layer
            map.addLayer({{
              'id': 'selected-area-fill',
              'type': 'fill',
              'source': 'selected-area',
              'layout': {{}},
              'paint': {{
                'fill-color': '#00ff88',
                'fill-opacity': 0.2
              }}
            }});

            // Add border for the polygon
            map.addLayer({{
              'id': 'selected-area-border',
              'type': 'line',
              'source': 'selected-area',
              'layout': {{}},
              'paint': {{
                'line-color': '#00ff88',
                'line-width': 2,
                'line-opacity': 0.8
              }}
            }});

            // Fly to the selected area with animation
            map.flyTo({{
              center: {map_center},
              zoom: {map_zoom},
              duration: 1500,
              essential: true
            }});
          }}
          ''' if bounds_data else ''}
        }});
      </script>
    </body>
    </html>
    """
    
    # Display the Mapbox HTML
    st.components.v1.html(mapbox_html, height=450)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis Results Section
    if st.session_state.analysis_results:
        st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
        
        # Results Header
        st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><h3>Analysis Results</h3><span class="status-badge">Complete</span></div>', unsafe_allow_html=True)
        
        results = st.session_state.analysis_results
        
        # Summary Statistics
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Summary Statistics</h3></div>', unsafe_allow_html=True)
        
        summary_data = []
        for index, data in results.items():
            if data['values']:
                values = [v for v in data['values'] if v is not None]
                if values:
                    summary_data.append({
                        'Index': index,
                        'Mean': round(sum(values) / len(values), 4),
                        'Min': round(min(values), 4),
                        'Max': round(max(values), 4),
                        'Count': len(values)
                    })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts Section
        if results:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">📈</div><h3 style="margin: 0;">Vegetation Analytics</h3></div>', unsafe_allow_html=True)
            
            for index, data in results.items():
                if data['dates'] and data['values'] and len(data['dates']) > 0 and len(data['values']) > 0:
                    try:
                        # Parse dates
                        dates = []
                        for date_str in data['dates']:
                            try:
                                if 'T' in date_str:
                                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                else:
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                dates.append(date_obj)
                            except:
                                continue
                        
                        values = [v for v in data['values'] if v is not None]
                        
                        if dates and values and len(dates) == len(values):
                            df = pd.DataFrame({'Date': dates, 'Value': values})
                            df = df.sort_values('Date')
                            
                            # Create chart with professional styling
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=df['Date'], 
                                y=df['Value'],
                                mode='lines+markers',
                                name=f'{index} Index',
                                line=dict(color='#00ff88', width=2),
                                marker=dict(
                                    size=5,
                                    color='#00ff88',
                                    line=dict(width=1, color='#ffffff')
                                ),
                                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.4f}<extra></extra>'
                            ))
                            
                            # Update layout
                            fig.update_layout(
                                title=f'{index} - Vegetation Analysis',
                                plot_bgcolor='#0a0a0a',
                                paper_bgcolor='#0a0a0a',
                                font=dict(color='#ffffff', size=10),
                                xaxis=dict(
                                    gridcolor='#222222',
                                    zerolinecolor='#222222',
                                    tickcolor='#444444',
                                    title_font_color='#ffffff',
                                    tickformat='%Y-%m-%d'
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
                                    borderwidth=1,
                                    x=0.01,
                                    y=0.99
                                ),
                                hovermode='x unified',
                                height=250,
                                margin=dict(t=40, b=40, l=40, r=40)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"Error creating chart for {index}: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Export Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">💾</div><h3 style="margin: 0;">Data Export</h3></div>', unsafe_allow_html=True)
        
        if st.button("📥 Download Results as CSV", type="primary", use_container_width=True, key="export_csv"):
            export_data = []
            for index, data in results.items():
                for date, value in zip(data['dates'], data['values']):
                    if value is not None:
                        export_data.append({
                            'Date': date,
                            'Index': index,
                            'Value': value
                        })
            
            if export_data:
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name=f"vegetation_indices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_csv"
                )
            else:
                st.warning("No data available for export")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 20px 0; margin-top: 20px; border-top: 1px solid #222222;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Created by Taibi Farouk Djilali • Clean Green & Black Design</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
        <span class="status-badge">3D Mapbox</span>
        <span class="status-badge">Earth Engine</span>
        <span class="status-badge">Streamlit</span>
        <span class="status-badge">Plotly</span>
    </div>
</div>
""", unsafe_allow_html=True)
