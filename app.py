import streamlit as st
import json
import ee
import traceback

# Minimal CSS - Only hide Streamlit elements
st.markdown("""
<style>
    /* Hide all Streamlit elements */
    .stApp {
        padding: 0 !important;
        margin: 0 !important;
        background: #000 !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit widgets */
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Earth Engine Initialization
def auto_initialize_earth_engine():
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

# Initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    if auto_initialize_earth_engine():
        st.session_state.ee_initialized = True
    else:
        st.session_state.ee_initialized = False

# Initialize session state
if 'countries' not in st.session_state:
    st.session_state.countries = []

# Page config
st.set_page_config(
    page_title="KHISBA GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper function to get countries
def get_countries():
    try:
        countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
        countries = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
        return sorted(countries) if countries else []
    except:
        return []

# Load countries if Earth Engine is initialized
if st.session_state.ee_initialized and not st.session_state.countries:
    with st.spinner("Loading countries..."):
        st.session_state.countries = get_countries()

# Main Mapbox HTML/JS Interface
mapbox_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KHISBA GIS - All-in-One Map</title>
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; }}
        #map {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        
        /* Loading overlay */
        #loading {{ 
            position: absolute; 
            top: 0; left: 0; 
            width: 100%; height: 100%; 
            background: #000; 
            z-index: 9999; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            color: #00ff88; 
        }}
        .spinner {{ 
            width: 50px; height: 50px; 
            border: 3px solid rgba(255,255,255,0.1); 
            border-top: 3px solid #00ff88; 
            border-radius: 50%; 
            animation: spin 1s linear infinite; 
            margin-bottom: 20px; 
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        
        /* Control Panel */
        #control-panel {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            width: 300px;
            color: white;
            backdrop-filter: blur(10px);
        }}
        
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .panel-title {{
            color: #00ff88;
            font-size: 16px;
            font-weight: bold;
        }}
        
        .close-btn {{
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }}
        
        select, input, button {{
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 5px;
            color: white;
        }}
        
        button {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: black;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }}
        
        button:hover {{
            opacity: 0.9;
        }}
        
        /* Results Panel */
        #results-panel {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            width: 350px;
            max-height: 400px;
            overflow-y: auto;
            color: white;
            backdrop-filter: blur(10px);
            display: none;
        }}
        
        .chart-container {{
            width: 100%;
            height: 200px;
            margin: 10px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
        }}
        
        /* Notification */
        #notification {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            color: white;
            backdrop-filter: blur(10px);
            display: none;
        }}
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading">
        <div class="spinner"></div>
        <div>Loading KHISBA GIS...</div>
    </div>
    
    <!-- Map Container -->
    <div id="map"></div>
    
    <!-- Control Panel -->
    <div id="control-panel">
        <div class="panel-header">
            <div class="panel-title">🌍 KHISBA GIS</div>
            <button class="close-btn" onclick="togglePanel()">×</button>
        </div>
        
        <!-- Area Selection -->
        <div>
            <label>Country:</label>
            <select id="country-select" onchange="loadAdmin1()">
                <option value="">Select Country</option>
            </select>
            
            <label>State/Province:</label>
            <select id="admin1-select" onchange="loadAdmin2()" disabled>
                <option value="">Select State/Province</option>
            </select>
            
            <label>Municipality:</label>
            <select id="admin2-select" onchange="selectArea()" disabled>
                <option value="">Select Municipality</option>
            </select>
        </div>
        
        <!-- Analysis Parameters -->
        <div style="margin-top: 15px;">
            <label>Start Date:</label>
            <input type="date" id="start-date" value="2023-01-01">
            
            <label>End Date:</label>
            <input type="date" id="end-date" value="2023-12-31">
            
            <label>Satellite Source:</label>
            <select id="satellite-select">
                <option value="sentinel2">Sentinel-2</option>
                <option value="landsat8">Landsat-8</option>
            </select>
            
            <label>Max Cloud Cover: <span id="cloud-value">20%</span></label>
            <input type="range" id="cloud-slider" min="0" max="100" value="20" 
                   oninput="document.getElementById('cloud-value').textContent = this.value + '%'">
            
            <label>Vegetation Indices:</label>
            <div id="indices-container" style="max-height: 150px; overflow-y: auto; margin: 5px 0;">
                <!-- Indices will be added here -->
            </div>
            
            <button onclick="runAnalysis()" style="margin-top: 10px;">🚀 Run Analysis</button>
        </div>
    </div>
    
    <!-- Results Panel -->
    <div id="results-panel">
        <div class="panel-header">
            <div class="panel-title">📊 Analysis Results</div>
            <button class="close-btn" onclick="document.getElementById('results-panel').style.display = 'none'">×</button>
        </div>
        <div id="results-content">
            <!-- Results will be shown here -->
        </div>
    </div>
    
    <!-- Notification -->
    <div id="notification">
        <div id="notification-message">Notification</div>
    </div>

    <script>
        // Mapbox Access Token
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
        
        // Initialize Map
        const map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/satellite-streets-v12',
            center: [0, 20],
            zoom: 2,
            pitch: 45,
            bearing: 0
        }});
        
        // Add map controls
        map.addControl(new mapboxgl.NavigationControl());
        map.addControl(new mapboxgl.ScaleControl());
        
        // Global variables
        let selectedArea = null;
        let selectedGeometry = null;
        
        // When map loads
        map.on('load', () => {{
            // Hide loading screen
            document.getElementById('loading').style.display = 'none';
            
            // Load countries from Streamlit
            loadCountries();
            
            // Load vegetation indices
            loadIndices();
            
            // Show notification
            showNotification('KHISBA GIS Ready!');
        }});
        
        // Toggle control panel
        function togglePanel() {{
            const panel = document.getElementById('control-panel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }}
        
        // Show notification
        function showNotification(message, type = 'info') {{
            const notification = document.getElementById('notification');
            const messageEl = document.getElementById('notification-message');
            
            messageEl.textContent = message;
            notification.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(() => {{
                notification.style.display = 'none';
            }}, 3000);
        }}
        
        // Load countries
        function loadCountries() {{
            // Get countries from Streamlit
            const countries = {json.dumps(st.session_state.countries)};
            
            const select = document.getElementById('country-select');
            select.innerHTML = '<option value="">Select Country</option>';
            
            countries.forEach(country => {{
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            }});
            
            showNotification(`Loaded {len(st.session_state.countries)} countries`);
        }}
        
        // Load admin1 regions
        async function loadAdmin1() {{
            const country = document.getElementById('country-select').value;
            if (!country) return;
            
            const select = document.getElementById('admin1-select');
            select.disabled = true;
            select.innerHTML = '<option value="">Loading...</option>';
            
            try {{
                // Send request to Streamlit backend
                const response = await fetchStreamlit('load_admin1', {{ country: country }});
                const admin1List = response.admin1 || [];
                
                select.innerHTML = '<option value="">Select State/Province</option>';
                admin1List.forEach(admin1 => {{
                    const option = document.createElement('option');
                    option.value = admin1;
                    option.textContent = admin1;
                    select.appendChild(option);
                }});
                select.disabled = false;
                
                showNotification(`Loaded ${{admin1List.length}} regions for ${{country}}`);
            }} catch (error) {{
                showNotification('Error loading regions', 'error');
                console.error(error);
            }}
        }}
        
        // Load admin2 regions
        async function loadAdmin2() {{
            const admin1 = document.getElementById('admin1-select').value;
            const country = document.getElementById('country-select').value;
            if (!admin1 || !country) return;
            
            const select = document.getElementById('admin2-select');
            select.disabled = true;
            select.innerHTML = '<option value="">Loading...</option>';
            
            try {{
                const response = await fetchStreamlit('load_admin2', {{ 
                    admin1: admin1, 
                    country: country 
                }});
                const admin2List = response.admin2 || [];
                
                select.innerHTML = '<option value="">Select Municipality</option>';
                admin2List.forEach(admin2 => {{
                    const option = document.createElement('option');
                    option.value = admin2;
                    option.textContent = admin2;
                    select.appendChild(option);
                }});
                select.disabled = false;
                
                showNotification(`Loaded ${{admin2List.length}} municipalities`);
            }} catch (error) {{
                showNotification('Error loading municipalities', 'error');
                console.error(error);
            }}
        }}
        
        // Select area
        async function selectArea() {{
            const country = document.getElementById('country-select').value;
            const admin1 = document.getElementById('admin1-select').value;
            const admin2 = document.getElementById('admin2-select').value;
            
            if (!country) {{
                showNotification('Please select a country first', 'error');
                return;
            }}
            
            let areaName = country;
            let level = 'country';
            
            if (admin1 && admin2) {{
                areaName = `${{admin2}}, ${{admin1}}, ${{country}}`;
                level = 'municipality';
            }} else if (admin1) {{
                areaName = `${{admin1}}, ${{country}}`;
                level = 'state';
            }}
            
            try {{
                const response = await fetchStreamlit('select_area', {{
                    country: country,
                    admin1: admin1,
                    admin2: admin2,
                    level: level
                }});
                
                if (response.geometry) {{
                    showAreaOnMap(response.geometry, areaName);
                    selectedArea = areaName;
                    showNotification(`Selected: ${{areaName}}`);
                }}
            }} catch (error) {{
                showNotification('Error selecting area', 'error');
                console.error(error);
            }}
        }}
        
        // Load vegetation indices
        function loadIndices() {{
            const indices = [
                'NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 
                'MSAVI', 'ARVI', 'VARI', 'OSAVI'
            ];
            
            const container = document.getElementById('indices-container');
            indices.forEach(index => {{
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.margin = '2px 0';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `index-${{index}}`;
                checkbox.value = index;
                checkbox.checked = index === 'NDVI' || index === 'EVI';
                
                const label = document.createElement('label');
                label.htmlFor = `index-${{index}}`;
                label.textContent = index;
                label.style.marginLeft = '5px';
                label.style.color = 'white';
                label.style.fontSize = '12px';
                
                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            }});
        }}
        
        // Run analysis
        async function runAnalysis() {{
            if (!selectedArea) {{
                showNotification('Please select an area first', 'error');
                return;
            }}
            
            // Get selected indices
            const selectedIndices = [];
            document.querySelectorAll('#indices-container input[type="checkbox"]:checked').forEach(cb => {{
                selectedIndices.push(cb.value);
            }});
            
            if (selectedIndices.length === 0) {{
                showNotification('Please select at least one vegetation index', 'error');
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
            
            showNotification('Running analysis...', 'info');
            
            try {{
                const response = await fetchStreamlit('run_analysis', params);
                
                if (response.results) {{
                    displayResults(response.results);
                    showNotification('Analysis complete!', 'success');
                }} else {{
                    showNotification(response.error || 'Analysis failed', 'error');
                }}
            }} catch (error) {{
                showNotification('Error running analysis: ' + error.message, 'error');
                console.error(error);
            }}
        }}
        
        // Display results
        function displayResults(results) {{
            const content = document.getElementById('results-content');
            const panel = document.getElementById('results-panel');
            
            let html = '<h3 style="color: #00ff88; margin-bottom: 10px;">Results for ' + selectedArea + '</h3>';
            
            // Show summary
            html += '<div style="margin-bottom: 15px;">';
            html += '<h4>Summary Statistics</h4>';
            
            Object.keys(results).forEach(index => {{
                const data = results[index];
                if (data.values && data.values.length > 0) {{
                    const values = data.values.filter(v => v !== null);
                    const avg = values.reduce((a, b) => a + b, 0) / values.length;
                    const max = Math.max(...values);
                    const min = Math.min(...values);
                    
                    html += `<div style="margin: 5px 0; padding: 5px; background: rgba(255,255,255,0.05); border-radius: 3px;">
                        <strong>${{index}}</strong>: Avg: ${{avg.toFixed(4)}}, Min: ${{min.toFixed(4)}}, Max: ${{max.toFixed(4)}}
                    </div>`;
                }}
            }});
            
            html += '</div>';
            
            // Add chart placeholders
            html += '<div style="margin-top: 15px;">';
            html += '<h4>Charts</h4>';
            Object.keys(results).forEach(index => {{
                html += `<div class="chart-container" id="chart-${{index}}"></div>`;
            }});
            html += '</div>';
            
            content.innerHTML = html;
            panel.style.display = 'block';
            
            // Create simple charts
            Object.keys(results).forEach(index => {{
                createSimpleChart(index, results[index]);
            }});
        }}
        
        // Create simple chart
        function createSimpleChart(index, data) {{
            if (!data.dates || !data.values || data.values.length === 0) return;
            
            const canvasId = `chart-${{index}}`;
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            // Create canvas if it doesn't exist
            if (!canvas.querySelector('canvas')) {{
                const realCanvas = document.createElement('canvas');
                realCanvas.width = 300;
                realCanvas.height = 100;
                canvas.appendChild(realCanvas);
            }}
            
            const ctx = canvas.querySelector('canvas').getContext('2d');
            const width = 300;
            const height = 100;
            
            // Clear canvas
            ctx.clearRect(0, 0, width, height);
            
            // Get data points (limit to 20 for simplicity)
            const values = data.values.slice(0, 20);
            const maxVal = Math.max(...values);
            const minVal = Math.min(...values);
            const range = maxVal - minVal || 1;
            
            // Draw line
            ctx.beginPath();
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 2;
            
            values.forEach((val, i) => {{
                const x = (i / (values.length - 1)) * width;
                const y = height - ((val - minVal) / range) * height * 0.8 - 10;
                
                if (i === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }});
            
            ctx.stroke();
        }}
        
        // Show area on map
        function showAreaOnMap(geometry, areaName) {{
            // Remove existing area
            if (map.getSource('selected-area')) {{
                map.removeLayer('selected-area-fill');
                map.removeLayer('selected-area-border');
                map.removeSource('selected-area');
            }}
            
            // Add new area
            map.addSource('selected-area', {{
                type: 'geojson',
                data: geometry
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
                    'line-width': 2
                }}
            }});
            
            // Fly to area
            const bounds = new mapboxgl.LngLatBounds();
            geometry.coordinates[0].forEach(coord => {{
                bounds.extend(coord);
            }});
            
            map.fitBounds(bounds, {{
                padding: 50,
                duration: 1000
            }});
        }}
        
        // Fetch data from Streamlit backend
        async function fetchStreamlit(action, data) {{
            // Create a unique ID for this request
            const requestId = Math.random().toString(36).substr(2, 9);
            
            // Create a hidden input to send data to Streamlit
            const input = document.createElement('input');
            input.type = 'hidden';
            input.id = 'streamlit-data-' + requestId;
            input.value = JSON.stringify({{ action: action, data: data, id: requestId }});
            document.body.appendChild(input);
            
            // Trigger Streamlit
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            
            // Wait for response
            return new Promise((resolve, reject) => {{
                const checkResponse = setInterval(() => {{
                    const responseInput = document.getElementById('streamlit-response-' + requestId);
                    if (responseInput) {{
                        clearInterval(checkResponse);
                        try {{
                            const response = JSON.parse(responseInput.value);
                            responseInput.remove();
                            input.remove();
                            resolve(response);
                        }} catch (error) {{
                            reject(error);
                        }}
                    }}
                }}, 100);
                
                // Timeout after 30 seconds
                setTimeout(() => {{
                    clearInterval(checkResponse);
                    reject(new Error('Request timeout'));
                }}, 30000);
            }});
        }}
    </script>
</body>
</html>
"""

# Display the map
st.components.v1.html(mapbox_html, height=700, scrolling=False)

# Hidden inputs for JavaScript-Streamlit communication
st.markdown('<div style="display: none;">', unsafe_allow_html=True)

# Create input for receiving JavaScript data
js_data = st.text_input("JS Data", key="js_data", label_visibility="collapsed")

# Create output for sending data back to JavaScript
response_data = st.text_input("Response Data", key="response_data", label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# Process JavaScript requests
if js_data:
    try:
        data = json.loads(js_data)
        action = data.get('action')
        request_id = data.get('id')
        
        response = {}
        
        if action == 'load_admin1':
            country = data.get('data', {}).get('country')
            if country and st.session_state.ee_initialized:
                try:
                    countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                    country_code = country_feature.get('ADM0_CODE').getInfo()
                    
                    admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                    admin1_fc = admin1_fc.filter(ee.Filter.eq('ADM0_CODE', country_code))
                    admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().getInfo()
                    
                    response = {'admin1': sorted(admin1_names) if admin1_names else []}
                except Exception as e:
                    response = {'error': str(e)}
        
        elif action == 'load_admin2':
            admin1 = data.get('data', {}).get('admin1')
            country = data.get('data', {}).get('country')
            
            if admin1 and country and st.session_state.ee_initialized:
                try:
                    # First get the admin1 code
                    admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                    admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', admin1)).first()
                    admin1_code = admin1_feature.get('ADM1_CODE').getInfo()
                    
                    # Then get admin2 for that admin1
                    admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")
                    admin2_fc = admin2_fc.filter(ee.Filter.eq('ADM1_CODE', admin1_code))
                    admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                    
                    response = {'admin2': sorted(admin2_names) if admin2_names else []}
                except Exception as e:
                    response = {'error': str(e)}
        
        elif action == 'select_area':
            country = data.get('data', {}).get('country')
            admin1 = data.get('data', {}).get('admin1')
            admin2 = data.get('data', {}).get('admin2')
            
            if country and st.session_state.ee_initialized:
                try:
                    # Get the geometry
                    if admin2:
                        admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")
                        admin2_feature = admin2_fc.filter(ee.Filter.eq('ADM2_NAME', admin2)).first()
                        geometry = admin2_feature.geometry()
                    elif admin1:
                        admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', admin1)).first()
                        geometry = admin1_feature.geometry()
                    else:
                        countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                        country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                        geometry = country_feature.geometry()
                    
                    # Get bounds and create GeoJSON
                    bounds = geometry.bounds().getInfo()
                    coords = bounds['coordinates'][0]
                    
                    geojson = {
                        'type': 'Polygon',
                        'coordinates': [coords]
                    }
                    
                    response = {'geometry': geojson}
                    
                except Exception as e:
                    response = {'error': str(e)}
        
        elif action == 'run_analysis':
            # Simplified analysis for demo
            response = {
                'results': {
                    'NDVI': {
                        'dates': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
                        'values': [0.4, 0.5, 0.6, 0.55]
                    },
                    'EVI': {
                        'dates': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
                        'values': [0.3, 0.4, 0.5, 0.45]
                    }
                }
            }
        
        # Send response back to JavaScript
        response_js = f"""
        <script>
        // Create response input
        const responseInput = document.createElement('input');
        responseInput.type = 'hidden';
        responseInput.id = 'streamlit-response-{request_id}';
        responseInput.value = '{json.dumps(response)}';
        document.body.appendChild(responseInput);
        </script>
        """
        
        st.components.v1.html(response_js, height=0)
        
    except json.JSONDecodeError:
        pass

# Keep Streamlit alive
st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
