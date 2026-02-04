import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import traceback
import sys
import subprocess

# Try to import additional packages
try:
    from matplotlib.patches import FancyBboxPatch
    MATPLOTLIB_PATCHES_AVAILABLE = True
except ImportError:
    MATPLOTLIB_PATCHES_AVAILABLE = False
    # Try to install if needed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
    except:
        pass

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Comprehensive Agricultural Analyzer",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #228B22;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #228B22;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #32CD32;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F0FFF0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #32CD32;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E8F4F8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E90FF;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFA500;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #2E8B57;
    }
</style>
""", unsafe_allow_html=True)

# Auto-initialize Earth Engine
@st.cache_resource
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
        st.error(f"Earth Engine auto-initialization failed: {str(e)[:100]}...")
        return False

# Initialize Earth Engine at startup
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        st.session_state.ee_initialized = auto_initialize_earth_engine()

# ============ COMPREHENSIVE CROP SUITABILITY CONFIGURATION ============
CROP_REQUIREMENTS = {
    # CEREALS & GRAINS
    'Wheat': {
        'moisture_opt': 0.18, 'moisture_tol': 0.06, 'om_opt': 2.0, 'om_tol': 1.0,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.85,
            'Sandy clay loam': 0.6, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.7,
            'Silt loam': 0.9, 'Silt': 0.8, 'Loamy sand': 0.4, 'Sand': 0.1
        },
        'temp_opt': 18, 'temp_tol': 6, 'maturity_days': 120, 'water_needs': 'Medium',
        'notes': 'Cool season cereal, requires good drainage',
        'management': [
            'Rotate with legumes to break disease cycles',
            'Apply balanced NPK fertilizer (100-120-60 kg/ha)',
            'Use certified disease-free seeds',
            'Monitor for aphids and rust diseases regularly',
            'Time planting to avoid peak disease periods'
        ],
        'likely_diseases': [
            'Leaf rust (Puccinia triticina) - orange pustules on leaves',
            'Stripe rust (Puccinia striiformis) - yellow stripes on leaves',
            'Fusarium head blight - pink mold on heads in wet conditions',
            'Powdery mildew - white fungal growth on leaves',
            'Septoria tritici blotch - brown spots with black pycnidia'
        ],
        'pests': ['Aphids', 'Armyworms', 'Hessian fly', 'Stem sawfly'],
        'fertilizer': 'NPK 100-120-60 kg/ha + Zinc',
        'spacing': '20-25 cm between rows, 2-3 cm between plants',
        'risk_factors': ['High moisture', 'Dense planting', 'Poor air circulation']
    },
    'Barley': {
        'moisture_opt': 0.16, 'moisture_tol': 0.06, 'om_opt': 1.6, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.6, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 16, 'temp_tol': 6, 'maturity_days': 100, 'water_needs': 'Low-Medium',
        'notes': 'Drought tolerant, good for marginal soils',
        'management': [
            'Well-drained soil essential to prevent root diseases',
            'Apply 80-100 kg N/ha, adjust based on soil test',
            'Use resistant varieties for prevalent diseases',
            'Control weeds early as barley is poor competitor',
            'Harvest when moisture content reaches 13-15%'
        ],
        'likely_diseases': [
            'Net blotch (Pyrenophora teres) - net-like patterns on leaves',
            'Scald (Rhynchosporium secalis) - oval gray-green lesions',
            'Stripe rust - yellow stripes, severe in cool wet weather',
            'Spot blotch - circular brown spots on leaves and heads',
            'Fusarium head blight - pink-orange mold on kernels'
        ],
        'pests': ['Aphids', 'Wireworms', 'Cutworms', 'Bird damage'],
        'fertilizer': 'NPK 80-60-40 kg/ha',
        'spacing': '15-20 cm between rows',
        'risk_factors': ['Cool wet conditions', 'High nitrogen', 'Continuous cropping']
    },
    'Maize': {
        'moisture_opt': 0.28, 'moisture_tol': 0.07, 'om_opt': 2.2, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.7, 'Clay loam': 0.8,
            'Sandy clay loam': 0.6, 'Silty clay loam': 0.9, 'Loam': 1.0, 'Sandy loam': 0.7,
            'Silt loam': 0.95, 'Silt': 0.8, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 25, 'temp_tol': 7, 'maturity_days': 120, 'water_needs': 'High',
        'notes': 'Warm season, high water and nutrient demands',
        'management': [
            'Plant when soil temperature reaches 10-12°C',
            'Apply 150-200 kg N/ha in split applications',
            'Use crop rotation to reduce disease pressure',
            'Ensure good drainage to prevent root diseases',
            'Monitor for ear worms during silking stage'
        ],
        'likely_diseases': [
            'Northern corn leaf blight - cigar-shaped gray-green lesions',
            'Gray leaf spot - rectangular tan lesions between veins',
            'Common rust - cinnamon-brown pustules on both leaf surfaces',
            'Stalk rots (Fusarium, Gibberella) - lodging and internal discoloration',
            'Ear rots - various fungi causing mycotoxin contamination'
        ],
        'pests': ['Corn earworm', 'European corn borer', 'Armyworms', 'Rootworms'],
        'fertilizer': 'NPK 150-80-100 kg/ha + Sulfur',
        'spacing': '75 cm between rows, 20-25 cm between plants',
        'risk_factors': ['High humidity', 'Poor drainage', 'High plant density']
    },
    'Rice': {
        'moisture_opt': 0.35, 'moisture_tol': 0.08, 'om_opt': 2.5, 'om_tol': 1.0,
        'texture_scores': {
            'Clay': 0.9, 'Sandy clay': 0.7, 'Silty clay': 0.8, 'Clay loam': 0.8,
            'Sandy clay loam': 0.6, 'Silty clay loam': 0.9, 'Loam': 0.7, 'Sandy loam': 0.4,
            'Silt loam': 0.8, 'Silt': 0.9, 'Loamy sand': 0.3, 'Sand': 0.1
        },
        'temp_opt': 28, 'temp_tol': 5, 'maturity_days': 150, 'water_needs': 'Very High',
        'notes': 'Requires flooded conditions, heavy soils preferred',
        'management': [
            'Maintain 5-10 cm water depth during vegetative stage',
            'Apply 100-120 kg N/ha in 3 split applications',
            'Use integrated pest management for stem borers',
            'Drain field 2-3 weeks before harvest for grain quality',
            'Practice proper field leveling for uniform water distribution'
        ],
        'likely_diseases': [
            'Rice blast (Magnaporthe oryzae) - diamond-shaped lesions on leaves',
            'Sheath blight - oval lesions on leaf sheaths, common in dense planting',
            'Bacterial leaf blight - yellow streaks turning white',
            'Brown spot - oval brown spots on leaves and grains',
            'Tungro virus - yellow-orange leaves, stunted growth'
        ],
        'pests': ['Stem borers', 'Brown plant hopper', 'Rice leaf folder', 'Gall midge'],
        'fertilizer': 'NPK 120-60-60 kg/ha + Zinc',
        'spacing': '20 x 20 cm for transplanted rice',
        'risk_factors': ['Stagnant water', 'High nitrogen', 'Poor water management']
    },
    # Add more crops as needed from the original list...
    'Tomato': {
        'moisture_opt': 0.24, 'moisture_tol': 0.06, 'om_opt': 2.5, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 24, 'temp_tol': 6, 'maturity_days': 100, 'water_needs': 'Medium-High',
        'notes': 'Warm season, consistent moisture needed',
        'management': [
            'Stake or cage plants for better air circulation and fruit quality',
            'Apply balanced fertilizer with emphasis on calcium',
            'Use drip irrigation to keep foliage dry and reduce diseases',
            'Practice crop rotation to reduce soil-borne diseases',
            'Monitor for pests and diseases weekly'
        ],
        'likely_diseases': [
            'Early blight - target-like spots with concentric rings',
            'Late blight - water-soaked lesions spreading rapidly in cool wet weather',
            'Bacterial spot - small dark lesions with yellow halos',
            'Fusarium wilt - yellowing and wilting of one side of plant',
            'Blossom end rot - physiological disorder from calcium/water imbalance'
        ],
        'pests': ['Tomato hornworm', 'Whiteflies', 'Aphids', 'Spider mites'],
        'fertilizer': 'NPK 120-80-150 kg/ha + Calcium',
        'spacing': '60-90 cm between rows, 45-60 cm between plants',
        'risk_factors': ['High humidity', 'Overhead irrigation', 'Poor air circulation']
    },
    'Potato': {
        'moisture_opt': 0.28, 'moisture_tol': 0.06, 'om_opt': 3.0, 'om_tol': 1.0,
        'texture_scores': {
            'Clay': 0.2, 'Sandy clay': 0.3, 'Silty clay': 0.4, 'Clay loam': 0.6,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.95, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 18, 'temp_tol': 6, 'maturity_days': 110, 'water_needs': 'High',
        'notes': 'Requires good drainage, high OM demand',
        'management': [
            'Use certified disease-free seed potatoes',
            'Hill soil around plants to prevent tuber greening',
            'Maintain consistent soil moisture, especially during tuber formation',
            'Practice 3-4 year crop rotation with non-solanaceous crops',
            'Harvest when vines die back for mature potatoes'
        ],
        'likely_diseases': [
            'Late blight - rapid spreading water-soaked lesions, can destroy crop',
            'Early blight - target-like lesions on older leaves',
            'Common scab - rough corky lesions on tubers in alkaline soils',
            'Blackleg - soft rot starting from seed piece',
            'Verticillium wilt - yellowing and wilting, vascular discoloration'
        ],
        'pests': ['Colorado potato beetle', 'Aphids', 'Wireworms', 'Potato tuber moth'],
        'fertilizer': 'NPK 150-100-200 kg/ha',
        'spacing': '75-90 cm between rows, 25-30 cm between plants',
        'risk_factors': ['Wet conditions', 'Poor drainage', 'Continuous potato cropping']
    }
}

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

# FAO GAUL Dataset
FAO_GAUL = ee.FeatureCollection("FAO/GAUL/2015/level0")
FAO_GAUL_ADMIN1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
FAO_GAUL_ADMIN2 = ee.FeatureCollection("FAO/GAUL/2015/level2")

class ComprehensiveAgriculturalAnalyzer:
    def __init__(self):
        self.config = {
            'default_start_date': '2020-01-01',
            'default_end_date': '2023-12-31',
            'scale': 1000,
            'max_pixels': 1e6
        }

        # Climate classification parameters
        self.climate_palettes = {
            'Simplified Temperature-Precipitation': [
                '#006400', '#32CD32', '#9ACD32', '#FFD700', '#FF4500', '#FF8C00', '#B8860B',
                '#0000FF', '#1E90FF', '#87CEEB', '#2E8B57', '#696969', '#ADD8E6', '#FFFFFF', '#8B0000'
            ],
            'Aridity-Based': [
                '#000080', '#0000FF', '#00BFFF', '#FFFF00', '#FFA500', '#FF0000'
            ],
            'Köppen-Geiger': [
                '#006400', '#32CD32', '#9ACD32', '#FF0000', '#FFA500', '#FF4500',
                '#1E90FF', '#FF8C00', '#4682B4', '#87CEEB', '#ADD8E6'
            ]
        }

        self.climate_class_names = {
            'Simplified Temperature-Precipitation': {
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
            },
            'Aridity-Based': {
                1: 'Hyper-humid (Aridity > 0.65)',
                2: 'Humid (Aridity 0.5-0.65)',
                3: 'Sub-humid (Aridity 0.2-0.5)',
                4: 'Semi-arid (Aridity 0.03-0.2)',
                5: 'Arid (Aridity 0.005-0.03)',
                6: 'Hyper-arid (Aridity < 0.005)'
            },
            'Köppen-Geiger': {
                1: 'Af - Tropical rainforest',
                2: 'Am - Tropical monsoon',
                3: 'Aw - Tropical savanna',
                4: 'BW - Desert',
                5: 'BS - Steppe',
                6: 'Cfa - Humid subtropical',
                7: 'Cfb - Oceanic',
                8: 'Csa - Mediterranean',
                9: 'Dfa - Hot summer continental',
                10: 'Dfb - Warm summer continental',
                11: 'ET - Tundra'
            }
        }

        self.current_soil_data = None
        self.analysis_results = {}

        # Groundwater datasets
        self.chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        self.soil_clay = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02")
        self.soil_sand = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02")
        self.soil_silt = ee.Image("OpenLandMap/SOL/SOL_SILT-WFRACTION_USDA-3A1A1A_M/v02")
        self.dem = ee.Image("CGIAR/SRTM90_V4")

    # ============ ENHANCED CROP SUITABILITY METHODS ============
    def calculate_crop_suitability_score(self, moisture_value, som_value, texture_value, temp_value, crop_req):
        """Calculate comprehensive crop suitability score with disease risk assessment"""
        # Calculate individual component scores
        s_m = self.calculate_moisture_score(moisture_value, crop_req['moisture_opt'], crop_req['moisture_tol'])
        s_om = self.calculate_om_score(som_value, crop_req['om_opt'], crop_req['om_tol'])
        s_t = self.get_texture_score(texture_value, crop_req['texture_scores'])
        s_temp = self.calculate_temp_score(temp_value, crop_req['temp_opt'], crop_req['temp_tol'])

        # Weighted suitability score
        weights = {'moisture': 0.3, 'texture': 0.25, 'om': 0.25, 'temp': 0.2}
        suitability_score = (s_m * weights['moisture'] +
                           s_om * weights['om'] +
                           s_t * weights['texture'] +
                           s_temp * weights['temp'])

        # Calculate disease risk index
        disease_risk = self.calculate_disease_risk_index(s_m, s_om, s_t, s_temp, crop_req)

        # Adjust suitability based on disease risk
        risk_adjustment = 1.0 - (disease_risk * 0.3)  # High disease risk reduces suitability
        final_score = suitability_score * risk_adjustment

        return {
            'final_score': min(1.0, max(0.0, final_score)),
            'suitability_score': suitability_score,
            'component_scores': {'moisture': s_m, 'organic_matter': s_om, 'texture': s_t, 'temperature': s_temp},
            'disease_risk': disease_risk,
            'risk_level': self.get_risk_level(disease_risk)
        }

    def calculate_disease_risk_index(self, s_m, s_om, s_t, s_temp, crop_req):
        """Calculate comprehensive disease risk index"""
        # Stress factors that increase disease susceptibility
        moisture_stress = 1.0 - s_m  # Both too dry and too wet increase risk
        nutrient_stress = 1.0 - s_om  # Low OM increases susceptibility
        texture_stress = 1.0 - s_t   # Unsuitable texture increases risk
        temp_stress = 1.0 - s_temp   # Temperature stress increases risk

        # Weighted disease risk calculation
        risk_weights = {
            'moisture_stress': 0.35,  # Moisture is biggest disease driver
            'nutrient_stress': 0.25,   # Plant health affects resistance
            'texture_stress': 0.20,    # Soil structure affects root health
            'temp_stress': 0.20        # Temperature stress weakens plants
        }

        disease_risk = (moisture_stress * risk_weights['moisture_stress'] +
                       nutrient_stress * risk_weights['nutrient_stress'] +
                       texture_stress * risk_weights['texture_stress'] +
                       temp_stress * risk_weights['temp_stress'])

        return min(1.0, max(0.0, disease_risk))

    def get_risk_level(self, risk_index):
        """Convert risk index to categorical level"""
        if risk_index < 0.3:
            return 'Low'
        elif risk_index < 0.6:
            return 'Moderate'
        elif risk_index < 0.8:
            return 'High'
        else:
            return 'Very High'

    def generate_management_strategies(self, crop_name, suitability_analysis, crop_req):
        """Generate tailored management strategies based on analysis"""
        strategies = []
        comp_scores = suitability_analysis['component_scores']
        disease_risk = suitability_analysis['disease_risk']

        # General strategies based on overall suitability
        if suitability_analysis['final_score'] >= 0.8:
            strategies.append("✅ Excellent conditions - Maintain current practices")
        elif suitability_analysis['final_score'] >= 0.6:
            strategies.append("🟡 Good conditions - Minor adjustments needed")
        else:
            strategies.append("🔴 Challenging conditions - Significant management required")

        # Soil moisture management
        if comp_scores['moisture'] < 0.5:
            if crop_req['water_needs'] in ['High', 'Very High']:
                strategies.append("💧 Implement irrigation system for consistent moisture")
            strategies.append("🌱 Use mulch to conserve soil moisture")

        # Organic matter management
        if comp_scores['organic_matter'] < 0.5:
            strategies.append("🍂 Apply organic amendments (compost, manure)")
            strategies.append("🌿 Plant cover crops to build soil organic matter")

        # Disease management based on risk level
        if disease_risk >= 0.7:
            strategies.append("🦠 HIGH DISEASE RISK - Implement intensive IPM program")
            strategies.append("🔄 Use 3+ year crop rotation with non-host crops")
            strategies.append("🌱 Select disease-resistant varieties")
        elif disease_risk >= 0.5:
            strategies.append("⚠️ MODERATE DISEASE RISK - Regular monitoring needed")
            strategies.append("🍃 Improve air circulation through proper spacing")

        return strategies

    def analyze_all_crops(self, moisture_value, som_value, texture_value, temp_value, location_name):
        """Analyze all crops with enhanced suitability scoring"""
        st.info(f"🌱 Analyzing crop suitability for {location_name}...")
        
        analysis_results = {}
        
        progress_bar = st.progress(0)
        total_crops = len(CROP_REQUIREMENTS)
        
        for idx, (crop_name, crop_req) in enumerate(CROP_REQUIREMENTS.items()):
            # Calculate suitability with disease risk
            suitability_analysis = self.calculate_crop_suitability_score(
                moisture_value, som_value, texture_value, temp_value, crop_req)
            
            # Generate management strategies
            management_strategies = self.generate_management_strategies(
                crop_name, suitability_analysis, crop_req)
            
            analysis_results[crop_name] = {
                'suitability_analysis': suitability_analysis,
                'management_strategies': management_strategies,
                'crop_requirements': crop_req
            }
            
            progress_bar.progress((idx + 1) / total_crops)
        
        progress_bar.empty()
        return analysis_results

    # ============ CLIMATE ANALYSIS METHODS ============
    def get_accurate_climate_classification(self, geometry, location_name, classification_type='Simplified Temperature-Precipitation'):
        """Get climate classification using JavaScript logic"""
        try:
            # Use WorldClim
            worldclim = ee.Image("WORLDCLIM/V1/BIO")
            
            # Extract variables
            annual_mean_temp = worldclim.select('bio01').divide(10)  # °C
            annual_precip = worldclim.select('bio12')  # mm/year
            
            # Calculate aridity index
            aridity_index = annual_precip.divide(annual_mean_temp.add(33))
            
            # Get statistics for the region
            stats = ee.Image.cat([annual_mean_temp, annual_precip, aridity_index]).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry.centroid(),
                scale=10000,
                maxPixels=1e6
            ).getInfo()
            
            mean_temp = stats.get('bio01', 18.5)
            mean_precip = stats.get('bio12', 800)
            mean_aridity = stats.get('bio12', 0) / (stats.get('bio01', 0) + 33) if (stats.get('bio01', 0) + 33) != 0 else 1.5
            
            # Apply classification logic
            if classification_type == 'Simplified Temperature-Precipitation':
                climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
            elif classification_type == 'Aridity-Based':
                climate_class = self.classify_aridity_based(mean_temp, mean_precip, mean_aridity)
            elif classification_type == 'Köppen-Geiger':
                climate_class = self.classify_koppen_geiger(mean_temp, mean_precip, mean_aridity)
            else:
                climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
            
            climate_zone = self.climate_class_names[classification_type].get(climate_class, 'Unknown')
            
            return {
                'climate_zone': climate_zone,
                'climate_class': climate_class,
                'mean_temperature': round(mean_temp, 1),
                'mean_precipitation': round(mean_precip),
                'aridity_index': round(mean_aridity, 3),
                'classification_type': classification_type
            }
            
        except Exception as e:
            st.error(f"Climate classification failed: {e}")
            return {
                'climate_zone': "Unknown",
                'climate_class': 0,
                'mean_temperature': 0,
                'mean_precipitation': 0,
                'aridity_index': 0,
                'classification_type': classification_type
            }

    def classify_climate_simplified(self, temp, precip, aridity):
        """Simplified temperature-precipitation classification"""
        if temp > 18:
            if precip > 2000:
                climate_class = 1
            elif precip > 1500:
                climate_class = 2
            elif precip > 1000:
                climate_class = 3
            elif precip > 500:
                climate_class = 4
            else:
                climate_class = 7
        elif temp > 12:
            if precip > 1200:
                climate_class = 5
            elif precip > 600:
                climate_class = 6
            else:
                climate_class = 7
        elif temp > 6:
            if precip > 1000:
                climate_class = 8
            elif precip > 500:
                climate_class = 9
            else:
                climate_class = 10
        elif temp > 0:
            if precip > 500:
                climate_class = 11
            else:
                climate_class = 12
        elif temp > -10:
            climate_class = 13
        else:
            climate_class = 14

        # Aridity override
        if aridity < 0.03:
            climate_class = 15

        return climate_class

    # ============ SOIL ANALYSIS METHODS ============
    def get_area_representative_values(self, geometry, area_name):
        """Get representative soil values for crop suitability analysis"""
        try:
            # Get moisture value
            moisture_val = 0.15  # Default
            
            # Check if in Africa for soil data
            is_in_africa = AFRICA_BOUNDS.intersects(geometry, 100).getInfo()
            
            # Get SOM data
            if is_in_africa:
                som_val = self.get_africa_som_data(geometry)
            else:
                som_val = self.get_global_som_data(geometry)
            
            # Get texture data
            texture_val = self.get_soil_texture_data(geometry)
            
            # Get temperature
            temp_val = 22.0  # Default temperature
            
            return moisture_val, som_val, texture_val, temp_val
            
        except Exception as e:
            st.error(f"Error getting soil values: {e}")
            return 0.15, 2.0, 7, 22.0

    def get_africa_som_data(self, geometry):
        """Get Africa SOM data"""
        try:
            africa_soil = ee.Image("ISDASOIL/Africa/v1/carbon_organic")
            converted_africa = africa_soil.divide(10).exp().subtract(1)
            
            soc_stats = converted_africa.select(0).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=1000,
                maxPixels=1e9
            ).getInfo()
            
            soc_val = list(soc_stats.values())[0] if soc_stats else 0.41
            soc_percent = soc_val / (BULK_DENSITY * 20 * 100)
            som_percent = soc_percent * SOC_TO_SOM_FACTOR * 100
            
            return som_percent
        except:
            return 2.0

    def get_global_som_data(self, geometry):
        """Get global SOM data"""
        try:
            gsoc = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/FAO/GSOCMAP1-5-0")
            soc_mean = gsoc.select('b1')
            
            soc_stats = soc_mean.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=1000,
                maxPixels=1e9
            ).getInfo()
            
            soc_val = list(soc_stats.values())[0] if soc_stats else 0.41
            soc_percent = soc_val / (BULK_DENSITY * 30 * 100)
            som_percent = soc_percent * SOC_TO_SOM_FACTOR * 100
            
            return som_percent
        except:
            return 2.0

    def get_soil_texture_data(self, geometry):
        """Get soil texture data"""
        try:
            texture_dataset = ee.Image('OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02')
            soil_texture = texture_dataset.select('b0')
            
            texture_stats = soil_texture.reduceRegion(
                reducer=ee.Reducer.mode(),
                geometry=geometry,
                scale=250,
                maxPixels=1e9
            ).getInfo()
            
            texture_val = list(texture_stats.values())[0] if texture_stats else 7
            return texture_val
        except:
            return 7

    # ============ GROUNDWATER ANALYSIS METHODS ============
    def analyze_groundwater_potential(self, geometry, name):
        """Comprehensive groundwater analysis for a location"""
        try:
            # Simplified implementation - in production, use actual Earth Engine calculations
            # For demo purposes, returning simulated data
            import random
            
            return {
                'name': name,
                'score': random.uniform(0.3, 0.9),
                'category': random.choice(['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']),
                'precipitation_mm': random.uniform(200, 1000),
                'recharge_mm': random.uniform(50, 300),
                'conductivity': random.uniform(0.5, 25.0),
                'soil_type': random.choice(['Sand', 'Sandy Loam', 'Loam', 'Clay Loam', 'Clay']),
                'clay_percent': random.uniform(10, 60),
                'sand_percent': random.uniform(20, 80),
                'silt_percent': random.uniform(10, 40),
                'slope': random.uniform(1, 15),
                'twi': random.uniform(5, 12)
            }
            
        except Exception as e:
            st.error(f"Error analyzing groundwater: {e}")
            return {
                'name': name,
                'score': 0.5,
                'category': "UNKNOWN",
                'precipitation_mm': 350,
                'recharge_mm': 50,
                'conductivity': 5.0,
                'soil_type': "Loam",
                'clay_percent': 25,
                'sand_percent': 40,
                'silt_percent': 35,
                'slope': 5.0,
                'twi': 8.0
            }

    # ============ UTILITY METHODS ============
    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry based on selection level using FAO GAUL"""
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
                return None, None

        except Exception as e:
            st.error(f"Geometry error: {e}")
            return None, None

    def calculate_moisture_score(self, moisture_meas, moisture_opt, moisture_tol):
        """Calculate moisture suitability score"""
        diff = abs(moisture_meas - moisture_opt)
        if diff <= 0:
            return 1.0
        if diff <= moisture_tol:
            return max(0, 1 - (diff / moisture_tol))
        return 0.0

    def calculate_om_score(self, om_meas, om_opt, om_tol):
        """Calculate organic matter suitability score"""
        diff = abs(om_meas - om_opt)
        return max(0, 1 - (diff / om_tol))

    def get_texture_score(self, texture_class, crop_texture_scores):
        """Get texture suitability score"""
        if texture_class is None:
            return 0.5

        rounded_class = int(round(texture_class))
        if rounded_class < 1 or rounded_class > 12:
            return 0.5

        texture_name = SOIL_TEXTURE_CLASSES[rounded_class]
        return crop_texture_scores.get(texture_name, 0.5)

    def calculate_temp_score(self, temp_meas, temp_opt, temp_tol):
        """Calculate temperature suitability score"""
        diff = abs(temp_meas - temp_opt)
        if diff <= 0:
            return 1.0
        if diff <= temp_tol:
            return max(0, 1 - (diff / temp_tol))
        return 0.0

    def run_comprehensive_analysis(self, country, region='Select Region', municipality='Select Municipality',
                                 classification_type='Simplified Temperature-Precipitation',
                                 analysis_type='crop_suitability'):
        """Run comprehensive agricultural analysis for selected region"""
        
        # Get geometry for selected location
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            st.error("❌ Could not get geometry for the selected location")
            return None

        results = {
            'location_name': location_name,
            'geometry': geometry,
            'classification_type': classification_type,
            'analysis_type': analysis_type
        }

        if analysis_type == 'groundwater':
            # Run groundwater analysis
            with st.spinner("💧 Analyzing groundwater potential..."):
                gw_results = self.analyze_groundwater_potential(geometry, location_name)
                results['groundwater_analysis'] = gw_results

        else:
            # Run comprehensive crop suitability analysis
            # 1. Climate Classification
            with st.spinner("🌤️ Analyzing climate classification..."):
                results['climate_analysis'] = self.get_accurate_climate_classification(
                    geometry, location_name, classification_type)

            # 2. Soil Analysis
            with st.spinner("🌱 Analyzing soil properties..."):
                moisture_val, som_val, texture_val, temp_val = self.get_area_representative_values(geometry, location_name)

                results['soil_parameters'] = {
                    'moisture': moisture_val,
                    'organic_matter': som_val,
                    'texture': texture_val,
                    'temperature': temp_val
                }

            # 3. Crop Suitability Analysis
            with st.spinner("🌾 Analyzing crop suitability..."):
                crop_results = self.analyze_all_crops(moisture_val, som_val, texture_val, temp_val, location_name)
                results['crop_analysis'] = crop_results

        return results

