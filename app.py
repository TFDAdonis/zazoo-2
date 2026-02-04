import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback

# Custom CSS for Map-Only Interface
st.markdown("""
<style>
    /* Hide everything except the map */
    .stApp {
        padding: 0 !important;
        margin: 0 !important;
        background: #000 !important;
        overflow: hidden !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* Full-screen map container */
    #map-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
    }
    
    /* Hide all Streamlit elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    .stApp > header {display: none !important;}
    
    /* Make Streamlit widgets invisible but functional */
    .stSelectbox, .stDateInput, .stSlider, .stButton, .stMultiSelect {
        opacity: 0;
        position: fixed;
        z-index: -9999;
        pointer-events: none;
    }
    
    /* Loading overlay */
    #loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: Arial, sans-serif;
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
    
    /* Force full viewport */
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
    }
</style>

<div id="loading-overlay">
    <div class="spinner"></div>
    <div>Loading KHISBA GIS...</div>
</div>

<script>
// Hide loading overlay when page loads
window.addEventListener('load', function() {
    setTimeout(function() {
        document.getElementById('loading-overlay').style.display = 'none';
    }, 1000);
});
</script>
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
        return False

# Initialize Earth Engine
if 'ee_auto_initialized' not in st.session_state:
    if auto_initialize_earth_engine():
        st.session_state.ee_auto_initialized = True
        st.session_state.ee_initialized = True
    else:
        st.session_state.ee_auto_initialized = False
        st.session_state.ee_initialized = False

# Initialize session state
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None
if 'countries' not in st.session_state:
    st.session_state.countries = []
if 'admin1' not in st.session_state:
    st.session_state.admin1 = []
if 'admin2' not in st.session_state:
    st.session_state.admin2 = []
if 'analysis_params' not in st.session_state:
    st.session_state.analysis_params = {
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'satellite': 'Sentinel-2',
        'cloud_cover': 20,
        'indices': ['NDVI', 'EVI']
    }

# Page configuration
st.set_page_config(
    page_title="KHISBA GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper Functions
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
        return []

# Create HTML/JavaScript interface that runs INSIDE Mapbox
mapbox_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KHISBA GIS - All-in-One Map</title>
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        body, html {
            width: 100%;
            height: 100%;
            overflow: hidden;
        }
        
        #map {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        /* KHISBA Header */
        #khisba-header {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 15px;
            max-width: 280px;
        }
        
        .app-title {
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
        }
        
        .app-subtitle {
            font-size: 12px;
            color: #999;
        }
        
        /* Control Panel - Hidden by default */
        #control-panel {
            position: absolute;
            top: 100px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 20px;
            width: 320px;
            max-height: 80vh;
            overflow-y: auto;
            display: none;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        
        .panel-title {
            color: #00ff88;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .panel-title .icon {
            width: 30px;
            height: 30px;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Tabs */
        .panel-tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 4px;
            margin-bottom: 20px;
        }
        
        .tab {
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
        
        .tab.active {
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
            font-weight: 600;
        }
        
        /* Form Elements */
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-label {
            display: block;
            color: #00ff88;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-select {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
            cursor: pointer;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3e%3cpath d='M7 10l5 5 5-5z'/%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 20px;
        }
        
        .form-select option {
            background: #000;
            color: white;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
        }
        
        .form-input:focus {
            border-color: #00ff88;
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
        }
        
        .date-row {
            display: flex;
            gap: 10px;
        }
        
        .date-row .form-group {
            flex: 1;
        }
        
        /* Slider */
        .slider-container {
            padding: 10px 0;
        }
        
        .slider-value {
            color: #00ff88;
            font-weight: 600;
            font-size: 14px;
            margin-left: 10px;
        }
        
        /* Checkbox Grid */
        .checkbox-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .checkbox-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .checkbox-item.selected {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        
        .checkbox-input {
            display: none;
        }
        
        .checkbox-label {
            color: white;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            flex: 1;
        }
        
        /* Buttons */
        .btn-primary {
            width: 100%;
            padding: 15px;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 10px;
            color: #000;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 10px;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
        }
        
        .btn-primary:active {
            transform: translateY(0);
        }
        
        .btn-secondary {
            width: 100%;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-top: 10px;
        }
        
        /* Selected Area Info */
        #selected-area-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 15px;
            max-width: 300px;
            display: none;
        }
        
        .area-title {
            color: #00ff88;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .area-name {
            color: white;
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 5px;
        }
        
        .area-details {
            color: #999;
            font-size: 12px;
            line-height: 1.4;
        }
        
        /* Results Panel */
        #results-panel {
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 20px;
            width: 350px;
            max-height: 70vh;
            overflow-y: auto;
            display: none;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        
        .chart-container {
            width: 100%;
            height: 200px;
            margin: 15px 0;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-label {
            color: #999;
            font-size: 12px;
        }
        
        .stat-value {
            color: #00ff88;
            font-weight: 600;
            font-size: 14px;
        }
        
        /* Control Buttons */
        .control-buttons {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
        }
        
        .control-btn {
            width: 45px;
            height: 45px;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .control-btn:hover {
            background: rgba(0, 255, 136, 0.1);
            transform: scale(1.1);
        }
        
        .control-btn.active {
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
        }
        
        /* Loading Overlay */
        #map-loading {
            position: absolute;
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
            color: white;
        }
        
        .map-spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid #00ff88;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        /* Notification */
        #notification {
            position: absolute;
            top: 80px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            max-width: 300px;
            display: none;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .notification-success {
            border-color: #00ff88;
        }
        
        .notification-error {
            border-color: #ff4444;
        }
        
        .notification-warning {
            border-color: #ffaa00;
        }
        
        .notification-title {
            color: #00ff88;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        /* Analysis Progress */
        #analysis-progress {
            position: absolute;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 15px;
            width: 300px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            width: 0%;
            transition: width 0.3s;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            #control-panel, #results-panel {
                width: 90%;
                left: 5%;
                right: 5%;
            }
            
            #khisba-header {
                width: 90%;
                left: 5%;
            }
            
            .control-buttons {
                top: 90px;
                right: 5%;
            }
        }
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="map-loading">
        <div class="map-spinner"></div>
        <div>Initializing KHISBA GIS...</div>
    </div>
    
    <!-- Map Container -->
    <div id="map"></div>
    
    <!-- Main Header -->
    <div id="khisba-header">
        <div class="app-title">🌍 KHISBA GIS</div>
        <div class="app-subtitle">Interactive Vegetation Analysis Platform</div>
        <div style="display: flex; gap: 5px; margin-top: 10px;">
            <span style="background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 500;">3D Mapbox</span>
            <span style="background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 500;">Earth Engine</span>
            <span style="background: rgba(0, 255, 136, 0.1); color: #00ff88; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 500;">Streamlit</span>
        </div>
    </div>
    
    <!-- Control Buttons -->
    <div class="control-buttons">
        <button class="control-btn" onclick="togglePanel('control')" title="Control Panel">⚙️</button>
        <button class="control-btn" onclick="togglePanel('results')" title="Results">📊</button>
        <button class="control-btn" onclick="togglePanel('layers')" title="Layers">🌿</button>
        <button class="control-btn" onclick="resetView()" title="Reset View">🏠</button>
    </div>
    
    <!-- Control Panel -->
    <div id="control-panel">
        <div class="panel-title">
            <div class="icon">📍</div>
            Area Selection & Analysis
        </div>
        
        <!-- Tabs -->
        <div class="panel-tabs">
            <button class="tab active" onclick="switchTab('select')">Select Area</button>
            <button class="tab" onclick="switchTab('analyze')">Analysis</button>
            <button class="tab" onclick="switchTab('export')">Export</button>
        </div>
        
        <!-- Tab Content: Select Area -->
        <div id="select-content" class="tab-content">
            <div class="form-group">
                <label class="form-label">Country</label>
                <select class="form-select" id="country-select" onchange="loadAdmin1(this.value)">
                    <option value="">Select a country</option>
                    <!-- Countries will be loaded here -->
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">State/Province</label>
                <select class="form-select" id="admin1-select" onchange="loadAdmin2(this.value)" disabled>
                    <option value="">Select state/province</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Municipality</label>
                <select class="form-select" id="admin2-select" onchange="selectArea(this.value)" disabled>
                    <option value="">Select municipality</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Or draw on map</label>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" onclick="startDrawing('polygon')">📐 Draw Polygon</button>
                    <button class="btn-secondary" onclick="startDrawing('rectangle')">⬜ Draw Rectangle</button>
                </div>
            </div>
            
            <div id="selected-area-preview" style="display: none;">
                <div style="color: #00ff88; font-size: 12px; margin: 10px 0;">Selected Area:</div>
                <div id="area-preview-name" style="color: white; font-weight: 500; margin-bottom: 10px;"></div>
            </div>
        </div>
        
        <!-- Tab Content: Analysis -->
        <div id="analyze-content" class="tab-content" style="display: none;">
            <div class="form-group">
                <label class="form-label">Time Period</label>
                <div class="date-row">
                    <div class="form-group">
                        <input type="date" class="form-input" id="start-date" value="2023-01-01">
                    </div>
                    <div class="form-group">
                        <input type="date" class="form-input" id="end-date" value="2023-12-31">
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Satellite Source</label>
                <select class="form-select" id="satellite-select">
                    <option value="sentinel2">Sentinel-2</option>
                    <option value="landsat8">Landsat-8</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Max Cloud Cover <span id="cloud-value" class="slider-value">20%</span></label>
                <div class="slider-container">
                    <input type="range" min="0" max="100" value="20" class="form-input" id="cloud-slider" 
                           style="width: 100%;" oninput="updateCloudValue(this.value)">
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Vegetation Indices</label>
                <div class="checkbox-grid" id="indices-grid">
                    <!-- Indices will be loaded here -->
                </div>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button class="btn-secondary" onclick="selectAllIndices()">Select All</button>
                    <button class="btn-secondary" onclick="clearAllIndices()">Clear All</button>
                </div>
            </div>
            
            <button class="btn-primary" onclick="runAnalysis()">🚀 Run Analysis</button>
        </div>
        
        <!-- Tab Content: Export -->
        <div id="export-content" class="tab-content" style="display: none;">
            <div style="color: #999; font-size: 13px; margin-bottom: 15px;">
                Export analysis results in various formats
            </div>
            
            <div class="form-group">
                <label class="form-label">Export Format</label>
                <select class="form-select" id="export-format">
                    <option value="csv">CSV Data</option>
                    <option value="geojson">GeoJSON</option>
                    <option value="png">Chart Image</option>
                    <option value="pdf">PDF Report</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Data Range</label>
                <select class="form-select" id="export-range">
                    <option value="full">Full Time Series</option>
                    <option value="monthly">Monthly Averages</option>
                    <option value="seasonal">Seasonal Summary</option>
                </select>
            </div>
            
            <button class="btn-primary" onclick="exportData()">📥 Download Data</button>
            <button class="btn-secondary" onclick="shareAnalysis()">🔗 Share Analysis</button>
        </div>
    </div>
    
    <!-- Selected Area Info -->
    <div id="selected-area-info">
        <div class="area-title">📍 Selected Area</div>
        <div class="area-name" id="selected-area-name">No area selected</div>
        <div class="area-details">
            <div id="selected-area-coords">Click on map or select from panel</div>
            <div id="selected-area-status" style="color: #00ff88; margin-top: 5px;">Ready for analysis</div>
        </div>
    </div>
    
    <!-- Results Panel -->
    <div id="results-panel">
        <div class="panel-title">
            <div class="icon">📊</div>
            Analysis Results
        </div>
        
        <div id="results-content">
            <div style="color: #999; font-size: 13px; margin-bottom: 15px;" id="results-message">
                Run analysis to see results
            </div>
            
            <div id="results-charts">
                <!-- Charts will be inserted here -->
            </div>
            
            <div id="results-stats">
                <!-- Statistics will be inserted here -->
            </div>
        </div>
    </div>
    
    <!-- Notification -->
    <div id="notification">
        <div class="notification-title" id="notification-title">Notification</div>
        <div id="notification-message">Message goes here</div>
    </div>
    
    <!-- Analysis Progress -->
    <div id="analysis-progress">
        <div style="color: white; font-weight: 500; margin-bottom: 5px;">Analyzing Vegetation...</div>
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
        <div style="color: #999; font-size: 12px; text-align: center;" id="progress-text">Initializing...</div>
    </div>

    <script>
        // Mapbox access token
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
        
        // Global variables
        let map;
        let selectedArea = null;
        let selectedGeometry = null;
        let analysisResults = null;
        let drawControl = null;
        
        // Initialize map
        function initMap() {
            map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/satellite-streets-v12',
                center: [0, 20],
                zoom: 2,
                pitch: 45,
                bearing: 0,
                antialias: true
            });
            
            // Add navigation controls
            map.addControl(new mapboxgl.NavigationControl({
                showCompass: true,
                showZoom: true
            }), 'top-right');
            
            map.addControl(new mapboxgl.ScaleControl({
                unit: 'metric'
            }));
            
            // Add fullscreen control
            map.addControl(new mapboxgl.FullscreenControl());
            
            // Wait for map to load
            map.on('load', () => {
                // Hide loading screen
                document.getElementById('map-loading').style.display = 'none';
                
                // Show notification
                showNotification('KHISBA GIS loaded!', 'success');
                
                // Load countries
                loadCountries();
                
                // Load vegetation indices
                loadIndices();
            });
            
            // Handle map clicks
            map.on('click', (e) => {
                // If we're in drawing mode, add point
                if (window.drawingMode) {
                    if (!window.drawnPoints) window.drawnPoints = [];
                    window.drawnPoints.push([e.lngLat.lng, e.lngLat.lat]);
                    
                    // If we have enough points for polygon (3+), draw it
                    if (window.drawnPoints.length >= 3 && window.drawingMode === 'polygon') {
                        completeDrawing();
                    }
                } else {
                    // Regular map click - show coordinates
                    updateSelectedAreaInfo('Map Click', `Lat: ${e.lngLat.lat.toFixed(4)}°, Lon: ${e.lngLat.lng.toFixed(4)}°`);
                }
            });
            
            // Handle map double click for rectangle drawing
            map.on('dblclick', (e) => {
                if (window.drawingMode === 'rectangle' && window.startPoint) {
                    const endPoint = [e.lngLat.lng, e.lngLat.lat];
                    selectRectangle(window.startPoint, endPoint);
                }
            });
        }
        
        // Load countries from Earth Engine via Streamlit
        function loadCountries() {
            // Send message to Streamlit to load countries
            window.parent.postMessage({
                type: 'load_countries'
            }, '*');
            
            // Show loading in country select
            const countrySelect = document.getElementById('country-select');
            countrySelect.innerHTML = '<option value="">Loading countries...</option>';
        }
        
        // Load admin1 regions
        function loadAdmin1(countryName) {
            if (!countryName) return;
            
            const admin1Select = document.getElementById('admin1-select');
            admin1Select.disabled = true;
            admin1Select.innerHTML = '<option value="">Loading...</option>';
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'load_admin1',
                country: countryName
            }, '*');
        }
        
        // Load admin2 regions
        function loadAdmin2(admin1Name) {
            if (!admin1Name) return;
            
            const admin2Select = document.getElementById('admin2-select');
            admin2Select.disabled = true;
            admin2Select.innerHTML = '<option value="">Loading...</option>';
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'load_admin2',
                admin1: admin1Name,
                country: document.getElementById('country-select').value
            }, '*');
        }
        
        // Select area
        function selectArea(areaName) {
            if (!areaName) return;
            
            const country = document.getElementById('country-select').value;
            const admin1 = document.getElementById('admin1-select').value;
            
            let fullName = areaName;
            if (admin1) fullName = `${areaName}, ${admin1}`;
            if (country) fullName = `${fullName}, ${country}`;
            
            // Send to Streamlit to get geometry
            window.parent.postMessage({
                type: 'select_area',
                areaName: fullName,
                level: areaName === admin1 ? 'admin1' : 'admin2'
            }, '*');
            
            // Update UI
            updateSelectedAreaInfo(fullName, 'Loading geometry...');
            showSelectedAreaPreview(fullName);
        }
        
        // Start drawing on map
        function startDrawing(mode) {
            window.drawingMode = mode;
            window.drawnPoints = [];
            window.startPoint = null;
            
            showNotification(`Click on map to draw ${mode === 'polygon' ? 'polygon points' : 'rectangle corners'}`, 'warning');
            
            if (mode === 'rectangle') {
                map.once('click', (e) => {
                    window.startPoint = [e.lngLat.lng, e.lngLat.lat];
                    showNotification('Click second corner to complete rectangle', 'warning');
                });
            }
        }
        
        // Complete drawing
        function completeDrawing() {
            if (window.drawingMode === 'polygon' && window.drawnPoints.length >= 3) {
                // Close the polygon
                window.drawnPoints.push(window.drawnPoints[0]);
                
                // Send to Streamlit
                window.parent.postMessage({
                    type: 'select_custom_area',
                    coordinates: window.drawnPoints,
                    type: 'polygon'
                }, '*');
                
                updateSelectedAreaInfo('Custom Polygon', `${window.drawnPoints.length - 1} points`);
            }
            
            // Reset drawing
            window.drawingMode = null;
            window.drawnPoints = null;
        }
        
        // Select rectangle
        function selectRectangle(startPoint, endPoint) {
            const coordinates = [
                startPoint,
                [endPoint[0], startPoint[1]],
                endPoint,
                [startPoint[0], endPoint[1]],
                startPoint // Close the polygon
            ];
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'select_custom_area',
                coordinates: coordinates,
                type: 'rectangle'
            }, '*');
            
            updateSelectedAreaInfo('Custom Rectangle', 'Drawn on map');
            
            // Reset drawing
            window.drawingMode = null;
            window.startPoint = null;
        }
        
        // Load vegetation indices
        function loadIndices() {
            const indices = [
                'NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI', 
                'ARVI', 'VARI', 'OSAVI', 'DVI', 'RVI', 'MSI'
            ];
            
            const grid = document.getElementById('indices-grid');
            grid.innerHTML = '';
            
            indices.forEach(index => {
                const div = document.createElement('div');
                div.className = 'checkbox-item';
                div.innerHTML = `
                    <input type="checkbox" class="checkbox-input" id="index-${index}" value="${index}">
                    <label class="checkbox-label" for="index-${index}">${index}</label>
                `;
                grid.appendChild(div);
                
                // Add click handler
                div.addEventListener('click', function() {
                    const checkbox = this.querySelector('input');
                    checkbox.checked = !checkbox.checked;
                    this.classList.toggle('selected', checkbox.checked);
                });
                
                // Default select NDVI and EVI
                if (index === 'NDVI' || index === 'EVI') {
                    div.querySelector('input').checked = true;
                    div.classList.add('selected');
                }
            });
        }
        
        // Select all indices
        function selectAllIndices() {
            document.querySelectorAll('#indices-grid .checkbox-input').forEach(cb => {
                cb.checked = true;
                cb.parentElement.classList.add('selected');
            });
        }
        
        // Clear all indices
        function clearAllIndices() {
            document.querySelectorAll('#indices-grid .checkbox-input').forEach(cb => {
                cb.checked = false;
                cb.parentElement.classList.remove('selected');
            });
        }
        
        // Run analysis
        function runAnalysis() {
            // Get selected indices
            const selectedIndices = [];
            document.querySelectorAll('#indices-grid .checkbox-input:checked').forEach(cb => {
                selectedIndices.push(cb.value);
            });
            
            if (selectedIndices.length === 0) {
                showNotification('Please select at least one vegetation index', 'error');
                return;
            }
            
            if (!selectedArea) {
                showNotification('Please select an area first', 'error');
                return;
            }
            
            // Get analysis parameters
            const params = {
                startDate: document.getElementById('start-date').value,
                endDate: document.getElementById('end-date').value,
                satellite: document.getElementById('satellite-select').value,
                cloudCover: document.getElementById('cloud-slider').value,
                indices: selectedIndices
            };
            
            // Show progress
            showAnalysisProgress();
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'run_analysis',
                params: params
            }, '*');
        }
        
        // Export data
        function exportData() {
            if (!analysisResults) {
                showNotification('No analysis results to export', 'error');
                return;
            }
            
            const format = document.getElementById('export-format').value;
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'export_data',
                format: format
            }, '*');
            
            showNotification(`Exporting as ${format.toUpperCase()}...`, 'success');
        }
        
        // Share analysis
        function shareAnalysis() {
            if (!analysisResults) {
                showNotification('No analysis to share', 'error');
                return;
            }
            
            showNotification('Share feature coming soon!', 'warning');
        }
        
        // Update cloud cover value display
        function updateCloudValue(value) {
            document.getElementById('cloud-value').textContent = value + '%';
        }
        
        // Switch tabs
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
                if (tab.textContent.includes(tabName.charAt(0).toUpperCase() + tabName.slice(1))) {
                    tab.classList.add('active');
                }
            });
            
            // Show corresponding content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(tabName + '-content').style.display = 'block';
        }
        
        // Toggle panels
        function togglePanel(panelName) {
            const panels = ['control-panel', 'results-panel'];
            const buttons = document.querySelectorAll('.control-btn');
            
            panels.forEach(panelId => {
                const panel = document.getElementById(panelId);
                const btn = buttons[Array.from(buttons).findIndex(b => b.onclick.toString().includes(panelName))];
                
                if (panelId === panelName + '-panel') {
                    if (panel.style.display === 'block') {
                        panel.style.display = 'none';
                        if (btn) btn.classList.remove('active');
                    } else {
                        panel.style.display = 'block';
                        if (btn) btn.classList.add('active');
                        // Hide other panels
                        panels.filter(p => p !== panelId).forEach(p => {
                            document.getElementById(p).style.display = 'none';
                            const otherBtn = buttons[Array.from(buttons).findIndex(b => b.onclick.toString().includes(p.replace('-panel', '')))];
                            if (otherBtn) otherBtn.classList.remove('active');
                        });
                    }
                }
            });
            
            // Always show selected area info
            if (selectedArea) {
                document.getElementById('selected-area-info').style.display = 'block';
            }
        }
        
        // Reset view
        function resetView() {
            map.flyTo({
                center: [0, 20],
                zoom: 2,
                pitch: 45,
                bearing: 0,
                duration: 1500
            });
        }
        
        // Update selected area info
        function updateSelectedAreaInfo(name, details) {
            selectedArea = name;
            document.getElementById('selected-area-name').textContent = name;
            document.getElementById('selected-area-coords').textContent = details;
            document.getElementById('selected-area-info').style.display = 'block';
        }
        
        // Show selected area preview
        function showSelectedAreaPreview(name) {
            const preview = document.getElementById('selected-area-preview');
            const previewName = document.getElementById('area-preview-name');
            
            previewName.textContent = name;
            preview.style.display = 'block';
        }
        
        // Show notification
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            const title = document.getElementById('notification-title');
            const msg = document.getElementById('notification-message');
            
            notification.className = '';
            notification.classList.add('notification-' + type);
            
            title.textContent = type.charAt(0).toUpperCase() + type.slice(1);
            msg.textContent = message;
            
            notification.style.display = 'block';
            
            // Auto hide after 3 seconds
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        // Show analysis progress
        function showAnalysisProgress() {
            const progress = document.getElementById('analysis-progress');
            const fill = document.getElementById('progress-fill');
            const text = document.getElementById('progress-text');
            
            progress.style.display = 'block';
            fill.style.width = '0%';
            text.textContent = 'Initializing...';
            
            // Simulate progress
            let progressValue = 0;
            const interval = setInterval(() => {
                progressValue += Math.random() * 10;
                if (progressValue > 90) progressValue = 90;
                fill.style.width = progressValue + '%';
                
                if (progressValue < 30) text.textContent = 'Downloading satellite data...';
                else if (progressValue < 60) text.textContent = 'Calculating indices...';
                else text.textContent = 'Processing results...';
                
                if (progressValue >= 90) {
                    clearInterval(interval);
                    text.textContent = 'Finishing up...';
                }
            }, 500);
        }
        
        // Hide analysis progress
        function hideAnalysisProgress() {
            document.getElementById('analysis-progress').style.display = 'none';
        }
        
        // Display results
        function displayResults(results) {
            const message = document.getElementById('results-message');
            const charts = document.getElementById('results-charts');
            const stats = document.getElementById('results-stats');
            
            // Update message
            message.innerHTML = `Analysis complete for <span style="color: #00ff88;">${selectedArea}</span>`;
            
            // Clear previous results
            charts.innerHTML = '';
            stats.innerHTML = '';
            
            // Create charts for each index
            Object.keys(results).forEach(index => {
                const data = results[index];
                
                if (data.dates && data.values && data.dates.length > 0) {
                    // Create chart container
                    const chartDiv = document.createElement('div');
                    chartDiv.className = 'chart-container';
                    chartDiv.innerHTML = `
                        <div style="color: white; font-weight: 500; margin-bottom: 5px;">${index}</div>
                        <canvas id="chart-${index}" width="300" height="150"></canvas>
                    `;
                    charts.appendChild(chartDiv);
                    
                    // Create simple chart
                    setTimeout(() => {
                        createMiniChart(`chart-${index}`, data.dates, data.values, index);
                    }, 100);
                    
                    // Add stats
                    const values = data.values.filter(v => v !== null);
                    if (values.length > 0) {
                        const avg = values.reduce((a, b) => a + b) / values.length;
                        const max = Math.max(...values);
                        const min = Math.min(...values);
                        
                        const statDiv = document.createElement('div');
                        statDiv.className = 'stat-item';
                        statDiv.innerHTML = `
                            <span class="stat-label">${index}</span>
                            <span class="stat-value">${avg.toFixed(4)}</span>
                        `;
                        stats.appendChild(statDiv);
                    }
                }
            });
            
            // Show results panel
            togglePanel('results');
        }
        
        // Create mini chart
        function createMiniChart(canvasId, dates, values, title) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            
            // Clear canvas
            ctx.clearRect(0, 0, width, height);
            
            // Draw chart
            if (values.length < 2) return;
            
            // Find min and max
            const minVal = Math.min(...values);
            const maxVal = Math.max(...values);
            const range = maxVal - minVal || 1;
            
            // Draw grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            
            // Draw data line
            ctx.beginPath();
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';
            
            values.forEach((val, i) => {
                const x = (i / (values.length - 1)) * width;
                const y = height - ((val - minVal) / range) * height * 0.8 - height * 0.1;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Draw points
            ctx.fillStyle = '#00ff88';
            values.forEach((val, i) => {
                if (i % 2 === 0) { // Show every other point
                    const x = (i / (values.length - 1)) * width;
                    const y = height - ((val - minVal) / range) * height * 0.8 - height * 0.1;
                    
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, Math.PI * 2);
                    ctx.fill();
                }
            });
        }
        
        // Handle messages from Streamlit
        window.addEventListener('message', function(event) {
            const data = event.data;
            
            switch(data.type) {
                case 'countries_loaded':
                    updateCountrySelect(data.countries);
                    break;
                    
                case 'admin1_loaded':
                    updateAdmin1Select(data.admin1);
                    break;
                    
                case 'admin2_loaded':
                    updateAdmin2Select(data.admin2);
                    break;
                    
                case 'area_selected':
                    showAreaOnMap(data.geometry);
                    break;
                    
                case 'analysis_complete':
                    hideAnalysisProgress();
                    analysisResults = data.results;
                    displayResults(data.results);
                    showNotification('Analysis completed successfully!', 'success');
                    break;
                    
                case 'analysis_error':
                    hideAnalysisProgress();
                    showNotification(data.message, 'error');
                    break;
                    
                case 'export_ready':
                    showNotification('Export ready for download', 'success');
                    break;
            }
        });
        
        // Update country select
        function updateCountrySelect(countries) {
            const select = document.getElementById('country-select');
            select.innerHTML = '<option value="">Select a country</option>';
            
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            });
        }
        
        // Update admin1 select
        function updateAdmin1Select(admin1List) {
            const select = document.getElementById('admin1-select');
            select.disabled = false;
            select.innerHTML = '<option value="">Select state/province</option>';
            
            if (admin1List && admin1List.length > 0) {
                admin1List.forEach(admin1 => {
                    const option = document.createElement('option');
                    option.value = admin1;
                    option.textContent = admin1;
                    select.appendChild(option);
                });
            }
        }
        
        // Update admin2 select
        function updateAdmin2Select(admin2List) {
            const select = document.getElementById('admin2-select');
            select.disabled = false;
            select.innerHTML = '<option value="">Select municipality</option>';
            
            if (admin2List && admin2List.length > 0) {
                admin2List.forEach(admin2 => {
                    const option = document.createElement('option');
                    option.value = admin2;
                    option.textContent = admin2;
                    select.appendChild(option);
                });
            }
        }
        
        // Show area on map
        function showAreaOnMap(geometry) {
            // Remove existing area if any
            if (map.getSource('selected-area')) {
                map.removeLayer('selected-area-fill');
                map.removeLayer('selected-area-border');
                map.removeSource('selected-area');
            }
            
            // Add new area
            map.addSource('selected-area', {
                'type': 'geojson',
                'data': geometry
            });
            
            map.addLayer({
                'id': 'selected-area-fill',
                'type': 'fill',
                'source': 'selected-area',
                'paint': {
                    'fill-color': '#00ff88',
                    'fill-opacity': 0.2
                }
            });
            
            map.addLayer({
                'id': 'selected-area-border',
                'type': 'line',
                'source': 'selected-area',
                'paint': {
                    'line-color': '#00ff88',
                    'line-width': 3,
                    'line-opacity': 0.8
                }
            });
            
            // Fly to area
            const bounds = new mapboxgl.LngLatBounds();
            geometry.geometry.coordinates[0].forEach(coord => {
                bounds.extend(coord);
            });
            
            map.fitBounds(bounds, {
                padding: 50,
                duration: 1500
            });
        }
        
        // Initialize map when page loads
        window.onload = initMap;
    </script>
</body>
</html>
"""

# Display the map interface
st.components.v1.html(mapbox_html, height=800, scrolling=False)

# Hidden Streamlit widgets for data processing
st.markdown('<div style="display: none;">', unsafe_allow_html=True)

# Create widgets for data exchange with JavaScript
if 'countries' not in st.session_state:
    st.session_state.countries = []

if st.session_state.ee_initialized:
    try:
        countries_fc = get_admin_boundaries(0)
        if countries_fc:
            st.session_state.countries = get_boundary_names(countries_fc, 0)
    except:
        st.session_state.countries = []

# Listen for JavaScript messages
js_code = """
<script>
// Send initial countries to JavaScript
window.addEventListener('load', function() {
    // Get countries from Streamlit
    const countries = %s;
    
    if (countries && countries.length > 0) {
        window.parent.postMessage({
            type: 'countries_loaded',
            countries: countries
        }, '*');
    }
});
</script>
""" % json.dumps(st.session_state.countries)

st.components.v1.html(js_code, height=0)

# Handle JavaScript messages through Streamlit components
if st.button("Force Refresh", key="refresh_button"):
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# JavaScript to Streamlit communication handler
js_to_python = """
<script>
// Function to send data to Streamlit
function sendToStreamlit(type, data) {
    // Create a hidden input and trigger Streamlit
    const input = document.createElement('input');
    input.type = 'hidden';
    input.id = 'js-data';
    input.value = JSON.stringify({type: type, data: data});
    document.body.appendChild(input);
    
    // Trigger change event
    const event = new Event('change');
    input.dispatchEvent(event);
}
</script>
"""

st.components.v1.html(js_to_python, height=0)

# Create a hidden text input to receive JavaScript data
js_data = st.text_input("JavaScript Data", key="js_data_input", label_visibility="collapsed")

if js_data:
    try:
        data = json.loads(js_data)
        st.write(f"Received from JavaScript: {data}")
        
        # Handle different message types
        if data.get('type') == 'load_countries':
            # Countries are already loaded
            pass
            
        elif data.get('type') == 'load_admin1':
            country = data.get('data', {}).get('country')
            if country:
                try:
                    countries_fc = get_admin_boundaries(0)
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                    admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                    admin1_names = get_boundary_names(admin1_fc, 1)
                    
                    # Send back to JavaScript
                    return_js = f"""
                    <script>
                    window.parent.postMessage({{
                        type: 'admin1_loaded',
                        admin1: {json.dumps(admin1_names)}
                    }}, '*');
                    </script>
                    """
                    st.components.v1.html(return_js, height=0)
                    
                except Exception as e:
                    st.error(f"Error loading admin1: {e}")
                    
        elif data.get('type') == 'load_admin2':
            admin1 = data.get('data', {}).get('admin1')
            country = data.get('data', {}).get('country')
            
            if admin1 and country:
                try:
                    countries_fc = get_admin_boundaries(0)
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                    admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                    admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', admin1)).first()
                    admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                    admin2_names = get_boundary_names(admin2_fc, 2)
                    
                    return_js = f"""
                    <script>
                    window.parent.postMessage({{
                        type: 'admin2_loaded',
                        admin2: {json.dumps(admin2_names)}
                    }}, '*');
                    </script>
                    """
                    st.components.v1.html(return_js, height=0)
                    
                except Exception as e:
                    st.error(f"Error loading admin2: {e}")
                    
    except json.JSONDecodeError:
        pass

# Footer (hidden but keeps Streamlit running)
st.markdown('<div style="height: 0; overflow: hidden;">Keeping Streamlit alive...</div>', unsafe_allow_html=True)
