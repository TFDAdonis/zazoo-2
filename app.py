import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback

# Custom CSS for Mobile Compatibility
st.markdown("""
<style>
    /* Base mobile styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stApp {
        background: #000000;
        color: #ffffff;
        padding: 0 !important;
        margin: 0 !important;
        overflow-x: hidden;
    }
    
    /* Remove all Streamlit padding and margins */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    /* Mobile viewport */
    .mobile-viewport {
        width: 100vw;
        height: 100vh;
        position: relative;
        overflow: hidden;
    }
    
    /* Full-screen map container */
    .map-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
    }
    
    /* Floating control panel (Google Earth style) */
    .floating-panel {
        position: absolute;
        bottom: 20px;
        left: 15px;
        right: 15px;
        z-index: 1000;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        display: none; /* Hidden by default, shown when needed */
    }
    
    .panel-visible {
        display: block !important;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Panel header */
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .panel-title {
        font-size: 18px;
        font-weight: 600;
        color: #00ff88;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .close-panel {
        background: none;
        border: none;
        color: #ffffff;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Tab navigation */
    .panel-tabs {
        display: flex;
        gap: 5px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 4px;
    }
    
    .tab-button {
        flex: 1;
        padding: 10px;
        text-align: center;
        background: none;
        border: none;
        color: #999;
        font-size: 13px;
        font-weight: 500;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tab-button.active {
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        color: #000;
        font-weight: 600;
    }
    
    /* Panel content */
    .panel-content {
        max-height: 60vh;
        overflow-y: auto;
        padding-right: 5px;
    }
    
    /* Mobile form elements */
    .mobile-select {
        width: 100%;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px 15px;
        color: white;
        font-size: 14px;
        margin-bottom: 10px;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
    }
    
    .mobile-select option {
        background: #000000;
        color: white;
    }
    
    .mobile-input {
        width: 100%;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px 15px;
        color: white;
        font-size: 14px;
        margin-bottom: 10px;
    }
    
    .mobile-button {
        width: 100%;
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        border: none;
        border-radius: 10px;
        padding: 15px;
        color: #000;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 10px;
        transition: transform 0.2s;
    }
    
    .mobile-button:active {
        transform: scale(0.98);
    }
    
    .mobile-button.secondary {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    /* Mobile slider */
    .mobile-slider {
        width: 100%;
        height: 40px;
        margin: 10px 0;
    }
    
    /* Checkbox group for indices */
    .checkbox-group {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin: 15px 0;
    }
    
    .checkbox-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        padding: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
    }
    
    /* Mobile charts */
    .mobile-chart {
        width: 100%;
        height: 200px;
        margin: 10px 0;
    }
    
    /* Info chips */
    .info-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px;
    }
    
    /* Top floating buttons */
    .top-controls {
        position: absolute;
        top: 20px;
        left: 15px;
        right: 15px;
        z-index: 1001;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .app-title {
        font-size: 20px;
        font-weight: 700;
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .floating-button {
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        cursor: pointer;
    }
    
    .floating-button.active {
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        color: #000;
    }
    
    /* Results panel */
    .results-panel {
        position: absolute;
        top: 80px;
        left: 15px;
        right: 15px;
        z-index: 999;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        max-height: 70vh;
        overflow-y: auto;
        display: none;
    }
    
    .results-visible {
        display: block !important;
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        display: none;
    }
    
    .loading-overlay.visible {
        display: flex;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top: 3px solid #00ff88;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Mobile swipe indicator */
    .swipe-indicator {
        position: absolute;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        font-size: 12px;
        z-index: 999;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .swipe-arrow {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Hide all Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Touch-friendly scrollbars */
    .panel-content::-webkit-scrollbar {
        width: 5px;
    }
    
    .panel-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .panel-content::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 136, 0.5);
        border-radius: 10px;
    }
</style>

<script>
// JavaScript for mobile interactions
document.addEventListener('DOMContentLoaded', function() {
    // Detect touch device
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isTouchDevice) {
        // Add touch-specific optimizations
        document.body.classList.add('touch-device');
        
        // Prevent zoom on double-tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
    
    // Handle panel visibility
    window.togglePanel = function(panelId) {
        const panel = document.getElementById(panelId);
        panel.classList.toggle('panel-visible');
    };
    
    // Handle tab switching
    window.switchTab = function(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.includes(tabName)) {
                btn.classList.add('active');
            }
        });
        
        // Show corresponding content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(tabName + '-content').style.display = 'block';
    };
    
    // Initialize first tab as active
    setTimeout(() => {
        if (document.querySelector('.tab-button')) {
            document.querySelector('.tab-button').click();
        }
    }, 100);
});
</script>
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
if 'current_panel' not in st.session_state:
    st.session_state.current_panel = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'select'

# Page configuration
st.set_page_config(
    page_title="Khisba GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
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

# Main Mobile Interface
st.markdown("""
<div class="mobile-viewport">
    <!-- Top Controls -->
    <div class="top-controls">
        <div class="app-title">🌍 KHISBA GIS</div>
        <div style="display: flex; gap: 8px;">
            <button class="floating-button" onclick="togglePanel('main-panel')">
                📍
            </button>
            <button class="floating-button" onclick="togglePanel('results-panel')">
                📊
            </button>
        </div>
    </div>
    
    <!-- Main Map -->
    <div class="map-container" id="map-container">
""", unsafe_allow_html=True)

# Generate Mapbox HTML for Mobile
if st.session_state.selected_coordinates:
    map_center = st.session_state.selected_coordinates['center']
    map_zoom = st.session_state.selected_coordinates['zoom']
    bounds_data = st.session_state.selected_coordinates['bounds']
else:
    map_center = [0, 20]
    map_zoom = 2
    bounds_data = None

mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KHISBA GIS Mobile</title>
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
    <style>
        #mobile-map {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }}
        .mapboxgl-popup {{
            max-width: 250px;
        }}
        .mapboxgl-popup-content {{
            background: rgba(0, 0, 0, 0.9);
            color: white;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
        }}
        .mapboxgl-popup-content h3 {{
            color: #00ff88;
            margin: 0 0 10px 0;
            font-size: 16px;
        }}
        .mapboxgl-popup-content p {{
            margin: 0;
            color: #cccccc;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="mobile-map"></div>
    
    <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
        
        // Mobile-optimized map with touch gestures
        const map = new mapboxgl.Map({{
            container: 'mobile-map',
            style: 'mapbox://styles/mapbox/satellite-streets-v12',
            center: {map_center},
            zoom: {map_zoom},
            pitch: 45,
            bearing: 0,
            interactive: true,
            touchZoomRotate: true,
            dragPan: true,
            scrollZoom: true,
            doubleClickZoom: true,
            keyboard: false,
            boxZoom: false
        }});
        
        // Disable rotation on mobile for better UX
        map.touchZoomRotate.disableRotation();
        
        // Add minimal controls
        map.addControl(new mapboxgl.NavigationControl({{
            showCompass: false,
            showZoom: true
        }}), 'top-right');
        
        map.on('load', () => {{
            // Add selected area if available
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
                        'fill-opacity': 0.2
                    }}
                }});
                
                map.addLayer({{
                    'id': 'selected-area-border',
                    'type': 'line',
                    'source': 'selected-area',
                    'paint': {{
                        'line-color': '#00ff88',
                        'line-width': 3,
                        'line-opacity': 0.8
                    }}
                }});
                
                // Fly to area
                map.flyTo({{
                    center: {map_center},
                    zoom: {map_zoom},
                    duration: 1500
                }});
            }}
            ''' if bounds_data else ''}
            
            // Add tap interaction
            map.on('click', (e) => {{
                // Send coordinates to Streamlit
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'map_click',
                        coordinates: e.lngLat.toArray()
                    }}, '*');
                }}
            }});
        }});
        
        // Handle window resize for mobile
        window.addEventListener('resize', () => {{
            map.resize();
        }});
    </script>
</body>
</html>
"""

st.components.v1.html(mapbox_html, height=600)

st.markdown("""
    </div>
    
    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loading-overlay">
        <div class="spinner"></div>
        <div id="loading-text">Initializing...</div>
    </div>
    
    <!-- Main Control Panel -->
    <div class="floating-panel" id="main-panel">
        <div class="panel-header">
            <div class="panel-title">📍 Area Selection</div>
            <button class="close-panel" onclick="togglePanel('main-panel')">×</button>
        </div>
        
        <div class="panel-tabs">
            <button class="tab-button active" onclick="switchTab('select')">Select Area</button>
            <button class="tab-button" onclick="switchTab('analyze')">Analysis</button>
            <button class="tab-button" onclick="switchTab('settings')">Settings</button>
        </div>
        
        <div class="panel-content">
""", unsafe_allow_html=True)

# TAB 1: Area Selection
st.markdown('<div id="select-content" class="tab-content">', unsafe_allow_html=True)

if st.session_state.ee_initialized:
    try:
        # Get countries
        countries_fc = get_admin_boundaries(0)
        if countries_fc:
            country_names = get_boundary_names(countries_fc, 0)
            
            # Country selection
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_country = st.selectbox(
                    "Country",
                    options=["Select a country"] + country_names,
                    index=0,
                    help="Choose a country for analysis",
                    key="mobile_country_select"
                )
            
            with col2:
                if selected_country != "Select a country":
                    st.markdown(f'<div class="info-chip">✓</div>', unsafe_allow_html=True)
            
            if selected_country and selected_country != "Select a country":
                # Get country code
                country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                
                # Get admin1 regions
                admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                if admin1_fc:
                    admin1_names = get_boundary_names(admin1_fc, 1)
                    
                    # Admin1 selection
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        selected_admin1 = st.selectbox(
                            "State/Province",
                            options=["Select state/province"] + admin1_names,
                            index=0,
                            help="Choose a state or province",
                            key="mobile_admin1_select"
                        )
                    
                    with col2:
                        if selected_admin1 != "Select state/province":
                            st.markdown(f'<div class="info-chip">✓</div>', unsafe_allow_html=True)
                    
                    if selected_admin1 and selected_admin1 != "Select state/province":
                        # Get admin1 code
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                        
                        # Get admin2 regions
                        admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                        if admin2_fc:
                            admin2_names = get_boundary_names(admin2_fc, 2)
                            
                            # Admin2 selection
                            selected_admin2 = st.selectbox(
                                "Municipality",
                                options=["Select municipality"] + admin2_names,
                                index=0,
                                help="Choose a municipality",
                                key="mobile_admin2_select"
                            )
                            
                            # Update selected area
                            if selected_admin2 and selected_admin2 != "Select municipality":
                                geometry = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', selected_admin2))
                                area_name = f"{selected_admin2}, {selected_admin1}"
                                area_level = "Municipality"
                            else:
                                geometry = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1))
                                area_name = f"{selected_admin1}"
                                area_level = "State/Province"
                        else:
                            geometry = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1))
                            area_name = f"{selected_admin1}"
                            area_level = "State/Province"
                    else:
                        geometry = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country))
                        area_name = selected_country
                        area_level = "Country"
                else:
                    geometry = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country))
                    area_name = selected_country
                    area_level = "Country"
                
                # Store in session state
                coords_info = get_geometry_coordinates(geometry)
                st.session_state.selected_geometry = geometry
                st.session_state.selected_coordinates = coords_info
                st.session_state.selected_area_name = area_name
                st.session_state.selected_area_level = area_level
                
                # Show selected area info
                st.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 10px; margin: 10px 0;">
                    <div style="color: #00ff88; font-weight: 600; font-size: 14px;">Selected Area</div>
                    <div style="color: white; font-size: 13px;">{area_name}</div>
                    <div style="color: #999; font-size: 12px;">Level: {area_level}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick action button
                if st.button("✅ Use This Area", type="primary", use_container_width=True):
                    st.success(f"Area selected: {area_name}")
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading boundaries: {str(e)}")
else:
    st.warning("Earth Engine not initialized. Please check connection.")