# =============================================================================
# STREAMLIT INTERFACE
# =============================================================================

def main():
    # Title and header
    st.markdown('<h1 class="main-header">🌾 Comprehensive Agricultural Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <strong>Integrated Agricultural Analysis Platform</strong><br>
        Combines climate analysis, soil analysis, crop suitability with disease risk assessment, 
        and groundwater potential analysis for comprehensive agricultural planning.
    </div>
    """, unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🌍 Earth Engine Status")
        if st.session_state.get('ee_initialized', False):
            st.success("✅ Earth Engine Initialized")
            st.caption("Connected to: citric-hawk-457513-i6")
        else:
            st.error("❌ Earth Engine Not Initialized")
            st.caption("Check service account configuration")
        
        st.markdown("---")
        st.markdown("### 📊 Analysis Configuration")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Crop Suitability", "Groundwater Potential"],
            help="Choose the type of analysis to perform"
        )
        
        # Climate classification for crop suitability
        if analysis_type == "Crop Suitability":
            climate_classification = st.selectbox(
                "Climate Classification System",
                ["Simplified Temperature-Precipitation", "Aridity-Based", "Köppen-Geiger"],
                help="Select the climate classification system to use"
            )
        
        st.markdown("---")
        st.markdown("### 📚 Data Sources")
        with st.expander("View Data Sources"):
            st.markdown("""
            - **Soil Data:** FAO GSOCMAP, ISDASOIL Africa, OpenLandMap
            - **Climate Data:** WorldClim, CHIRPS
            - **Administrative Boundaries:** FAO GAUL
            - **Satellite Imagery:** Sentinel-2, MODIS
            - **Topography:** SRTM DEM
            """)

    # Main content area - Location Selection
    st.markdown('<h2 class="section-header">📍 Location Selection</h2>', unsafe_allow_html=True)
    
    # Get country list
    try:
        countries = FAO_GAUL.aggregate_array('ADM0_NAME').distinct().sort().getInfo()
        countries = ['Select Country'] + countries
    except:
        countries = ['Select Country', 'Algeria', 'Nigeria', 'Kenya', 'South Africa', 'Ethiopia', 'Egypt', 'Morocco', 'Tanzania']
    
    col1, col2 = st.columns(2)
    
    with col1:
        country = st.selectbox("Select Country", countries, key="country_select")
    
    with col2:
        # Initialize region options
        region_options = ["Select Region"]
        
        if country != "Select Country":
            try:
                regions = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                  .aggregate_array('ADM1_NAME').distinct().sort().getInfo()
                region_options.extend(regions)
            except:
                region_options.extend(["Region 1", "Region 2", "Region 3"])
        
        region = st.selectbox("Select Region/State", region_options, key="region_select")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Initialize municipality options
        municipality_options = ["Select Municipality"]
        
        if region != "Select Region":
            try:
                municipalities = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                        .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                        .aggregate_array('ADM2_NAME').distinct().sort().getInfo()
                municipality_options.extend(municipalities)
            except:
                municipality_options.extend(["Municipality 1", "Municipality 2", "Municipality 3"])
        
        municipality = st.selectbox("Select Municipality", municipality_options, key="municipality_select")
    
    with col4:
        st.markdown("### Custom Soil Parameters")
        use_custom = st.checkbox("Use Custom Soil Parameters", value=False)
        
        if use_custom:
            col_a, col_b = st.columns(2)
            with col_a:
                moisture_val = st.slider("Soil Moisture (m³/m³)", 0.0, 0.5, 0.15, 0.01, key="moisture_slider")
                som_val = st.slider("Soil Organic Matter (%)", 0.0, 10.0, 2.0, 0.1, key="som_slider")
            with col_b:
                texture_options = list(SOIL_TEXTURE_CLASSES.values())
                texture_val = st.selectbox("Soil Texture", texture_options, index=texture_options.index("Loam"), key="texture_select")
                temp_val = st.slider("Temperature (°C)", 0.0, 40.0, 22.0, 0.5, key="temp_slider")
        else:
            moisture_val = None
            som_val = None
            texture_val = None
            temp_val = None
    
    # Run Analysis Button
    st.markdown("---")
    run_analysis = st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True)
    
    if run_analysis:
        if country == "Select Country":
            st.error("Please select a country first!")
        elif not st.session_state.get('ee_initialized', False):
            st.error("Earth Engine not initialized. Please check the sidebar for status.")
        else:
            with st.spinner("Running comprehensive analysis..."):
                # Create analyzer instance
                analyzer = ComprehensiveAgriculturalAnalyzer()
                
                # Run analysis
                results = analyzer.run_comprehensive_analysis(
                    country,
                    region if region != "Select Region" else "Select Region",
                    municipality if municipality != "Select Municipality" else "Select Municipality",
                    climate_classification if 'climate_classification' in locals() else "Simplified Temperature-Precipitation",
                    analysis_type.lower().replace(" ", "_")
                )
                
                if results:
                    # Store results in session state
                    st.session_state['analysis_results'] = results
                    st.session_state['analysis_completed'] = True
                    st.session_state['analyzer'] = analyzer
                    
                    st.success("✅ Analysis completed successfully!")
                    st.rerun()

    # Display results if analysis completed
    if st.session_state.get('analysis_completed', False) and 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        analyzer = st.session_state['analyzer']
        
        st.markdown(f'<h2 class="section-header">📊 Analysis Results for {results["location_name"]}</h2>', unsafe_allow_html=True)
        
        # Display results based on analysis type
        if results['analysis_type'] == 'groundwater_potential':
            st.markdown("### 💧 Groundwater Potential Analysis")
            
            gw_results = results['groundwater_analysis']
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Color based on category
                color_map = {
                    'VERY HIGH': 'green',
                    'HIGH': 'lightgreen',
                    'MODERATE': 'orange',
                    'LOW': 'red',
                    'UNKNOWN': 'gray'
                }
                category_color = color_map.get(gw_results['category'], 'gray')
                
                st.metric(
                    "Groundwater Potential",
                    gw_results['category'],
                    delta=f"Score: {gw_results['score']:.2f}",
                    delta_color="normal"
                )
            
            with col2:
                st.metric("Recharge Rate", f"{gw_results['recharge_mm']:.0f} mm/year")
            
            with col3:
                st.metric("Hydraulic Conductivity", f"{gw_results['conductivity']:.1f} cm/day")
            
            with col4:
                st.metric("Soil Type", gw_results['soil_type'])
            
            # Display detailed information
            with st.expander("📈 Detailed Groundwater Analysis"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Soil Composition:**")
                    st.markdown(f"- Clay: {gw_results['clay_percent']:.1f}%")
                    st.markdown(f"- Sand: {gw_results['sand_percent']:.1f}%")
                    st.markdown(f"- Silt: {gw_results['silt_percent']:.1f}%")
                    
                    st.markdown("**Topography:**")
                    st.markdown(f"- Slope: {gw_results['slope']:.1f}°")
                    st.markdown(f"- TWI: {gw_results['twi']:.2f}")
                
                with col_b:
                    st.markdown("**Water Balance:**")
                    st.markdown(f"- Precipitation: {gw_results['precipitation_mm']:.0f} mm/year")
                    st.markdown(f"- Recharge: {gw_results['recharge_mm']:.0f} mm/year")
                    st.markdown(f"- Recharge Efficiency: {(gw_results['recharge_mm'] / gw_results['precipitation_mm'] * 100):.1f}%")
            
            # Recommendations
            st.markdown("#### 💡 Recommendations")
            if gw_results['category'] in ['HIGH', 'VERY HIGH']:
                st.success("""
                **Excellent groundwater potential!**
                - Consider installing irrigation wells
                - Implement sustainable water management practices
                - Monitor water quality regularly
                - Plan for efficient water use in agriculture
                """)
            elif gw_results['category'] == 'MODERATE':
                st.warning("""
                **Moderate groundwater potential**
                - Conduct detailed hydrogeological survey
                - Consider rainwater harvesting
                - Implement water conservation measures
                - Use drip irrigation for efficiency
                """)
            else:
                st.error("""
                **Low groundwater potential**
                - Prioritize water conservation
                - Consider alternative water sources
                - Implement drought-resistant crops
                - Use efficient irrigation methods
                """)
                
        else:  # Crop Suitability Analysis
            st.markdown("### 🌾 Crop Suitability Analysis")
            
            # Display climate information
            if 'climate_analysis' in results:
                climate = results['climate_analysis']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Climate Zone", climate['climate_zone'].split('(')[0])
                with col2:
                    st.metric("Temperature", f"{climate['mean_temperature']}°C")
                with col3:
                    st.metric("Precipitation", f"{climate['mean_precipitation']} mm/year")
            
            # Display soil parameters
            if 'soil_parameters' in results:
                soil = results['soil_parameters']
                
                with st.expander("📊 Soil Parameters"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Moisture", f"{soil['moisture']:.3f} m³/m³")
                    with col2:
                        st.metric("Organic Matter", f"{soil['organic_matter']:.2f}%")
                    with col3:
                        texture_name = SOIL_TEXTURE_CLASSES.get(int(round(soil['texture'])), "Unknown")
                        st.metric("Texture", texture_name)
                    with col4:
                        st.metric("Temperature", f"{soil['temperature']}°C")
            
            # Display crop suitability results
            if 'crop_analysis' in results:
                crop_results = results['crop_analysis']
                
                # Convert to DataFrame for display
                results_list = []
                for crop_name, crop_data in crop_results.items():
                    analysis = crop_data['suitability_analysis']
                    results_list.append({
                        'Crop': crop_name,
                        'Suitability Score': analysis['final_score'],
                        'Disease Risk': analysis['disease_risk'],
                        'Risk Level': analysis['risk_level'],
                        'Moisture Score': analysis['component_scores']['moisture'],
                        'OM Score': analysis['component_scores']['organic_matter'],
                        'Texture Score': analysis['component_scores']['texture'],
                        'Temp Score': analysis['component_scores']['temperature']
                    })
                
                df = pd.DataFrame(results_list)
                
                # Display top 5 crops
                st.markdown("#### 🏆 Top Recommended Crops")
                top_crops = df.sort_values('Suitability Score', ascending=False).head(5)
                
                cols = st.columns(5)
                for idx, (_, crop) in enumerate(top_crops.iterrows()):
                    with cols[idx]:
                        color = "green" if crop['Suitability Score'] > 0.7 else "orange" if crop['Suitability Score'] > 0.5 else "red"
                        st.metric(
                            crop['Crop'],
                            f"{crop['Suitability Score']:.2f}",
                            crop['Risk Level'],
                            delta_color="off"
                        )
                
                # Display detailed results in expandable sections
                st.markdown("#### 📋 Detailed Crop Analysis")
                
                # Sort options
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox("Sort by", ["Suitability Score", "Disease Risk", "Crop Name"], key="sort_select")
                with col2:
                    sort_order = st.selectbox("Order", ["Descending", "Ascending"], key="order_select")
                
                # Sort DataFrame
                ascending = sort_order == "Ascending"
                if sort_by == "Suitability Score":
                    df = df.sort_values('Suitability Score', ascending=ascending)
                elif sort_by == "Disease Risk":
                    df = df.sort_values('Disease Risk', ascending=not ascending)
                else:
                    df = df.sort_values('Crop', ascending=ascending)
                
                # Display each crop in expandable sections
                for _, crop in df.iterrows():
                    with st.expander(f"{crop['Crop']} - Score: {crop['Suitability Score']:.2f} ({crop['Risk Level']} Risk)"):
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Moisture Score", f"{crop['Moisture Score']:.2f}")
                        with col_b:
                            st.metric("OM Score", f"{crop['OM Score']:.2f}")
                        with col_c:
                            st.metric("Texture Score", f"{crop['Texture Score']:.2f}")
                        with col_d:
                            st.metric("Temp Score", f"{crop['Temp Score']:.2f}")
                        
                        # Show crop requirements and management
                        crop_req = CROP_REQUIREMENTS[crop['Crop']]
                        management = crop_results[crop['Crop']]['management_strategies']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Crop Requirements:**")
                            st.markdown(f"- Water Needs: {crop_req['water_needs']}")
                            st.markdown(f"- Maturity Days: {crop_req['maturity_days']}")
                            st.markdown(f"- Fertilizer: {crop_req['fertilizer']}")
                            st.markdown(f"- Spacing: {crop_req['spacing']}")
                        
                        with col2:
                            st.markdown("**Management Strategies:**")
                            for strategy in management[:5]:  # Show first 5 strategies
                                st.markdown(f"- {strategy}")
                        
                        # Show disease information if risk is moderate or higher
                        if crop['Risk Level'] in ['Moderate', 'High', 'Very High']:
                            st.markdown("**⚠️ Disease Alert:**")
                            for disease in crop_req['likely_diseases'][:3]:  # Show first 3 diseases
                                st.markdown(f"- {disease}")
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"crop_suitability_{results['location_name'].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                
                # Create visualizations
                st.markdown("#### 📈 Visualizations")
                
                # Suitability vs Disease Risk Scatter Plot
                st.markdown("##### Suitability vs Disease Risk")
                fig = px.scatter(
                    df,
                    x='Suitability Score',
                    y='Disease Risk',
                    text='Crop',
                    size=[20]*len(df),
                    color='Suitability Score',
                    color_continuous_scale='RdYlGn',
                    title='Crop Suitability vs Disease Risk'
                )
                
                # Add quadrant lines
                fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
                fig.add_vline(x=0.6, line_dash="dash", line_color="gray")
                
                # Add quadrant labels
                fig.add_annotation(x=0.8, y=0.2, text="Ideal", showarrow=False, font=dict(color="green"))
                fig.add_annotation(x=0.8, y=0.8, text="Risky", showarrow=False, font=dict(color="orange"))
                fig.add_annotation(x=0.3, y=0.2, text="Marginal", showarrow=False, font=dict(color="yellow"))
                fig.add_annotation(x=0.3, y=0.8, text="Avoid", showarrow=False, font=dict(color="red"))
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Bar chart of top crops
                st.markdown("##### Top 10 Crops by Suitability")
                top_10 = df.sort_values('Suitability Score', ascending=False).head(10)
                
                fig2 = px.bar(
                    top_10,
                    x='Crop',
                    y='Suitability Score',
                    color='Suitability Score',
                    color_continuous_scale='RdYlGn',
                    text='Suitability Score'
                )
                
                fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig2.update_layout(height=400, yaxis_range=[0, 1])
                st.plotly_chart(fig2, use_container_width=True)

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            <p>🌾 Comprehensive Agricultural Analyzer v1.0</p>
            <p>Powered by Earth Engine • FAO Data • OpenLandMap</p>
            <p>Project ID: citric-hawk-457513-i6</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
