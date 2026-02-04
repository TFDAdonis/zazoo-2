import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback

# Custom CSS for Integrated Map & UI
st.markdown("""
<style>
    /* Base styling */
    .stApp {
        background: #000000;
        color: #ffffff;
        min-height: 100vh;
    }
    
    /* Mobile-first design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.25rem !important;
            max-width: 100% !important;
        }
        
        .desktop-only {
            display: none !important;
        }
        
        h1 {
            font-size: 1.4rem !important;
            margin-bottom: 0.3rem !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .integrated-container {
            height: 85vh !important;
        }
        
        .map-panel {
            height: 50% !important;
        }
        
        .ui-panel {
            height: 50% !important;
            padding: 8px !important;
        }
        
        .ui-section {
            max-height: 120px !important;
            overflow-y: auto !important;
            margin-bottom: 5px !important;
        }
        
        .chart-container {
            max-height: 150px !important;
            margin-bottom: 5px !important;
        }
        
        .stButton > button {
            padding: 8px 10px !important;
            font-size: 12px !important;
            margin: 2px 0 !important;
            min-height: 36px !important;
        }
        
        .compact-select {
            margin-bottom: 5px !important;
        }
        
        .compact-slider {
            margin: 5px 0 !important;
        }
    }
    
    /* Desktop styles */
    @media (min-width: 769px) {
        .mobile-only {
            display: none !important;
        }
        
        .integrated-container {
            height: 85vh !important;
        }
        
        .map-panel {
            height: 65% !important;
        }
        
        .ui-panel {
            height: 35% !important;
            padding: 15px !important;
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
    
    /* Integrated Container */
    .integrated-container {
        display: flex;
        flex-direction: column;
        background: var(--primary-black);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-gray);
        width: 100%;
    }
    
    /* Map Panel */
    .map-panel {
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    /* UI Panel */
    .ui-panel {
        width: 100%;
        background: var(--card-black);
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    
    /* UI Sections */
    .ui-section {
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        backdrop-filter: blur(5px);
    }
    
    .ui-section-title {
        color: var(--primary-green);
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .ui-section-content {
        max-height: 100px;
        overflow-y: auto;
    }
    
    /* Compact controls */
    .compact-row {
        display: flex;
        gap: 8px;
        margin-bottom: 5px;
    }
    
    .compact-col {
        flex: 1;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        height: 150px;
        backdrop-filter: blur(5px);
    }
    
    .chart-title {
        color: var(--primary-green);
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 5px;
        text-align: center;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 2px 6px;
        background: rgba(0, 255, 136, 0.1);
        color: var(--primary-green);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin: 1px;
    }
    
    /* Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        margin-bottom: 8px;
        flex-wrap: wrap;
    }
    
    /* Mobile toggle */
    .mobile-toggle {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: rgba(10, 10, 10, 0.9);
        border: 1px solid var(--border-gray);
        border-radius: 20px;
        padding: 5px 10px;
        color: var(--primary-green);
        font-size: 11px;
        cursor: pointer;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 4px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-black);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-green);
        border-radius: 2px;
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
        return False

# Initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    if auto_initialize_earth_engine():
        st.session_state.ee_initialized = True
    else:
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
if 'ui_collapsed' not in st.session_state:
    st.session_state.ui_collapsed = False

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - Integrated View",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header
st.markdown("""
<div class="app-header">
    <div>
        <h1>🌍 KHISBA GIS</h1>
        <p style="color: #999999; margin: 0; font-size: 12px;">Integrated Vegetation Analytics</p>
    </div>
    <div>
        <span class="status-indicator">Online</span>
        <span class="status-indicator">🌿</span>
        <span class="status-indicator">Mapbox</span>
    </div>
</div>
""", unsafe_allow_html=True)

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
    except Exception:
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
    except Exception:
        return {'center': [0, 20], 'bounds': None, 'zoom': 2}

# Main Integrated Container
st.markdown('<div class="integrated-container">', unsafe_allow_html=True)

# Map Panel (Top 65% on desktop, 50% on mobile)
st.markdown('<div class="map-panel">', unsafe_allow_html=True)

# Mobile toggle button
toggle_label = "▲" if st.session_state.ui_collapsed else "▼"
st.markdown(f'''
<div class="mobile-toggle" onclick="toggleUI()">
    {toggle_label}
</div>
''', unsafe_allow_html=True)

# Prepare map data
map_center = [0, 20]
map_zoom = 2
bounds_data = None
selected_area_info = ""

if st.session_state.selected_coordinates:
    map_center = st.session_state.selected_coordinates['center']
    map_zoom = st.session_state.selected_coordinates['zoom']
    bounds_data = st.session_state.selected_coordinates['bounds']
    selected_area_info = f"""
    <div style="position: absolute; top: 10px; left: 10px; background: rgba(10, 10, 10, 0.9); color: white; padding: 10px; border-radius: 6px; border: 1px solid #222222; font-family: 'Inter', sans-serif; font-size: 12px; z-index: 1000; max-width: 200px;">
        <div style="color: #00ff88; font-weight: 600; margin-bottom: 5px;">📍 {st.session_state.selected_area_name[:25]}{'...' if st.session_state.selected_area_name and len(st.session_state.selected_area_name) > 25 else ''}</div>
        <div style="color: #cccccc; font-size: 11px;">{st.session_state.selected_area_level}</div>
    </div>
    """

# Integrated Mapbox HTML with inline UI elements
mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Integrated GIS</title>
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
    
    /* Map overlays */
    .map-overlay {{
      position: absolute;
      background: rgba(10, 10, 10, 0.85);
      border: 1px solid #222222;
      border-radius: 8px;
      color: white;
      font-family: 'Inter', sans-serif;
      z-index: 1000;
      backdrop-filter: blur(5px);
    }}
    
    .coordinates-overlay {{
      bottom: 10px;
      left: 10px;
      padding: 8px 12px;
      font-size: 11px;
    }}
    
    .quick-controls {{
      top: 10px;
      right: 10px;
      padding: 10px;
      min-width: 150px;
    }}
    
    .control-button {{
      display: block;
      width: 100%;
      background: linear-gradient(90deg, #00ff88, #00cc6a);
      color: #000000;
      border: none;
      padding: 8px;
      margin: 3px 0;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
    }}
    
    .control-button:hover {{
      opacity: 0.9;
    }}
    
    /* Mini charts overlay */
    .charts-overlay {{
      bottom: 50px;
      left: 10px;
      right: 10px;
      padding: 8px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
    }}
    
    .mini-chart {{
      flex: 0 0 auto;
      width: 100px;
      height: 60px;
      background: rgba(0, 0, 0, 0.7);
      border-radius: 4px;
      padding: 4px;
    }}
    
    .chart-value {{
      color: #00ff88;
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      margin: 2px 0;
    }}
    
    .chart-label {{
      color: #cccccc;
      font-size: 9px;
      text-align: center;
    }}
    
    /* Legend overlay */
    .legend-overlay {{
      bottom: 10px;
      right: 10px;
      padding: 8px;
      font-size: 10px;
    }}
    
    .legend-item {{
      display: flex;
      align-items: center;
      margin: 2px 0;
    }}
    
    .legend-color {{
      width: 12px;
      height: 12px;
      margin-right: 6px;
      border-radius: 2px;
    }}
    
    /* Selected area overlay */
    .area-overlay {{
      top: 50px;
      left: 10px;
      max-width: 180px;
      padding: 10px;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  
  {selected_area_info}
  
  <div class="map-overlay coordinates-overlay">
    <div>Lat: <span id="lat">0.00°</span></div>
    <div>Lon: <span id="lon">0.00°</span></div>
  </div>
  
  <div class="map-overlay quick-controls">
    <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 8px;">Quick Actions</div>
    <button class="control-button" onclick="zoomToSelection()">📍 Zoom to Area</button>
    <button class="control-button" onclick="resetView()">🌍 Reset View</button>
    <button class="control-button" onclick="toggleSatellite()">🛰️ Toggle View</button>
  </div>
  
  <!-- Mini Charts (will be populated by JavaScript) -->
  <div class="map-overlay charts-overlay" id="miniCharts">
    <div class="mini-chart">
      <div class="chart-label">NDVI</div>
      <div class="chart-value" id="ndviValue">0.00</div>
    </div>
    <div class="mini-chart">
      <div class="chart-label">EVI</div>
      <div class="chart-value" id="eviValue">0.00</div>
    </div>
    <div class="mini-chart">
      <div class="chart-label">Vegetation</div>
      <div class="chart-value" id="vegValue">0%</div>
    </div>
  </div>
  
  <!-- Legend -->
  <div class="map-overlay legend-overlay">
    <div style="color: #00ff88; font-size: 11px; font-weight: 600; margin-bottom: 5px;">Legend</div>
    <div class="legend-item">
      <div class="legend-color" style="background: #00ff88;"></div>
      <div>Selected Area</div>
    </div>
    <div class="legend-item">
      <div class="legend-color" style="background: #ffaa00;"></div>
      <div>High Vegetation</div>
    </div>
    <div class="legend-item">
      <div class="legend-color" style="background: #ff4444;"></div>
      <div>Low Vegetation</div>
    </div>
  </div>
  
  <script>
    mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
    
    let currentStyle = 'satellite';
    const map = new mapboxgl.Map({{
      container: 'map',
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: {map_center},
      zoom: {map_zoom},
      pitch: 45,
      bearing: 0,
      touchZoomRotate: true,
      dragPan: true,
      cooperativeGestures: false
    }});
    
    // Add controls
    map.addControl(new mapboxgl.NavigationControl());
    
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
    
    // Add selected area
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
        
        // Update mini charts with mock data
        updateMiniCharts();
      }}
      ''' if bounds_data else ''}
    }});
    
    // Functions for quick controls
    function zoomToSelection() {{
      {f'''
      if ({bounds_data}) {{
        const bounds = {bounds_data};
        const center = {map_center};
        map.flyTo({{
          center: center,
          zoom: 8,
          duration: 1000
        }});
      }}
      ''' if bounds_data else '''
      alert("No area selected");
      '''}
    }}
    
    function resetView() {{
      map.flyTo({{
        center: [0, 20],
        zoom: 2,
        duration: 1000
      }});
    }}
    
    function toggleSatellite() {{
      if (currentStyle === 'satellite') {{
        map.setStyle('mapbox://styles/mapbox/outdoors-v12');
        currentStyle = 'outdoors';
      }} else {{
        map.setStyle('mapbox://styles/mapbox/satellite-streets-v12');
        currentStyle = 'satellite';
      }}
    }}
    
    // Update mini charts with mock/real data
    function updateMiniCharts() {{
      // Mock data - replace with real data from analysis
      const ndvi = (Math.random() * 0.8).toFixed(2);
      const evi = (Math.random() * 0.6).toFixed(2);
      const vegetation = Math.round(Math.random() * 100);
      
      document.getElementById('ndviValue').textContent = ndvi;
      document.getElementById('eviValue').textContent = evi;
      document.getElementById('vegValue').textContent = vegetation + '%';
    }}
    
    // Update charts every 5 seconds (simulate live data)
    setInterval(updateMiniCharts, 5000);
    
    // Initial update
    updateMiniCharts();
  </script>
</body>
</html>
"""

# Display the integrated map
st.components.v1.html(mapbox_html, height=400)

st.markdown('</div>', unsafe_allow_html=True)  # Close map panel

# UI Panel (Bottom 35% on desktop, 50% on mobile) - Only show if not collapsed
if not st.session_state.ui_collapsed:
    st.markdown('<div class="ui-panel">', unsafe_allow_html=True)
    
    # Create two columns for controls and charts
    col_controls, col_charts = st.columns([1, 1])
    
    with col_controls:
        # Area Selection Section
        st.markdown('<div class="ui-section">', unsafe_allow_html=True)
        st.markdown('<div class="ui-section-title">📍 Area Selection</div>', unsafe_allow_html=True)
        
        if st.session_state.ee_initialized:
            try:
                countries_fc = get_admin_boundaries(0)
                if countries_fc:
                    country_names = get_boundary_names(countries_fc, 0)
                    selected_country = st.selectbox(
                        "Country",
                        options=["Select country"] + country_names,
                        index=0,
                        key="country_integrated",
                        label_visibility="collapsed"
                    )
                    
                    if selected_country and selected_country != "Select country":
                        country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                        
                        admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                        if admin1_fc:
                            admin1_names = get_boundary_names(admin1_fc, 1)
                            selected_admin1 = st.selectbox(
                                "State",
                                options=["Select state"] + admin1_names,
                                index=0,
                                key="admin1_integrated",
                                label_visibility="collapsed"
                            )
                            
                            if selected_admin1 and selected_admin1 != "Select state":
                                admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                                
                                admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                                if admin2_fc:
                                    admin2_names = get_boundary_names(admin2_fc, 2)
                                    selected_admin2 = st.selectbox(
                                        "Municipality",
                                        options=["Select municipality"] + admin2_names,
                                        index=0,
                                        key="admin2_integrated",
                                        label_visibility="collapsed"
                                    )
            except Exception:
                pass
        
        # Update selected area
        if st.button("✅ Set Area", use_container_width=True):
            if selected_country and selected_country != "Select country":
                try:
                    if selected_admin2 and selected_admin2 != "Select municipality":
                        geometry = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', selected_admin2))
                        area_name = f"{selected_admin2}, {selected_country}"
                        area_level = "Municipality"
                    elif selected_admin1 and selected_admin1 != "Select state":
                        geometry = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1))
                        area_name = f"{selected_admin1}, {selected_country}"
                        area_level = "State"
                    else:
                        geometry = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country))
                        area_name = selected_country
                        area_level = "Country"
                    
                    coords_info = get_geometry_coordinates(geometry)
                    
                    st.session_state.selected_geometry = geometry
                    st.session_state.selected_coordinates = coords_info
                    st.session_state.selected_area_name = area_name
                    st.session_state.selected_area_level = area_level
                    
                    st.rerun()
                except Exception:
                    pass
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis Settings Section
        st.markdown('<div class="ui-section">', unsafe_allow_html=True)
        st.markdown('<div class="ui-section-title">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start",
                value=datetime(2023, 1, 1),
                key="start_integrated",
                label_visibility="collapsed"
            )
        with col2:
            end_date = st.date_input(
                "End",
                value=datetime(2023, 12, 31),
                key="end_integrated",
                label_visibility="collapsed"
            )
        
        satellite = st.selectbox(
            "Satellite",
            options=["Sentinel-2", "Landsat-8"],
            key="satellite_integrated",
            label_visibility="collapsed"
        )
        
        cloud_cover = st.slider(
            "Cloud Cover %",
            min_value=0,
            max_value=100,
            value=20,
            key="cloud_integrated",
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Run Analysis Button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if not st.session_state.selected_geometry:
                st.error("Please select an area first")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        # Mock analysis results
                        results = {}
                        indices = ['NDVI', 'EVI', 'SAVI', 'NDWI']
                        
                        for index in indices:
                            dates = [
                                '2023-01-15', '2023-02-15', '2023-03-15', '2023-04-15',
                                '2023-05-15', '2023-06-15', '2023-07-15', '2023-08-15',
                                '2023-09-15', '2023-10-15', '2023-11-15', '2023-12-15'
                            ]
                            base_value = 0.3 if index == 'NDVI' else 0.2
                            values = [base_value + (i * 0.05) + (0.1 * (ord(index[0]) % 5) / 10) for i in range(12)]
                            results[index] = {'dates': dates, 'values': values}
                        
                        st.session_state.analysis_results = results
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    except Exception:
                        st.error("Analysis failed")
    
    with col_charts:
        # Display charts if analysis results exist
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Show first 2 charts
            for i, (index, data) in enumerate(list(results.items())[:2]):
                if data['dates'] and data['values']:
                    try:
                        st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown(f'<div class="chart-title">{index}</div>', unsafe_allow_html=True)
                        
                        # Create mini chart
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data['dates'],
                            y=data['values'],
                            mode='lines',
                            line=dict(color='#00ff88', width=2)
                        ))
                        
                        fig.update_layout(
                            height=100,
                            margin=dict(l=0, r=0, t=0, b=0),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False
                            ),
                            yaxis=dict(
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        # Show current value
                        if data['values']:
                            current_value = data['values'][-1]
                            trend = "↗️" if len(data['values']) > 1 and data['values'][-1] > data['values'][-2] else "↘️"
                            st.markdown(f'<div style="text-align: center; color: #00ff88; font-size: 14px; font-weight: bold;">{current_value:.3f} {trend}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception:
                        pass
            
            # Show summary for remaining indices
            if len(results) > 2:
                st.markdown('<div class="ui-section">', unsafe_allow_html=True)
                st.markdown('<div class="ui-section-title">📊 Summary</div>', unsafe_allow_html=True)
                
                summary_text = ""
                for index, data in list(results.items())[2:4]:  # Show next 2
                    if data['values']:
                        avg = sum(data['values']) / len(data['values'])
                        summary_text += f"{index}: {avg:.3f}<br>"
                
                if summary_text:
                    st.markdown(f'<div style="color: #cccccc; font-size: 11px;">{summary_text}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show placeholder charts
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">NDVI</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align: center; color: #666666; margin-top: 40px;">Run analysis to see data</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">EVI</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align: center; color: #666666; margin-top: 40px;">Run analysis to see data</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close UI panel

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 10px; padding: 8px 0; margin-top: 5px;">
    <p style="margin: 2px 0;">KHISBA GIS • Integrated Map & Analytics</p>
    <p style="margin: 2px 0; font-size: 9px;">🌍 Map + 📊 Charts + ⚙️ Controls = Unified View</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close integrated container

# JavaScript for UI toggle
st.markdown("""
<script>
function toggleUI() {
    // Send message to Streamlit
    window.parent.postMessage({
        'type': 'streamlit:setComponentValue',
        'value': 'toggle_ui'
    }, '*');
}
</script>
""", unsafe_allow_html=True)

# Handle UI toggle
if st.query_params.get("toggle_ui") == "true":
    st.session_state.ui_collapsed = not st.session_state.ui_collapsed
    st.query_params.clear()
