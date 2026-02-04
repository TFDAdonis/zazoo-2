import streamlit as st
import json

# Minimal Streamlit app that just loads the HTML
st.set_page_config(
    page_title="KHISBA GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load countries (pre-loaded for simplicity)
countries = [
    "United States", "Canada", "Mexico", "United Kingdom", "France", "Germany",
    "Spain", "Italy", "Australia", "Brazil", "India", "China", "Japan",
    "South Africa", "Egypt", "Nigeria", "Kenya", "Saudi Arabia", "Turkey",
    "Russia", "Argentina", "Chile", "Colombia", "Peru", "Indonesia",
    "Malaysia", "Thailand", "Vietnam", "Pakistan", "Bangladesh"
]

# Create the complete HTML/JS app
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KHISBA GIS - Full Screen</title>
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
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
            z-index: 1;
        }}

        /* Loading screen */
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
            transition: opacity 0.5s;
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
        #control-panel {{
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #00ff88;
            border-radius: 15px;
            padding: 20px;
            width: 350px;
            max-height: 80vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
            display: block;
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
            font-size: 22px;
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
            transition: all 0.2s;
        }}

        .close-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
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
            padding: 10px 5px;
            text-align: center;
            background: none;
            border: none;
            color: #999;
            font-size: 12px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .tab:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        .tab.active {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
        }}

        /* Form elements */
        .form-group {{
            margin-bottom: 15px;
        }}

        .form-label {{
            display: block;
            color: #00ff88;
            font-size: 11px;
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
            cursor: pointer;
        }}

        .form-select:hover, .form-input:hover {{
            border-color: rgba(0, 255, 136, 0.3);
        }}

        .form-select:focus, .form-input:focus {{
            border-color: #00ff88;
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
        }}

        .form-select option {{
            background: #000;
            color: white;
        }}

        /* Buttons */
        .btn {{
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }}

        .btn:active {{
            transform: translateY(0);
        }}

        .btn-primary {{
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            color: #000;
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
            gap: 8px;
            margin: 15px 0;
            max-height: 180px;
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

        .checkbox-input {{
            display: none;
        }}

        .checkbox-label {{
            color: white;
            font-size: 12px;
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
            width: 380px;
            max-height: 70vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
            display: none;
        }}

        .result-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }}

        .result-title {{
            color: #00ff88;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .result-value {{
            color: white;
            font-size: 20px;
            font-weight: 700;
        }}

        /* Notification */
        #notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px 20px;
            color: white;
            backdrop-filter: blur(10px);
            display: none;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
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

        /* Custom scrollbar */
        #control-panel::-webkit-scrollbar,
        #results-panel::-webkit-scrollbar,
        .checkbox-grid::-webkit-scrollbar {{
            width: 6px;
        }}

        #control-panel::-webkit-scrollbar-track,
        #results-panel::-webkit-scrollbar-track,
        .checkbox-grid::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }}

        #control-panel::-webkit-scrollbar-thumb,
        #results-panel::-webkit-scrollbar-thumb,
        .checkbox-grid::-webkit-scrollbar-thumb {{
            background: rgba(0, 255, 136, 0.5);
            border-radius: 10px;
        }}

        #control-panel::-webkit-scrollbar-thumb:hover,
        #results-panel::-webkit-scrollbar-thumb:hover,
        .checkbox-grid::-webkit-scrollbar-thumb:hover {{
            background: rgba(0, 255, 136, 0.8);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            #control-panel, #results-panel {{
                width: calc(100vw - 40px);
                left: 20px;
                right: 20px;
            }}

            #control-panel {{
                top: 10px;
                max-height: 70vh;
            }}

            #results-panel {{
                bottom: 10px;
                max-height: 50vh;
            }}

            #quick-actions {{
                bottom: 10px;
                padding: 8px 15px;
            }}

            .app-title {{
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-overlay">
        <div class="spinner"></div>
        <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">KHISBA GIS</div>
        <div style="color: #999; font-size: 14px;">Loading 3D Global Vegetation Analysis...</div>
    </div>

    <!-- Map Container -->
    <div id="map"></div>

    <!-- Main Control Panel -->
    <div id="control-panel">
        <div class="panel-header">
            <div class="app-title"><i class="fas fa-globe-americas"></i> KHISBA GIS</div>
            <button class="close-btn" onclick="togglePanel('control')">×</button>
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
                <label class="form-label"><i class="fas fa-flag"></i> Country</label>
                <select class="form-select" id="country-select" onchange="onCountryChange()">
                    <option value="">Select a country</option>
                    <!-- Countries will be loaded here -->
                </select>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-map"></i> State/Province</label>
                <select class="form-select" id="admin1-select" onchange="onAdmin1Change()" disabled>
                    <option value="">Select state/province</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-city"></i> Municipality</label>
                <select class="form-select" id="admin2-select" onchange="onAdmin2Change()" disabled>
                    <option value="">Select municipality</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-draw-polygon"></i> Or Draw Area</label>
                <div style="display: flex; gap: 8px; margin-top: 8px;">
                    <button class="btn-secondary" onclick="startDrawing('polygon')" style="flex: 1;">
                        <i class="fas fa-draw-polygon"></i> Polygon
                    </button>
                    <button class="btn-secondary" onclick="startDrawing('rectangle')" style="flex: 1;">
                        <i class="fas fa-square"></i> Rectangle
                    </button>
                </div>
            </div>

            <div id="selected-area-preview" style="display: none; margin-top: 15px; padding: 15px; background: rgba(0, 255, 136, 0.1); border-radius: 8px;">
                <div style="color: #00ff88; font-weight: 600; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-map-marker-alt"></i> Selected Area
                </div>
                <div id="selected-area-name" style="color: white; font-weight: 500; font-size: 14px; margin-bottom: 5px;"></div>
                <div id="selected-area-details" style="color: #999; font-size: 11px;"></div>
            </div>

            <button class="btn-primary" onclick="confirmSelection()" style="margin-top: 15px;">
                <i class="fas fa-check-circle"></i> Confirm Selection
            </button>
        </div>

        <!-- Tab Content: Analyze -->
        <div id="tab-analyze" class="tab-content" style="display: none;">
            <div class="form-group">
                <label class="form-label"><i class="fas fa-calendar-alt"></i> Time Period</label>
                <div style="display: flex; gap: 10px;">
                    <input type="date" class="form-input" id="start-date" value="2023-01-01" style="flex: 1;">
                    <input type="date" class="form-input" id="end-date" value="2023-12-31" style="flex: 1;">
                </div>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-satellite"></i> Satellite Source</label>
                <select class="form-select" id="satellite-select">
                    <option value="sentinel2">Sentinel-2</option>
                    <option value="landsat8">Landsat-8</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-cloud"></i> Max Cloud Cover: <span id="cloud-value" style="color: #00ff88; font-weight: 600;">20%</span></label>
                <input type="range" class="form-input" id="cloud-slider" min="0" max="100" value="20" 
                       oninput="document.getElementById('cloud-value').textContent = this.value + '%'" style="width: 100%; padding: 0;">
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-leaf"></i> Vegetation Indices</label>
                <div class="checkbox-grid" id="indices-container">
                    <!-- Indices will be loaded here -->
                </div>
                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    <button class="btn-secondary" onclick="selectAllIndices()" style="flex: 1;">
                        <i class="fas fa-check-double"></i> Select All
                    </button>
                    <button class="btn-secondary" onclick="clearAllIndices()" style="flex: 1;">
                        <i class="fas fa-times"></i> Clear All
                    </button>
                </div>
            </div>

            <button class="btn-primary" onclick="runAnalysis()">
                <i class="fas fa-rocket"></i> Run Analysis
            </button>
        </div>

        <!-- Tab Content: Export -->
        <div id="tab-export" class="tab-content" style="display: none;">
            <div style="color: #999; font-size: 13px; margin-bottom: 20px; line-height: 1.5;">
                <i class="fas fa-info-circle"></i> Export your analysis results in various formats
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-file-export"></i> Export Format</label>
                <select class="form-select" id="export-format">
                    <option value="csv">CSV Data</option>
                    <option value="json">JSON Format</option>
                    <option value="geojson">GeoJSON</option>
                    <option value="png">Chart Image</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label"><i class="fas fa-filter"></i> Data Range</label>
                <select class="form-select" id="export-range">
                    <option value="full">Full Dataset</option>
                    <option value="monthly">Monthly Averages</option>
                    <option value="summary">Summary Statistics</option>
                </select>
            </div>

            <button class="btn-primary" onclick="exportData()">
                <i class="fas fa-download"></i> Download Export
            </button>
            <button class="btn-secondary" onclick="shareResults()" style="margin-top: 10px;">
                <i class="fas fa-share-alt"></i> Share Results
            </button>
        </div>
    </div>

    <!-- Results Panel -->
    <div id="results-panel">
        <div class="panel-header">
            <div class="app-title" style="font-size: 18px;"><i class="fas fa-chart-bar"></i> Analysis Results</div>
            <button class="close-btn" onclick="togglePanel('results')">×</button>
        </div>
        <div id="results-content">
            <!-- Results will be loaded here -->
        </div>
    </div>

    <!-- Quick Actions Bar -->
    <div id="quick-actions">
        <button class="action-btn" onclick="togglePanel('control')" title="Control Panel">
            <i class="fas fa-sliders-h"></i>
        </button>
        <button class="action-btn" onclick="togglePanel('results')" title="Results">
            <i class="fas fa-chart-line"></i>
        </button>
        <button class="action-btn" onclick="resetView()" title="Reset View">
            <i class="fas fa-home"></i>
        </button>
        <button class="action-btn" onclick="toggleFullscreen()" title="Full Screen">
            <i class="fas fa-expand"></i>
        </button>
        <button class="action-btn" onclick="showHelp()" title="Help">
            <i class="fas fa-question"></i>
        </button>
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
        let drawPolygon = null;
        
        // Sample data for demo
        const sampleAdmin1Data = {{
            "United States": ["California", "Texas", "New York", "Florida", "Illinois", "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan"],
            "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick", "Newfoundland", "Prince Edward Island"],
            "Mexico": ["Mexico City", "Jalisco", "Veracruz", "Puebla", "Guanajuato", "Chiapas", "Nuevo León", "Michoacán", "Oaxaca", "Chihuahua"],
            "United Kingdom": ["England", "Scotland", "Wales", "Northern Ireland"],
            "France": ["Île-de-France", "Provence-Alpes-Côte d'Azur", "Auvergne-Rhône-Alpes", "Occitanie", "Nouvelle-Aquitaine"],
            "Germany": ["Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony", "Hesse"],
            "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia"],
            "Brazil": ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia", "Rio Grande do Sul"],
            "India": ["Maharashtra", "Uttar Pradesh", "Delhi", "Karnataka", "Tamil Nadu"],
            "China": ["Beijing", "Shanghai", "Guangdong", "Jiangsu", "Zhejiang"]
        }};
        
        const sampleAdmin2Data = {{
            "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
            "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
            "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse"],
            "Ontario": ["Toronto", "Ottawa", "Mississauga", "Brampton", "Hamilton"],
            "Quebec": ["Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil"],
            "England": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds"],
            "Scotland": ["Glasgow", "Edinburgh", "Aberdeen", "Dundee", "Inverness"],
            "Bavaria": ["Munich", "Nuremberg", "Augsburg", "Regensburg", "Ingolstadt"],
            "New South Wales": ["Sydney", "Newcastle", "Wollongong", "Central Coast", "Blue Mountains"],
            "São Paulo": ["São Paulo City", "Campinas", "São Bernardo do Campo", "Santo André", "Osasco"]
        }};
        
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
                attributionControl: false,
                interactive: true
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
                setTimeout(() => {{
                    document.getElementById('loading-overlay').style.opacity = '0';
                    setTimeout(() => {{
                        document.getElementById('loading-overlay').style.display = 'none';
                    }}, 500);
                }}, 1000);
                
                // Load initial data
                loadCountries();
                loadIndices();
                
                // Show welcome message
                setTimeout(() => {{
                    showNotification('🌍 KHISBA GIS Ready! Select an area to begin analysis.', 'info');
                }}, 1500);
            }});
            
            // Make sure map is interactive
            map.on('render', () => {{
                map.resize();
            }});
        }}
        
        // Load countries
        function loadCountries() {{
            const countries = {json.dumps(countries)};
            const select = document.getElementById('country-select');
            
            countries.forEach(country => {{
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            }});
        }}
        
        // When country changes
        function onCountryChange() {{
            const country = document.getElementById('country-select').value;
            if (!country) return;
            
            const admin1Select = document.getElementById('admin1-select');
            admin1Select.disabled = false;
            admin1Select.innerHTML = '<option value="">Select state/province</option>';
            
            // Load from sample data or show message
            if (sampleAdmin1Data[country]) {{
                sampleAdmin1Data[country].forEach(admin1 => {{
                    const option = document.createElement('option');
                    option.value = admin1;
                    option.textContent = admin1;
                    admin1Select.appendChild(option);
                }});
                showNotification(`Loaded ${{sampleAdmin1Data[country].length}} provinces for ${{country}}`, 'success');
            }} else {{
                // Demo mode - create sample provinces
                for (let i = 1; i <= 5; i++) {{
                    const option = document.createElement('option');
                    option.value = `Province ${{i}}`;
                    option.textContent = `Province ${{i}}`;
                    admin1Select.appendChild(option);
                }}
                showNotification(`Demo: Showing sample provinces for ${{country}}`, 'info');
            }}
            
            // Reset admin2
            const admin2Select = document.getElementById('admin2-select');
            admin2Select.innerHTML = '<option value="">Select municipality</option>';
            admin2Select.disabled = true;
            
            updateSelectedAreaPreview();
        }}
        
        // When admin1 changes
        function onAdmin1Change() {{
            const admin1 = document.getElementById('admin1-select').value;
            const country = document.getElementById('country-select').value;
            if (!admin1 || !country) return;
            
            const admin2Select = document.getElementById('admin2-select');
            admin2Select.disabled = false;
            admin2Select.innerHTML = '<option value="">Select municipality</option>';
            
            // Load from sample data or show message
            const key = admin1;
            if (sampleAdmin2Data[key]) {{
                sampleAdmin2Data[key].forEach(admin2 => {{
                    const option = document.createElement('option');
                    option.value = admin2;
                    option.textContent = admin2;
                    admin2Select.appendChild(option);
                }});
                showNotification(`Loaded ${{sampleAdmin2Data[key].length}} municipalities`, 'success');
            }} else {{
                // Demo mode - create sample municipalities
                for (let i = 1; i <= 5; i++) {{
                    const option = document.createElement('option');
                    option.value = `Municipality ${{i}}`;
                    option.textContent = `Municipality ${{i}}`;
                    admin2Select.appendChild(option);
                }}
                showNotification(`Demo: Showing sample municipalities`, 'info');
            }}
            
            updateSelectedAreaPreview();
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
            
            if (!country) {{
                document.getElementById('selected-area-preview').style.display = 'none';
                return;
            }}
            
            let areaName = country;
            let details = 'Country level analysis';
            
            if (admin1 && admin2) {{
                areaName = `${{admin2}}, ${{admin1}}`;
                details = `Municipality in ${{country}}`;
            }} else if (admin1) {{
                areaName = `${{admin1}}, ${{country}}`;
                details = 'Province level analysis';
            }}
            
            document.getElementById('selected-area-name').textContent = areaName;
            document.getElementById('selected-area-details').textContent = details;
            document.getElementById('selected-area-preview').style.display = 'block';
            
            selectedArea = areaName;
        }}
        
        // Confirm selection
        function confirmSelection() {{
            if (!selectedArea) {{
                showNotification('Please select an area first', 'warning');
                return;
            }}
            
            const country = document.getElementById('country-select').value;
            const admin1 = document.getElementById('admin1-select').value;
            const admin2 = document.getElementById('admin2-select').value;
            
            showNotification(`Selected: ${{selectedArea}}`, 'success');
            
            // Generate sample geometry based on selection
            let center, zoom;
            
            if (admin2) {{
                // Municipality level - zoomed in
                center = [getRandomLon(-120, -70), getRandomLat(25, 45)];
                zoom = 10;
            }} else if (admin1) {{
                // Province level
                center = [getRandomLon(-130, -65), getRandomLat(20, 50)];
                zoom = 7;
            }} else {{
                // Country level
                if (country === "United States") {{
                    center = [-98.5, 39.5];
                    zoom = 4;
                }} else if (country === "Canada") {{
                    center = [-106.3, 56.1];
                    zoom = 3;
                }} else {{
                    center = [getRandomLon(-180, 180), getRandomLat(-60, 70)];
                    zoom = 5;
                }}
            }}
            
            // Create a sample bounding box
            const bounds = createBoundingBox(center[0], center[1], zoom);
            showAreaOnMap(bounds);
            
            // Switch to analyze tab
            switchTab('analyze');
        }}
        
        // Helper function to create bounding box
        function createBoundingBox(lon, lat, zoom) {{
            const size = 100 / zoom; // Size depends on zoom level
            return [
                [lon - size, lat - size],
                [lon + size, lat - size],
                [lon + size, lat + size],
                [lon - size, lat + size],
                [lon - size, lat - size] // Close the polygon
            ];
        }}
        
        // Helper functions for random coordinates
        function getRandomLon(min, max) {{
            return Math.random() * (max - min) + min;
        }}
        
        function getRandomLat(min, max) {{
            return Math.random() * (max - min) + min;
        }}
        
        // Start drawing on map
        function startDrawing(mode) {{
            drawingMode = mode;
            drawnPoints = [];
            
            showNotification(`Click on map to draw ${{mode === 'polygon' ? 'polygon points' : 'rectangle corners'}}. Double-click to finish.`, 'info');
            
            // Change cursor
            map.getCanvas().style.cursor = 'crosshair';
            
            // Setup click handler
            map.once('click', handleDrawingClick);
        }}
        
        // Handle drawing clicks
        function handleDrawingClick(e) {{
            if (!drawingMode) return;
            
            drawnPoints.push([e.lngLat.lng, e.lngLat.lat]);
            
            // Remove existing drawing layer if any
            if (drawPolygon) {{
                map.removeLayer('draw-polygon-fill');
                map.removeLayer('draw-polygon-border');
                map.removeSource('draw-polygon');
            }}
            
            // Show preview of drawn area
            if (drawnPoints.length > 1) {{
                let previewCoords = drawnPoints;
                
                if (drawingMode === 'rectangle' && drawnPoints.length === 2) {{
                    const [p1, p2] = drawnPoints;
                    previewCoords = [
                        p1,
                        [p2[0], p1[1]],
                        p2,
                        [p1[0], p2[1]],
                        p1
                    ];
                }}
                
                if (drawingMode === 'polygon') {{
                    previewCoords.push(drawnPoints[0]); // Close polygon for preview
                }}
                
                map.addSource('draw-polygon', {{
                    type: 'geojson',
                    data: {{
                        type: 'Feature',
                        geometry: {{
                            type: 'Polygon',
                            coordinates: [previewCoords]
                        }}
                    }}
                }});
                
                map.addLayer({{
                    id: 'draw-polygon-fill',
                    type: 'fill',
                    source: 'draw-polygon',
                    paint: {{
                        'fill-color': '#00ff88',
                        'fill-opacity': 0.1
                    }}
                }});
                
                map.addLayer({{
                    id: 'draw-polygon-border',
                    type: 'line',
                    source: 'draw-polygon',
                    paint: {{
                        'line-color': '#00ff88',
                        'line-width': 2,
                        'line-dasharray': [2, 2]
                    }}
                }});
                
                drawPolygon = true;
            }}
            
            // For rectangle, complete after 2 points
            if (drawingMode === 'rectangle' && drawnPoints.length === 2) {{
                completeDrawing();
            }} else {{
                // Continue listening for clicks
                map.once('click', handleDrawingClick);
            }}
        }}
        
        // Complete drawing (on double-click)
        map.on('dblclick', () => {{
            if (drawingMode === 'polygon' && drawnPoints.length >= 3) {{
                completeDrawing();
            }}
        }});
        
        // Complete drawing process
        function completeDrawing() {{
            if (!drawingMode || drawnPoints.length < (drawingMode === 'rectangle' ? 2 : 3)) return;
            
            let finalCoords = drawnPoints;
            
            if (drawingMode === 'rectangle' && drawnPoints.length === 2) {{
                const [p1, p2] = drawnPoints;
                finalCoords = [
                    p1,
                    [p2[0], p1[1]],
                    p2,
                    [p1[0], p2[1]],
                    p1
                ];
            }} else if (drawingMode === 'polygon') {{
                finalCoords.push(drawnPoints[0]); // Close polygon
            }}
            
            // Show the drawn area
            showAreaOnMap(finalCoords);
            
            // Update selected area preview
            selectedArea = `${{drawingMode === 'rectangle' ? 'Rectangle' : 'Polygon'}} Area`;
            document.getElementById('selected-area-name').textContent = selectedArea;
            document.getElementById('selected-area-details').textContent = `${{drawnPoints.length}} points drawn`;
            document.getElementById('selected-area-preview').style.display = 'block';
            
            showNotification(`${{drawingMode === 'rectangle' ? 'Rectangle' : 'Polygon'}} created successfully!`, 'success');
            
            // Clean up
            resetDrawing();
            
            // Switch to analyze tab
            switchTab('analyze');
        }}
        
        // Reset drawing state
        function resetDrawing() {{
            drawingMode = null;
            drawnPoints = [];
            
            // Remove drawing layers
            if (drawPolygon) {{
                map.removeLayer('draw-polygon-fill');
                map.removeLayer('draw-polygon-border');
                map.removeSource('draw-polygon');
                drawPolygon = null;
            }}
            
            // Reset cursor
            map.getCanvas().style.cursor = '';
            
            // Remove click listeners
            map.off('click', handleDrawingClick);
        }}
        
        // Show area on map
        function showAreaOnMap(coordinates) {{
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
                    geometry: {{
                        type: 'Polygon',
                        coordinates: [coordinates]
                    }},
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
            
            // Calculate bounds and zoom to area
            const bounds = new mapboxgl.LngLatBounds();
            coordinates.forEach(coord => {{
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
                    <input type="checkbox" class="checkbox-input" id="index-${{index}}" value="${{index}}" 
                           ${{index === 'NDVI' || index === 'EVI' ? 'checked' : ''}}>
                    <label class="checkbox-label" for="index-${{index}}">${{index}}</label>
                `;
                container.appendChild(div);
                
                // Add click handler
                div.addEventListener('click', function(e) {{
                    e.stopPropagation();
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
            showNotification('All indices selected', 'success');
        }}
        
        // Clear all indices
        function clearAllIndices() {{
            document.querySelectorAll('#indices-container .checkbox-item').forEach(item => {{
                item.classList.remove('selected');
                item.querySelector('input').checked = false;
            }});
            showNotification('All indices cleared', 'info');
        }}
        
        // Run analysis
        function runAnalysis() {{
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
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            const satellite = document.getElementById('satellite-select').value;
            const cloudCover = document.getElementById('cloud-slider').value;
            
            showNotification(`Running analysis for ${{selectedArea}}...`, 'info');
            
            // Simulate analysis (in real app, this would call an API)
            setTimeout(() => {{
                // Generate sample results
                const results = {{}};
                selectedIndices.forEach(index => {{
                    const values = [];
                    for (let i = 0; i < 12; i++) {{
                        // Generate realistic values for each index
                        let baseValue = 0;
                        switch(index) {{
                            case 'NDVI': baseValue = 0.6; break;
                            case 'EVI': baseValue = 0.4; break;
                            case 'NDWI': baseValue = 0.3; break;
                            case 'SAVI': baseValue = 0.5; break;
                            default: baseValue = 0.4;
                        }}
                        // Add some variation
                        values.push(baseValue + (Math.random() * 0.3 - 0.15));
                    }}
                    results[index] = {{
                        values: values,
                        average: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(4),
                        min: Math.min(...values).toFixed(4),
                        max: Math.max(...values).toFixed(4)
                    }};
                }});
                
                displayResults(results);
                showNotification('Analysis complete! Results are ready.', 'success');
            }}, 2000);
        }}
        
        // Display results
        function displayResults(results) {{
            const content = document.getElementById('results-content');
            const panel = document.getElementById('results-panel');
            
            let html = `
                <div style="color: #00ff88; font-weight: 600; margin-bottom: 15px; font-size: 16px;">
                    <i class="fas fa-map-marker-alt"></i> ${{selectedArea}}
                </div>
                <div style="color: #999; margin-bottom: 20px; font-size: 12px;">
                    Analysis completed with ${{Object.keys(results).length}} vegetation indices
                </div>
            `;
            
            // Create result cards for each index
            Object.keys(results).forEach(index => {{
                const data = results[index];
                const percentage = ((data.average - data.min) / (data.max - data.min || 1)) * 100;
                
                html += `
                    <div class="result-card">
                        <div class="result-title">
                            <span>${{index}}</span>
                            <span class="result-value">${{data.average}}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #999; font-size: 11px; margin-bottom: 8px;">
                            <div>Min: ${{data.min}}</div>
                            <div>Max: ${{data.max}}</div>
                        </div>
                        <div style="height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; width: ${{percentage}}%; background: linear-gradient(90deg, #00ff88, #00cc6a); border-radius: 3px;"></div>
                        </div>
                    </div>
                `;
            }});
            
            // Add export button
            html += `
                <button class="btn-primary" onclick="exportData()" style="margin-top: 10px;">
                    <i class="fas fa-download"></i> Export These Results
                </button>
            `;
            
            content.innerHTML = html;
            panel.style.display = 'block';
        }}
        
        // Export data
        function exportData() {{
            showNotification('Preparing export file...', 'info');
            
            // Simulate export preparation
            setTimeout(() => {{
                // Create a dummy download
                const data = "Vegetation Index,Average,Min,Max\\nNDVI,0.65,0.45,0.78\\nEVI,0.42,0.32,0.55\\nNDWI,0.28,0.18,0.42";
                const blob = new Blob([data], {{ type: 'text/csv' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `khisba_export_${{selectedArea.replace(/[^a-z0-9]/gi, '_').toLowerCase()}}_${{new Date().toISOString().slice(0,10)}}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showNotification('Export downloaded successfully!', 'success');
            }}, 1000);
        }}
        
        // Share results
        function shareResults() {{
            if (navigator.share) {{
                navigator.share({{
                    title: 'KHISBA GIS Analysis Results',
                    text: `Check out my vegetation analysis for ${{selectedArea}} on KHISBA GIS`,
                    url: window.location.href
                }})
                .then(() => showNotification('Results shared successfully!', 'success'))
                .catch(error => showNotification('Sharing cancelled', 'info'));
            }} else {{
                showNotification('Web Share API not supported in this browser', 'warning');
            }}
        }}
        
        // Toggle panels
        function togglePanel(panel) {{
            if (panel === 'control') {{
                const panel = document.getElementById('control-panel');
                panel.style.display = panel.style.display === 'none' ? 'block' : 'block';
            }} else if (panel === 'results') {{
                const panel = document.getElementById('results-panel');
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            }}
        }}
        
        // Switch tabs
        function switchTab(tabName) {{
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Activate clicked tab
            document.querySelectorAll('.tab').forEach(tab => {{
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
            showNotification('View reset to global scale', 'info');
        }}
        
        // Toggle fullscreen
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(err => {{
                    showNotification(`Error attempting to enable fullscreen: ${{err.message}}`, 'error');
                }});
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}
        
        // Show help
        function showHelp() {{
            showNotification('KHISBA GIS: 1) Select area 2) Configure analysis 3) Run analysis 4) View/Export results', 'info');
        }}
        
        // Show notification
        function showNotification(message, type = 'info') {{
            const notification = document.getElementById('notification');
            const messageEl = document.getElementById('notification-message');
            
            messageEl.innerHTML = `<i class="fas fa-${{type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}}"></i> ${{message}}`;
            notification.style.display = 'block';
            
            // Set color based on type
            notification.style.borderColor = 
                type === 'error' ? '#ff4444' : 
                type === 'warning' ? '#ffaa00' : 
                type === 'success' ? '#00ff88' : '#00ff88';
            
            // Auto hide after 5 seconds
            setTimeout(() => {{
                notification.style.display = 'none';
            }}, 5000);
        }}
        
        // Initialize everything when page loads
        window.addEventListener('DOMContentLoaded', () => {{
            initMap();
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    resetDrawing();
                }} else if (e.key === 'h' || e.key === 'H') {{
                    togglePanel('control');
                }} else if (e.key === 'r' || e.key === 'R') {{
                    togglePanel('results');
                }} else if (e.key === '1') {{
                    switchTab('select');
                }} else if (e.key === '2') {{
                    switchTab('analyze');
                }} else if (e.key === '3') {{
                    switchTab('export');
                }}
            }});
            
            // Handle fullscreen change
            document.addEventListener('fullscreenchange', () => {{
                map.resize();
            }});
        }});
    </script>
</body>
</html>
"""

# Display the complete HTML app
st.components.v1.html(html_content, height=800, scrolling=False)

# Add some hidden Streamlit elements to keep it alive
st.markdown("""
<div style="display: none;">
    <div id="keep-alive"></div>
</div>
""", unsafe_allow_html=True)
