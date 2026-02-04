import streamlit as st
import json

# Set page config
st.set_page_config(
    page_title="KHISBA GIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS to hide Streamlit elements
st.markdown("""
<style>
    /* Hide all Streamlit elements */
    .stApp { padding: 0 !important; margin: 0 !important; }
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    #MainMenu, footer, header, .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Create the complete HTML app with embedded JavaScript
html_content = """
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body, html { width: 100%; height: 100%; overflow: hidden; background: #000; }
        #map { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        
        /* Loading screen */
        #loading { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000; z-index: 9999; display: flex; flex-direction: column; 
            align-items: center; justify-content: center; color: #00ff88; 
        }
        .spinner { 
            width: 60px; height: 60px; border: 4px solid rgba(0,255,136,0.1); 
            border-top: 4px solid #00ff88; border-radius: 50%; 
            animation: spin 1s linear infinite; margin-bottom: 20px; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Control panel */
        #control-panel {
            position: fixed; top: 20px; left: 20px; z-index: 1000;
            background: rgba(0,0,0,0.9); border: 1px solid #00ff88; border-radius: 10px;
            padding: 15px; width: 320px; max-height: 80vh; overflow-y: auto;
            color: white; display: block;
        }
        .panel-header { 
            display: flex; justify-content: space-between; align-items: center; 
            margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #00ff88; 
        }
        .app-title { color: #00ff88; font-size: 20px; font-weight: bold; }
        .close-btn { background: none; border: none; color: white; font-size: 24px; cursor: pointer; }
        
        /* Tabs */
        .tabs { display: flex; background: #111; border-radius: 8px; padding: 4px; margin-bottom: 15px; }
        .tab { flex: 1; padding: 8px; text-align: center; background: none; border: none; 
               color: #999; cursor: pointer; border-radius: 6px; }
        .tab.active { background: #00ff88; color: #000; font-weight: bold; }
        
        /* Form elements */
        select, input, button { 
            width: 100%; padding: 10px; margin: 5px 0; background: #111; 
            border: 1px solid #333; border-radius: 5px; color: white; 
        }
        button { background: #00ff88; color: #000; font-weight: bold; cursor: pointer; }
        button:hover { opacity: 0.9; }
        
        /* Results panel */
        #results-panel {
            position: fixed; bottom: 20px; right: 20px; z-index: 1000;
            background: rgba(0,0,0,0.9); border: 1px solid #00ff88; border-radius: 10px;
            padding: 15px; width: 350px; max-height: 60vh; overflow-y: auto;
            color: white; display: none;
        }
        
        /* Quick actions */
        #quick-actions {
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
            z-index: 1000; background: rgba(0,0,0,0.8); border: 1px solid #00ff88;
            border-radius: 20px; padding: 10px; display: flex; gap: 10px;
        }
        .action-btn { 
            width: 40px; height: 40px; background: #111; border: none; border-radius: 50%;
            color: white; cursor: pointer; display: flex; align-items: center; justify-content: center;
        }
    </style>
</head>
<body>
    <!-- Loading -->
    <div id="loading">
        <div class="spinner"></div>
        <div>Loading KHISBA GIS...</div>
    </div>
    
    <!-- Map -->
    <div id="map"></div>
    
    <!-- Control Panel -->
    <div id="control-panel">
        <div class="panel-header">
            <div class="app-title">🌍 KHISBA GIS</div>
            <button class="close-btn" onclick="togglePanel()">×</button>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('select')">Select</button>
            <button class="tab" onclick="switchTab('analyze')">Analyze</button>
            <button class="tab" onclick="switchTab('export')">Export</button>
        </div>
        
        <div id="tab-select">
            <label>Country:</label>
            <select id="country-select" onchange="loadProvinces()">
                <option value="">Select Country</option>
            </select>
            
            <label>State/Province:</label>
            <select id="province-select" onchange="loadMunicipalities()" disabled>
                <option value="">Select Province</option>
            </select>
            
            <label>Municipality:</label>
            <select id="municipality-select" onchange="selectArea()" disabled>
                <option value="">Select Municipality</option>
            </select>
            
            <div style="margin-top: 15px;">
                <button onclick="startDrawing('polygon')" style="margin-bottom: 5px;">📐 Draw Polygon</button>
                <button onclick="startDrawing('rectangle')">⬜ Draw Rectangle</button>
            </div>
            
            <div id="area-info" style="display: none; margin-top: 15px; padding: 10px; background: rgba(0,255,136,0.1); border-radius: 5px;">
                <div style="color: #00ff88; font-weight: bold;">Selected Area:</div>
                <div id="area-name">No area selected</div>
            </div>
            
            <button onclick="confirmSelection()" style="margin-top: 15px; background: #00cc6a;">✅ Confirm Selection</button>
        </div>
        
        <div id="tab-analyze" style="display: none;">
            <label>Start Date:</label>
            <input type="date" id="start-date" value="2023-01-01">
            
            <label>End Date:</label>
            <input type="date" id="end-date" value="2023-12-31">
            
            <label>Satellite:</label>
            <select id="satellite">
                <option value="sentinel2">Sentinel-2</option>
                <option value="landsat8">Landsat-8</option>
            </select>
            
            <label>Max Cloud: <span id="cloud-value">20%</span></label>
            <input type="range" id="cloud" min="0" max="100" value="20" oninput="updateCloud()">
            
            <div style="margin-top: 15px;">
                <div style="color: #00ff88; margin-bottom: 5px;">Vegetation Indices:</div>
                <div id="indices" style="max-height: 150px; overflow-y: auto;">
                    <!-- Indices will be added here -->
                </div>
            </div>
            
            <button onclick="runAnalysis()" style="margin-top: 15px;">🚀 Run Analysis</button>
        </div>
        
        <div id="tab-export" style="display: none;">
            <div style="color: #999; margin-bottom: 15px;">Export your analysis results</div>
            
            <label>Format:</label>
            <select id="export-format">
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="geojson">GeoJSON</option>
            </select>
            
            <button onclick="exportData()" style="margin-top: 10px;">📥 Download</button>
            <button onclick="shareResults()" style="margin-top: 10px; background: #333;">🔗 Share</button>
        </div>
    </div>
    
    <!-- Results Panel -->
    <div id="results-panel">
        <div class="panel-header">
            <div class="app-title">📊 Results</div>
            <button class="close-btn" onclick="document.getElementById('results-panel').style.display = 'none'">×</button>
        </div>
        <div id="results-content">
            Results will appear here...
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div id="quick-actions">
        <button class="action-btn" onclick="togglePanel()">⚙️</button>
        <button class="action-btn" onclick="toggleResults()">📊</button>
        <button class="action-btn" onclick="resetView()">🏠</button>
        <button class="action-btn" onclick="fullscreen()">⛶</button>
    </div>

    <script>
        // Initialize Mapbox
        mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';
        
        let map;
        let selectedArea = null;
        let drawingMode = null;
        let drawnPoints = [];
        
        // Initialize map
        function initMap() {
            map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/satellite-streets-v12',
                center: [0, 20],
                zoom: 2,
                pitch: 45
            });
            
            // Add controls
            map.addControl(new mapboxgl.NavigationControl());
            
            map.on('load', () => {
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                
                // Load initial data
                loadCountries();
                loadIndices();
                
                // Show welcome
                setTimeout(() => {
                    alert('KHISBA GIS Ready! Select an area to begin.');
                }, 500);
            });
            
            // Handle map clicks for drawing
            map.on('click', (e) => {
                if (drawingMode) {
                    handleMapClick(e.lngLat);
                }
            });
        }
        
        // Load countries
        function loadCountries() {
            const countries = [
                "United States", "Canada", "Mexico", "United Kingdom", "France",
                "Germany", "Italy", "Spain", "Australia", "Brazil", "India",
                "China", "Japan", "Russia", "South Africa", "Egypt"
            ];
            
            const select = document.getElementById('country-select');
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            });
        }
        
        // Load provinces
        function loadProvinces() {
            const country = document.getElementById('country-select').value;
            if (!country) return;
            
            const provinces = ["California", "Texas", "New York", "Florida", "Washington"];
            const select = document.getElementById('province-select');
            
            select.innerHTML = '<option value="">Select Province</option>';
            provinces.forEach(province => {
                const option = document.createElement('option');
                option.value = province;
                option.textContent = province;
                select.appendChild(option);
            });
            select.disabled = false;
        }
        
        // Load municipalities
        function loadMunicipalities() {
            const province = document.getElementById('province-select').value;
            if (!province) return;
            
            const municipalities = ["City A", "City B", "City C", "City D", "City E"];
            const select = document.getElementById('municipality-select');
            
            select.innerHTML = '<option value="">Select Municipality</option>';
            municipalities.forEach(municipality => {
                const option = document.createElement('option');
                option.value = municipality;
                option.textContent = municipality;
                select.appendChild(option);
            });
            select.disabled = false;
        }
        
        // Select area
        function selectArea() {
            const country = document.getElementById('country-select').value;
            const province = document.getElementById('province-select').value;
            const municipality = document.getElementById('municipality-select').value;
            
            let areaName = country;
            if (province && municipality) {
                areaName = `${municipality}, ${province}, ${country}`;
            } else if (province) {
                areaName = `${province}, ${country}`;
            }
            
            selectedArea = areaName;
            document.getElementById('area-name').textContent = areaName;
            document.getElementById('area-info').style.display = 'block';
            
            // Show on map
            showAreaOnMap();
        }
        
        // Confirm selection
        function confirmSelection() {
            if (!selectedArea) {
                alert('Please select an area first');
                return;
            }
            
            alert(`Selected: ${selectedArea}`);
            switchTab('analyze');
        }
        
        // Start drawing
        function startDrawing(type) {
            drawingMode = type;
            drawnPoints = [];
            alert(`Click on map to draw ${type}. Click 3+ times for polygon, 2 times for rectangle.`);
        }
        
        // Handle map click for drawing
        function handleMapClick(lngLat) {
            if (!drawingMode) return;
            
            drawnPoints.push([lngLat.lng, lngLat.lat]);
            
            if (drawingMode === 'rectangle' && drawnPoints.length === 2) {
                completeDrawing();
            }
        }
        
        // Complete drawing
        function completeDrawing() {
            if (drawnPoints.length < 2) return;
            
            let coords;
            if (drawingMode === 'rectangle' && drawnPoints.length === 2) {
                const [p1, p2] = drawnPoints;
                coords = [p1, [p2[0], p1[1]], p2, [p1[0], p2[1]], p1];
            } else if (drawingMode === 'polygon' && drawnPoints.length >= 3) {
                coords = [...drawnPoints, drawnPoints[0]];
            } else {
                return;
            }
            
            selectedArea = `${drawingMode.charAt(0).toUpperCase() + drawingMode.slice(1)} Area`;
            document.getElementById('area-name').textContent = selectedArea;
            document.getElementById('area-info').style.display = 'block';
            
            showAreaOnMap(coords);
            drawingMode = null;
        }
        
        // Show area on map
        function showAreaOnMap(coords = null) {
            // Create default coordinates if none provided
            if (!coords) {
                coords = [
                    [-100, 40],
                    [-90, 40],
                    [-90, 30],
                    [-100, 30],
                    [-100, 40]
                ];
            }
            
            // Remove existing area
            if (map.getSource('selected-area')) {
                map.removeLayer('selected-area-fill');
                map.removeLayer('selected-area-border');
                map.removeSource('selected-area');
            }
            
            // Add new area
            map.addSource('selected-area', {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    geometry: {
                        type: 'Polygon',
                        coordinates: [coords]
                    }
                }
            });
            
            map.addLayer({
                id: 'selected-area-fill',
                type: 'fill',
                source: 'selected-area',
                paint: {
                    'fill-color': '#00ff88',
                    'fill-opacity': 0.2
                }
            });
            
            map.addLayer({
                id: 'selected-area-border',
                type: 'line',
                source: 'selected-area',
                paint: {
                    'line-color': '#00ff88',
                    'line-width': 2
                }
            });
            
            // Zoom to area
            const bounds = new mapboxgl.LngLatBounds();
            coords.forEach(coord => bounds.extend(coord));
            map.fitBounds(bounds, { padding: 50 });
        }
        
        // Load vegetation indices
        function loadIndices() {
            const indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI', 'ARVI', 'VARI'];
            const container = document.getElementById('indices');
            
            indices.forEach(index => {
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.margin = '5px 0';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `index-${index}`;
                checkbox.value = index;
                checkbox.checked = index === 'NDVI' || index === 'EVI';
                
                const label = document.createElement('label');
                label.htmlFor = `index-${index}`;
                label.textContent = index;
                label.style.marginLeft = '8px';
                label.style.color = 'white';
                
                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            });
        }
        
        // Update cloud cover
        function updateCloud() {
            const value = document.getElementById('cloud').value;
            document.getElementById('cloud-value').textContent = value + '%';
        }
        
        // Run analysis
        function runAnalysis() {
            if (!selectedArea) {
                alert('Please select an area first');
                return;
            }
            
            // Get selected indices
            const selectedIndices = [];
            document.querySelectorAll('#indices input[type="checkbox"]:checked').forEach(cb => {
                selectedIndices.push(cb.value);
            });
            
            if (selectedIndices.length === 0) {
                alert('Please select at least one vegetation index');
                return;
            }
            
            alert(`Running analysis for ${selectedArea} with ${selectedIndices.length} indices...`);
            
            // Simulate analysis
            setTimeout(() => {
                const results = {};
                selectedIndices.forEach(index => {
                    results[index] = {
                        average: (0.4 + Math.random() * 0.3).toFixed(3),
                        min: (0.3 + Math.random() * 0.1).toFixed(3),
                        max: (0.5 + Math.random() * 0.2).toFixed(3)
                    };
                });
                
                displayResults(results);
                alert('Analysis complete!');
            }, 2000);
        }
        
        // Display results
        function displayResults(results) {
            const content = document.getElementById('results-content');
            const panel = document.getElementById('results-panel');
            
            let html = `<h3 style="color: #00ff88; margin-bottom: 10px;">${selectedArea}</h3>`;
            
            Object.keys(results).forEach(index => {
                const data = results[index];
                html += `
                    <div style="background: #111; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        <div style="color: #00ff88; font-weight: bold;">${index}</div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span>Avg: ${data.average}</span>
                            <span>Min: ${data.min}</span>
                            <span>Max: ${data.max}</span>
                        </div>
                    </div>
                `;
            });
            
            content.innerHTML = html;
            panel.style.display = 'block';
        }
        
        // Export data
        function exportData() {
            alert('Exporting data...');
            // Simulate download
            setTimeout(() => {
                alert('Export complete! File downloaded.');
            }, 1000);
        }
        
        // Share results
        function shareResults() {
            alert('Share feature coming soon!');
        }
        
        // Toggle control panel
        function togglePanel() {
            const panel = document.getElementById('control-panel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
        
        // Toggle results panel
        function toggleResults() {
            const panel = document.getElementById('results-panel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
        
        // Switch tabs
        function switchTab(tabName) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.textContent.toLowerCase() === tabName.toLowerCase()) {
                    tab.classList.add('active');
                }
            });
            
            // Show content
            document.getElementById('tab-select').style.display = 'none';
            document.getElementById('tab-analyze').style.display = 'none';
            document.getElementById('tab-export').style.display = 'none';
            document.getElementById(`tab-${tabName}`).style.display = 'block';
        }
        
        // Reset view
        function resetView() {
            map.flyTo({
                center: [0, 20],
                zoom: 2,
                pitch: 45
            });
        }
        
        // Fullscreen
        function fullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }
        
        // Initialize when page loads
        window.addEventListener('load', initMap);
    </script>
</body>
</html>
"""

# Display the HTML content
st.components.v1.html(html_content, height=800, scrolling=False)

# Add minimal Streamlit content to keep it alive
st.markdown("""
<div style="display: none;">
    Streamlit app running...
</div>
""", unsafe_allow_html=True)
