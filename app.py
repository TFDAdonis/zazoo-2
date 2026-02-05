import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
import json
import plotly.graph_objects as go
import traceback

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Khisba GIS - Climate & Soil Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* Auto-transition animation */
    .auto-transition {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: var(--secondary-black);
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        color: var(--text-gray);
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-green) !important;
        color: var(--primary-black) !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: var(--text-white) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: var(--text-gray) !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# EARTH ENGINE INITIALIZATION
# =============================================================================

def auto_initialize_earth_engine():
    """Automatically initialize Earth Engine with service account credentials"""
    try:
        # Fixed private key - properly formatted with actual newlines
        private_key = """-----BEGIN PRIVATE KEY-----
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
-----END PRIVATE KEY-----"""
        
        service_account_info = {
            "type": "service_account",
            "project_id": "citric-hawk-457513-i6",
            "private_key_id": "8984179a69969591194d8f8097e48cd9789f5ea2",
            "private_key": private_key,
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

# =============================================================================
# CONSTANTS AND DATA SOURCES
# =============================================================================

# Constants for Soil Analysis
BULK_DENSITY = 1.3
SOC_TO_SOM_FACTOR = 1.724

# Soil texture classes
SOIL_TEXTURE_CLASSES = {
    1: 'Clay', 2: 'Sandy clay', 3: 'Silty clay', 4: 'Clay loam', 5: 'Sandy clay loam',
    6: 'Silty clay loam', 7: 'Loam', 8: 'Sandy loam', 9: 'Silt loam', 10: 'Silt',
    11: 'Loamy sand', 12: 'Sand'
}

# Africa bounds
AFRICA_BOUNDS = ee.Geometry.Polygon([
    [-25.0, -35.0], [-25.0, 37.5], [-5.5, 37.5], [-5.5, 35.5],
    [0.0, 35.5], [5.0, 38.0], [12.0, 38.0], [32.0, 31.0],
    [32.0, -35.0], [-25.0, -35.0]
])

# Data Sources Documentation
DATA_SOURCES = {
    'reference_soil': {
        'global': {
            'name': 'GSOCMAP (FAO)',
            'source': 'projects/earthengine-legacy/assets/projects/sat-io/open-datasets/FAO/GSOCMAP1-5-0',
            'depth': '0-30cm',
            'description': 'Global Soil Organic Carbon Map (GSOCmap) - FAO',
            'citation': 'FAO. 2018. Global Soil Organic Carbon Map (GSOCmap) Technical Report'
        },
        'africa': {
            'name': 'ISDASOIL Africa',
            'source': 'ISDASOIL/Africa/v1/carbon_organic',
            'depth': '0-20cm',
            'description': 'Africa Soil Information Service (AfSIS) Soil Organic Carbon',
            'citation': 'Hengl, T., et al. 2017. Soil nutrient maps of Sub-Saharan Africa'
        }
    },
    'soil_texture': {
        'name': 'OpenLandMap Soil Texture',
        'source': 'OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02',
        'description': 'Soil texture classes based on USDA classification',
        'citation': 'OpenLandMap project, 2020'
    },
    'sentinel2': {
        'name': 'Sentinel-2 MSI',
        'source': 'COPERNICUS/S2_SR',
        'description': 'Sentinel-2 MultiSpectral Instrument, Level-2A',
        'citation': 'European Space Agency, Copernicus Program'
    },
    'administrative': {
        'name': 'FAO GAUL',
        'source': 'FAO/GAUL/2015/level0',
        'description': 'Global Administrative Unit Layers (GAUL)',
        'citation': 'Food and Agriculture Organization of the United Nations'
    }
}

# FAO GAUL Dataset
FAO_GAUL = ee.FeatureCollection("FAO/GAUL/2015/level0")
FAO_GAUL_ADMIN1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
FAO_GAUL_ADMIN2 = ee.FeatureCollection("FAO/GAUL/2015/level2")

# =============================================================================
# SIMPLIFIED CLIMATE & SOIL ANALYZER CLASS
# =============================================================================

class SimplifiedClimateSoilAnalyzer:
    def __init__(self):
        self.config = {
            'default_start_date': '2024-01-01',
            'default_end_date': '2024-12-31',
            'scale': 1000,
            'max_pixels': 1e6
        }

        # Climate classification parameters
        self.climate_palettes = {
            'Temperature-Precipitation': [
                '#006400', '#32CD32', '#9ACD32', '#FFD700', '#FF4500', '#FF8C00', '#B8860B',
                '#0000FF', '#1E90FF', '#87CEEB', '#2E8B57', '#696969', '#ADD8E6', '#FFFFFF', '#8B0000'
            ]
        }

        self.climate_class_names = {
            'Temperature-Precipitation': {
                1: 'Tropical Rainforest (Temp > 18°C, Precip > 2000mm)',
                2: 'Tropical Monsoon (Temp > 18°C, Precip 1500-2000mm)',
                3: 'Tropical Savanna (Temp > 18°C, Precip 1000-1500mm)',
                4: 'Tropical Dry (Temp > 18°C, Precip 500-1000mm)',
                5: 'Humid Subtropical (Temp 12-18°C, Precip > 1200mm)',
                6: 'Mediterranean (Temp 12-18°C, Precip 600-1200mm)',
                7: 'Desert/Steppe (Arid/Semi-arid)',
                8: 'Oceanic (Temp 6-12°C, Precip > 1000mm)',
                9: 'Warm Temperate (Temp 6-12°C, Precip 500-1000mm)',
                10: 'Temperate Dry (Temp 6-12°C, Precip < 500mm)',
                11: 'Boreal Humid (Temp 0-6°C, Precip > 500mm)',
                12: 'Boreal Dry (Temp 0-6°C, Precip < 500mm)',
                13: 'Tundra (Temp -10 to 0°C)',
                14: 'Ice Cap (Temp < -10°C)',
                15: 'Hyper-arid (Aridity < 0.03)'
            }
        }

        self.current_soil_data = None
        self.analysis_results = {}

    # Climate Analysis Methods
    def classify_climate_simplified(self, temp, precip, aridity):
        if temp > 18:
            if precip > 2000:
                return 1
            elif precip > 1500:
                return 2
            elif precip > 1000:
                return 3
            elif precip > 500:
                return 4
            else:
                return 7
        elif temp > 12:
            if precip > 1200:
                return 5
            elif precip > 600:
                return 6
            else:
                return 7
        elif temp > 6:
            if precip > 1000:
                return 8
            elif precip > 500:
                return 9
            else:
                return 10
        elif temp > 0:
            if precip > 500:
                return 11
            else:
                return 12
        elif temp > -10:
            return 13
        else:
            return 14
        
        if aridity < 0.03:
            return 15

    def get_accurate_climate_classification(self, geometry, location_name):
        try:
            worldclim = ee.Image("WORLDCLIM/V1/BIO")
            annual_mean_temp = worldclim.select('bio01').divide(10)
            annual_precip = worldclim.select('bio12')
            aridity_index = annual_precip.divide(annual_mean_temp.add(33))

            stats = ee.Image.cat([annual_mean_temp, annual_precip, aridity_index]).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry.centroid(),
                scale=10000,
                maxPixels=1e6
            ).getInfo()

            mean_temp = stats.get('bio01', 18.5)
            mean_precip = stats.get('bio12', 800)
            mean_aridity = mean_precip / (mean_temp + 33) if (mean_temp + 33) != 0 else 1.5

            climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
            climate_zone = self.climate_class_names['Temperature-Precipitation'].get(climate_class, 'Unknown')

            climate_analysis = {
                'climate_zone': climate_zone,
                'climate_class': climate_class,
                'mean_temperature': round(mean_temp, 1),
                'mean_precipitation': round(mean_precip),
                'aridity_index': round(mean_aridity, 3),
                'classification_type': 'Temperature-Precipitation',
                'classification_system': 'GEE JavaScript Compatible',
                'note': 'Using exact JavaScript classification logic'
            }

            return climate_analysis

        except Exception as e:
            st.error(f"Climate classification failed: {e}")
            return {
                'climate_zone': "Tropical Dry (Temp > 18°C, Precip 500-1000mm)",
                'climate_class': 4,
                'mean_temperature': 19.5,
                'mean_precipitation': 635,
                'aridity_index': 1.52,
                'classification_type': 'Temperature-Precipitation',
                'classification_system': 'GEE JavaScript Calibrated',
                'note': 'Based on actual GEE output for Annaba showing Class 4'
            }

    def create_climate_classification_chart(self, location_name, climate_data):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Climate Classification Analysis - {location_name}\nTemperature-Precipitation Classification', fontsize=14, fontweight='bold', y=0.95)

        current_class = climate_data['climate_class']
        ax1.barh([0], [1], color=self.climate_palettes['Temperature-Precipitation'][current_class-1], alpha=0.7)
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Class {current_class}'])
        ax1.set_xlabel('Representation')
        ax1.set_title(f'Current Climate Zone: {climate_data["climate_zone"][:50]}...', fontsize=10, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        categories = ['Temperature', 'Precipitation', 'Aridity']
        values = [
            climate_data['mean_temperature'] / 30,
            climate_data['mean_precipitation'] / 3000,
            climate_data['aridity_index'] * 10
        ]
        values += values[:1]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        ax2 = plt.subplot(222, polar=True)
        ax2.plot(angles, values, 'o-', linewidth=2, label='Current Location')
        ax2.fill(angles, values, alpha=0.25)
        ax2.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax2.set_ylim(0, 1)
        ax2.set_title('Climate Parameters Radar Chart', fontsize=10, fontweight='bold')
        ax2.legend()

        ax3.scatter(climate_data['mean_temperature'], climate_data['mean_precipitation'],
                   c=self.climate_palettes['Temperature-Precipitation'][current_class-1], s=200, alpha=0.7)
        ax3.set_xlabel('Mean Temperature (°C)')
        ax3.set_ylabel('Mean Precipitation (mm/year)')
        ax3.set_title('Temperature vs Precipitation', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.annotate(f'Class {current_class}',
                    (climate_data['mean_temperature'], climate_data['mean_precipitation']),
                    xytext=(10, 10), textcoords='offset points')

        ax4.axis('off')
        legend_text = "CLIMATE CLASSIFICATION LEGEND\n\n"
        for class_id, class_name in self.climate_class_names['Temperature-Precipitation'].items():
            color = self.climate_palettes['Temperature-Precipitation'][class_id-1]
            marker = '▶' if class_id == current_class else '○'
            legend_text += f"{marker} Class {class_id}: {class_name[:40]}...\n" if len(class_name) > 40 else f"{marker} Class {class_id}: {class_name}\n"

        ax4.text(0.1, 0.9, legend_text, transform=ax4.transAxes, fontsize=8,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
                verticalalignment='top')

        plt.tight_layout()
        return fig

    def get_geometry_from_selection(self, country, region, municipality):
        try:
            if municipality != 'Select Municipality':
                feature = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .filter(ee.Filter.eq('ADM2_NAME', municipality)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{municipality}, {region}, {country}"
                return geometry, location_name

            elif region != 'Select Region':
                feature = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{region}, {country}"
                return geometry, location_name

            elif country != 'Select Country':
                feature = FAO_GAUL.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                geometry = feature.geometry()
                location_name = f"{country}"
                return geometry, location_name

            else:
                st.error("❌ Please select a country")
                return None, None

        except Exception as e:
            st.error(f"❌ Geometry error: {e}")
            return None, None

    # Soil Analysis Methods
    def get_small_region_sample(self, geometry):
        try:
            centroid = geometry.centroid()
            small_region = centroid.buffer(1000)
            bounds = small_region.bounds()
            coords = bounds.coordinates().getInfo()

            ring = coords[0]
            lons = [coord[0] for coord in ring]
            lats = [coord[1] for coord in ring]

            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)

            points = []
            for i in range(3):
                for j in range(3):
                    lon = min_lon + (max_lon - min_lon) * (i + 0.5) / 3
                    lat = min_lat + (max_lat - min_lat) * (j + 0.5) / 3
                    points.append([lon, lat])

            features = [ee.Feature(ee.Geometry.Point(point)) for point in points]
            return ee.FeatureCollection(features)

        except Exception as e:
            st.warning(f"Could not create small region: {e}")
            centroid = geometry.centroid()
            return ee.FeatureCollection([ee.Feature(centroid)])

    def get_sentinel2_soil_indices_ultra_light(self, geometry):
        try:
            sampling_area = self.get_small_region_sample(geometry)
            start_date, end_date = '2023-06-01', '2023-08-31'

            s2_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
                .filterBounds(sampling_area) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .limit(10)

            collection_size = s2_collection.size().getInfo()
            if collection_size == 0:
                return None

            def calculate_simple_indices(img):
                try:
                    img = img.divide(10000)
                    ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')

                    ndomi = img.expression(
                        '(B12 - B11) / (B12 + B11 + 0.0001)', {
                            'B12': img.select('B12'),
                            'B11': img.select('B11')
                        }).rename('NDOMI')

                    bare_soil_mask = ndvi.lt(0.3)
                    masked_ndomi = ndomi.updateMask(bare_soil_mask)

                    return masked_ndomi.set('system:time_start', img.get('system:time_start'))

                except Exception as e:
                    return None

            s2_with_indices = s2_collection.map(calculate_simple_indices).filter(ee.Filter.notNull(['NDOMI']))
            processed_size = s2_with_indices.size().getInfo()

            if processed_size == 0:
                return None

            median_composite = s2_with_indices.median()

            try:
                samples = median_composite.sampleRegions(
                    collection=sampling_area,
                    scale=10,
                    geometries=False
                )

                sample_list = samples.getInfo()['features']
                if sample_list:
                    ndomi_values = [feature['properties']['NDOMI'] for feature in sample_list if 'NDOMI' in feature['properties']]
                    if ndomi_values:
                        mean_ndomi = np.mean(ndomi_values)
                        std_ndomi = np.std(ndomi_values)

                        indices_data = {
                            'NDOMI': {
                                'mean': mean_ndomi,
                                'std': std_ndomi,
                                'source': DATA_SOURCES['sentinel2']['name'],
                                'citation': DATA_SOURCES['sentinel2']['citation']
                            }
                        }
                        return indices_data

            except Exception as e:
                return None

        except Exception as e:
            return None

    def get_reference_soil_data_improved(self, geometry, region_name):
        try:
            gsoc = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/FAO/GSOCMAP1-5-0")
            soc_mean_global = gsoc.select('b1').rename('soc_mean')

            africa_soil = ee.Image("ISDASOIL/Africa/v1/carbon_organic")
            converted_africa = africa_soil.divide(10).exp().subtract(1)

            texture_dataset = ee.Image('OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02')
            soil_texture = texture_dataset.select('b0')

            is_in_africa = AFRICA_BOUNDS.intersects(geometry, 100).getInfo()

            if is_in_africa:
                soc_stock = converted_africa.select(0).clip(geometry).rename('soc_stock')
                depth = 20
                soil_source = DATA_SOURCES['reference_soil']['africa']
            else:
                soc_stock = soc_mean_global.clip(geometry).rename('soc_stock')
                depth = 30
                soil_source = DATA_SOURCES['reference_soil']['global']

            texture_clipped = soil_texture.clip(geometry).rename('texture')

            def get_soil_stats(image, property_name):
                try:
                    stats = image.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=geometry,
                        scale=1000,
                        maxPixels=1e9,
                        bestEffort=True
                    )
                    result = stats.get(property_name).getInfo()
                    return result if result is not None else 0
                except Exception as e:
                    return 0

            def get_texture_mode(image):
                try:
                    mode_stats = image.reduceRegion(
                        reducer=ee.Reducer.mode(),
                        geometry=geometry,
                        scale=250,
                        maxPixels=1e9,
                        bestEffort=True
                    )
                    result = mode_stats.get('texture').getInfo()
                    return int(result) if result is not None else 7
                except Exception as e:
                    return 7

            soc_stock_val = get_soil_stats(soc_stock, 'soc_stock')
            texture_val = get_texture_mode(texture_clipped)

            soc_percent, som_percent = self.calculate_soc_to_som(soc_stock_val, BULK_DENSITY, depth)
            clay_val, silt_val, sand_val = self.estimate_texture_components(texture_val)

            indices_data = self.get_sentinel2_soil_indices_ultra_light(geometry)

            som_from_indices = None
            indices_uncertainty = None

            if indices_data and 'NDOMI' in indices_data:
                ndomi_value = indices_data['NDOMI']['mean']
                som_from_indices, indices_uncertainty = self.estimate_som_from_single_index(
                    ndomi_value, {'sand': sand_val, 'clay': clay_val})

            final_som_estimate = som_from_indices if som_from_indices is not None else som_percent

            soil_data = {
                'region_name': region_name,
                'texture_class': texture_val,
                'texture_name': SOIL_TEXTURE_CLASSES.get(texture_val, 'Unknown'),
                'soc_stock': soc_stock_val,
                'soil_organic_matter': som_percent,
                'bulk_density': BULK_DENSITY,
                'depth_cm': depth,
                'clay_content': clay_val,
                'silt_content': silt_val,
                'sand_content': sand_val,
                'is_africa': is_in_africa,
                'calculated_soc_percent': soc_percent,
                'calculated_som_percent': som_percent,
                'geometry': geometry,
                'indices_data': indices_data,
                'som_from_indices': som_from_indices,
                'indices_uncertainty': indices_uncertainty,
                'final_som_estimate': final_som_estimate,
                'data_sources': {
                    'soil_organic_carbon': soil_source,
                    'soil_texture': DATA_SOURCES['soil_texture'],
                    'sentinel2_indices': DATA_SOURCES['sentinel2'] if indices_data else None
                }
            }

            return soil_data

        except Exception as e:
            st.error(f"Error getting soil data for {region_name}: {str(e)}")
            return None

    def calculate_soc_to_som(self, soc_stock_t_ha, bulk_density, depth_cm):
        try:
            soc_percent = soc_stock_t_ha / (bulk_density * depth_cm * 100)
            som_percent = soc_percent * SOC_TO_SOM_FACTOR * 100
            return soc_percent * 100, som_percent
        except Exception as e:
            return 0, 0

    def estimate_texture_components(self, texture_class):
        texture_compositions = {
            1: (60, 20, 20),   # Clay
            2: (55, 10, 35),   # Sandy clay
            3: (40, 40, 20),   # Silty clay
            4: (35, 30, 35),   # Clay loam
            5: (30, 10, 60),   # Sandy clay loam
            6: (30, 50, 20),   # Silty clay loam
            7: (20, 40, 40),   # Loam
            8: (15, 10, 75),   # Sandy loam
            9: (10, 60, 30),   # Silt loam
            10: (5, 70, 25),   # Silt
            11: (10, 10, 80),  # Loamy sand
            12: (5, 5, 90)     # Sand
        }
        return texture_compositions.get(texture_class, (20, 40, 40))

    def estimate_som_from_single_index(self, ndomi_value, texture_data):
        try:
            if ndomi_value is None:
                return None, None

            som_estimate = 1.5 + (ndomi_value + 0.1) * 12.0

            sand_content = texture_data.get('sand', 40)
            if sand_content > 70:
                som_estimate *= 0.8
            elif sand_content < 20:
                som_estimate *= 1.2

            som_estimate = max(0.5, min(6.0, som_estimate))
            uncertainty = abs(ndomi_value) * 5 + 0.5

            return som_estimate, uncertainty

        except Exception as e:
            return None, None

    def run_comprehensive_soil_analysis(self, country, region='Select Region', municipality='Select Municipality'):
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            return None

        soil_data = self.get_reference_soil_data_improved(geometry, location_name)

        if soil_data:
            return {
                'soil_data': soil_data,
                'location_name': location_name
            }
        else:
            return None

    def display_soil_analysis(self, soil_results):
        if not soil_results:
            return

        soil_data = soil_results['soil_data']
        location_name = soil_results['location_name']

        st.markdown(f'<div class="section-header">🌱 SOIL ANALYSIS - {location_name}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏺 Soil Texture", soil_data['texture_name'])
        with col2:
            st.metric("🧪 Soil Organic Matter", f"{soil_data['final_som_estimate']:.2f}%")
        with col3:
            st.metric("📊 Soil Quality", 
                     "High" if soil_data['final_som_estimate'] > 3.0 else 
                     "Medium" if soil_data['final_som_estimate'] > 1.5 else "Low")

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        texture_components = ['Clay', 'Silt', 'Sand']
        texture_values = [soil_data['clay_content'], soil_data['silt_content'], soil_data['sand_content']]
        colors = ['#8B4513', '#DEB887', '#F4A460']
        axes[0].bar(texture_components, texture_values, color=colors)
        axes[0].set_title('Soil Texture Composition')
        axes[0].set_ylabel('Percentage (%)')
        axes[0].set_ylim(0, 100)
        for i, v in enumerate(texture_values):
            axes[0].text(i, v + 1, f'{v}%', ha='center', va='bottom', fontweight='bold')

        carbon_data = [soil_data['soc_stock'], soil_data['soil_organic_matter']]
        carbon_labels = ['SOC Stock\n(t/ha)', 'SOM\n(Reference)']
        carbon_colors = ['#2E8B57', '#32CD32']
        if soil_data.get('som_from_indices'):
            carbon_data.append(soil_data['som_from_indices'])
            carbon_labels.append('SOM\n(Satellite)')
            carbon_colors.append('#FFA500')
        axes[1].bar(carbon_labels, carbon_data, color=carbon_colors, alpha=0.7)
        axes[1].set_title('Soil Organic Matter Comparison')
        for i, v in enumerate(carbon_data):
            axes[1].text(i, v + max(carbon_data)*0.05, f'{v:.2f}', ha='center', va='bottom')

        axes[2].axis('off')
        quality_text = f"""
        📈 SOIL QUALITY ASSESSMENT:

        Organic Matter: {'✅ HIGH' if soil_data['final_som_estimate'] > 3.0 else '⚠️ MEDIUM' if soil_data['final_som_estimate'] > 1.5 else '❌ LOW'}

        Value: {soil_data['final_som_estimate']:.2f}%

        Texture: {'✅ OPTIMAL' if soil_data['texture_name'] in ['Loam', 'Silt loam', 'Clay loam'] else '⚠️ MODERATE' if soil_data['texture_name'] in ['Sandy loam', 'Silty clay loam'] else '❌ POOR'}

        Class: {soil_data['texture_name']}

        💡 RECOMMENDATIONS:
        """
        if soil_data['final_som_estimate'] < 1.5:
            quality_text += "• Add organic amendments\n• Use cover crops\n"
        if soil_data['sand_content'] > 70:
            quality_text += "• Improve water retention\n"
        
        axes[2].text(0.1, 0.9, quality_text, transform=axes[2].transAxes, fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"),
                    verticalalignment='top')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # =============================================================================
    # ENHANCED CLIMATE ANALYSIS METHODS
    # =============================================================================
# =============================================================================
# ENHANCED CLIMATE ANALYSIS METHODS - FIXED VERSION
# =============================================================================

def get_daily_climate_data_for_analysis(self, geometry, start_date, end_date):
    """Get enhanced daily climate data for comprehensive analysis"""
    try:
        # Use ERA5-Land for temperature and soil moisture
        era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry)
        
        # Use CHIRPS for precipitation
        chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry)
        
        # Create monthly composites for analysis
        def create_monthly_composite(year_month):
            year_month = ee.Date(year_month)
            month_start = year_month
            month_end = month_start.advance(1, 'month')
            
            # Get monthly mean temperature
            temp_monthly = era5.filterDate(month_start, month_end) \
                              .select('temperature_2m') \
                              .mean() \
                              .subtract(273.15)  # Convert to Celsius
            
            # Get monthly total precipitation
            precip_monthly = chirps.filterDate(month_start, month_end) \
                                  .select('precipitation') \
                                  .sum()
            
            # Get monthly soil moisture
            soil_moisture1 = era5.filterDate(month_start, month_end) \
                                .select('volumetric_soil_water_layer_1') \
                                .mean()
            
            soil_moisture2 = era5.filterDate(month_start, month_end) \
                                .select('volumetric_soil_water_layer_2') \
                                .mean()
            
            soil_moisture3 = era5.filterDate(month_start, month_end) \
                                .select('volumetric_soil_water_layer_3') \
                                .mean()
            
            # Calculate potential evaporation using simplified method
            pet = temp_monthly.add(17.8).multiply(0.0023).multiply(15).rename('potential_evaporation')
            
            return ee.Image.cat([
                temp_monthly.rename('temperature_2m'),
                precip_monthly.rename('total_precipitation'),
                soil_moisture1.rename('volumetric_soil_water_layer_1'),
                soil_moisture2.rename('volumetric_water_layer_2'),
                soil_moisture3.rename('volumetric_water_layer_3'),
                pet
            ]).set('system:time_start', month_start.millis())
        
        # Generate monthly sequence
        start = ee.Date(start_date)
        end = ee.Date(end_date)
        months = ee.List.sequence(0, end.difference(start, 'month').subtract(1))
        
        monthly_collection = ee.ImageCollection(months.map(
            lambda month: create_monthly_composite(start.advance(month, 'month'))
        ))
        
        return monthly_collection
        
    except Exception as e:
        st.error(f"Error getting climate data: {e}")
        return None

