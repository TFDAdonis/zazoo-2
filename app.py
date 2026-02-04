import streamlit as st
import json
import ee
import traceback

# Minimal CSS for full-screen
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    
    /* Make sure the map container is full screen */
    iframe {
        width: 100vw !important;
        height: 100vh !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Earth Engine
@st.cache_resource
def init_earth_engine():
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
        st.error(f"Earth Engine initialization failed: {str(e)}")
        return False

# Initialize session state
if 'ee_initialized' not in st.session_state:
    if init_earth_engine():
        st.session_state.ee_initialized = True
    else:
        st.session_state.ee_initialized = False

if 'countries' not in st.session_state:
    st.session_state.countries = []

# Load countries
if st.session_state.ee_initialized and not st.session_state.countries:
    try:
        countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
        countries = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
        st.session_state.countries = sorted(countries) if countries else []
    except:
        st.session_state.countries = ["United States", "Canada", "Mexico", "United Kingdom", "France", "Germany", "Australia", "Brazil", "India", "China"]

# Page config
st.set_page_config(
    page_title="KHISBA GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main Mapbox Interface with FULL SCREEN
mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KHISBA GIS - Full Screen</title>
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
    <style>
        * {{ 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        body, html {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: #000;
        }}
        
        #map {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
        }}
        
        /* Loading overlay */
        #loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #000;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #00ff88;
        }}
        
        .spinner {{
            width: 60px;
            height: 60px;
            border: 4px solid rgba(0, 255, 136, 0.1);
            border-top: 4px solid #00ff88;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Main control panel */
        #main-panel {{
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #00ff88;
            border-radius: 15px;
            padding: 20px;
            width: 350px;
            max-height: 85vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        }}
        
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(0, 255, 136, 0.3);
        }}
        
        .app-title {{
            color: #00ff88;
            font-size: 24px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .close-btn {{
            background: none;
            border: none;
            color: #999;
            font-size: 24px;
            cursor: pointer;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}
        
        .close-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 4px;
            margin-bottom: 20px;
        }}
        
        .tab {{
            flex: 1;
            padding: 10px;
            text-align: center;
            background: none;
            border: none;
            color: #999;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .tab.active {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
        }}
        
        /* Form styles */
        .form-group {{
            margin-bottom: 15px;
        }}
        
        .form-label {{
            display: block;
            color: #00ff88;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .form-select, .form-input {{
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
            transition: all 0.2s;
        }}
        
        .form-select:focus, .form-input:focus {{
            border-color: #00ff88;
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
        }}
        
        .form-select option {{
            background: #000;
            color: white;
        }}
        
        /* Button styles */
        .btn {{
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
        }}
        
        .btn-primary {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        /* Checkbox grid */
        .checkbox-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .checkbox-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .checkbox-item.selected {{
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }}
        
        .checkbox-label {{
            color: white;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
        }}
        
        /* Results panel */
        #results-panel {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #00ff88;
            border-radius: 15px;
            padding: 20px;
            width: 400px;
            max-height: 70vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
            display: none;
        }}
        
        /* Notification */
        #notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px 20px;
            color: white;
            backdrop-filter: blur(10px);
            display: none;
            animation: slideIn 0.3s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(100px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        /* Quick actions bar */
        #quick-actions {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 50px;
            padding: 10px 20px;
            display: flex;
            gap: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .action-btn {{
            width: 45px;
            height: 45px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}
        
        .action-btn:hover {{
            background: rgba(0, 255, 136, 0.2);
            transform: scale(1.1);
        }}
        
        .action-btn.active {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
        }}
        
        /* Map controls */
        .mapboxgl-ctrl-top-right {{
            top: 100px !important;
            right: 20px !important;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            #main-panel, #results-panel {{
                width: calc(100vw - 40px);
                left: 20px;
                right: 20px;
            }}
            
            #main-panel {{
                top: 10px;
                max-height: 80vh;
            }}
            
            #results-panel {{
                bottom: 10px;
                max-height: 60vh;
            }}
            
            #quick-actions {{
                bottom: 10px;
                padding: 8px 15px;
            }}
        }}
        
        /* Hide scrollbar but keep functionality */
        #main-panel::-webkit-scrollbar {{
            width: 5px;
        }}
        
        #main-panel::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }}
        
        #main-panel::-webkit-scrollbar-thumb {{
            background: rgba(0, 255, 136, 0.5);
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-overlay">
        <div class="spinner"></div>
        <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">KHISBA GIS</div>
        <div style="color: #999; font-size: 14px;">Initializing 3D Earth Engine...</div>
    </div>
    
    <!-- Map Container -->
    <div id="map"></div>
    
    <!-- Main Control Panel -->
    <div id="main-panel">
        <div class="panel-header">
            <div class="app-title">🌍 KHISBA GIS</div>
            <button class="close-btn" onclick="togglePanel('main')">×</button>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('select')">Select</button>
            <button class="tab" onclick="switchTab('analyze')">Analyze</button>
            <button class="tab" onclick="switchTab('export')">Export</button>
        </div>
        
        <!-- Tab Content: Select Area -->
        <div id="tab-select" class="tab-content">
            <div class="form-group">
                <label class="form-label">Country</label>
                <select class="form-select" id="country-select" onchange="onCountryChange()">
                    <option value="">Select a country</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">State/Province</label>
                <select class="form-select" id="admin1-select" onchange="onAdmin1Change()" disabled>
                    <option value="">Select state/province</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Municipality (Optional)</label>
                <select class="form-select" id="admin2-select" onchange="onAdmin2Change()" disabled>
                    <option value="">Select municipality</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Or Draw on Map</label>
                <div style="display: flex; gap: 10px; margin-top: 5px;">
                    <button class="btn-secondary" onclick="startDrawing('polygon')" style="flex: 1;">📐 Draw</button>
                    <button class="btn-secondary" onclick="startDrawing('rectangle')" style="flex: 1;">⬜ Rectangle</button>
                </div>
            </div>
            
            <div id="selected-area-preview" style="display: none; margin-top: 15px; padding: 15px; background: rgba(0, 255, 136, 0.1); border-radius: 8px;">
                <div style="color: #00ff88; font-weight: 600; margin-bottom: 5px;">Selected Area:</div>
                <div id="selected-area-name" style="color: white; font-weight: 500;"></div>
                <div id="selected-area-details" style="color: #999; font-size: 12px; margin-top: 5px;"></div>
            </div>
            
            <button class="btn-primary" onclick="confirmSelection()" style="margin-top: 20px;">✅ Confirm Selection</button>
        </div>
        
        <!-- Tab Content: Analyze -->
        <div id="tab-analyze" class="tab-content" style="display: none;">
            <div class="form-group">
                <label class="form-label">Time Period</label>
                <div style="display: flex; gap: 10px;">
                    <input type="date" class="form-input" id="start-date" value="2023-01-01" style="flex: 1;">
                    <input type="date" class="form-input" id="end-date" value="2023-12-31" style="flex: 1;">
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
                <label class="form-label">Max Cloud Cover: <span id="cloud-value" style="color: #00ff88;">20%</span></label>
                <input type="range" class="form-input" id="cloud-slider" min="0" max="100" value="20" 
                       oninput="document.getElementById('cloud-value').textContent = this.value + '%'" style="width: 100%;">
            </div>
            
            <div class="form-group">
                <label class="form-label">Vegetation Indices</label>
                <div class="checkbox-grid" id="indices-container">
                    <!-- Indices will be loaded here -->
                </div>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button class="btn-secondary" onclick="selectAllIndices()" style="flex: 1;">Select All</button>
                    <button class="btn-secondary" onclick="clearAllIndices()" style="flex: 1;">Clear All</button>
                </div>
            </div>
            
            <button class="btn-primary" onclick="runAnalysis()">🚀 Run Analysis</button>
        </div>
        
        <!-- Tab Content: Export -->
        <div id="tab-export" class="tab-content" style="display: none;">
            <div style="color: #999; font-size: 14px; margin-bottom: 20px;">
                Export your analysis results in various formats
            </div>
            
            <div class="form-group">
                <label class="form-label">Export Format</label>
                <select class="form-select" id="export-format">
                    <option value="csv">CSV Data</option>
                    <option value="json">JSON</option>
                    <option value="geojson">GeoJSON</option>
                    <option value="png">Chart Image</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Data Range</label>
                <select class="form-select" id="export-range">
                    <option value="full">Full Dataset</option>
                    <option value="monthly">Monthly Averages</option>
                    <option value="summary">Summary Statistics</option>
                </select>
            </div>
            
            <button class="btn-primary" onclick="exportData()">📥 Download Export</button>
            <button class="btn-secondary" onclick="shareResults()" style="margin-top: 10px;">🔗 Share Results</button>
        </div>
    </div>
    
    <!-- Results Panel -->
    <div id="results-panel">
        <div class="panel-header">
            <div class="app-title" style="font-size: 20px;">📊 Analysis Results</div>
            <button class="close-btn" onclick="togglePanel('results')">×</button>
        </div>
        <div id="results-content">
            <!-- Results will be loaded here -->
        </div>
    </div>
    
    <!-- Quick Actions Bar -->
    <div id="quick-actions">
        <button class="action-btn" onclick="togglePanel('main')" title="Control Panel">⚙️</button>
        <button class="action-btn" onclick="togglePanel('results')" title="Results">📊</button>
        <button class="action-btn" onclick="resetView()" title="Reset View">🏠</button>
        <button class="action-btn" onclick="toggleFullscreen()" title="Full Screen">⛶</button>
        <button class="action-btn" onclick="showHelp()" title="Help">❓</button>
    </div>
    
    <!-- Notification -->
    <div id="notification">
        <div id="notification-message"></div>
    </div>

    <script>
        // Mapbox Access Token
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
        
        // Global variables
        let map = null;
        let selectedArea = null;
        let selectedGeometry = null;
        let drawingMode = null;
        let drawnPoints = [];
        
        // Initialize the map
        function initMap() {{
            map = new mapboxgl.Map({{
                container: 'map',
                style: 'mapbox://styles/mapbox/satellite-streets-v12',
                center: [0, 20],
                zoom: 2,
                pitch: 45,
                bearing: 0,
                antialias: true,
                attributionControl: false
            }});
            
            // Add navigation controls
            map.addControl(new mapboxgl.NavigationControl({{
                showCompass: true,
                showZoom: true
            }}), 'top-right');
            
            // Add scale control
            map.addControl(new mapboxgl.ScaleControl({{
                unit: 'metric'
            }}));
            
            // When map loads
            map.on('load', () => {{
                // Hide loading screen
                document.getElementById('loading-overlay').style.display = 'none';
                
                // Load initial data
                loadCountries();
                loadIndices();
                
                // Show welcome message
                showNotification('KHISBA GIS Ready! Select an area to begin analysis.');
            }});
            
            // Handle map clicks for drawing
            map.on('click', (e) => {{
                if (drawingMode) {{
                    handleDrawingClick(e.lngLat);
                }}
            }});
            
            // Handle double-click to complete drawing
            map.on('dblclick', () => {{
                if (drawingMode && drawnPoints.length >= 3) {{
                    completeDrawing();
                }}
            }});
        }}
        
        // Load countries from Streamlit
        function loadCountries() {{
            const countries = {json.dumps(st.session_state.countries)};
            const select = document.getElementById('country-select');
            
            countries.forEach(country => {{
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            }});
            
            showNotification(`Loaded ${{countries.length}} countries`);
        }}
        
        // When country changes
        async function onCountryChange() {{
            const country = document.getElementById('country-select').value;
            if (!country) return;
            
            const admin1Select = document.getElementById('admin1-select');
            admin1Select.disabled = true;
            admin1Select.innerHTML = '<option value="">Loading provinces...</option>';
            
            try {{
                const response = await callStreamlit('get_admin1', {{ country: country }});
                
                admin1Select.innerHTML = '<option value="">Select state/province</option>';
                if (response.admin1 && response.admin1.length > 0) {{
                    response.admin1.forEach(admin1 => {{
                        const option = document.createElement('option');
                        option.value = admin1;
                        option.textContent = admin1;
                        admin1Select.appendChild(option);
                    }});
                    admin1Select.disabled = false;
                    showNotification(`Loaded ${{response.admin1.length}} provinces for ${{country}}`);
                }} else {{
                    admin1Select.innerHTML = '<option value="">No provinces found</option>';
                    showNotification('No provinces found for this country', 'warning');
                }}
                
                // Reset admin2
                const admin2Select = document.getElementById('admin2-select');
                admin2Select.innerHTML = '<option value="">Select municipality</option>';
                admin2Select.disabled = true;
                
            }} catch (error) {{
                showNotification('Error loading provinces: ' + error.message, 'error');
                admin1Select.innerHTML = '<option value="">Error loading</option>';
            }}
        }}
        
        // When admin1 changes
        async function onAdmin1Change() {{
            const admin1 = document.getElementById('admin1-select').value;
            const country = document.getElementById('country-select').value;
            if (!admin1 || !country) return;
            
            const admin2Select = document.getElementById('admin2-select');
            admin2Select.disabled = true;
            admin2Select.innerHTML = '<option value="">Loading municipalities...</option>';
            
            try {{
                const response = await callStreamlit('get_admin2', {{ 
                    country: country, 
                    admin1: admin1 
                }});
                
                admin2Select.innerHTML = '<option value="">Select municipality</option>';
                if (response.admin2 && response.admin2.length > 0) {{
                    response.admin2.forEach(admin2 => {{
                        const option = document.createElement('option');
                        option.value = admin2;
                        option.textContent = admin2;
                        admin2Select.appendChild(option);
                    }});
                    admin2Select.disabled = false;
                    showNotification(`Loaded ${{response.admin2.length}} municipalities`);
                }} else {{
                    admin2Select.innerHTML = '<option value="">No municipalities found</option>';
                    showNotification('No municipalities found', 'warning');
                }}
            }} catch (error) {{
                showNotification('Error loading municipalities', 'error');
                admin2Select.innerHTML = '<option value="">Error loading</option>';
            }}
        }}
        
        // When admin2 changes
        function onAdmin2Change() {{
            updateSelectedAreaPreview();
        }}
        
        // Update selected area preview
        function updateSelectedAreaPreview() {{
            const country = document.getElementById('country-select').value;
            const admin1 = document.getElementById('admin1-select').value;
            const admin2 = document.getElementById('admin2-select').value;
            
            if (!country) return;
            
            let areaName = country;
            let details = 'Country level';
            
            if (admin1 && admin2) {{
                areaName = `${{admin2}}, ${{admin1}}, ${{country}}`;
                details = 'Municipality level';
            }} else if (admin1) {{
                areaName = `${{admin1}}, ${{country}}`;
                details = 'Province level';
            }}
            
            document.getElementById('selected-area-name').textContent = areaName;
            document.getElementById('selected-area-details').textContent = details;
            document.getElementById('selected-area-preview').style.display = 'block';
            
            selectedArea = areaName;
        }}
        
        // Confirm selection
        async function confirmSelection() {{
            if (!selectedArea) {{
                showNotification('Please select an area first', 'warning');
                return;
            }}
            
            const country = document.getElementById('country-select').value;
            const admin1 = document.getElementById('admin1-select').value;
            const admin2 = document.getElementById('admin2-select').value;
            
            try {{
                showNotification('Loading area geometry...', 'info');
                
                const response = await callStreamlit('get_geometry', {{
                    country: country,
                    admin1: admin1,
                    admin2: admin2
                }});
                
                if (response.geometry) {{
                    showAreaOnMap(response.geometry);
                    showNotification('Area selected successfully!', 'success');
                    // Switch to analyze tab
                    switchTab('analyze');
                }} else {{
                    showNotification('Could not load area geometry', 'error');
                }}
            }} catch (error) {{
                showNotification('Error: ' + error.message, 'error');
            }}
        }}
        
        // Start drawing on map
        function startDrawing(mode) {{
            drawingMode = mode;
            drawnPoints = [];
            
            if (mode === 'rectangle') {{
                showNotification('Click two points to draw a rectangle', 'info');
            }} else {{
                showNotification('Click points to draw a polygon (double-click to finish)', 'info');
            }}
        }}
        
        // Handle drawing clicks
        function handleDrawingClick(lngLat) {{
            if (!drawingMode) return;
            
            drawnPoints.push([lngLat.lng, lngLat.lat]);
            
            // For rectangle, complete after 2 points
            if (drawingMode === 'rectangle' && drawnPoints.length === 2) {{
                completeRectangleDrawing();
            }}
        }}
        
        // Complete rectangle drawing
        function completeRectangleDrawing() {{
            if (drawnPoints.length !== 2) return;
            
            const [p1, p2] = drawnPoints;
            const rectangleCoords = [
                p1,
                [p2[0], p1[1]],
                p2,
                [p1[0], p2[1]],
                p1  // Close the polygon
            ];
            
            createCustomArea(rectangleCoords, 'Rectangle');
            resetDrawing();
        }}
        
        // Complete polygon drawing
        function completeDrawing() {{
            if (drawnPoints.length < 3) return;
            
            // Close the polygon
            drawnPoints.push(drawnPoints[0]);
            createCustomArea(drawnPoints, 'Custom Polygon');
            resetDrawing();
        }}
        
        // Reset drawing state
        function resetDrawing() {{
            drawingMode = null;
            drawnPoints = [];
        }}
        
        // Create custom area
        async function createCustomArea(coordinates, type) {{
            try {{
                const response = await callStreamlit('create_custom_area', {{
                    coordinates: coordinates,
                    type: type
                }});
                
                if (response.geometry) {{
                    showAreaOnMap(response.geometry);
                    selectedArea = `${{type}} Area`;
                    
                    document.getElementById('selected-area-name').textContent = selectedArea;
                    document.getElementById('selected-area-details').textContent = `${{coordinates.length}} points drawn`;
                    document.getElementById('selected-area-preview').style.display = 'block';
                    
                    showNotification('${{type}} created successfully!', 'success');
                }}
            }} catch (error) {{
                showNotification('Error creating area: ' + error.message, 'error');
            }}
        }}
        
        // Show area on map
        function showAreaOnMap(geometry) {{
            // Remove existing area if any
            if (map.getSource('selected-area')) {{
                map.removeLayer('selected-area-fill');
                map.removeLayer('selected-area-border');
                map.removeSource('selected-area');
            }}
            
            // Add new area
            map.addSource('selected-area', {{
                type: 'geojson',
                data: {{
                    type: 'Feature',
                    geometry: geometry,
                    properties: {{ name: selectedArea }}
                }}
            }});
            
            map.addLayer({{
                id: 'selected-area-fill',
                type: 'fill',
                source: 'selected-area',
                paint: {{
                    'fill-color': '#00ff88',
                    'fill-opacity': 0.2
                }}
            }});
            
            map.addLayer({{
                id: 'selected-area-border',
                type: 'line',
                source: 'selected-area',
                paint: {{
                    'line-color': '#00ff88',
                    'line-width': 3
                }}
            }});
            
            // Zoom to area
            const bounds = new mapboxgl.LngLatBounds();
            geometry.coordinates[0].forEach(coord => {{
                bounds.extend(coord);
            }});
            
            map.fitBounds(bounds, {{
                padding: 50,
                duration: 1500
            }});
        }}
        
        // Load vegetation indices
        function loadIndices() {{
            const indices = [
                'NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 
                'MSAVI', 'ARVI', 'VARI', 'OSAVI', 'DVI', 
                'RVI', 'MSI', 'NDMI', 'NBR', 'NDSI'
            ];
            
            const container = document.getElementById('indices-container');
            indices.forEach(index => {{
                const div = document.createElement('div');
                div.className = 'checkbox-item';
                div.innerHTML = `
                    <input type="checkbox" id="index-${{index}}" value="${{index}}" 
                           ${{index === 'NDVI' || index === 'EVI' ? 'checked' : ''}}>
                    <label class="checkbox-label" for="index-${{index}}">${{index}}</label>
                `;
                container.appendChild(div);
                
                // Add click handler
                div.addEventListener('click', function(e) {{
                    const checkbox = this.querySelector('input');
                    checkbox.checked = !checkbox.checked;
                    this.classList.toggle('selected', checkbox.checked);
                }});
                
                // Set initial selected state
                if (index === 'NDVI' || index === 'EVI') {{
                    div.classList.add('selected');
                }}
            }});
        }}
        
        // Select all indices
        function selectAllIndices() {{
            document.querySelectorAll('#indices-container .checkbox-item').forEach(item => {{
                item.classList.add('selected');
                item.querySelector('input').checked = true;
            }});
        }}
        
        // Clear all indices
        function clearAllIndices() {{
            document.querySelectorAll('#indices-container .checkbox-item').forEach(item => {{
                item.classList.remove('selected');
                item.querySelector('input').checked = false;
            }});
        }}
        
        // Run analysis
        async function runAnalysis() {{
            if (!selectedArea) {{
                showNotification('Please select an area first', 'warning');
                return;
            }}
            
            // Get selected indices
            const selectedIndices = [];
            document.querySelectorAll('#indices-container input:checked').forEach(checkbox => {{
                selectedIndices.push(checkbox.value);
            }});
            
            if (selectedIndices.length === 0) {{
                showNotification('Please select at least one vegetation index', 'warning');
                return;
            }}
            
            // Get parameters
            const params = {{
                startDate: document.getElementById('start-date').value,
                endDate: document.getElementById('end-date').value,
                satellite: document.getElementById('satellite-select').value,
                cloudCover: document.getElementById('cloud-slider').value,
                indices: selectedIndices
            }};
            
            showNotification('Running analysis... This may take a moment.', 'info');
            
            try {{
                const response = await callStreamlit('run_analysis', params);
                
                if (response.results) {{
                    displayResults(response.results);
                    showNotification('Analysis complete!', 'success');
                }} else {{
                    showNotification(response.error || 'Analysis failed', 'error');
                }}
            }} catch (error) {{
                showNotification('Analysis error: ' + error.message, 'error');
            }}
        }}
        
        // Display results
        function displayResults(results) {{
            const content = document.getElementById('results-content');
            const panel = document.getElementById('results-panel');
            
            let html = `
                <div style="color: #00ff88; font-weight: 600; margin-bottom: 15px; font-size: 18px;">
                    ${{selectedArea}}
                </div>
                <div style="color: #999; margin-bottom: 20px;">
                    Analysis completed with ${{Object.keys(results).length}} indices
                </div>
            `;
            
            // Create result cards for each index
            Object.keys(results).forEach(index => {{
                const data = results[index];
                
                if (data.values && data.values.length > 0) {{
                    const values = data.values.filter(v => v !== null);
                    const avg = values.reduce((a, b) => a + b, 0) / values.length;
                    const max = Math.max(...values);
                    const min = Math.min(...values);
                    
                    html += `
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <div style="color: #00ff88; font-weight: 600;">${{index}}</div>
                                <div style="color: white; font-weight: 600; font-size: 16px;">${{avg.toFixed(4)}}</div>
                            </div>
                            <div style="display: flex; justify-content: space-between; color: #999; font-size: 12px;">
                                <div>Min: ${{min.toFixed(4)}}</div>
                                <div>Max: ${{max.toFixed(4)}}</div>
                                <div>Points: ${{values.length}}</div>
                            </div>
                            <div style="margin-top: 10px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden;">
                                <div style="height: 100%; width: ${{((avg - min) / (max - min || 1)) * 100}}%; background: #00ff88; border-radius: 2px;"></div>
                            </div>
                        </div>
                    `;
                }}
            }});
            
            content.innerHTML = html;
            panel.style.display = 'block';
        }}
        
        // Export data
        async function exportData() {{
            showNotification('Preparing export...', 'info');
            
            const format = document.getElementById('export-format').value;
            const range = document.getElementById('export-range').value;
            
            try {{
                const response = await callStreamlit('export_data', {{
                    format: format,
                    range: range
                }});
                
                if (response.download_url) {{
                    // Create download link
                    const a = document.createElement('a');
                    a.href = response.download_url;
                    a.download = `khisba_export.${{format}}`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    showNotification('Export downloaded!', 'success');
                }}
            }} catch (error) {{
                showNotification('Export failed: ' + error.message, 'error');
            }}
        }}
        
        // Share results
        function shareResults() {{
            showNotification('Share feature coming soon!', 'info');
        }}
        
        // Toggle panels
        function togglePanel(panel) {{
            const mainPanel = document.getElementById('main-panel');
            const resultsPanel = document.getElementById('results-panel');
            
            if (panel === 'main') {{
                mainPanel.style.display = mainPanel.style.display === 'none' ? 'block' : 'none';
            }} else if (panel === 'results') {{
                resultsPanel.style.display = resultsPanel.style.display === 'none' ? 'block' : 'none';
            }}
        }}
        
        // Switch tabs
        function switchTab(tabName) {{
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
                if (tab.textContent.toLowerCase() === tabName.toLowerCase()) {{
                    tab.classList.add('active');
                }}
            }});
            
            // Show corresponding content
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.style.display = 'none';
            }});
            document.getElementById(`tab-${{tabName}}`).style.display = 'block';
        }}
        
        // Reset view
        function resetView() {{
            map.flyTo({{
                center: [0, 20],
                zoom: 2,
                pitch: 45,
                bearing: 0,
                duration: 1500
            }});
        }}
        
        // Toggle fullscreen
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}
        
        // Show help
        function showHelp() {{
            showNotification('KHISBA GIS: 1) Select area 2) Configure analysis 3) Run analysis 4) View results', 'info');
        }}
        
        // Show notification
        function showNotification(message, type = 'info') {{
            const notification = document.getElementById('notification');
            const messageEl = document.getElementById('notification-message');
            
            messageEl.textContent = message;
            notification.style.display = 'block';
            
            // Set color based on type
            notification.style.borderColor = 
                type === 'error' ? '#ff4444' : 
                type === 'warning' ? '#ffaa00' : 
                type === 'success' ? '#00ff88' : '#00ff88';
            
            // Auto hide
            setTimeout(() => {{
                notification.style.display = 'none';
            }}, 5000);
        }}
        
        // Call Streamlit backend
        async function callStreamlit(action, data) {{
            const requestId = 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            
            return new Promise((resolve, reject) => {{
                // Send request to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit_request',
                    action: action,
                    data: data,
                    requestId: requestId
                }}, '*');
                
                // Listen for response
                const responseHandler = (event) => {{
                    if (event.data.type === 'streamlit_response' && event.data.requestId === requestId) {{
                        window.removeEventListener('message', responseHandler);
                        
                        if (event.data.success) {{
                            resolve(event.data.response);
                        }} else {{
                            reject(new Error(event.data.error));
                        }}
                    }}
                }};
                
                window.addEventListener('message', responseHandler);
                
                // Timeout after 30 seconds
                setTimeout(() => {{
                    window.removeEventListener('message', responseHandler);
                    reject(new Error('Request timeout'));
                }}, 30000);
            }});
        }}
        
        // Initialize when page loads
        window.addEventListener('DOMContentLoaded', initMap);
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                resetDrawing();
            }} else if (e.key === 'h' || e.key === 'H') {{
                togglePanel('main');
            }} else if (e.key === 'r' || e.key === 'R') {{
                togglePanel('results');
            }}
        }});
    </script>
