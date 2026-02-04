import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import traceback
import sys
import subprocess

# Try to import seaborn, install if not available
try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    # Try to install seaborn
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "seaborn"])
        import seaborn as sns
        SEABORN_AVAILABLE = True
        st.success("✅ Successfully installed seaborn")
    except:
        st.warning("⚠️ Could not install seaborn. Some visualizations may be limited.")

# Try to import matplotlib patches
try:
    from matplotlib.patches import FancyBboxPatch
    MATPLOTLIB_PATCHES_AVAILABLE = True
except ImportError:
    MATPLOTLIB_PATCHES_AVAILABLE = False

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

# Title and header
st.markdown('<h1 class="main-header">🌾 Comprehensive Agricultural Analyzer</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <strong>Integrated Agricultural Analysis Platform</strong><br>
    Combines climate analysis, soil analysis, crop suitability with disease risk assessment, and groundwater potential analysis for comprehensive agricultural planning.
</div>
""", unsafe_allow_html=True)

# Initialize Earth Engine status
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
        ["Crop Suitability", "Groundwater Potential", "Comprehensive Analysis"],
        help="Choose the type of analysis to perform"
    )
    
    # Climate classification for crop suitability
    if analysis_type in ["Crop Suitability", "Comprehensive Analysis"]:
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

# ============ COMPREHENSIVE CROP SUITABILITY CONFIGURATION ============
CROP_REQUIREMENTS = {
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
    'Soybean': {
        'moisture_opt': 0.22, 'moisture_tol': 0.06, 'om_opt': 1.5, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 24, 'temp_tol': 6, 'maturity_days': 110, 'water_needs': 'Medium',
        'notes': 'Warm season, nitrogen-fixing',
        'management': [
            'Plant when soil temperature reaches 15°C',
            'Inoculate seeds with Bradyrhizobium japonicum',
            'Apply phosphorus fertilizer for better nodulation',
            'Control weeds early as soybeans are poor competitors',
            'Harvest when leaves yellow and pods rattle'
        ],
        'likely_diseases': [
            'Soybean rust - tan to reddish-brown pustules on leaves',
            'Sclerotinia stem rot - white mold and sclerotia formation',
            'Phytophthora root rot - damping off and root decay',
            'Brown stem rot - internal browning of stems',
            'Sudden death syndrome - interveinal chlorosis and leaf drop'
        ],
        'pests': ['Soybean aphid', 'Bean leaf beetle', 'Stink bugs', 'Caterpillars'],
        'fertilizer': 'NPK 30-80-60 kg/ha + Rhizobium inoculation',
        'spacing': '45-75 cm between rows, 3-5 cm between plants',
        'risk_factors': ['High humidity', 'Dense canopy', 'Continuous soybean cropping']
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
            }
        }

    # ============ CROP SUITABILITY METHODS ============
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
        risk_adjustment = 1.0 - (disease_risk * 0.3)
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
        moisture_stress = 1.0 - s_m
        nutrient_stress = 1.0 - s_om
        texture_stress = 1.0 - s_t
        temp_stress = 1.0 - s_temp

        # Weighted disease risk calculation
        risk_weights = {
            'moisture_stress': 0.35,
            'nutrient_stress': 0.25,
            'texture_stress': 0.20,
            'temp_stress': 0.20
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

    def analyze_all_crops(self, moisture_value, som_value, texture_value, temp_value, location_name):
        """Analyze all crops with enhanced suitability scoring"""
        analysis_results = {}

        for crop_name, crop_req in CROP_REQUIREMENTS.items():
            # Calculate suitability with disease risk
            suitability_analysis = self.calculate_crop_suitability_score(
                moisture_value, som_value, texture_value, temp_value, crop_req)

            analysis_results[crop_name] = {
                'suitability_analysis': suitability_analysis,
                'crop_requirements': crop_req
            }

        return analysis_results

    # ============ UTILITY METHODS ============
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

        # Convert to texture name
        if isinstance(texture_class, str):
            texture_name = texture_class
        elif 1 <= texture_class <= 12:
            texture_name = SOIL_TEXTURE_CLASSES[int(round(texture_class))]
        else:
            texture_name = "Loam"  # Default
        
        return crop_texture_scores.get(texture_name, 0.5)

    def calculate_temp_score(self, temp_meas, temp_opt, temp_tol):
        """Calculate temperature suitability score"""
        diff = abs(temp_meas - temp_opt)
        if diff <= 0:
            return 1.0
        if diff <= temp_tol:
            return max(0, 1 - (diff / temp_tol))
        return 0.0

    def analyze_groundwater(self, location_name):
        """Analyze groundwater potential for a location"""
        # Simulate analysis - replace with actual Earth Engine calls
        return {
            'score': np.random.uniform(0.2, 0.95),
            'category': np.random.choice(['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']),
            'recharge_mm': np.random.uniform(50, 300),
            'conductivity': np.random.uniform(0.5, 25.0),
            'soil_type': np.random.choice(['Sand', 'Sandy Loam', 'Loam', 'Clay Loam', 'Clay'])
        }

# Main content area
tab1, tab2, tab3 = st.tabs(["📍 Location Selection", "📊 Analysis Results", "📈 Visualizations"])

with tab1:
    st.markdown('<h2 class="section-header">Location Selection</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Country Selection")
        countries = ["Select Country", "Algeria", "Nigeria", "Kenya", "South Africa", "Ethiopia", "Egypt", "Morocco", "Tanzania"]
        country = st.selectbox("Select Country", countries)
    
    with col2:
        st.markdown("### Region Selection")
        region_options = ["Select Region"]
        if country != "Select Country":
            region_options.extend(["Region 1", "Region 2", "Region 3"])
        region = st.selectbox("Select Region/State", region_options)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Municipality Selection")
        municipality_options = ["Select Municipality"]
        if region != "Select Region":
            municipality_options.extend(["Municipality 1", "Municipality 2", "Municipality 3"])
        municipality = st.selectbox("Select Municipality", municipality_options)
    
    with col4:
        st.markdown("### Custom Soil Parameters")
        use_custom = st.checkbox("Use Custom Soil Parameters", value=True)
        
        if use_custom:
            col_a, col_b = st.columns(2)
            with col_a:
                moisture_val = st.slider("Soil Moisture (m³/m³)", 0.0, 0.5, 0.15, 0.01)
                som_val = st.slider("Soil Organic Matter (%)", 0.0, 10.0, 2.0, 0.1)
            with col_b:
                texture_options = list(SOIL_TEXTURE_CLASSES.values())
                texture_val = st.selectbox("Soil Texture", texture_options, index=texture_options.index("Loam"))
                temp_val = st.slider("Temperature (°C)", 0.0, 40.0, 22.0, 0.5)
        else:
            moisture_val = 0.15
            som_val = 2.0
            texture_val = "Loam"
            temp_val = 22.0
    
    # Run Analysis Button
    st.markdown("---")
    run_analysis = st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True)
    
    if run_analysis:
        if country == "Select Country":
            st.error("Please select a country first!")
        elif not st.session_state.get('ee_initialized', False):
            st.error("Earth Engine not initialized. Please check the sidebar for status.")
        else:
            st.session_state['analysis_started'] = True
            st.session_state['selected_location'] = f"{municipality if municipality != 'Select Municipality' else ''} {region if region != 'Select Region' else ''} {country}".strip()
            st.session_state['analysis_type'] = analysis_type
            st.session_state['soil_params'] = {
                'moisture': moisture_val,
                'organic_matter': som_val,
                'texture': texture_val,
                'temperature': temp_val
            }
            st.rerun()

# Results Tab
with tab2:
    if 'analysis_started' in st.session_state and st.session_state['analysis_started']:
        st.markdown(f'<h2 class="section-header">Analysis Results for {st.session_state["selected_location"]}</h2>', unsafe_allow_html=True)
        
        # Create analyzer instance
        analyzer = ComprehensiveAgriculturalAnalyzer()
        
        # Display results based on analysis type
        if st.session_state['analysis_type'] == "Crop Suitability":
            st.markdown("### 🌾 Crop Suitability Analysis")
            
            # Get soil parameters
            soil_params = st.session_state['soil_params']
            
            # Get analysis results
            with st.spinner("Analyzing crop suitability..."):
                crop_results = analyzer.analyze_all_crops(
                    soil_params['moisture'],
                    soil_params['organic_matter'],
                    soil_params['texture'],
                    soil_params['temperature'],
                    st.session_state['selected_location']
                )
            
            # Convert to DataFrame
            results_list = []
            for crop_name, results in crop_results.items():
                suit = results['suitability_analysis']
                results_list.append({
                    'Crop': crop_name,
                    'Suitability Score': suit['final_score'],
                    'Disease Risk': suit['disease_risk'],
                    'Risk Level': suit['risk_level'],
                    'Moisture Score': suit['component_scores']['moisture'],
                    'OM Score': suit['component_scores']['organic_matter'],
                    'Texture Score': suit['component_scores']['texture'],
                    'Temp Score': suit['component_scores']['temperature']
                })
            
            results_df = pd.DataFrame(results_list)
            
            # Display top crops
            st.markdown("#### 🏆 Top Recommended Crops")
            top_crops = results_df.sort_values('Suitability Score', ascending=False).head(5)
            
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
            
            # Display detailed results
            st.markdown("#### 📋 Detailed Crop Analysis")
            
            # Sort options
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("Sort by", ["Suitability Score", "Disease Risk", "Crop Name"])
            with col2:
                sort_order = st.selectbox("Order", ["Descending", "Ascending"])
            
            # Sort DataFrame
            ascending = sort_order == "Ascending"
            if sort_by == "Suitability Score":
                results_df = results_df.sort_values('Suitability Score', ascending=ascending)
            elif sort_by == "Disease Risk":
                results_df = results_df.sort_values('Disease Risk', ascending=not ascending)
            else:
                results_df = results_df.sort_values('Crop', ascending=ascending)
            
            # Display as expandable sections
            for _, crop in results_df.iterrows():
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
                    
                    # Show crop requirements
                    crop_req = CROP_REQUIREMENTS[crop['Crop']]
                    st.markdown(f"**Water Needs:** {crop_req['water_needs']}")
                    st.markdown(f"**Maturity Days:** {crop_req['maturity_days']}")
                    st.markdown(f"**Fertilizer:** {crop_req['fertilizer']}")
                    
                    # Show management tips
                    st.markdown("**Management Tips:**")
                    for tip in crop_req['management'][:3]:
                        st.markdown(f"- {tip}")
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"crop_suitability_{st.session_state['selected_location'].replace(' ', '_')}.csv",
                mime="text/csv"
            )
            
        elif st.session_state['analysis_type'] == "Groundwater Potential":
            st.markdown("### 💧 Groundwater Potential Analysis")
            
            with st.spinner("Analyzing groundwater potential..."):
                gw_results = analyzer.analyze_groundwater(st.session_state['selected_location'])
            
            # Display groundwater metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Color based on category
                color_map = {
                    'VERY HIGH': 'green',
                    'HIGH': 'lightgreen',
                    'MODERATE': 'orange',
                    'LOW': 'red'
                }
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
            
            # Recommendations
            st.markdown("#### 💡 Recommendations")
            if gw_results['category'] in ['HIGH', 'VERY HIGH']:
                st.success("""
                **Excellent groundwater potential!**
                - Consider installing irrigation wells
                - Implement sustainable water management practices
                - Monitor water quality regularly
                """)
            elif gw_results['category'] == 'MODERATE':
                st.warning("""
                **Moderate groundwater potential**
                - Conduct detailed hydrogeological survey
                - Consider rainwater harvesting
                - Implement water conservation measures
                """)
            else:
                st.error("""
                **Low groundwater potential**
                - Prioritize water conservation
                - Consider alternative water sources
                - Implement drought-resistant crops
                """)
        
        else:  # Comprehensive Analysis
            st.markdown("### 📊 Comprehensive Analysis")
            
            # Get soil parameters
            soil_params = st.session_state['soil_params']
            
            # Create columns for different analyses
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🌾 Crop Suitability Summary")
                with st.spinner("Analyzing crops..."):
                    crop_results = analyzer.analyze_all_crops(
                        soil_params['moisture'],
                        soil_params['organic_matter'],
                        soil_params['texture'],
                        soil_params['temperature'],
                        st.session_state['selected_location']
                    )
                
                # Convert to list for display
                crop_list = []
                for crop_name, results in crop_results.items():
                    suit = results['suitability_analysis']
                    crop_list.append({
                        'Crop': crop_name,
                        'Score': suit['final_score'],
                        'Risk': suit['risk_level']
                    })
                
                crop_df = pd.DataFrame(crop_list).sort_values('Score', ascending=False)
                
                # Display top 5 crops
                st.markdown("**Top 5 Recommended Crops:**")
                for _, crop in crop_df.head().iterrows():
                    st.markdown(f"- **{crop['Crop']}**: {crop['Score']:.2f} ({crop['Risk']} risk)")
            
            with col2:
                st.markdown("#### 💧 Groundwater Potential")
                with st.spinner("Analyzing groundwater..."):
                    gw_results = analyzer.analyze_groundwater(st.session_state['selected_location'])
                
                st.metric("Potential", gw_results['category'], f"Score: {gw_results['score']:.2f}")
                st.metric("Annual Recharge", f"{gw_results['recharge_mm']:.0f} mm")
                st.metric("Soil Type", gw_results['soil_type'])
            
            # Overall assessment
            st.markdown("#### 📈 Overall Assessment")
            
            # Calculate overall score
            crop_scores = [result['suitability_analysis']['final_score'] for result in crop_results.values()]
            avg_crop_score = np.mean(crop_scores) if crop_scores else 0
            gw_score = gw_results['score']
            
            overall_score = (avg_crop_score * 0.6 + gw_score * 0.4)
            
            if overall_score > 0.7:
                st.success(f"""
                **Excellent Agricultural Potential** (Score: {overall_score:.2f})
                
                This location shows strong potential for agricultural development with good crop suitability 
                and adequate water resources. Consider diversified farming with high-value crops.
                """)
            elif overall_score > 0.5:
                st.warning(f"""
                **Moderate Agricultural Potential** (Score: {overall_score:.2f})
                
                This location has moderate potential. Focus on soil improvement and water conservation 
                measures. Consider crops with moderate water requirements.
                """)
            else:
                st.error(f"""
                **Limited Agricultural Potential** (Score: {overall_score:.2f})
                
                Agricultural development in this area may be challenging. Consider alternative land uses 
                or specialized drought-resistant crops with extensive irrigation infrastructure.
                """)

# Visualizations Tab
with tab3:
    if 'analysis_started' in st.session_state and st.session_state['analysis_started']:
        st.markdown(f'<h2 class="section-header">Visualizations for {st.session_state["selected_location"]}</h2>', unsafe_allow_html=True)
        
        # Visualization options
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["Crop Suitability Chart", "Groundwater Analysis", "Soil Properties", "Climate Data"]
        )
        
        if viz_type == "Crop Suitability Chart":
            st.markdown("### 🌾 Crop Suitability Visualization")
            
            # Get analyzer instance
            analyzer = ComprehensiveAgriculturalAnalyzer()
            soil_params = st.session_state['soil_params']
            
            # Get crop results
            with st.spinner("Loading crop data..."):
                crop_results = analyzer.analyze_all_crops(
                    soil_params['moisture'],
                    soil_params['organic_matter'],
                    soil_params['texture'],
                    soil_params['temperature'],
                    st.session_state['selected_location']
                )
            
            # Prepare data for visualization
            crops = list(crop_results.keys())
            suitability_scores = [results['suitability_analysis']['final_score'] for results in crop_results.values()]
            disease_risks = [results['suitability_analysis']['disease_risk'] for results in crop_results.values()]
            
            # Create DataFrame
            viz_df = pd.DataFrame({
                'Crop': crops,
                'Suitability': suitability_scores,
                'Disease Risk': disease_risks
            })
            
            # Sort by suitability
            viz_df = viz_df.sort_values('Suitability', ascending=False)
            
            # Create Plotly figure
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Suitability Scores', 'Disease Risk Assessment'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Suitability bars
            colors_suit = ['green' if s > 0.7 else 'orange' if s > 0.5 else 'red' for s in viz_df['Suitability']]
            fig.add_trace(
                go.Bar(
                    x=viz_df['Crop'],
                    y=viz_df['Suitability'],
                    name='Suitability',
                    marker_color=colors_suit,
                    text=viz_df['Suitability'].round(2),
                    textposition='auto',
                ),
                row=1, col=1
            )
            
            # Disease risk bars
            colors_risk = ['red' if r > 0.6 else 'orange' if r > 0.3 else 'green' for r in viz_df['Disease Risk']]
            fig.add_trace(
                go.Bar(
                    x=viz_df['Crop'],
                    y=viz_df['Disease Risk'],
                    name='Disease Risk',
                    marker_color=colors_risk,
                    text=viz_df['Disease Risk'].round(2),
                    textposition='auto',
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=500,
                showlegend=False,
                title_text=f"Crop Analysis - {st.session_state['selected_location']}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot of Suitability vs Disease Risk
            st.markdown("### 📊 Suitability vs Disease Risk Scatter Plot")
            
            fig2 = px.scatter(
                viz_df,
                x='Suitability',
                y='Disease Risk',
                text='Crop',
                size=[20]*len(viz_df),
                color='Suitability',
                color_continuous_scale='RdYlGn',
                title='Suitability vs Disease Risk'
            )
            
            # Add quadrant lines
            fig2.add_hline(y=0.5, line_dash="dash", line_color="gray")
            fig2.add_vline(x=0.6, line_dash="dash", line_color="gray")
            
            # Add quadrant labels
            fig2.add_annotation(x=0.8, y=0.2, text="Ideal", showarrow=False, font=dict(color="green"))
            fig2.add_annotation(x=0.8, y=0.8, text="Risky", showarrow=False, font=dict(color="orange"))
            fig2.add_annotation(x=0.3, y=0.2, text="Marginal", showarrow=False, font=dict(color="yellow"))
            fig2.add_annotation(x=0.3, y=0.8, text="Avoid", showarrow=False, font=dict(color="red"))
            
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)
            
        elif viz_type == "Groundwater Analysis":
            st.markdown("### 💧 Groundwater Potential Visualization")
            
            # Get groundwater results
            analyzer = ComprehensiveAgriculturalAnalyzer()
            with st.spinner("Loading groundwater data..."):
                gw_results = analyzer.analyze_groundwater(st.session_state['selected_location'])
            
            # Create radar chart for groundwater components
            categories = ['Recharge', 'Infiltration', 'Storage', 'Quality', 'Accessibility']
            
            # Generate component values
            if gw_results['category'] == 'VERY HIGH':
                values = [0.9, 0.8, 0.7, 0.6, 0.9]
            elif gw_results['category'] == 'HIGH':
                values = [0.8, 0.7, 0.6, 0.5, 0.8]
            elif gw_results['category'] == 'MODERATE':
                values = [0.6, 0.5, 0.4, 0.5, 0.6]
            else:
                values = [0.3, 0.4, 0.3, 0.4, 0.3]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Groundwater Potential',
                fillcolor='rgba(30, 144, 255, 0.5)',
                line=dict(color='rgb(30, 144, 255)', width=2)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True,
                height=500,
                title=f"Groundwater Potential Components - {st.session_state['selected_location']}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Soil Properties":
            st.markdown("### 🌱 Soil Properties Analysis")
            
            soil_params = st.session_state['soil_params']
            
            # Create tabs for different soil visualizations
            soil_tab1, soil_tab2, soil_tab3 = st.tabs(["Texture Analysis", "Nutrient Levels", "SOM Analysis"])
            
            with soil_tab1:
                st.markdown("#### Soil Texture Analysis")
                
                current_texture = soil_params['texture']
                
                # Create a bar chart showing texture scores for different crops
                st.markdown("##### Texture Suitability for Major Crops")
                
                crops_to_show = ['Wheat', 'Maize', 'Rice', 'Tomato', 'Potato']
                texture_scores = {}
                
                for crop in crops_to_show:
                    if crop in CROP_REQUIREMENTS:
                        score = CROP_REQUIREMENTS[crop]['texture_scores'].get(current_texture, 0.5)
                        texture_scores[crop] = score
                
                # Create bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(texture_scores.keys()),
                        y=list(texture_scores.values()),
                        marker_color=['green' if s > 0.7 else 'orange' if s > 0.5 else 'red' for s in texture_scores.values()],
                        text=[f'{s:.2f}' for s in texture_scores.values()],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title=f"Texture Suitability for Current Soil: {current_texture}",
                    yaxis_title="Suitability Score",
                    yaxis_range=[0, 1],
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Texture properties
                st.markdown("##### Soil Texture Properties")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Current Texture", current_texture)
                    if current_texture in ['Clay', 'Silty clay', 'Clay loam']:
                        st.info("**Properties:** High water retention, slow drainage")
                    elif current_texture in ['Loam', 'Silt loam']:
                        st.success("**Properties:** Ideal for most crops, good drainage")
                    else:
                        st.warning("**Properties:** Fast drainage, low water retention")
                
                with col2:
                    # Texture improvement suggestions
                    st.markdown("**Improvement Suggestions:**")
                    if current_texture in ['Clay', 'Silty clay']:
                        st.markdown("- Add organic matter")
                        st.markdown("- Use sand amendments")
                        st.markdown("- Practice minimum tillage")
                    elif current_texture in ['Sand', 'Loamy sand']:
                        st.markdown("- Add clay or silt")
                        st.markdown("- Use organic mulches")
                        st.markdown("- Implement cover cropping")
            
            with soil_tab2:
                st.markdown("#### Soil Nutrient Levels")
                
                # Simulated nutrient data
                nutrients = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Calcium (Ca)', 'Magnesium (Mg)']
                levels = np.random.uniform(20, 90, len(nutrients))
                
                fig = go.Figure(data=[go.Bar(
                    x=nutrients,
                    y=levels,
                    text=[f'{l:.0f}%' for l in levels],
                    textposition='auto',
                    marker_color=['#FF6B6B' if l < 40 else '#4ECDC4' if l < 70 else '#45B7D1' for l in levels]
                )])
                
                fig.update_layout(
                    title="Soil Nutrient Sufficiency Levels",
                    yaxis_title="Sufficiency Level (%)",
                    yaxis_range=[0, 100],
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Nutrient recommendations
                st.markdown("##### Nutrient Management Recommendations")
                
                nutrient_cols = st.columns(len(nutrients))
                for idx, (nutrient, level) in enumerate(zip(nutrients, levels)):
                    with nutrient_cols[idx]:
                        if level < 40:
                            st.error(f"{nutrient.split(' ')[0]}")
                            st.caption("Deficient")
                        elif level < 70:
                            st.warning(f"{nutrient.split(' ')[0]}")
                            st.caption("Adequate")
                        else:
                            st.success(f"{nutrient.split(' ')[0]}")
                            st.caption("Sufficient")
            
            with soil_tab3:
                st.markdown("#### Soil Organic Matter Analysis")
                
                # Current SOM value
                current_som = soil_params['organic_matter']
                
                col1, col2 = st.columns(2)
                with col1:
                    # SOM gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=current_som,
                        title={'text': "Soil Organic Matter (%)"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 10]},
                            'bar': {'color': "brown"},
                            'steps': [
                                {'range': [0, 1], 'color': "red"},
                                {'range': [1, 2], 'color': "orange"},
                                {'range': [2, 3.5], 'color': "yellow"},
                                {'range': [3.5, 5], 'color': "lightgreen"},
                                {'range': [5, 10], 'color': "darkgreen"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': current_som
                            }
                        }
                    ))
                    
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("##### SOM Interpretation")
                    if current_som < 1.0:
                        st.error("**Very Low** - Immediate improvement needed")
                        st.markdown("""
                        - Add 10-15 tons/ha of compost
                        - Plant green manure crops
                        - Reduce tillage intensity
                        """)
                    elif current_som < 2.0:
                        st.warning("**Low** - Improvement recommended")
                        st.markdown("""
                        - Add 5-10 tons/ha organic matter
                        - Incorporate crop residues
                        - Use cover crops
                        """)
                    elif current_som < 3.5:
                        st.success("**Adequate** - Maintain current level")
                        st.markdown("""
                        - Regular organic amendments
                        - Balanced fertilization
                        - Conservation tillage
                        """)
                    else:
                        st.success("**High** - Excellent soil health")
                        st.markdown("""
                        - Maintain current practices
                        - Continue organic additions
                        - Monitor soil health
                        """)
                
                # SOM impact on yield
                st.markdown("##### SOM Impact on Crop Yields")
                crops = ['Wheat', 'Maize', 'Potato', 'Tomato']
                yield_improvement = [min(100, current_som * 15),
                                   min(100, current_som * 12),
                                   min(100, current_som * 20),
                                   min(100, current_som * 18)]
                
                fig2 = go.Figure(data=[go.Bar(
                    x=crops,
                    y=yield_improvement,
                    text=[f'{y:.0f}%' for y in yield_improvement],
                    textposition='auto',
                    marker_color='green'
                )])
                
                fig2.update_layout(
                    title="Potential Yield Improvement with Current SOM Level",
                    yaxis_title="Yield Improvement (%)",
                    yaxis_range=[0, 100],
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
        
        else:  # Climate Data
            st.markdown("### 🌤️ Climate Data Visualization")
            
            # Mock climate data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Generate realistic climate data based on location
            location = st.session_state['selected_location'].lower()
            
            if 'algeria' in location or 'morocco' in location:
                # Mediterranean climate
                temp_min = [8, 9, 11, 13, 16, 20, 23, 23, 20, 16, 12, 9]
                temp_max = [16, 17, 19, 22, 25, 29, 32, 32, 29, 25, 20, 17]
                precipitation = [80, 70, 60, 40, 30, 10, 5, 10, 30, 60, 90, 100]
            elif 'kenya' in location or 'tanzania' in location:
                # Tropical climate
                temp_min = [18, 18, 19, 19, 18, 17, 16, 16, 17, 18, 18, 18]
                temp_max = [28, 29, 29, 27, 26, 25, 24, 25, 27, 28, 27, 27]
                precipitation = [60, 70, 90, 150, 120, 40, 30, 40, 50, 80, 120, 100]
            elif 'south africa' in location:
                # Temperate climate
                temp_min = [15, 15, 13, 10, 7, 4, 4, 5, 8, 10, 12, 14]
                temp_max = [26, 26, 25, 22, 19, 17, 16, 18, 21, 23, 24, 25]
                precipitation = [15, 20, 25, 40, 50, 60, 60, 50, 40, 30, 20, 15]
            else:
                # Default temperate climate
                temp_min = [5, 6, 9, 12, 16, 19, 21, 21, 18, 14, 9, 6]
                temp_max = [12, 13, 16, 20, 24, 27, 29, 29, 26, 21, 16, 13]
                precipitation = [80, 70, 70, 60, 50, 40, 30, 40, 50, 70, 80, 90]
            
            temp_avg = [(min_v + max_v) / 2 for min_v, max_v in zip(temp_min, temp_max)]
            
            # Create climate charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Temperature chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months,
                    y=temp_max,
                    name='Max Temp',
                    line=dict(color='red', width=3),
                    mode='lines+markers'
                ))
                fig.add_trace(go.Scatter(
                    x=months,
                    y=temp_avg,
                    name='Avg Temp',
                    line=dict(color='orange', width=3),
                    mode='lines+markers'
                ))
                fig.add_trace(go.Scatter(
                    x=months,
                    y=temp_min,
                    name='Min Temp',
                    line=dict(color='blue', width=3),
                    mode='lines+markers',
                    fill='tonexty',
                    fillcolor='rgba(0, 0, 255, 0.1)'
                ))
                
                fig.update_layout(
                    title="Monthly Temperature Range",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Precipitation chart
                fig = go.Figure(data=[go.Bar(
                    x=months,
                    y=precipitation,
                    marker_color='lightblue',
                    text=[f'{p:.0f}mm' for p in precipitation],
                    textposition='auto'
                )])
                
                fig.update_layout(
                    title="Monthly Precipitation",
                    yaxis_title="Precipitation (mm)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Growing season analysis
            st.markdown("#### 🌱 Growing Season Analysis")
            
            # Determine growing season based on temperature
            growing_months = [i for i, temp in enumerate(temp_avg) if temp >= 10]
            growing_season_length = len(growing_months)
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                avg_temp = np.mean(temp_avg)
                st.metric("Average Temperature", f"{avg_temp:.1f}°C")
            
            with col4:
                total_precip = sum(precipitation)
                st.metric("Annual Precipitation", f"{total_precip:.0f} mm")
            
            with col5:
                st.metric("Growing Season", f"{growing_season_length} months")
            
            # Growing season visualization
            if growing_months:
                growing_season_names = [months[i] for i in growing_months]
                st.markdown(f"**Optimal Growing Months:** {', '.join(growing_season_names)}")
                
                # Create growing season chart
                season_data = pd.DataFrame({
                    'Month': months,
                    'Temperature': temp_avg,
                    'Precipitation': precipitation,
                    'Growing Season': [1 if i in growing_months else 0 for i in range(12)]
                })
                
                fig3 = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig3.add_trace(
                    go.Scatter(x=season_data['Month'], y=season_data['Temperature'],
                             name="Temperature", mode='lines+markers',
                             line=dict(color='red', width=2)),
                    secondary_y=False
                )
                
                fig3.add_trace(
                    go.Bar(x=season_data['Month'], y=season_data['Precipitation'],
                          name="Precipitation", marker_color='lightblue', opacity=0.6),
                    secondary_y=True
                )
                
                # Highlight growing season
                for month_idx in growing_months:
                    fig3.add_vrect(
                        x0=month_idx-0.5, x1=month_idx+0.5,
                        fillcolor="green", opacity=0.1,
                        layer="below", line_width=0
                    )
                
                fig3.update_layout(
                    title="Growing Season Analysis",
                    height=400,
                    hovermode='x unified'
                )
                
                fig3.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
                fig3.update_yaxes(title_text="Precipitation (mm)", secondary_y=True)
                
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.warning("Growing season limited due to low temperatures")

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

# Requirements file creation
with st.sidebar:
    with st.expander("📦 Requirements"):
        st.code("""streamlit>=1.28.0
earthengine-api>=0.1.375
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
matplotlib>=3.7.0
seaborn>=0.12.0""")
        
        if st.button("Generate requirements.txt"):
            requirements = """streamlit>=1.28.0
earthengine-api>=0.1.375
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
matplotlib>=3.7.0
seaborn>=0.12.0"""
            st.download_button(
                label="Download requirements.txt",
                data=requirements,
                file_name="requirements.txt",
                mime="text/plain"
            )