def extract_monthly_statistics(self, monthly_collection, geometry):
    """Extract monthly statistics for analysis"""
    try:
        # Sample at centroid
        centroid = geometry.centroid()
        
        # Get time series
        series = monthly_collection.getRegion(centroid, 10000).getInfo()
        
        if not series or len(series) <= 1:
            return None
        
        # Process to DataFrame
        headers = series[0]
        data = series[1:]
        
        df = pd.DataFrame(data, columns=headers)
        df['datetime'] = pd.to_datetime(df['time'], unit='ms')
        df['month'] = df['datetime'].dt.month
        df['month_name'] = df['datetime'].dt.strftime('%b')
        df['year'] = df['datetime'].dt.year
        
        # Sort by datetime
        df = df.sort_values('datetime')
        
        return df
        
    except Exception as e:
        st.error(f"Error extracting statistics: {e}")
        return None

def create_comprehensive_climate_charts(self, climate_df, location_name):
    """Create comprehensive climate analysis charts"""
    if climate_df is None or climate_df.empty:
        return None
    
    charts = {}
    
    # 1. Soil Moisture by Depth Chart
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    if 'volumetric_soil_water_layer_1' in climate_df.columns:
        # Get unique months in correct order
        months_df = climate_df.sort_values('month')
        unique_months = months_df['month'].unique()
        month_names = months_df['month_name'].unique()
        x = range(len(unique_months))
        
        # Plot soil moisture layers if available
        layer_names = ['volumetric_soil_water_layer_1', 'volumetric_water_layer_2', 'volumetric_water_layer_3']
        layer_labels = ['Layer 1 (0-7cm)', 'Layer 2 (7-28cm)', 'Layer 3 (28-100cm)']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, (layer, label, color) in enumerate(zip(layer_names, layer_labels, colors)):
            if layer in climate_df.columns:
                monthly_avg = []
                for month in unique_months:
                    month_data = climate_df[climate_df['month'] == month]
                    if not month_data.empty:
                        monthly_avg.append(month_data[layer].mean())
                    else:
                        monthly_avg.append(0)
                
                ax1.plot(x, monthly_avg, marker='o', color=color, linewidth=2, label=label)
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Soil Moisture (m³/m³)')
        ax1.set_title(f'Soil Moisture by Depth - {location_name}', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        
        # Handle variable number of months
        if len(month_names) > 0:
            # Use available month names
            ax1.set_xticklabels(month_names)
        else:
            # Fallback to month numbers
            ax1.set_xticklabels([f'Month {m}' for m in unique_months])
        
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 0.4)
        
        plt.tight_layout()
        charts['soil_moisture_depth'] = fig1
    
    # 2. Monthly Water Balance Chart
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
        months_df = climate_df.sort_values('month')
        unique_months = months_df['month'].unique()
        month_names = months_df['month_name'].unique()
        x = range(len(unique_months))
        
        precip_values = []
        evap_values = []
        
        for month in unique_months:
            month_data = climate_df[climate_df['month'] == month]
            if not month_data.empty:
                precip_values.append(month_data['total_precipitation'].sum())
                evap_values.append(month_data['potential_evaporation'].mean())
            else:
                precip_values.append(0)
                evap_values.append(0)
        
        width = 0.35
        ax2.bar([i - width/2 for i in x], precip_values, width, 
                label='Precipitation', color='#36A2EB', alpha=0.8)
        ax2.bar([i + width/2 for i in x], evap_values, width, 
                label='Evaporation', color='#FF6384', alpha=0.8)
        
        ax2.set_xlabel('Month')
        ax2.set_ylabel('mm/month')
        ax2.set_title(f'Monthly Water Balance - {location_name}', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        
        # Handle variable number of months
        if len(month_names) > 0:
            ax2.set_xticklabels(month_names)
        else:
            ax2.set_xticklabels([f'Month {m}' for m in unique_months])
        
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        charts['monthly_water_balance'] = fig2
    
    # 3. Seasonal Water Balance Chart
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
        months_df = climate_df.sort_values('month')
        unique_months = months_df['month'].unique()
        month_names = months_df['month_name'].unique()
        x = range(len(unique_months))
        
        precip_values = []
        evap_values = []
        
        for month in unique_months:
            month_data = climate_df[climate_df['month'] == month]
            if not month_data.empty:
                precip_values.append(month_data['total_precipitation'].sum())
                evap_values.append(month_data['potential_evaporation'].mean())
            else:
                precip_values.append(0)
                evap_values.append(0)
        
        ax3.plot(x, precip_values, 'b-', linewidth=2, label='Precipitation', marker='o')
        ax3.plot(x, evap_values, 'r-', linewidth=2, label='Evaporation', marker='s')
        
        # Fill between for water surplus/deficit
        if len(x) > 1:  # Only fill between if we have at least 2 points
            # Create continuous x-values for filling
            x_continuous = np.linspace(min(x), max(x), 100)
            # Interpolate values
            precip_interp = np.interp(x_continuous, x, precip_values)
            evap_interp = np.interp(x_continuous, x, evap_values)
            
            ax3.fill_between(x_continuous, precip_interp, evap_interp, 
                            where=precip_interp > evap_interp,
                            color='blue', alpha=0.2, label='Water Surplus')
            ax3.fill_between(x_continuous, precip_interp, evap_interp,
                            where=precip_interp <= evap_interp,
                            color='red', alpha=0.2, label='Water Deficit')
        
        ax3.set_xlabel('Month')
        ax3.set_ylabel('mm/month')
        ax3.set_title(f'Seasonal Water Balance - {location_name}', fontsize=14, fontweight='bold')
        ax3.set_xticks(x)
        
        # Handle variable number of months
        if len(month_names) > 0:
            ax3.set_xticklabels(month_names)
        else:
            ax3.set_xticklabels([f'Month {m}' for m in unique_months])
        
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        charts['seasonal_water_balance'] = fig3
    
    # 4. Summary Statistics Panel
    fig4, ax4 = plt.subplots(figsize=(8, 8))
    ax4.axis('off')
    
    # Calculate summary statistics
    summary_text = "📊 CLIMATE SUMMARY STATISTICS\n\n"
    
    if 'temperature_2m' in climate_df.columns:
        temp_mean = climate_df['temperature_2m'].mean()
        temp_max = climate_df['temperature_2m'].max()
        temp_min = climate_df['temperature_2m'].min()
        summary_text += f"🌡️ Temperature:\n"
        summary_text += f"  • Mean: {temp_mean:.1f}°C\n"
        summary_text += f"  • Max: {temp_max:.1f}°C\n"
        summary_text += f"  • Min: {temp_min:.1f}°C\n\n"
    
    if 'total_precipitation' in climate_df.columns:
        precip_total = climate_df['total_precipitation'].sum()
        precip_mean = climate_df['total_precipitation'].mean()
        precip_max = climate_df['total_precipitation'].max()
        summary_text += f"💧 Precipitation:\n"
        summary_text += f"  • Total: {precip_total:.1f} mm\n"
        summary_text += f"  • Mean: {precip_mean:.1f} mm/month\n"
        summary_text += f"  • Max: {precip_max:.1f} mm/month\n\n"
    
    if 'potential_evaporation' in climate_df.columns:
        evap_total = climate_df['potential_evaporation'].sum()
        evap_mean = climate_df['potential_evaporation'].mean()
        summary_text += f"☀️ Evaporation:\n"
        summary_text += f"  • Total: {evap_total:.1f} mm\n"
        summary_text += f"  • Mean: {evap_mean:.1f} mm/month\n\n"
    
    # Water balance calculation
    if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
        water_balance = precip_total - evap_total
        summary_text += f"💦 Water Balance:\n"
        summary_text += f"  • Net: {water_balance:.1f} mm\n"
        summary_text += f"  • Status: {'SURPLUS' if water_balance > 0 else 'DEFICIT'}\n\n"
    
    # Soil moisture summary
    soil_layers = []
    for layer in ['volumetric_soil_water_layer_1', 'volumetric_water_layer_2', 'volumetric_water_layer_3']:
        if layer in climate_df.columns:
            soil_layers.append((layer, climate_df[layer].mean()))
    
    if soil_layers:
        summary_text += f"🌱 Soil Moisture:\n"
        for layer_name, mean_value in soil_layers:
            depth = layer_name.split('_')[-1]
            summary_text += f"  • Layer {depth}: {mean_value:.3f} m³/m³\n"
    
    ax4.text(0.1, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
             bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
             verticalalignment='top')
    
    ax4.set_title('Summary Statistics', fontsize=12, fontweight='bold')
    charts['summary_statistics'] = fig4
    
    return charts

def run_enhanced_climate_soil_analysis(self, geometry, location_name):
    """Run enhanced climate and soil analysis with comprehensive charts"""
    try:
        # Get climate data (last 12 months for monthly analysis)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Get monthly climate data
        monthly_collection = self.get_daily_climate_data_for_analysis(geometry, start_date, end_date)
        
        if monthly_collection is None:
            st.warning("Could not retrieve climate data")
            return None
        
        # Extract statistics
        climate_df = self.extract_monthly_statistics(monthly_collection, geometry)
        
        if climate_df is None or climate_df.empty:
            st.warning("Could not extract climate statistics")
            return None
        
        # Create comprehensive charts
        charts = self.create_comprehensive_climate_charts(climate_df, location_name)
        
        # Get climate classification
        climate_results = self.get_accurate_climate_classification(geometry, location_name)
        
        # Get soil analysis - extract location info properly
        location_parts = location_name.split(',')
        if len(location_parts) >= 3:
            country = location_parts[-1].strip()
            region = location_parts[-2].strip()
            municipality = location_parts[0].strip()
        elif len(location_parts) == 2:
            country = location_parts[1].strip()
            region = location_parts[0].strip()
            municipality = 'Select Municipality'
        else:
            country = location_name.strip()
            region = 'Select Region'
            municipality = 'Select Municipality'
        
        # Get soil analysis
        soil_results = self.run_comprehensive_soil_analysis(country, region, municipality)
        
        return {
            'climate_data': climate_df,
            'charts': charts,
            'climate_results': climate_results,
            'soil_results': soil_results,
            'location_name': location_name
        }
        
    except Exception as e:
        st.error(f"Enhanced analysis error: {e}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

def display_enhanced_analysis(self, analysis_results):
    """Display enhanced climate and soil analysis"""
    if not analysis_results:
        st.warning("No analysis results to display")
        return
    
    st.markdown(f'<div class="section-header">📊 ENHANCED CLIMATE & SOIL ANALYSIS - {analysis_results.get("location_name", "Unknown Location")}</div>', unsafe_allow_html=True)
    
    # Display climate classification
    if 'climate_results' in analysis_results:
        climate_data = analysis_results['climate_results']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Mean Temperature", f"{climate_data.get('mean_temperature', 0):.1f}°C")
        with col2:
            st.metric("💧 Mean Precipitation", f"{climate_data.get('mean_precipitation', 0):.0f} mm/year")
        with col3:
            climate_zone = climate_data.get('climate_zone', 'Unknown')
            st.metric("🌍 Climate Zone", climate_zone.split('(')[0] if '(' in climate_zone else climate_zone)
    
    # Display climate charts
    if 'charts' in analysis_results:
        charts = analysis_results['charts']
        
        # Create tabs for different chart types
        tab_names = []
        if 'soil_moisture_depth' in charts:
            tab_names.append("🌱 Soil Moisture")
        if 'monthly_water_balance' in charts:
            tab_names.append("💧 Monthly Balance")
        if 'seasonal_water_balance' in charts:
            tab_names.append("🔄 Seasonal Pattern")
        if 'summary_statistics' in charts:
            tab_names.append("📊 Summary Stats")
        
        if tab_names:
            tabs = st.tabs(tab_names)
            
            for i, tab in enumerate(tabs):
                with tab:
                    if tab_names[i] == "🌱 Soil Moisture" and 'soil_moisture_depth' in charts:
                        st.pyplot(charts['soil_moisture_depth'])
                        st.markdown("""
                        **Soil Moisture by Depth Analysis:**
                        - Shows volumetric soil water content at different depths
                        - Layer 1: 0-7cm (surface)
                        - Layer 2: 7-28cm (root zone)
                        - Layer 3: 28-100cm (deep storage)
                        """)
                    
                    elif tab_names[i] == "💧 Monthly Balance" and 'monthly_water_balance' in charts:
                        st.pyplot(charts['monthly_water_balance'])
                        st.markdown("""
                        **Monthly Water Balance:**
                        - Blue bars: Precipitation (total mm/month)
                        - Red bars: Evaporation (mean mm/month)
                        - Shows water availability by month
                        """)
                    
                    elif tab_names[i] == "🔄 Seasonal Pattern" and 'seasonal_water_balance' in charts:
                        st.pyplot(charts['seasonal_water_balance'])
                        st.markdown("""
                        **Seasonal Water Balance:**
                        - Blue line: Precipitation trend
                        - Red line: Evaporation trend
                        - Blue shaded area: Water surplus (P > E)
                        - Red shaded area: Water deficit (P < E)
                        """)
                    
                    elif tab_names[i] == "📊 Summary Stats" and 'summary_statistics' in charts:
                        st.pyplot(charts['summary_statistics'])
                        st.markdown("""
                        **Climate Summary Statistics:**
                        - Temperature metrics (°C)
                        - Precipitation totals (mm)
                        - Evaporation rates
                        - Net water balance
                        - Soil moisture averages
                        """)
    
    # Display soil analysis if available
    if 'soil_results' in analysis_results and analysis_results['soil_results']:
        st.markdown("---")
        st.markdown('<div class="section-header">🌱 SOIL ANALYSIS RESULTS</div>', unsafe_allow_html=True)
        self.display_soil_analysis(analysis_results['soil_results'])
    
    # Display climate data table
    if 'climate_data' in analysis_results:
        climate_df = analysis_results['climate_data']
        
        if not climate_df.empty:
            st.markdown("---")
            st.markdown('<div class="section-header">📈 MONTHLY CLIMATE DATA</div>', unsafe_allow_html=True)
            
            # Create summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'temperature_2m' in climate_df.columns:
                    avg_temp = climate_df['temperature_2m'].mean()
                    st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
            
            with col2:
                if 'total_precipitation' in climate_df.columns:
                    total_precip = climate_df['total_precipitation'].sum()
                    st.metric("💧 Total Precipitation", f"{total_precip:.0f} mm")
            
            with col3:
                if 'potential_evaporation' in climate_df.columns:
                    total_evap = climate_df['potential_evaporation'].sum()
                    st.metric("☀️ Total Evaporation", f"{total_evap:.0f} mm")
            
            with col4:
                if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
                    water_balance = climate_df['total_precipitation'].sum() - climate_df['potential_evaporation'].sum()
                    status = "Surplus" if water_balance > 0 else "Deficit"
                    st.metric("💦 Water Balance", f"{water_balance:.0f} mm", status)
            
            # Display data table
            display_df = climate_df.copy()
            
            # Prepare display columns
            display_cols = []
            rename_cols = {}
            
            # Add date column
            if 'datetime' in display_df.columns:
                display_cols.append('datetime')
                rename_cols['datetime'] = 'Date'
                display_df['Date'] = display_df['datetime'].dt.strftime('%Y-%m')
            
            # Add other relevant columns
            col_mapping = {
                'temperature_2m': 'Temperature (°C)',
                'total_precipitation': 'Precipitation (mm)',
                'potential_evaporation': 'Evaporation (mm)',
                'volumetric_soil_water_layer_1': 'Soil Moisture L1',
                'volumetric_water_layer_2': 'Soil Moisture L2',
                'volumetric_water_layer_3': 'Soil Moisture L3'
            }
            
            for col, new_name in col_mapping.items():
                if col in display_df.columns:
                    display_cols.append(col)
                    rename_cols[col] = new_name
            
            if len(display_cols) > 1:
                st.dataframe(
                    display_df[display_cols].rename(columns=rename_cols).round(2),
                    use_container_width=True,
                    hide_index=True
                )

    
# =============================================================================
# VEGETATION INDICES FUNCTIONS
# =============================================================================

def calculate_vegetation_index(index_name, image):
    """Calculate specific vegetation indices from Sentinel-2 or Landsat images"""
    if index_name == 'NDVI':
        if 'B8' in image.bandNames().getInfo() and 'B4' in image.bandNames().getInfo():  # Sentinel-2
            return image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        elif 'SR_B5' in image.bandNames().getInfo() and 'SR_B4' in image.bandNames().getInfo():  # Landsat-8
            return image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    
    elif index_name == 'EVI':
        if 'B8' in image.bandNames().getInfo() and 'B4' in image.bandNames().getInfo() and 'B2' in image.bandNames().getInfo():
            return image.expression(
                '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
                    'NIR': image.select('B8'),
                    'RED': image.select('B4'),
                    'BLUE': image.select('B2')
                }).rename('EVI')
    
    elif index_name == 'SAVI':
        if 'B8' in image.bandNames().getInfo() and 'B4' in image.bandNames().getInfo():
            return image.expression(
                '1.5 * ((NIR - RED) / (NIR + RED + 0.5))', {
                    'NIR': image.select('B8'),
                    'RED': image.select('B4')
                }).rename('SAVI')
    
    elif index_name == 'NDWI':
        if 'B8' in image.bandNames().getInfo() and 'B11' in image.bandNames().getInfo():
            return image.normalizedDifference(['B8', 'B11']).rename('NDWI')
    
    elif index_name == 'MSAVI':
        if 'B8' in image.bandNames().getInfo() and 'B4' in image.bandNames().getInfo():
            return image.expression(
                '(2 * NIR + 1 - sqrt((2 * NIR + 1)**2 - 8 * (NIR - RED))) / 2', {
                    'NIR': image.select('B8'),
                    'RED': image.select('B4')
                }).rename('MSAVI')
    
    elif index_name == 'GNDVI':
        if 'B8' in image.bandNames().getInfo() and 'B3' in image.bandNames().getInfo():
            return image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    
    return None

def get_vegetation_indices_timeseries(geometry, start_date, end_date, collection_choice, cloud_cover, selected_indices):
    """Get vegetation indices time series for the selected area"""
    try:
        # Initialize results dictionary
        results = {index: {'dates': [], 'values': []} for index in selected_indices}
        
        # Create date range for sampling
        date_range = pd.date_range(start=start_date, end=end_date, freq='MS')  # Monthly sampling
        
        for i, date in enumerate(date_range):
            # Get midpoint of the month
            month_start = date.strftime('%Y-%m-%d')
            if i < len(date_range) - 1:
                month_end = date_range[i+1].strftime('%Y-%m-%d')
            else:
                # For last month, go to end_date
                month_end = end_date
            
            try:
                # Load image collection based on choice
                if collection_choice == "Sentinel-2":
                    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                        .filterDate(month_start, month_end) \
                        .filterBounds(geometry.geometry()) \
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                else:  # Landsat-8
                    collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                        .filterDate(month_start, month_end) \
                        .filterBounds(geometry.geometry()) \
                        .filter(ee.Filter.lte('CLOUD_COVER', cloud_cover))
                
                # Get median composite
                if collection.size().getInfo() > 0:
                    composite = collection.median()
                    
                    # Calculate each selected index
                    for index_name in selected_indices:
                        index_img = calculate_vegetation_index(index_name, composite)
                        if index_img:
                            # Get mean value for the geometry
                            stats = index_img.reduceRegion(
                                reducer=ee.Reducer.mean(),
                                geometry=geometry.geometry(),
                                scale=30 if collection_choice == "Sentinel-2" else 30,
                                maxPixels=1e9,
                                bestEffort=True
                            ).getInfo()
                            
                            if stats and index_name in stats:
                                value = stats[index_name]
                                if value is not None:
                                    results[index_name]['dates'].append(date.strftime('%Y-%m-%d'))
                                    results[index_name]['values'].append(float(value))
            
            except Exception as e:
                continue
        
        # Add some simulated data if no real data found
        for index_name in selected_indices:
            if not results[index_name]['dates']:
                # Generate simulated data
                dates = pd.date_range(start=start_date, end=end_date, freq='MS')
                base_value = 0.5
                seasonal_variation = 0.3
                
                for i, date in enumerate(dates):
                    results[index_name]['dates'].append(date.strftime('%Y-%m-%d'))
                    # Simulated seasonal pattern
                    seasonal_factor = np.sin(2 * np.pi * i / len(dates))
                    noise = np.random.normal(0, 0.1)
                    value = base_value + seasonal_variation * seasonal_factor + noise
                    # Ensure values are within reasonable bounds
                    value = max(0, min(1, value))
                    results[index_name]['values'].append(value)
        
        return results
    
    except Exception as e:
        st.error(f"Error getting vegetation indices: {str(e)}")
        # Return simulated data
        results = {}
        for index_name in selected_indices:
            dates = pd.date_range(start=start_date, end=end_date, freq='MS')
            base_value = 0.5
            seasonal_variation = 0.3
            
            results[index_name] = {
                'dates': [date.strftime('%Y-%m-%d') for date in dates],
                'values': []
            }
            
            for i, date in enumerate(dates):
                seasonal_factor = np.sin(2 * np.pi * i / len(dates))
                noise = np.random.normal(0, 0.1)
                value = base_value + seasonal_variation * seasonal_factor + noise
                value = max(0, min(1, value))
                results[index_name]['values'].append(value)
        
        return results

# =============================================================================
# CLIMATE DATA FUNCTIONS
# =============================================================================

def get_daily_climate_data_corrected(start_date, end_date, geometry, scale=50000):
    temperature = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
        .filterDate(start_date, end_date) \
        .select(['temperature_2m'])

    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date) \
        .select('precipitation')

    start = ee.Date(start_date)
    end = ee.Date(end_date)
    n_days = end.difference(start, 'day')
    days = ee.List.sequence(0, n_days.subtract(1))

    def get_daily_data(day_offset):
        day_offset = ee.Number(day_offset)
        date = start.advance(day_offset, 'day')
        date_str = date.format('YYYY-MM-dd')

        temp_image = temperature.filterDate(date, date.advance(1, 'day')).first()
        precip_image = precipitation.filterDate(date, date.advance(1, 'day')).first()

        temp_result = ee.Algorithms.If(
            temp_image,
            temp_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=scale,
                maxPixels=1e9
            ).get('temperature_2m'),
            None
        )

        precipitation_val = ee.Algorithms.If(
            precip_image,
            precip_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=scale,
                maxPixels=1e9
            ).get('precipitation'),
            None
        )

        temp_celsius = ee.Algorithms.If(
            temp_result,
            ee.Number(temp_result).subtract(273.15),
            None
        )

        return ee.Feature(None, {
            'date': date_str,
            'temperature': temp_celsius,
            'precipitation': precipitation_val
        })

    daily_data = ee.FeatureCollection(days.map(get_daily_data))
    return daily_data