</body>
</html>
"""

# Display the full-screen map
st.components.v1.html(mapbox_html, height=800, scrolling=False)

# Hidden Streamlit widgets for data processing
st.markdown('<div style="display: none;">', unsafe_allow_html=True)

# Create hidden input for JavaScript communication
js_request = st.text_input("JS Request", key="js_request", label_visibility="collapsed")

# Process JavaScript requests
if js_request:
    try:
        data = json.loads(js_request)
        action = data.get('action')
        request_id = data.get('requestId')
        
        response = {}
        
        if st.session_state.ee_initialized:
            if action == 'get_admin1':
                country = data.get('data', {}).get('country')
                if country:
                    try:
                        # Get country code
                        countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                        country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                        country_code = country_feature.get('ADM0_CODE').getInfo()
                        
                        # Get admin1 for this country
                        admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                        admin1_fc = admin1_fc.filter(ee.Filter.eq('ADM0_CODE', country_code))
                        admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().getInfo()
                        
                        response = {'admin1': sorted(admin1_names) if admin1_names else []}
                    except Exception as e:
                        response = {'error': f"Error loading provinces: {str(e)}"}
                        
            elif action == 'get_admin2':
                country = data.get('data', {}).get('country')
                admin1 = data.get('data', {}).get('admin1')
                
                if country and admin1:
                    try:
                        # First get the admin1 feature
                        admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', admin1)).first()
                        admin1_code = admin1_feature.get('ADM1_CODE').getInfo()
                        
                        # Get admin2 for this admin1
                        admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")
                        admin2_fc = admin2_fc.filter(ee.Filter.eq('ADM1_CODE', admin1_code))
                        admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                        
                        response = {'admin2': sorted(admin2_names) if admin2_names else []}
                    except Exception as e:
                        response = {'error': f"Error loading municipalities: {str(e)}"}
                        
            elif action == 'get_geometry':
                country = data.get('data', {}).get('country')
                admin1 = data.get('data', {}).get('admin1')
                admin2 = data.get('data', {}).get('admin2')
                
                try:
                    if admin2:
                        # Get municipality geometry
                        admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")
                        admin2_feature = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', admin2)).first()
                        geometry = admin2_feature.geometry()
                    elif admin1:
                        # Get province geometry
                        admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', admin1)).first()
                        geometry = admin1_feature.geometry()
                    else:
                        # Get country geometry
                        countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                        country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                        geometry = country_feature.geometry()
                    
                    # Convert to GeoJSON
                    bounds = geometry.bounds().getInfo()
                    coords = bounds['coordinates'][0]
                    
                    geojson = {
                        'type': 'Polygon',
                        'coordinates': [coords]
                    }
                    
                    response = {'geometry': geojson}
                    
                except Exception as e:
                    response = {'error': f"Error getting geometry: {str(e)}"}
                    
            elif action == 'create_custom_area':
                coordinates = data.get('data', {}).get('coordinates')
                
                if coordinates and len(coordinates) >= 3:
                    geojson = {
                        'type': 'Polygon',
                        'coordinates': [coordinates]
                    }
                    response = {'geometry': geojson}
                else:
                    response = {'error': 'Invalid coordinates'}
                    
            elif action == 'run_analysis':
                # Simplified analysis for demo
                response = {
                    'results': {
                        'NDVI': {'values': [0.4, 0.5, 0.6, 0.55, 0.52]},
                        'EVI': {'values': [0.3, 0.4, 0.5, 0.45, 0.42]},
                        'NDWI': {'values': [0.2, 0.3, 0.35, 0.32, 0.3]},
                        'SAVI': {'values': [0.35, 0.45, 0.55, 0.5, 0.48]}
                    }
                }
                
            elif action == 'export_data':
                response = {
                    'download_url': 'data:text/csv;base64,' + b64encode(b"test,data\n1,2\n3,4").decode()
                }
                
        else:
            response = {'error': 'Earth Engine not initialized'}
        
        # Send response back to JavaScript
        response_js = f"""
        <script>
        window.parent.postMessage({{
            type: 'streamlit_response',
            requestId: '{request_id}',
            success: {json.dumps('error' not in response)},
            response: {json.dumps(response)}
        }}, '*');
        </script>
        """
        
        st.components.v1.html(response_js, height=0)
        
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")

# Initialize communication script
init_script = """
<script>
// Listen for Streamlit requests
window.addEventListener('message', function(event) {
    if (event.data.type === 'streamlit_request') {
        // Forward to Streamlit
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'js-request-input';
        input.value = JSON.stringify(event.data);
        document.body.appendChild(input);
        
        // Trigger Streamlit
        const inputEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(inputEvent);
    }
});
</script>
"""

st.components.v1.html(init_script, height=0)

# Create the hidden input for JavaScript
st.markdown('<input type="hidden" id="js-request-input">', unsafe_allow_html=True)

# Keep Streamlit running
st.markdown('<div style="height: 1px;"></div>', unsafe_allow_html=True)
