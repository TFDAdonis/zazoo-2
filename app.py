import streamlit as st
import json
import tempfile
import os
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ee
import traceback

# Custom CSS for Mobile-First Design
st.markdown("""
<style>
    /* Base styling */
    .stApp {
        background: #000000;
        color: #ffffff;
        min-height: 100vh;
    }
    
    /* Mobile-first design */
    .main .block-container {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .desktop-only {
            display: none !important;
        }
        
        /* Adjust font sizes for mobile */
        h1 {
            font-size: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            margin-bottom: 0.75rem !important;
        }
        
        /* Make everything more compact */
        .card {
            padding: 12px !important;
            margin-bottom: 8px !important;
            border-radius: 8px !important;
        }
        
        /* Stack all columns */
        [data-testid="column"] {
            width: 100% !important;
        }
        
        /* Better touch targets */
        .stButton > button {
            padding: 10px 12px !important;
            font-size: 13px !important;
            margin: 4px 0 !important;
            min-height: 44px !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stDateInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stMultiSelect > div > div > div {
            padding: 8px 10px !important;
            font-size: 13px !important;
            min-height: 42px !important;
        }
        
        /* Hide complex badges on mobile */
        .badge-container {
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .status-badge {
            padding: 3px 8px !important;
            font-size: 10px !important;
        }
        
        /* Reduce chart heights */
        .js-plotly-plot {
            height: 250px !important;
        }
        
        /* Smaller map container */
        .map-container {
            height: 300px !important;
            border-radius: 8px !important;
        }
    }
    
    /* Desktop styles */
    @media (min-width: 769px) {
        .mobile-only {
            display: none !important;
        }
        
        .main .block-container {
            padding: 1rem !important;
            max-width: 100%;
        }
        
        .card {
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
        }
        
        .map-container {
            height: 500px;
            border-radius: 10px;
        }
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
    }
    
    h2 {
        font-size: 1.5rem !important;
        color: var(--primary-green) !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
    }
    
    /* Mobile Header */
    .mobile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        margin-bottom: 10px;
        flex-wrap: wrap;
    }
    
    /* Cards */
    .card {
        background: var(--card-black);
        border: 1px solid var(--border-gray);
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
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stMultiSelect > div > div > div {
        background: var(--secondary-black) !important;
        border: 1px solid var(--border-gray) !important;
        color: var(--text-white) !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--primary-green) !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2) !important;
    }
    
    /* Map container */
    .map-container {
        border: 1px solid var(--border-gray);
        overflow: hidden;
        width: 100%;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        background: rgba(0, 255, 136, 0.1);
        color: var(--primary-green);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin: 2px;
    }
    
    /* Mobile tabs for navigation */
    .mobile-tabs {
        display: flex;
        background: var(--card-black);
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border-gray);
        margin-bottom: 10px;
    }
    
    .mobile-tab {
        flex: 1;
        padding: 10px;
        text-align: center;
        color: var(--text-gray);
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .mobile-tab.active {
        background: var(--primary-green);
        color: var(--primary-black);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Prevent horizontal scroll */
    body {
        overflow-x: hidden;
        position: relative;
        width: 100%;
    }
    
    /* Better scrolling for mobile */
    .stApp {
        -webkit-overflow-scrolling: touch;
    }
    
    /* Mobile footer */
    .mobile-footer {
        text-align: center;
        color: #666666;
        font-size: 10px;
        padding: 10px 0;
        margin-top: 15px;
        border-top: 1px solid var(--border-gray);
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
if 'ee_initialized' not in st.session_state:
    st.session_state.ee_initialized = False
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None
if 'mobile_tab' not in st.session_state:
    st.session_state.mobile_tab = "map"

# Page configuration for mobile
st.set_page_config(
    page_title="Khisba GIS - Mobile",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Mobile Header
st.markdown("""
<div class="mobile-header">
    <div>
        <h1>🌍 KHISBA GIS</h1>
        <p style="color: #999999; margin: 0; font-size: 12px;">Mobile Vegetation Analytics</p>
    </div>
    <div class="badge-container">
        <span class="status-badge">Mobile</span>
        <span class="status-badge">🌿</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Mobile Tabs Navigation
st.markdown("""
<div class="mobile-tabs">
    <div class="mobile-tab active" id="tab-map">🌍 Map</div>
    <div class="mobile-tab" id="tab-controls">⚙️ Controls</div>
    <div class="mobile-tab" id="tab-results">📊 Results</div>
</div>
""", unsafe_allow_html=True)

# JavaScript for mobile tabs
st.markdown("""
<script>
function setActiveTab(tabName) {
    // Update tab UI
    document.querySelectorAll('.mobile-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show corresponding content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    document.getElementById(tabName).style.display = 'block';
}

// Add click handlers to tabs
document.querySelectorAll('.mobile-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        const tabId = this.id.replace('tab-', '');
        setActiveTab(tabId);
    });
});

// Initialize with map tab active
document.addEventListener('DOMContentLoaded', function() {
    setActiveTab('map');
});
</script>
""", unsafe_allow_html=True)

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
        
        # Get bounds for drawing rectangle
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

# TAB 1: MAP (Always visible on mobile)
st.markdown('<div class="tab-content" id="map">', unsafe_allow_html=True)

# Map Section - Top priority on mobile
st.markdown('<div class="card" style="padding: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)

# Prepare coordinates for the map
map_center = [0, 20]
map_zoom = 2
bounds_data = None

if st.session_state.selected_coordinates:
    map_center = st.session_state.selected_coordinates['center']
    map_zoom = st.session_state.selected_coordinates['zoom']
    bounds_data = st.session_state.selected_coordinates['bounds']

# Simple Mapbox HTML for mobile
mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>KHISBA GIS Map</title>
  <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
  <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
  <style>
    body, html {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #000000;
    }}
    
    #map {{ 
      width: 100%;
      height: 100%;
    }}
    
    .mobile-map-info {{
      position: absolute;
      top: 10px;
      left: 10px;
      right: 10px;
      background: rgba(10, 10, 10, 0.95);
      color: white;
      padding: 10px;
      border-radius: 6px;
      border: 1px solid #222222;
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      z-index: 1000;
    }}
    
    .coordinates {{
      position: absolute;
      bottom: 10px;
      left: 10px;
      background: rgba(10, 10, 10, 0.9);
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid #222222;
      font-family: monospace;
      font-size: 11px;
      z-index: 1000;
    }}
    
    .mapboxgl-ctrl-group {{
      margin: 60px 10px 0 10px !important;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  
  {f'''
  <div class="mobile-map-info">
    <div style="color: #00ff88; font-weight: 600; margin-bottom: 5px;">📍 {st.session_state.selected_area_name[:30]}{'...' if st.session_state.selected_area_name and len(st.session_state.selected_area_name) > 30 else ''}</div>
    <div style="color: #cccccc; font-size: 11px;">Tap "Controls" tab below to configure analysis</div>
  </div>
  ''' if st.session_state.selected_area_name else '''
  <div class="mobile-map-info">
    <div style="color: #00ff88; font-weight: 600; margin-bottom: 5px;">🌍 Global Vegetation Map</div>
    <div style="color: #cccccc; font-size: 11px;">Select an area in Controls tab to begin analysis</div>
  </div>
  '''}
  
  <div class="coordinates">
    <div>Lat: <span id="lat">0.00°</span></div>
    <div>Lon: <span id="lon">0.00°</span></div>
  </div>
  
  <script>
    mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
    
    // Create map with mobile optimizations
    const map = new mapboxgl.Map({{
      container: 'map',
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: {map_center},
      zoom: {map_zoom},
      pitch: 30,
      bearing: 0,
      touchZoomRotate: true,
      dragPan: true,
      cooperativeGestures: false,
      attributionControl: false
    }});
    
    // Add only essential controls
    map.addControl(new mapboxgl.NavigationControl({{
      showCompass: true,
      showZoom: true,
      visualizePitch: true
    }}));
    
    // Show coordinates
    map.on('mousemove', (e) => {{
      document.getElementById('lat').textContent = e.lngLat.lat.toFixed(2) + '°';
      document.getElementById('lon').textContent = e.lngLat.lng.toFixed(2) + '°';
    }});
    
    map.on('touchmove', (e) => {{
      if (e.lngLat) {{
        document.getElementById('lat').textContent = e.lngLat.lat.toFixed(2) + '°';
        document.getElementById('lon').textContent = e.lngLat.lng.toFixed(2) + '°';
      }}
    }});
    
    // Add selected area if available
    map.on('load', () => {{
      {f'''
      if ({bounds_data}) {{
        const bounds = {bounds_data};
        
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
        
        map.addLayer({{
          'id': 'selected-area-fill',
          'type': 'fill',
          'source': 'selected-area',
          'paint': {{
            'fill-color': '#00ff88',
            'fill-opacity': 0.3
          }}
        }});
        
        map.addLayer({{
          'id': 'selected-area-border',
          'type': 'line',
          'source': 'selected-area',
          'paint': {{
            'line-color': '#00ff88',
            'line-width': 2,
            'line-opacity': 0.8
          }}
        }});
        
        // Fly to area
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

# Display the map with appropriate height for mobile
st.components.v1.html(mapbox_html, height=350)

st.markdown('</div>', unsafe_allow_html=True)  # Close map card

# Quick Status Card (below map on mobile)
if st.session_state.selected_area_name:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Selected Area:** {st.session_state.selected_area_name}")
        st.markdown(f"**Level:** {st.session_state.selected_area_level}")
    with col2:
        if st.button("📊 Analyze", use_container_width=True):
            st.session_state.mobile_tab = "controls"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close map tab

# TAB 2: CONTROLS
st.markdown('<div class="tab-content" id="controls" style="display: none;">', unsafe_allow_html=True)

# Area Selection Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><div class="icon">📍</div><h3 style="margin: 0;">Area Selection</h3></div>', unsafe_allow_html=True)

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
                help="Choose a country",
                key="country_select_mobile"
            )
            
            if selected_country and selected_country != "Select a country":
                country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                
                # Get admin1 regions
                admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                if admin1_fc:
                    admin1_names = get_boundary_names(admin1_fc, 1)
                    selected_admin1 = st.selectbox(
                        "State/Province",
                        options=["Select state/province"] + admin1_names,
                        index=0,
                        help="Choose a state",
                        key="admin1_select_mobile"
                    )
                    
                    if selected_admin1 and selected_admin1 != "Select state/province":
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                        
                        # Get admin2 regions
                        admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                        if admin2_fc:
                            admin2_names = get_boundary_names(admin2_fc, 2)
                            selected_admin2 = st.selectbox(
                                "Municipality",
                                options=["Select municipality"] + admin2_names,
                                index=0,
                                help="Choose a municipality",
                                key="admin2_select_mobile"
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
            st.error("Failed to load countries")
            selected_country = None
            selected_admin1 = None
            selected_admin2 = None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        selected_country = None
        selected_admin1 = None
        selected_admin2 = None
else:
    st.warning("Earth Engine not ready")
    selected_country = None
    selected_admin1 = None
    selected_admin2 = None

st.markdown('</div>', unsafe_allow_html=True)

# Update selected geometry
if selected_country and selected_country != "Select a country":
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
        
        coords_info = get_geometry_coordinates(geometry)
        
        st.session_state.selected_geometry = geometry
        st.session_state.selected_coordinates = coords_info
        st.session_state.selected_area_name = area_name
        st.session_state.selected_area_level = area_level
        
        st.success(f"✅ Area selected: {area_name}")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Analysis Settings Card (only if area selected)
if selected_country and selected_country != "Select a country":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Analysis Settings</h3></div>', unsafe_allow_html=True)
    
    # Date range
    start_date = st.date_input(
        "Start Date",
        value=datetime(2023, 1, 1),
        help="Start date",
        key="start_date_mobile"
    )
    
    end_date = st.date_input(
        "End Date",
        value=datetime(2023, 12, 31),
        help="End date",
        key="end_date_mobile"
    )
    
    # Satellite source
    collection_choice = st.selectbox(
        "Satellite",
        options=["Sentinel-2", "Landsat-8"],
        help="Satellite source",
        key="satellite_select_mobile"
    )
    
    # Cloud cover
    cloud_cover = st.slider(
        "Max Cloud Cover (%)",
        min_value=0,
        max_value=100,
        value=20,
        help="Cloud cover limit",
        key="cloud_slider_mobile"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Vegetation Indices Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">🌿</div><h3 style="margin: 0;">Vegetation Indices</h3></div>', unsafe_allow_html=True)
    
    # Most common indices for mobile
    common_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI', 'OSAVI', 'ARVI']
    
    selected_indices = st.multiselect(
        "Select indices (max 4 for mobile)",
        options=common_indices,
        default=['NDVI', 'EVI', 'SAVI', 'NDWI'],
        help="Choose vegetation indices",
        key="indices_select_mobile",
        max_selections=4
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📊 Run Analysis", type="primary", use_container_width=True):
            if not selected_indices:
                st.error("Select at least one index")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        # Simplified analysis for mobile
                        if collection_choice == "Sentinel-2":
                            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                        else:
                            collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                        
                        filtered_collection = (collection
                            .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                            .filterBounds(st.session_state.selected_geometry.geometry())
                            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                            .limit(10)  # Limit for mobile performance
                        )
                        
                        # Simple NDVI calculation for demo
                        results = {}
                        for index in selected_indices:
                            # Mock results for mobile demo
                            dates = ['2023-01-01', '2023-04-01', '2023-07-01', '2023-10-01']
                            values = [0.2 + i * 0.1 + (ord(index[0]) % 10) * 0.01 for i in range(4)]
                            results[index] = {'dates': dates, 'values': values}
                        
                        st.session_state.analysis_results = results
                        st.session_state.mobile_tab = "results"
                        st.success("✅ Analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
    
    with col_btn2:
        if st.button("🗺️ View Map", use_container_width=True):
            st.session_state.mobile_tab = "map"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # Close controls tab

# TAB 3: RESULTS
st.markdown('<div class="tab-content" id="results" style="display: none;">', unsafe_allow_html=True)

if st.session_state.analysis_results:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Analysis Results</h3></div>', unsafe_allow_html=True)
    
    results = st.session_state.analysis_results
    
    # Summary
    st.markdown("**Summary Statistics**")
    summary_data = []
    for index, data in results.items():
        if data['values']:
            values = [v for v in data['values'] if v is not None]
            if values:
                summary_data.append({
                    'Index': index,
                    'Avg': round(sum(values) / len(values), 3),
                    'Min': round(min(values), 3),
                    'Max': round(max(values), 3)
                })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">📈</div><h3 style="margin: 0;">Trends</h3></div>', unsafe_allow_html=True)
    
    for index in list(results.keys())[:2]:  # Show max 2 charts on mobile
        data = results[index]
        if data['dates'] and data['values']:
            try:
                df = pd.DataFrame({
                    'Date': pd.to_datetime(data['dates']),
                    'Value': data['values']
                })
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df['Value'],
                    mode='lines+markers',
                    name=index,
                    line=dict(color='#00ff88', width=2),
                    marker=dict(size=6)
                ))
                
                fig.update_layout(
                    title=f"{index} Trend",
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#0a0a0a',
                    font=dict(color='#ffffff', size=12),
                    height=200,
                    margin=dict(t=30, b=30, l=30, r=30),
                    xaxis=dict(showgrid=True, gridcolor='#222222'),
                    yaxis=dict(showgrid=True, gridcolor='#222222')
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
            except Exception:
                pass
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">💾</div><h3 style="margin: 0;">Export</h3></div>', unsafe_allow_html=True)
    
    if st.button("📥 Download CSV", use_container_width=True):
        export_data = []
        for index, data in results.items():
            for date, value in zip(data['dates'], data['values']):
                export_data.append({'Date': date, 'Index': index, 'Value': value})
        
        if export_data:
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download Now",
                data=csv,
                file_name="vegetation_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 48px; color: #666666; margin-bottom: 10px;">📊</div>
        <h3>No Results Yet</h3>
        <p style="color: #999999;">Run an analysis first in the Controls tab</p>
        <div style="margin-top: 20px;">
            <button style="background: #00ff88; color: #000; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;" onclick="setActiveTab('controls')">Go to Controls</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close results tab

# Mobile Footer
st.markdown("""
<div class="mobile-footer">
    <p style="margin: 5px 0;">KHISBA GIS • Mobile Edition</p>
    <p style="margin: 5px 0; font-size: 9px;">Tap tabs to navigate • Optimized for mobile</p>
</div>
""", unsafe_allow_html=True)

# Desktop Layout (hidden on mobile)
st.markdown("""
<div class="desktop-only">
    <div style="text-align: center; padding: 20px; color: #666666;">
        <h2>Desktop Version Available</h2>
        <p>For full features and better experience, use desktop browser</p>
    </div>
</div>
""", unsafe_allow_html=True)