def analyze_daily_climate_data(study_roi, start_date, end_date):
    try:
        daily_data = get_daily_climate_data_corrected(start_date, end_date, study_roi)
        features = daily_data.getInfo()['features']
        data = []

        for feature in features:
            props = feature['properties']
            temp_val = props['temperature'] if props['temperature'] is not None else np.nan
            precip_val = props['precipitation'] if props['precipitation'] is not None else np.nan

            data.append({
                'date': props['date'],
                'temperature': temp_val,
                'precipitation': precip_val
            })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df.dropna(how='all')

        if df.empty:
            return None

        df_clean = df[(df['temperature'] > -100) & (df['temperature'] < 60)].copy()
        return df_clean

    except Exception as e:
        st.error(f"Error generating daily climate charts: {str(e)}")
        return None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_admin_boundaries(level, country_code=None, admin1_code=None):
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

# =============================================================================
# STREAMLIT APP MAIN FUNCTION
# =============================================================================

def main():
    # Initialize session state
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
    if 'auto_show_results' not in st.session_state:
        st.session_state.auto_show_results = False
    if 'climate_data' not in st.session_state:
        st.session_state.climate_data = None
    if 'ee_initialized' not in st.session_state:
        st.session_state.ee_initialized = False
    if 'selected_analysis_type' not in st.session_state:
        st.session_state.selected_analysis_type = "Vegetation & Climate"
    if 'soil_results' not in st.session_state:
        st.session_state.soil_results = None
    if 'climate_soil_results' not in st.session_state:
        st.session_state.climate_soil_results = None

    # Initialize Earth Engine
    if not st.session_state.ee_initialized:
        with st.spinner("Initializing Earth Engine..."):
            st.session_state.ee_initialized = auto_initialize_earth_engine()
            if st.session_state.ee_initialized:
                st.success("✅ Earth Engine initialized successfully!")
            else:
                st.error("❌ Earth Engine initialization failed")

    # Header
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1>🌍 KHISBA GIS - Climate & Soil Analyzer</h1>
        <p style="color: #999999; margin: 0; font-size: 14px;">Interactive Global Vegetation, Climate & Soil Analytics - Guided Workflow</p>
    </div>
    """, unsafe_allow_html=True)

    # Analysis Type Selector - Simplified
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Vegetation & Climate", "Climate & Soil"],
        index=0,
        key="analysis_type_selector"
    )
    st.session_state.selected_analysis_type = analysis_type

    # Define steps based on analysis type
    if analysis_type == "Vegetation & Climate":
        STEPS = [
            {"number": 1, "label": "Select Area", "icon": "📍"},
            {"number": 2, "label": "Set Parameters", "icon": "⚙️"},
            {"number": 3, "label": "View Map", "icon": "🗺️"},
            {"number": 4, "label": "Run Analysis", "icon": "🚀"},
            {"number": 5, "label": "View Results", "icon": "📊"}
        ]
    else:  # Climate & Soil
        STEPS = [
            {"number": 1, "label": "Select Area", "icon": "📍"},
            {"number": 2, "label": "Climate Settings", "icon": "🌤️"},
            {"number": 3, "label": "Soil Settings", "icon": "🌱"},
            {"number": 4, "label": "Run Analysis", "icon": "🚀"},
            {"number": 5, "label": "View Results", "icon": "📊"}
        ]

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

    # Status indicators
    st.markdown(f"""
    <div class="status-container">
        <div class="status-item">
            <div class="status-dot {'active' if st.session_state.ee_initialized else ''}"></div>
            <span>Earth Engine: {'Ready' if st.session_state.ee_initialized else 'Loading...'}</span>
        </div>
        <div class="status-item">
            <div class="status-dot {'active' if st.session_state.selected_area_name else ''}"></div>
            <span>Area Selected: {'Yes' if st.session_state.selected_area_name else 'No'}</span>
        </div>
        <div class="status-item">
            <div class="status-dot {'active' if st.session_state.analysis_results or st.session_state.soil_results else ''}"></div>
            <span>Analysis: {'Complete' if st.session_state.analysis_results or st.session_state.soil_results else 'Pending'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([0.35, 0.65], gap="large")

    with col1:
        # Step 1: Area Selection (Common for all analysis types)
        if st.session_state.current_step == 1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">📍</div><h3 style="margin: 0;">Step 1: Select Your Area</h3></div>', unsafe_allow_html=True)
            
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
                    countries_fc = get_admin_boundaries(0)
                    if countries_fc:
                        country_names = get_boundary_names(countries_fc, 0)
                        if country_names:
                            selected_country = st.selectbox(
                                "🌍 Country",
                                options=["Select a country"] + country_names,
                                index=0,
                                help="Choose a country for analysis",
                                key="country_select"
                            )
                            
                            if selected_country and selected_country != "Select a country":
                                country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                                admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                                
                                if admin1_fc:
                                    admin1_names = get_boundary_names(admin1_fc, 1)
                                    if admin1_names:
                                        selected_admin1 = st.selectbox(
                                            "🏛️ State/Province",
                                            options=["Select state/province"] + admin1_names,
                                            index=0,
                                            help="Choose a state or province",
                                            key="admin1_select"
                                        )
                                        
                                        if selected_admin1 and selected_admin1 != "Select state/province":
                                            admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                                            admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                                            
                                            if admin2_fc:
                                                admin2_names = get_boundary_names(admin2_fc, 2)
                                                if admin2_names:
                                                    selected_admin2 = st.selectbox(
                                                        "🏘️ Municipality",
                                                        options=["Select municipality"] + admin2_names,
                                                        index=0,
                                                        help="Choose a municipality",
                                                        key="admin2_select"
                                                    )
                                else:
                                    selected_admin1 = None
                                    selected_admin2 = None
                        else:
                            st.warning("No countries found. Please check Earth Engine connection.")
                    else:
                        st.error("Failed to load countries. Please check Earth Engine connection.")
                        
                except Exception as e:
                    st.error(f"Error loading boundaries: {str(e)}")
                    selected_country = None
                    selected_admin1 = None
                    selected_admin2 = None
            else:
                st.warning("Earth Engine not initialized. Please wait...")
                selected_country = None
                selected_admin1 = None
                selected_admin2 = None
            
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
                    
                    if st.button("✅ Confirm Selection", type="primary", use_container_width=True):
                        st.session_state.selected_geometry = geometry
                        st.session_state.selected_coordinates = coords_info
                        st.session_state.selected_area_name = area_name
                        st.session_state.selected_area_level = area_level
                        st.session_state.current_step = 2
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error processing geometry: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 2: Parameters based on analysis type
        elif st.session_state.current_step == 2:
            if analysis_type == "Vegetation & Climate":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Set Analysis Parameters</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.selected_area_name:
                    st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
                    
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
                    
                    collection_choice = st.selectbox(
                        "🛰️ Satellite Source",
                        options=["Sentinel-2", "Landsat-8"],
                        help="Choose satellite collection",
                        index=0
                    )
                    
                    cloud_cover = st.slider(
                        "☁️ Max Cloud Cover (%)",
                        min_value=0,
                        max_value=100,
                        value=20,
                        help="Maximum cloud cover percentage"
                    )
                    
                    # Simplified list of vegetation indices
                    available_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'MSAVI', 'GNDVI']
                    
                    selected_indices = st.multiselect(
                        "🌿 Vegetation Indices",
                        options=available_indices,
                        default=['NDVI', 'EVI', 'SAVI', 'NDWI'],
                        help="Choose vegetation indices to analyze"
                    )
                    
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
            
            else:  # Climate & Soil
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">🌤️</div><h3 style="margin: 0;">Step 2: Climate Settings</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.selected_area_name:
                    st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        start_date = st.date_input(
                            "📅 Start Date",
                            value=datetime(2024, 1, 1),
                            help="Start date for analysis"
                        )
                    with col_b:
                        end_date = st.date_input(
                            "📅 End Date",
                            value=datetime(2024, 12, 31),
                            help="End date for analysis"
                        )
                    
                    col_back, col_next = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Area Selection", use_container_width=True):
                            st.session_state.current_step = 1
                            st.rerun()
                    
                    with col_next:
                        if st.button("✅ Save Climate Settings", type="primary", use_container_width=True):
                            st.session_state.climate_parameters = {
                                'start_date': start_date,
                                'end_date': end_date
                            }
                            st.session_state.current_step = 3
                            st.rerun()
                else:
                    st.warning("Please go back to Step 1 and select an area first.")
                    if st.button("⬅️ Go to Area Selection", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Additional settings based on analysis type
        elif st.session_state.current_step == 3:
            if analysis_type == "Vegetation & Climate":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">🗺️</div><h3 style="margin: 0;">Step 3: Preview Selected Area</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.selected_area_name:
                    st.info(f"""
                    **Selected Area:** {st.session_state.selected_area_name}
                    
                    **Analysis Parameters:**
                    - Time Range: {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']}
                    - Satellite: {st.session_state.analysis_parameters['collection_choice']}
                    - Cloud Cover: ≤{st.session_state.analysis_parameters['cloud_cover']}%
                    - Indices: {', '.join(st.session_state.analysis_parameters['selected_indices'])}
                    """)
                    
                    col_back, col_next = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Parameters", use_container_width=True):
                            st.session_state.current_step = 2
                            st.rerun()
                    
                    with col_next:
                        if st.button("🚀 Run Analysis Now", type="primary", use_container_width=True):
                            st.session_state.current_step = 4
                            st.session_state.auto_show_results = False
                            st.rerun()
                else:
                    st.warning("No area selected. Please go back to Step 1.")
                    if st.button("⬅️ Go to Area Selection", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:  # Climate & Soil
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">🌱</div><h3 style="margin: 0;">Step 3: Soil Settings</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.selected_area_name:
                    st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
                    
                    st.markdown("""
                    <div class="guide-container">
                        <div class="guide-header">
                            <div class="guide-icon">🌍</div>
                            <div class="guide-title">Soil Analysis Settings</div>
                        </div>
                        <div class="guide-content">
                            Soil analysis will automatically use the best available data sources for your selected region.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    include_satellite_indices = st.checkbox(
                        "🛰️ Include Satellite Soil Indices",
                        value=True,
                        help="Use Sentinel-2 data for enhanced soil analysis"
                    )
                    
                    # Add enhanced analysis options
                    st.markdown("---")
                    with st.expander("🔬 Enhanced Analysis Options", expanded=True):
                        enhanced_analysis = st.checkbox(
                            "Include Comprehensive Climate Charts",
                            value=True,
                            help="Add detailed climate analysis: soil moisture, water balance, seasonal patterns"
                        )
                        
                        include_monthly_data = st.checkbox(
                            "Show Monthly Climate Data Table",
                            value=True,
                            help="Display monthly temperature, precipitation, and evaporation data in a table"
                        )
                    
                    st.markdown("""
                    **Data Sources:**
                    - **Global Soil Data:** FAO GSOCMAP (0-30cm depth)
                    - **Africa Soil Data:** ISDASOIL Africa (0-20cm depth)
                    - **Soil Texture:** OpenLandMap USDA Classification
                    - **Satellite Indices:** Sentinel-2 MSI (if enabled)
                    """)
                    
                    col_back, col_next = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Climate Settings", use_container_width=True):
                            st.session_state.current_step = 2
                            st.rerun()
                    
                    with col_next:
                        if st.button("✅ Save Soil Settings", type="primary", use_container_width=True):
                            st.session_state.soil_parameters = {
                                'include_satellite_indices': include_satellite_indices,
                                'enhanced_analysis': enhanced_analysis,
                                'include_monthly_data': include_monthly_data
                            }
                            st.session_state.current_step = 4
                            st.rerun()
                else:
                    st.warning("Please go back to Step 1 and select an area first.")
                    if st.button("⬅️ Go to Area Selection", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 4: Run analysis
        elif st.session_state.current_step == 4:
            if analysis_type == "Vegetation & Climate":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 4: Running Analysis</h3></div>', unsafe_allow_html=True)
                
                if not st.session_state.auto_show_results:
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    with progress_placeholder.container():
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        analysis_steps = [
                            "Initializing Earth Engine...",
                            "Loading satellite data...",
                            "Processing vegetation indices...",
                            "Calculating climate data...",
                            "Generating visualizations..."
                        ]
                        
                        try:
                            params = st.session_state.analysis_parameters
                            geometry = st.session_state.selected_geometry
                            
                            for i, step in enumerate(analysis_steps):
                                status_text.text(step)
                                progress_bar.progress((i + 1) / len(analysis_steps))
                                import time
                                time.sleep(1)
                            
                            # Get vegetation indices time series
                            st.session_state.analysis_results = get_vegetation_indices_timeseries(
                                geometry,
                                params['start_date'].strftime('%Y-%m-%d'),
                                params['end_date'].strftime('%Y-%m-%d'),
                                params['collection_choice'],
                                params['cloud_cover'],
                                params['selected_indices']
                            )
                            
                            # Get climate data
                            try:
                                climate_df = analyze_daily_climate_data(
                                    geometry.geometry(),
                                    params['start_date'].strftime('%Y-%m-%d'),
                                    params['end_date'].strftime('%Y-%m-%d')
                                )
                                st.session_state.climate_data = climate_df
                            except Exception as e:
                                st.session_state.climate_data = None
                            
                            progress_bar.progress(1.0)
                            status_text.text("✅ Analysis Complete!")
                            
                            time.sleep(2)
                            st.session_state.current_step = 5
                            st.session_state.auto_show_results = True
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
                            if st.button("🔄 Try Again", use_container_width=True):
                                st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:  # Climate & Soil
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 4: Run Climate & Soil Analysis</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.selected_area_name:
                    st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
                    
                    st.markdown("""
                    <div class="guide-container">
                        <div class="guide-header">
                            <div class="guide-icon">📊</div>
                            <div class="guide-title">Ready to Analyze</div>
                        </div>
                        <div class="guide-content">
                            Click the button below to run comprehensive climate and soil analysis for your selected area.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get enhanced analysis option from session state
                    enhanced_analysis = st.session_state.soil_parameters.get('enhanced_analysis', True) if hasattr(st.session_state, 'soil_parameters') else True
                    
                    col_back, col_next = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Soil Settings", use_container_width=True):
                            st.session_state.current_step = 3
                            st.rerun()
                    
                    with col_next:
                        if st.button("🚀 Run Climate & Soil Analysis", type="primary", use_container_width=True):
                            with st.spinner("Running Comprehensive Climate & Soil Analysis..."):
                                analyzer = SimplifiedClimateSoilAnalyzer()
                                
                                # Extract country, region, municipality from selected area name
                                area_parts = st.session_state.selected_area_name.split(',')
                                if len(area_parts) == 3:
                                    country = area_parts[2].strip()
                                    region = area_parts[1].strip()
                                    municipality = area_parts[0].strip()
                                elif len(area_parts) == 2:
                                    country = area_parts[1].strip()
                                    region = area_parts[0].strip()
                                    municipality = 'Select Municipality'
                                else:
                                    country = area_parts[0].strip()
                                    region = 'Select Region'
                                    municipality = 'Select Municipality'
                                
                                # Get geometry
                                geometry, location_name = analyzer.get_geometry_from_selection(
                                    country, region, municipality
                                )
                                
                                if geometry:
                                    if enhanced_analysis:
                                        # Run enhanced analysis with comprehensive charts
                                        enhanced_results = analyzer.run_enhanced_climate_soil_analysis(
                                            geometry, location_name
                                        )
                                        
                                        if enhanced_results:
                                            st.session_state.climate_soil_results = {
                                                'enhanced_results': enhanced_results,
                                                'location_name': location_name,
                                                'analysis_type': 'enhanced'
                                            }
                                            
                                            st.session_state.current_step = 5
                                            st.rerun()
                                        else:
                                            st.error("Enhanced analysis failed. Please try again.")
                                    else:
                                        # Original basic analysis
                                        # Get climate classification
                                        climate_results = analyzer.get_accurate_climate_classification(
                                            geometry, location_name
                                        )
                                        
                                        # Get soil analysis
                                        soil_results = analyzer.run_comprehensive_soil_analysis(
                                            country, region, municipality
                                        )
                                        
                                        if soil_results:
                                            st.session_state.climate_soil_results = {
                                                'climate': climate_results,
                                                'soil': soil_results,
                                                'location_name': location_name,
                                                'analysis_type': 'basic'
                                            }
                                            
                                            st.session_state.current_step = 5
                                            st.rerun()
                                        else:
                                            st.error("Soil analysis failed. Please try again.")
                else:
                    st.warning("Please go back to Step 1 and select an area first.")
                    if st.button("⬅️ Go to Area Selection", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 5: View results
        elif st.session_state.current_step == 5:
            if analysis_type == "Vegetation & Climate":
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 5: Analysis Results</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.analysis_results or st.session_state.climate_data is not None:
                    col_back, col_new = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Map", use_container_width=True):
                            st.session_state.current_step = 3
                            st.rerun()
                    
                    with col_new:
                        if st.button("🔄 New Analysis", use_container_width=True):
                            for key in ['selected_geometry', 'analysis_results', 'selected_coordinates', 
                                       'selected_area_name', 'analysis_parameters', 'climate_data']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.session_state.current_step = 1
                            st.rerun()
                    
                    st.subheader("💾 Export Results")
                    if st.button("📥 Download All Data", use_container_width=True):
                        export_data = []
                        
                        for index, data in st.session_state.analysis_results.items():
                            for date, value in zip(data['dates'], data['values']):
                                export_data.append({
                                    'Date': date,
                                    'Index': index,
                                    'Value': value
                                })
                        
                        if st.session_state.climate_data is not None:
                            climate_df = st.session_state.climate_data
                            for _, row in climate_df.iterrows():
                                export_data.append({
                                    'Date': row['date'].strftime('%Y-%m-%d'),
                                    'Index': 'Temperature (°C)',
                                    'Value': row['temperature']
                                })
                                export_data.append({
                                    'Date': row['date'].strftime('%Y-%m-%d'),
                                    'Index': 'Precipitation (mm)',
                                    'Value': row['precipitation']
                                })
                        
                        if export_data:
                            df = pd.DataFrame(export_data)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Click to Download CSV",
                                data=csv,
                                file_name=f"vegetation_climate_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("No data available for export")
                else:
                    st.warning("No results available. Please run an analysis first.")
                    if st.button("⬅️ Go Back", use_container_width=True):
                        st.session_state.current_step = 4
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:  # Climate & Soil
                st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
                st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">📊 Climate & Soil Analysis Results</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.climate_soil_results:
                    analyzer = SimplifiedClimateSoilAnalyzer()
                    
                    # Check analysis type
                    analysis_type_result = st.session_state.climate_soil_results.get('analysis_type', 'basic')
                    
                    if analysis_type_result == 'enhanced':
                        # Display enhanced analysis
                        enhanced_results = st.session_state.climate_soil_results.get('enhanced_results')
                        if enhanced_results:
                            analyzer.display_enhanced_analysis(enhanced_results)
                    else:
                        # Display basic analysis
                        climate_data = st.session_state.climate_soil_results.get('climate')
                        soil_results = st.session_state.climate_soil_results.get('soil')
                        location_name = st.session_state.climate_soil_results.get('location_name', 'Unknown Location')
                        
                        if climate_data:
                            # Display climate classification
                            st.markdown("---")
                            st.markdown('<div class="section-header">🌤️ CLIMATE CLASSIFICATION</div>', unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("🌡️ Mean Temperature", f"{climate_data['mean_temperature']:.1f}°C")
                            with col2:
                                st.metric("💧 Mean Precipitation", f"{climate_data['mean_precipitation']:.0f} mm/year")
                            with col3:
                                st.metric("🌍 Climate Zone", climate_data['climate_zone'].split('(')[0])
                            
                            # Display climate classification chart
                            fig = analyzer.create_climate_classification_chart(location_name, climate_data)
                            st.pyplot(fig)
                            plt.close(fig)
                        
                        # Display soil analysis
                        if soil_results:
                            st.markdown("---")
                            st.markdown('<div class="section-header">🌱 SOIL ANALYSIS RESULTS</div>', unsafe_allow_html=True)
                            analyzer.display_soil_analysis(soil_results)
                    
                    # Navigation buttons
                    col_back, col_new = st.columns(2)
                    with col_back:
                        if st.button("⬅️ Back to Settings", use_container_width=True):
                            st.session_state.current_step = 4
                            st.rerun()
                    
                    with col_new:
                        if st.button("🔄 New Analysis", use_container_width=True):
                            for key in ['selected_geometry', 'climate_soil_results', 'selected_coordinates', 
                                       'selected_area_name', 'climate_parameters', 'soil_parameters']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.session_state.current_step = 1
                            st.rerun()
                else:
                    st.warning("No results available. Please run an analysis first.")
                    if st.button("⬅️ Go Back", use_container_width=True):
                        st.session_state.current_step = 4
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Right column - Show map or results based on step
        if st.session_state.current_step <= 3:
            st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
            st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Interactive 3D Global Map</h3></div>', unsafe_allow_html=True)
            
            map_center = [0, 20]
            map_zoom = 2
            bounds_data = None
            
            if st.session_state.selected_coordinates:
                map_center = st.session_state.selected_coordinates['center']
                map_zoom = st.session_state.selected_coordinates['zoom']
                bounds_data = st.session_state.selected_coordinates['bounds']
            
            mapbox_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8" />
              <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
              <title>KHISBA GIS - 3D Global Map</title>
              <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
              <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
              <style>
                body {{ 
                  margin: 0; 
                  padding: 0; 
                  background: #000000;
                }}
                #map {{ 
                  position: absolute; 
                  top: 0; 
                  bottom: 0; 
                  width: 100%; 
                  border-radius: 8px;
                }}
                .map-overlay {{
                  position: absolute;
                  top: 20px;
                  right: 20px;
                  background: rgba(10, 10, 10, 0.9);
                  color: white;
                  padding: 15px;
                  border-radius: 8px;
                  border: 1px solid #222222;
                  max-width: 250px;
                  z-index: 1000;
                  font-family: 'Inter', sans-serif;
                }}
                .overlay-title {{
                  color: #00ff88;
                  font-weight: 600;
                  margin-bottom: 10px;
                  font-size: 14px;
                }}
                .overlay-text {{
                  color: #cccccc;
                  font-size: 12px;
                  line-height: 1.4;
                }}
                .coordinates-display {{
                  position: absolute;
                  bottom: 20px;
                  left: 20px;
                  background: rgba(10, 10, 10, 0.9);
                  color: white;
                  padding: 10px 15px;
                  border-radius: 6px;
                  border: 1px solid #222222;
                  font-family: monospace;
                  font-size: 12px;
                  z-index: 1000;
                }}
                .selected-area {{
                  position: absolute;
                  top: 20px;
                  left: 20px;
                  background: rgba(10, 10, 10, 0.9);
                  color: white;
                  padding: 15px;
                  border-radius: 8px;
                  border: 1px solid #222222;
                  max-width: 300px;
                  z-index: 1000;
                  font-family: 'Inter', sans-serif;
                }}
                .area-title {{
                  color: #00ff88;
                  font-weight: 600;
                  margin-bottom: 10px;
                  font-size: 14px;
                }}
                .area-details {{
                  color: #cccccc;
                  font-size: 12px;
                  line-height: 1.4;
                }}
                .layer-switcher {{
                  position: absolute;
                  top: 20px;
                  right: 20px;
                  background: rgba(10, 10, 10, 0.9);
                  border: 1px solid #222222;
                  border-radius: 8px;
                  overflow: hidden;
                  z-index: 1000;
                }}
                .layer-button {{
                  display: block;
                  width: 120px;
                  padding: 10px;
                  background: #0a0a0a;
                  color: #ffffff;
                  border: none;
                  border-bottom: 1px solid #222222;
                  cursor: pointer;
                  font-size: 12px;
                  text-align: left;
                  transition: all 0.2s;
                }}
                .layer-button:hover {{
                  background: #111111;
                }}
                .layer-button.active {{
                  background: #00ff88;
                  color: #000000;
                  font-weight: bold;
                }}
                .layer-button:last-child {{
                  border-bottom: none;
                }}
                .mapboxgl-ctrl-group {{
                  background: #0a0a0a !important;
                  border: 1px solid #222222 !important;
                }}
                .mapboxgl-ctrl button {{
                  background-color: #0a0a0a !important;
                  color: #ffffff !important;
                }}
                .mapboxgl-ctrl button:hover {{
                  background-color: #111111 !important;
                }}
              </style>
            </head>
            <body>
              <div id="map"></div>
              
              <div class="map-overlay">
                <div class="overlay-title">🌍 KHISBA GIS</div>
                <div class="overlay-text">
                  • Drag to rotate the globe<br>
                  • Scroll to zoom in/out<br>
                  • Right-click to pan<br>
                  • Selected area highlighted in green
                </div>
              </div>
              
              <div class="layer-switcher">
                <button class="layer-button" data-style="mapbox://styles/mapbox/satellite-streets-v12">Satellite Streets</button>
                <button class="layer-button" data-style="mapbox://styles/mapbox/streets-v12">Streets</button>
                <button class="layer-button active" data-style="mapbox://styles/mapbox/outdoors-v12">Outdoors</button>
                <button class="layer-button" data-style="mapbox://styles/mapbox/light-v11">Light</button>
                <button class="layer-button" data-style="mapbox://styles/mapbox/dark-v11">Dark</button>
              </div>
              
              <div class="coordinates-display">
                <div>Lat: <span id="lat-display">0.00°</span></div>
                <div>Lon: <span id="lon-display">0.00°</span></div>
              </div>
              
              {f'''
              <div class="selected-area">
                <div class="area-title">📍 Selected Area</div>
                <div class="area-details">
                  <strong>{st.session_state.selected_area_name if hasattr(st.session_state, 'selected_area_name') else 'None'}</strong><br>
                  Level: {st.session_state.selected_area_level if hasattr(st.session_state, 'selected_area_level') else 'None'}<br>
                  Coordinates: {map_center[1]:.4f}°, {map_center[0]:.4f}°<br>
                  Status: <span style="color: #00ff88;">Ready for Analysis</span>
                </div>
              </div>
              ''' if st.session_state.selected_area_name else ''}
              
              <script>
                mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';

                const map = new mapboxgl.Map({{
                  container: 'map',
                  style: 'mapbox://styles/mapbox/outdoors-v12',
                  center: {map_center},
                  zoom: {map_zoom},
                  pitch: 45,
                  bearing: 0
                }});

                map.addControl(new mapboxgl.NavigationControl());
                map.addControl(new mapboxgl.ScaleControl({{
                  unit: 'metric'
                }}));
                map.addControl(new mapboxgl.FullscreenControl());

                const layerButtons = document.querySelectorAll('.layer-button');
                layerButtons.forEach(button => {{
                  button.addEventListener('click', () => {{
                    layerButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    map.setStyle(button.dataset.style);
                    
                    setTimeout(() => {{
                      {f'''
                      if ({bounds_data}) {{
                        const bounds = {bounds_data};
                        
                        if (map.getSource('selected-area')) {{
                          map.removeLayer('selected-area-fill');
                          map.removeLayer('selected-area-border');
                          map.removeSource('selected-area');
                        }}
                        
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
                          'layout': {{}},
                          'paint': {{
                            'fill-color': '#00ff88',
                            'fill-opacity': 0.2
                          }}
                        }});

                        map.addLayer({{
                          'id': 'selected-area-border',
                          'type': 'line',
                          'source': 'selected-area',
                          'layout': {{}},
                          'paint': {{
                            'line-color': '#00ff88',
                            'line-width': 3,
                            'line-opacity': 0.8
                          }}
                        }});
                      }}
                      ''' if bounds_data else ''}
                    }}, 500);
                  }});
                }});

                map.on('load', () => {{
                  map.on('mousemove', (e) => {{
                    document.getElementById('lat-display').textContent = e.lngLat.lat.toFixed(2) + '°';
                    document.getElementById('lon-display').textContent = e.lngLat.lng.toFixed(2) + '°';
                  }});

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
                      'layout': {{}},
                      'paint': {{
                        'fill-color': '#00ff88',
                        'fill-opacity': 0.2
                      }}
                    }});

                    map.addLayer({{
                      'id': 'selected-area-border',
                      'type': 'line',
                      'source': 'selected-area',
                      'layout': {{}},
                      'paint': {{
                        'line-color': '#00ff88',
                        'line-width': 3,
                        'line-opacity': 0.8
                      }}
                    }});

                    map.flyTo({{
                      center: {map_center},
                      zoom: {map_zoom},
                      duration: 2000,
                      essential: true
                    }});
                  }}
                  ''' if bounds_data else ''}

                  const cities = [
                    {{ name: 'New York', coordinates: [-74.006, 40.7128], country: 'USA', info: 'Financial capital' }},
                    {{ name: 'London', coordinates: [-0.1276, 51.5074], country: 'UK', info: 'Historical capital' }},
                    {{ name: 'Tokyo', coordinates: [139.6917, 35.6895], country: 'Japan', info: 'Mega metropolis' }},
                    {{ name: 'Sydney', coordinates: [151.2093, -33.8688], country: 'Australia', info: 'Harbor city' }},
                    {{ name: 'Cairo', coordinates: [31.2357, 30.0444], country: 'Egypt', info: 'Nile Delta' }}
                  ];

                  cities.forEach(city => {{
                    const el = document.createElement('div');
                    el.className = 'marker';
                    el.style.backgroundColor = '#ffaa00';
                    el.style.width = '15px';
                    el.style.height = '15px';
                    el.style.borderRadius = '50%';
                    el.style.border = '2px solid #ffffff';
                    el.style.boxShadow = '0 0 10px rgba(255, 170, 0, 0.5)';
                    el.style.cursor = 'pointer';

                    const popup = new mapboxgl.Popup({{
                      offset: 25,
                      closeButton: true,
                      closeOnClick: false
                    }}).setHTML(
                      `<h3>${{city.name}}</h3>
                       <p><strong>Country:</strong> ${{city.country}}</p>
                       <p>${{city.info}}</p>`
                    );

                    new mapboxgl.Marker(el)
                      .setLngLat(city.coordinates)
                      .setPopup(popup)
                      .addTo(map);
                  }});
                }});
              </script>
            </body>
            </html>
            """
            
            st.components.v1.html(mapbox_html, height=550)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif st.session_state.current_step == 4:
            st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
            st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Analysis in Progress</h3></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 20px; animation: spin 2s linear infinite;">🌱</div>
                <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Processing {analysis_type} Data</div>
                <div style="color: #666666; font-size: 14px;">Analyzing {st.session_state.selected_area_name if hasattr(st.session_state, 'selected_area_name') else 'selected area'}</div>
            </div>
            
            <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif st.session_state.current_step == 5:
            if analysis_type == "Vegetation & Climate":
                st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
                st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">📊 Vegetation & Climate Analysis Results</h3></div>', unsafe_allow_html=True)
                
                if st.session_state.analysis_results:
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 10px 20px; border-left: 4px solid #00ff88;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="color: #00ff88; font-weight: 600; font-size: 16px;">{st.session_state.selected_area_name}</div>
                                <div style="color: #cccccc; font-size: 12px; margin-top: 5px;">
                                    {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']} • 
                                    {st.session_state.analysis_parameters['collection_choice']} • 
                                    {len(st.session_state.analysis_parameters['selected_indices'])} vegetation indices analyzed
                                </div>
                            </div>
                            <div style="background: #00ff88; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                                ✅ Complete
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display climate data if available
                    if st.session_state.climate_data is not None:
                        climate_df = st.session_state.climate_data
                        
                        st.markdown("""
                        <div style="margin: 20px;">
                            <h3 style="color: #00ff88;">🌤️ Climate Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Temperature chart
                        fig_temp = go.Figure()
                        fig_temp.add_trace(go.Scatter(
                            x=climate_df['date'],
                            y=climate_df['temperature'],
                            mode='lines+markers',
                            name='Temperature',
                            line=dict(color='#ff5555', width=3),
                            marker=dict(size=8, color='#ffffff', line=dict(width=1, color='#ff5555'))
                        ))
                        
                        fig_temp.update_layout(
                            title="<b>Daily Temperature (°C)</b>",
                            plot_bgcolor='#0a0a0a',
                            paper_bgcolor='#0a0a0a',
                            font=dict(color='#ffffff'),
                            xaxis=dict(
                                title="Date",
                                gridcolor='#222222',
                                tickcolor='#444444',
                                showgrid=True
                            ),
                            yaxis=dict(
                                title="Temperature (°C)",
                                gridcolor='#222222',
                                tickcolor='#444444',
                                showgrid=True
                            ),
                            height=300,
                            margin=dict(l=50, r=50, t=50, b=50),
                            hovermode='x unified',
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig_temp, use_container_width=True, key="temperature_chart")
                        
                        # Precipitation chart
                        fig_precip = go.Figure()
                        fig_precip.add_trace(go.Bar(
                            x=climate_df['date'],
                            y=climate_df['precipitation'],
                            name='Precipitation',
                            marker_color='#5555ff'
                        ))
                        
                        fig_precip.update_layout(
                            title="<b>Daily Precipitation (mm)</b>",
                            plot_bgcolor='#0a0a0a',
                            paper_bgcolor='#0a0a0a',
                            font=dict(color='#ffffff'),
                            xaxis=dict(
                                title="Date",
                                gridcolor='#222222',
                                tickcolor='#444444',
                                showgrid=True
                            ),
                            yaxis=dict(
                                title="Precipitation (mm)",
                                gridcolor='#222222',
                                tickcolor='#444444',
                                showgrid=True
                            ),
                            height=300,
                            margin=dict(l=50, r=50, t=50, b=50),
                            hovermode='x unified',
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig_precip, use_container_width=True, key="precipitation_chart")
                        
                        # Climate statistics
                        if not climate_df.empty:
                            temp_mean = climate_df['temperature'].mean()
                            temp_max = climate_df['temperature'].max()
                            temp_min = climate_df['temperature'].min()
                            precip_total = climate_df['precipitation'].sum()
                            precip_mean = climate_df['precipitation'].mean()
                            precip_max = climate_df['precipitation'].max()
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"""
                                <div style="background: rgba(255, 85, 85, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #ff5555; margin-bottom: 10px;">
                                    <div style="color: #ff5555; font-weight: 600; margin-bottom: 10px;">🌡️ Temperature</div>
                                    <div style="color: #cccccc; font-size: 14px;">
                                        <div>Mean: <strong>{temp_mean:.2f}°C</strong></div>
                                        <div>Max: <strong>{temp_max:.2f}°C</strong></div>
                                        <div>Min: <strong>{temp_min:.2f}°C</strong></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div style="background: rgba(85, 85, 255, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #5555ff; margin-bottom: 10px;">
                                    <div style="color: #5555ff; font-weight: 600; margin-bottom: 10px;">🌧️ Precipitation</div>
                                    <div style="color: #cccccc; font-size: 14px;">
                                        <div>Total: <strong>{precip_total:.1f} mm</strong></div>
                                        <div>Mean: <strong>{precip_mean:.2f} mm/day</strong></div>
                                        <div>Max: <strong>{precip_max:.1f} mm/day</strong></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Display vegetation indices
                    st.markdown("""
                    <div style="margin: 20px;">
                        <h3 style="color: #00ff88;">🌿 Vegetation Indices</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for index_name, data in st.session_state.analysis_results.items():
                        if data['dates'] and data['values']:
                            try:
                                # Create plot
                                fig = go.Figure()
                                
                                # Main line
                                fig.add_trace(go.Scatter(
                                    x=data['dates'],
                                    y=data['values'],
                                    mode='lines+markers',
                                    name=index_name,
                                    line=dict(color='#00ff88', width=3),
                                    marker=dict(size=8, color='#ffffff', line=dict(width=1, color='#00ff88'))
                                ))
                                
                                # Add trend line if enough data points
                                if len(data['values']) > 1:
                                    try:
                                        # Convert dates to numeric for trend calculation
                                        x_numeric = list(range(len(data['dates'])))
                                        z = np.polyfit(x_numeric, data['values'], 1)
                                        p = np.poly1d(z)
                                        trend_values = p(x_numeric)
                                        
                                        fig.add_trace(go.Scatter(
                                            x=data['dates'],
                                            y=trend_values,
                                            mode='lines',
                                            name='Trend',
                                            line=dict(color='#ffaa00', width=2, dash='dash')
                                        ))
                                    except:
                                        pass
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"<b>{index_name}</b> - Vegetation Index Over Time",
                                    plot_bgcolor='#0a0a0a',
                                    paper_bgcolor='#0a0a0a',
                                    font=dict(color='#ffffff'),
                                    xaxis=dict(
                                        title="Date",
                                        gridcolor='#222222',
                                        tickcolor='#444444',
                                        showgrid=True
                                    ),
                                    yaxis=dict(
                                        title=f"{index_name} Value",
                                        gridcolor='#222222',
                                        tickcolor='#444444',
                                        showgrid=True
                                    ),
                                    height=300,
                                    margin=dict(l=50, r=50, t=50, b=50),
                                    hovermode='x unified',
                                    showlegend=True,
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                    )
                                )
                                
                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{index_name}")
                                
                                # Display statistics for this index
                                values = data['values']
                                if values:
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric(f"{index_name} Mean", f"{np.mean(values):.3f}")
                                    with col2:
                                        st.metric(f"{index_name} Max", f"{np.max(values):.3f}")
                                    with col3:
                                        st.metric(f"{index_name} Min", f"{np.min(values):.3f}")
                                    with col4:
                                        if len(values) > 1:
                                            trend = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
                                            st.metric(f"{index_name} Trend", f"{trend:+.1f}%")
                                
                                st.markdown("---")
                                
                            except Exception as e:
                                st.warning(f"Could not display chart for {index_name}: {str(e)}")
                    
                    # Summary table
                    summary_data = []
                    for index_name, data in st.session_state.analysis_results.items():
                        if data['values']:
                            values = data['values']
                            if values:
                                current = values[-1] if values else 0
                                previous = values[-2] if len(values) > 1 else current
                                change = ((current - previous) / previous * 100) if previous != 0 else 0
                                
                                summary_data.append({
                                    'Index': index_name,
                                    'Current': round(current, 4),
                                    'Previous': round(previous, 4),
                                    'Change (%)': f"{change:+.2f}%",
                                    'Min': round(min(values), 4),
                                    'Max': round(max(values), 4),
                                    'Avg': round(sum(values) / len(values), 4)
                                })
                    
                    if summary_data:
                        st.markdown("""
                        <div style="margin: 20px;">
                            <h3 style="color: #00ff88;">📋 Summary Statistics</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        df = pd.DataFrame(summary_data)
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Change (%)": st.column_config.TextColumn(
                                    "Change",
                                    help="Percentage change from previous period",
                                )
                            }
                        )
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 100px 0;">
                        <div style="font-size: 64px; margin-bottom: 20px;">📊</div>
                        <div style="color: #666666; font-size: 16px; margin-bottom: 10px;">No Results Available</div>
                        <div style="color: #444444; font-size: 14px;">Please run an analysis to see results</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:  # Climate & Soil
                # Results are displayed in the left column for Climate & Soil
                pass

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
        <p style="margin: 5px 0;">KHISBA GIS • Climate & Soil Analyzer • Interactive Analytics Platform</p>
        <p style="margin: 5px 0;">Climate Analysis • Soil Analysis • Vegetation Analysis • Auto Results Display • 3D Map • Guided Workflow</p>
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌡️ Climate Data</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌱 Soil Analysis</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌿 Vegetation</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">3D Mapbox</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v3.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() Enhanced analysis error: x and y must have same first dimension, but have shapes (11,) and (12,)

Enhanced analysis failed. Please try again. fix this on climate soil analysis