st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Analysis Settings
st.markdown('<div id="analyze-content" class="tab-content" style="display: none;">', unsafe_allow_html=True)

if st.session_state.selected_area_name:
    st.markdown(f"""
    <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 10px; margin-bottom: 15px;">
        <div style="color: #00ff88; font-weight: 600; font-size: 13px;">📍 Analyzing:</div>
        <div style="color: white; font-size: 14px; font-weight: 500;">{st.session_state.selected_area_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2023, 1, 1),
            help="Start date for analysis",
            key="mobile_start_date"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2023, 12, 31),
            help="End date for analysis",
            key="mobile_end_date"
        )
    
    # Satellite source
    collection_choice = st.selectbox(
        "Satellite Source",
        options=["Sentinel-2", "Landsat-8"],
        help="Choose satellite collection",
        key="mobile_satellite_select"
    )
    
    # Cloud cover
    cloud_cover = st.slider(
        "Max Cloud Cover (%)",
        min_value=0,
        max_value=100,
        value=20,
        help="Maximum cloud cover percentage",
        key="mobile_cloud_slider"
    )
    
    # Vegetation indices
    st.markdown('<div style="margin: 15px 0 10px 0; color: #00ff88; font-weight: 600; font-size: 14px;">Vegetation Indices</div>', unsafe_allow_html=True)
    
    # Popular indices for mobile
    popular_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI', 'ARVI', 'VARI']
    
    selected_indices = st.multiselect(
        "Select indices (tap to select)",
        options=popular_indices,
        default=['NDVI', 'EVI'],
        help="Choose vegetation indices to analyze",
        key="mobile_indices_select"
    )
    
    # Run analysis button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True, key="mobile_run_analysis"):
        if not selected_indices:
            st.error("Please select at least one vegetation index")
        else:
            # Show loading
            st.markdown("""
            <script>
                document.getElementById('loading-overlay').classList.add('visible');
                document.getElementById('loading-text').textContent = 'Running analysis...';
            </script>
            """, unsafe_allow_html=True)
            
            # Run analysis
            with st.spinner("Analyzing vegetation indices..."):
                try:
                    # Simplified analysis (same as before but adapted for mobile)
                    if collection_choice == "Sentinel-2":
                        collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                    else:
                        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                    
                    filtered_collection = (collection
                        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                        .filterBounds(st.session_state.selected_geometry.geometry())
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                    )
                    
                    # Calculate indices
                    results = {}
                    for index in selected_indices:
                        # Simplified calculation
                        def calculate_index(image):
                            if index == 'NDVI':
                                nir = image.select('B8' if collection_choice == 'Sentinel-2' else 'B5')
                                red = image.select('B4' if collection_choice == 'Sentinel-2' else 'B4')
                                return nir.subtract(red).divide(nir.add(red))
                            elif index == 'EVI':
                                nir = image.select('B8' if collection_choice == 'Sentinel-2' else 'B5')
                                red = image.select('B4' if collection_choice == 'Sentinel-2' else 'B4')
                                blue = image.select('B2' if collection_choice == 'Sentinel-2' else 'B2')
                                return nir.subtract(red).multiply(2.5).divide(
                                    nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
                                )
                            # Add other indices as needed
                            return None
                        
                        time_series = filtered_collection.map(lambda img: ee.Feature(None, {
                            'date': img.date().format(),
                            'value': calculate_index(img)
                        }))
                        
                        time_series_list = time_series.getInfo()
                        
                        dates = []
                        values = []
                        
                        if 'features' in time_series_list:
                            for feature in time_series_list['features']:
                                props = feature['properties']
                                if 'value' in props and props['value'] is not None and 'date' in props:
                                    dates.append(props['date'])
                                    values.append(props['value'])
                        
                        results[index] = {'dates': dates, 'values': values}
                    
                    st.session_state.analysis_results = results
                    
                    # Hide loading and show results
                    st.markdown("""
                    <script>
                        document.getElementById('loading-overlay').classList.remove('visible');
                        togglePanel('results-panel');
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.success("Analysis completed! View results in the Results panel.")
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.markdown("""
                    <script>
                        document.getElementById('loading-overlay').classList.remove('visible');
                    </script>
                    """, unsafe_allow_html=True)
else:
    st.info("Please select an area first in the 'Select Area' tab.")

st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: Settings
st.markdown('<div id="settings-content" class="tab-content" style="display: none;">', unsafe_allow_html=True)

st.markdown('<div style="color: #00ff88; font-weight: 600; margin-bottom: 15px;">App Settings</div>', unsafe_allow_html=True)

# Map style
map_style = st.selectbox(
    "Map Style",
    options=["Satellite", "Street", "Outdoors", "Dark", "Light"],
    index=0,
    key="mobile_map_style"
)

# Analysis parameters
st.markdown('<div style="margin-top: 20px; color: #00ff88; font-weight: 600;">Analysis Parameters</div>', unsafe_allow_html=True)

analysis_scale = st.slider(
    "Analysis Scale (meters)",
    min_value=10,
    max_value=1000,
    value=30,
    step=10,
    key="mobile_analysis_scale"
)

cache_results = st.checkbox("Cache analysis results", value=True, key="mobile_cache")

# App info
st.markdown("""
<div style="margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 10px;">
    <div style="color: #00ff88; font-weight: 600; margin-bottom: 10px;">App Information</div>
    <div style="color: #999; font-size: 12px; line-height: 1.5;">
        <strong>KHISBA GIS Mobile v2.0</strong><br>
        Interactive Vegetation Analysis<br>
        Earth Engine + Mapbox + Streamlit<br>
        Optimized for mobile devices
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Clear Cache & Reset", type="secondary", use_container_width=True):
    st.session_state.analysis_results = None
    st.session_state.selected_geometry = None
    st.success("Cache cleared!")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
    
    <!-- Results Panel -->
    <div class="results-panel" id="results-panel">
        <div class="panel-header">
            <div class="panel-title">📊 Analysis Results</div>
            <button class="close-panel" onclick="togglePanel('results-panel')">×</button>
        </div>
        
        <div class="panel-content" id="results-content">
""", unsafe_allow_html=True)

# Display Results
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Summary
    st.markdown(f"""
    <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 10px; margin-bottom: 15px;">
        <div style="color: #00ff88; font-weight: 600; font-size: 13px;">📈 Analysis Complete</div>
        <div style="color: white; font-size: 14px;">{st.session_state.selected_area_name}</div>
        <div style="color: #999; font-size: 12px;">{len(results)} indices analyzed</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    for index, data in results.items():
        if data['dates'] and data['values']:
            try:
                # Create mini chart for mobile
                dates = data['dates'][:10]  # Limit for mobile
                values = data['values'][:10]
                
                if dates and values:
                    # Simple text-based chart
                    avg_value = sum(values) / len(values) if values else 0
                    max_value = max(values) if values else 0
                    min_value = min(values) if values else 0
                    
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="color: #00ff88; font-weight: 600; font-size: 14px;">{index}</div>
                            <div style="color: white; font-weight: 600; font-size: 16px;">{avg_value:.4f}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #999; font-size: 11px;">
                            <div>Min: {min_value:.4f}</div>
                            <div>Max: {max_value:.4f}</div>
                            <div>Points: {len(values)}</div>
                        </div>
                        <div style="margin-top: 10px;">
                            <div style="background: rgba(255, 255, 255, 0.1); height: 4px; border-radius: 2px;">
                                <div style="background: #00ff88; height: 100%; width: 50%; border-radius: 2px;"></div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                pass
    
    # Export options
    st.markdown("""
    <div style="margin-top: 20px;">
        <div style="color: #00ff88; font-weight: 600; margin-bottom: 10px; font-size: 14px;">Export Results</div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <button class="mobile-button secondary" onclick="alert('CSV export coming soon!')">📥 CSV</button>
            <button class="mobile-button secondary" onclick="alert('Chart export coming soon!')">📈 Chart</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No analysis results yet. Run an analysis first!")

st.markdown("""
        </div>
    </div>
    
    <!-- Swipe Indicator -->
    <div class="swipe-indicator" id="swipe-indicator">
        <div class="swipe-arrow">↑</div>
        <div>Swipe up for controls</div>
    </div>
</div>

<script>
// Show swipe indicator on first load
setTimeout(() => {
    if (!localStorage.getItem('khisba_mobile_shown')) {
        document.getElementById('swipe-indicator').style.display = 'flex';
        localStorage.setItem('khisba_mobile_shown', 'true');
        setTimeout(() => {
            document.getElementById('swipe-indicator').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('swipe-indicator').style.display = 'none';
            }, 1000);
        }, 3000);
    }
}, 1000);

// Handle tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Show selected tab content
    document.getElementById(tabName + '-content').style.display = 'block';
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Activate corresponding button
    document.querySelectorAll('.tab-button').forEach(btn => {
        if (btn.textContent.includes(tabName.charAt(0).toUpperCase() + tabName.slice(1))) {
            btn.classList.add('active');
        }
    });
}

// Handle panel toggling
function togglePanel(panelId) {
    const panel = document.getElementById(panelId);
    panel.classList.toggle('panel-visible');
    
    // Hide other panels
    if (panelId === 'main-panel') {
        document.getElementById('results-panel').classList.remove('panel-visible');
    } else if (panelId === 'results-panel') {
        document.getElementById('main-panel').classList.remove('panel-visible');
    }
}
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="position: fixed; bottom: 5px; left: 0; right: 0; text-align: center; color: #666; font-size: 10px; z-index: 1000;">
    KHISBA GIS Mobile • Touch-optimized • v2.0
</div>
""", unsafe_allow_html=True)
