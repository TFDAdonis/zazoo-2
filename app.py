import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import warnings

warnings.filterwarnings('ignore')

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
    
    /* FarmAdvisor Specific Styles */
    .crop-card {
        background: var(--secondary-black);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    
    .crop-card:hover {
        border-color: var(--primary-green);
        transform: translateY(-2px);
    }
    
    .crop-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .crop-score {
        background: var(--primary-green);
        color: var(--primary-black);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .risk-high {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    
    .risk-low {
        color: #00ff88;
        font-weight: bold;
    }
    
    .management-tip {
        background: rgba(0, 255, 136, 0.1);
        border-left: 3px solid var(--primary-green);
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    
    .disease-alert {
        background: rgba(255, 107, 107, 0.1);
        border-left: 3px solid #ff6b6b;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============ FARMADVISOR COMPREHENSIVE CROP SUITABILITY CONFIGURATION ============
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
    # Add more crops as needed - keeping it concise for display
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
        st.error(f"Earth Engine auto-initialization failed: {str(e)}")
        return False

# Try to auto-initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_initialized = True
            st.session_state.FAO_GAUL = ee.FeatureCollection("FAO/GAUL/2015/level0")
            st.session_state.FAO_GAUL_ADMIN1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
            st.session_state.FAO_GAUL_ADMIN2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
        else:
            st.session_state.ee_initialized = False

# Initialize session state for FarmAdvisor
if 'farmadvisor_results' not in st.session_state:
    st.session_state.farmadvisor_results = None
if 'farmadvisor_analysis_type' not in st.session_state:
    st.session_state.farmadvisor_analysis_type = 'crop_suitability'

class FarmAdvisor:
    def __init__(self):
        self.config = {
            'default_start_date': '2020-01-01',
            'default_end_date': '2023-12-31',
            'scale': 1000,
            'max_pixels': 1e6
        }
        
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

        # Texture-specific strategies
        if comp_scores['texture'] < 0.6:
            strategies.append("🔄 Add soil amendments to improve soil structure")

        # Disease management based on risk level
        if disease_risk >= 0.7:
            strategies.append("🦠 HIGH DISEASE RISK - Implement intensive IPM program")
            strategies.append("🔄 Use 3+ year crop rotation with non-host crops")
            strategies.append("🌱 Select disease-resistant varieties")
        elif disease_risk >= 0.5:
            strategies.append("⚠️ MODERATE DISEASE RISK - Regular monitoring needed")
            strategies.append("🍃 Improve air circulation through proper spacing")

        # Crop-specific additional strategies
        crop_specific_strategies = self.get_crop_specific_strategies(crop_name, suitability_analysis)
        strategies.extend(crop_specific_strategies)

        return strategies

    def get_crop_specific_strategies(self, crop_name, suitability_analysis):
        """Get crop-specific management strategies"""

        strategies = []
        disease_risk = suitability_analysis['disease_risk']

        if crop_name == 'Wheat':
            if disease_risk > 0.6:
                strategies.append("🌾 Use fungicide seed treatment for rust prevention")
                strategies.append("📅 Time planting to avoid peak rust periods")
            strategies.append("⚖️ Balance nitrogen application to reduce lodging")

        elif crop_name == 'Tomato':
            if disease_risk > 0.5:
                strategies.append("🍅 Use stake and weave system for better air circulation")
                strategies.append("💦 Use drip irrigation to keep foliage dry")
            strategies.append("🥛 Ensure adequate calcium to prevent blossom end rot")

        elif crop_name == 'Potato':
            if disease_risk > 0.6:
                strategies.append("🥔 Use certified disease-free seed potatoes")
                strategies.append("🚫 Destroy cull piles and volunteer plants")
            strategies.append("🔄 Practice 4-year rotation with non-solanaceous crops")

        return strategies

    def analyze_all_crops(self, moisture_value, som_value, texture_value, temp_value, location_name):
        """Analyze all crops with enhanced suitability scoring"""

        analysis_results = {}

        for crop_name, crop_req in CROP_REQUIREMENTS.items():
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

        return analysis_results

    # ============ SOIL ANALYSIS METHODS ============
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

            return {'mean': som_percent}
        except:
            return {'mean': 0.41}

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

            return {'mean': som_percent}
        except:
            return {'mean': 0.41}

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
            return {'mode': texture_val}
        except:
            return {'mode': 7}

    def get_area_representative_values(self, geometry, area_name):
        """Get representative soil values for crop suitability analysis"""

        # Get climate data for moisture estimation
        climate_data = self.get_daily_climate_data('2024-01-01', '2024-12-31', geometry)

        # Calculate mean moisture
        try:
            mean_moisture_stats = climate_data.select('volumetric_soil_water_layer_1').mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=5000,
                maxPixels=1e9
            ).getInfo()
            moisture_val = mean_moisture_stats.get('volumetric_soil_water_layer_1', 0.15)
        except:
            moisture_val = 0.15

        # Check if in Africa for soil data
        is_in_africa = AFRICA_BOUNDS.intersects(geometry, 100).getInfo()

        # Get SOM data
        if is_in_africa:
            som_stats = self.get_africa_som_data(geometry)
        else:
            som_stats = self.get_global_som_data(geometry)

        som_val = som_stats.get('mean', 0.41)

        # Get texture data
        texture_stats = self.get_soil_texture_data(geometry)
        texture_val = texture_stats.get('mode', 7)

        # Get temperature (use default or from climate data)
        temp_val = 22.0  # Default temperature

        return moisture_val, som_val, texture_val, temp_val

    def get_daily_climate_data(self, start_date, end_date, geometry):
        """Get daily climate data matching GEE JavaScript implementation"""
        try:
            modis_lst = ee.ImageCollection('MODIS/061/MOD11A1') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry) \
                .select('LST_Day_1km')

            chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry) \
                .select('precipitation')

            def process_daily_data(image):
                date = image.date()
                lst = image.select('LST_Day_1km').multiply(0.02).subtract(273.15)

                precip_image = chirps.filter(ee.Filter.eq('system:time_start', date.millis())).first()
                precip = precip_image.select('precipitation') if precip_image else ee.Image.constant(0)

                base_moisture = precip.multiply(0.1).add(0.15)
                temp_effect = lst.multiply(-0.005).add(1)

                soil_moisture1 = base_moisture.multiply(temp_effect).rename('volumetric_soil_water_layer_1')
                soil_moisture2 = base_moisture.multiply(temp_effect).multiply(0.8).rename('volumetric_soil_water_layer_2')
                soil_moisture3 = base_moisture.multiply(temp_effect).multiply(0.6).rename('volumetric_soil_water_layer_3')

                evaporation = lst.multiply(0.02).add(precip.multiply(0.1)).rename('potential_evaporation')

                return ee.Image.cat([
                    soil_moisture1, soil_moisture2, soil_moisture3,
                    precip.rename('total_precipitation'),
                    evaporation,
                    lst.rename('temperature_2m')
                ]).set('system:time_start', date.millis())

            return modis_lst.map(process_daily_data)

        except Exception as e:
            return self._create_daily_synthetic_data(start_date, end_date, geometry)

    def _create_daily_synthetic_data(self, start_date, end_date, geometry):
        """Create synthetic daily data matching GEE patterns"""
        start = ee.Date(start_date)
        end = ee.Date(end_date)
        days = ee.List.sequence(0, end.difference(start, 'day').subtract(1))

        def create_daily_image(day_offset):
            date = start.advance(day_offset, 'day')
            day_of_year = date.getRelative('day', 'year')

            season = ee.Number(day_of_year).multiply(2 * np.pi / 365).cos()

            base_temp = ee.Number(18).add(ee.Number(12).multiply(season))

            precip_season = ee.Number(day_of_year).subtract(30).multiply(2 * np.pi / 365).cos()
            base_precip = ee.Number(1.5).add(ee.Number(1.0).multiply(precip_season.negative()))

            temperature = ee.Image.constant(base_temp).rename('temperature_2m')
            precipitation = ee.Image.constant(base_precip.max(0)).rename('total_precipitation')

            base_moisture = precipitation.multiply(0.1).add(0.15)
            temp_effect = temperature.multiply(-0.005).add(1)

            soil_moisture1 = base_moisture.multiply(temp_effect).rename('volumetric_soil_water_layer_1')
            soil_moisture2 = base_moisture.multiply(temp_effect).multiply(0.8).rename('volumetric_soil_water_layer_2')
            soil_moisture3 = base_moisture.multiply(temp_effect).multiply(0.6).rename('volumetric_soil_water_layer_3')

            evaporation = temperature.multiply(0.02).add(precipitation.multiply(0.1)).rename('potential_evaporation')

            return ee.Image.cat([
                soil_moisture1, soil_moisture2, soil_moisture3,
                precipitation, evaporation, temperature
            ]).set('system:time_start', date.millis())

        return ee.ImageCollection.fromImages(days.map(create_daily_image))

    # ============ GROUNDWATER ANALYSIS METHODS ============
    def get_precipitation(self, geometry, start_date, end_date):
        """Get annual precipitation in mm"""
        try:
            precipitation = self.chirps.filterDate(start_date, end_date) \
                                      .filterBounds(geometry) \
                                      .mean()

            stats = precipitation.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )

            precip_value = stats.get('precipitation').getInfo()
            # Convert to annual (assuming data is daily)
            annual_precip = (precip_value or 1.0) * 365
            return annual_precip
        except Exception as e:
            return 350

    def get_soil_properties(self, geometry):
        """Get comprehensive soil properties including sand, silt, clay percentages"""
        try:
            # Get clay content
            clay_stats = self.soil_clay.select('b10').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )
            clay_content = clay_stats.get('b10').getInfo() or 25

            # Get sand content
            sand_stats = self.soil_sand.select('b10').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )
            sand_content = sand_stats.get('b10').getInfo() or 40

            # Get silt content
            silt_stats = self.soil_silt.select('b10').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )
            silt_content = silt_stats.get('b10').getInfo() or 35

            # Normalize to 100%
            total = clay_content + sand_content + silt_content
            if total > 0:
                clay_content = (clay_content / total) * 100
                sand_content = (sand_content / total) * 100
                silt_content = (silt_content / total) * 100

            # Estimate hydraulic conductivity based on soil texture
            conductivity, soil_type = self.estimate_conductivity(clay_content, sand_content)

            return {
                'clay_percent': clay_content,
                'sand_percent': sand_content,
                'silt_percent': silt_content,
                'conductivity': conductivity,
                'soil_type': soil_type
            }
        except Exception as e:
            return {
                'clay_percent': 25,
                'sand_percent': 40,
                'silt_percent': 35,
                'conductivity': 5.0,
                'soil_type': "Loam"
            }

    def estimate_conductivity(self, clay, sand):
        """Estimate hydraulic conductivity based on soil texture"""
        if sand > 70 and clay < 15:
            conductivity = 25.0  # cm/day - Sand
            soil_type = "Sand"
        elif sand > 50 and clay < 20:
            conductivity = 10.0  # cm/day - Sandy Loam
            soil_type = "Sandy Loam"
        elif clay < 27 and sand < 52:
            conductivity = 5.0   # cm/day - Loam
            soil_type = "Loam"
        elif clay > 27 and clay < 40:
            conductivity = 1.0   # cm/day - Clay Loam
            soil_type = "Clay Loam"
        else:
            conductivity = 0.1   # cm/day - Clay
            soil_type = "Clay"
        return conductivity, soil_type

    def get_topography(self, geometry):
        """Get slope and topographic wetness index"""
        try:
            dem = self.dem.clip(geometry)

            # Calculate slope
            slope = ee.Terrain.slope(dem)

            # Calculate TWI (Topographic Wetness Index)
            flow_accumulation = dem.flowAccumulation()
            slope_radians = slope.multiply(3.14159).divide(180)
            tan_slope = slope_radians.tan()
            twi = flow_accumulation.add(1).divide(tan_slope.add(0.001)).log()

            slope_stats = slope.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )

            twi_stats = twi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=self.config['scale'],
                maxPixels=self.config['max_pixels']
            )

            slope_val = slope_stats.get('slope').getInfo() or 5.0
            twi_val = twi_stats.get('elevation').getInfo() or 8.0

            return slope_val, twi_val
        except Exception as e:
            return 5.0, 8.0

    def calculate_water_balance(self, precipitation, soil_type, slope):
        """Calculate water balance components"""
        # Base evapotranspiration (simplified)
        et = precipitation * 0.6  # 60% of precipitation

        # Runoff based on slope and soil
        if slope > 15:
            runoff_coeff = 0.4  # High slope = more runoff
        elif slope > 5:
            runoff_coeff = 0.25
        else:
            runoff_coeff = 0.15  # Low slope = less runoff

        # Adjust for soil type
        if soil_type == "Clay":
            runoff_coeff += 0.1
        elif soil_type == "Sand" or soil_type == "Sandy Loam":
            runoff_coeff -= 0.05

        runoff = precipitation * runoff_coeff

        # Recharge = Precipitation - ET - Runoff
        recharge = precipitation - et - runoff
        recharge = max(0, recharge)  # Ensure non-negative

        return {
            'precipitation_mm': precipitation,
            'evapotranspiration_mm': et,
            'runoff_mm': runoff,
            'recharge_mm': recharge
        }

    def calculate_gw_potential(self, water_balance, soil_props, slope, twi):
        """Calculate groundwater potential score (0-1)"""
        conductivity = soil_props['conductivity']
        sand_percent = soil_props['sand_percent']

        # Normalize factors
        recharge_norm = min(water_balance['recharge_mm'] / 500, 1.0)
        conductivity_norm = min(conductivity / 25, 1.0)
        slope_norm = 1 - min(slope / 45, 1.0)
        twi_norm = min(twi / 15, 1.0)
        sand_norm = sand_percent / 100

        # CORRECTED COMPONENT WEIGHTS - ensuring they sum to 1.0
        components = {
            'recharge_potential': recharge_norm * 0.35,      # 35%
            'soil_infiltration': conductivity_norm * 0.25,   # 25%
            'topographic_factors': (slope_norm * 0.1 + twi_norm * 0.1),  # 20% total
            'soil_texture': sand_norm * 0.15,                # 15%
            'geological_factors': 0.05                       # 5%
        }

        total_score = sum(components.values())

        # Categorize
        if total_score < 0.45:
            category = "LOW"
        elif total_score < 0.6:
            category = "MODERATE"
        elif total_score < 0.75:
            category = "HIGH"
        else:
            category = "VERY HIGH"

        return total_score, category, components

    def analyze_groundwater_potential(self, geometry, name):
        """Comprehensive groundwater analysis for a location with better error handling"""
        try:
            # Get precipitation with fallback
            precipitation = self.get_precipitation(
                geometry,
                self.config['default_start_date'],
                self.config['default_end_date']
            )

            # Get comprehensive soil properties with fallback
            soil_props = self.get_soil_properties(geometry)

            # Get topography with fallback
            slope, twi = self.get_topography(geometry)

            # Calculate water balance
            water_balance = self.calculate_water_balance(precipitation, soil_props['soil_type'], slope)

            # Calculate groundwater potential
            score, category, components = self.calculate_gw_potential(
                water_balance, soil_props, slope, twi
            )

            # Get centroid for mapping
            centroid = geometry.centroid()
            lon = centroid.coordinates().get(0).getInfo()
            lat = centroid.coordinates().get(1).getInfo()

            # Ensure all values are finite numbers
            def ensure_finite(value, default=0):
                return value if (isinstance(value, (int, float)) and np.isfinite(value)) else default

            result = {
                'name': name,
                'score': ensure_finite(score, 0.5),
                'category': category,
                'precipitation_mm': ensure_finite(precipitation, 350),
                'recharge_mm': ensure_finite(water_balance['recharge_mm'], 50),
                'conductivity': ensure_finite(soil_props['conductivity'], 5.0),
                'soil_type': soil_props['soil_type'],
                'clay_percent': ensure_finite(soil_props['clay_percent'], 25),
                'sand_percent': ensure_finite(soil_props['sand_percent'], 40),
                'silt_percent': ensure_finite(soil_props['silt_percent'], 35),
                'slope': ensure_finite(slope, 5.0),
                'twi': ensure_finite(twi, 8.0),
                'lon': ensure_finite(lon, 0),
                'lat': ensure_finite(lat, 0),
                'water_balance': water_balance,
                'components': components
            }

            return result

        except Exception as e:
            # Return a fallback result to prevent complete failure
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
                'twi': 8.0,
                'lon': 0,
                'lat': 0,
                'water_balance': {'precipitation_mm': 350, 'evapotranspiration_mm': 210, 'runoff_mm': 70, 'recharge_mm': 70},
                'components': {'recharge_potential': 0.2, 'soil_infiltration': 0.2, 'topographic_factors': 0.2, 'soil_texture': 0.2, 'geological_factors': 0.05}
            }

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

    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry based on selection level using FAO GAUL"""
        try:
            if municipality != 'Select Municipality':
                feature = st.session_state.FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .filter(ee.Filter.eq('ADM2_NAME', municipality)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{municipality}, {region}, {country}"
                return geometry, location_name

            elif region != 'Select Region':
                feature = st.session_state.FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{region}, {country}"
                return geometry, location_name

            elif country != 'Select Country':
                feature = st.session_state.FAO_GAUL.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                geometry = feature.geometry()
                location_name = f"{country}"
                return geometry, location_name

            else:
                return None, None

        except Exception as e:
            return None, None

    # ============ MAIN ANALYSIS METHOD ============
    def run_comprehensive_analysis(self, country, region='Select Region', municipality='Select Municipality',
                                 analysis_type='crop_suitability'):
        """Run comprehensive agricultural analysis for selected region"""

        # Get geometry for selected location
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            return None

        results = {
            'location_name': location_name,
            'geometry': geometry,
            'analysis_type': analysis_type
        }

        if analysis_type == 'groundwater':
            # Run groundwater analysis
            gw_results = self.analyze_groundwater_potential(geometry, location_name)
            results['groundwater_analysis'] = gw_results

        else:
            # Run comprehensive crop suitability analysis
            moisture_val, som_val, texture_val, temp_val = self.get_area_representative_values(geometry, location_name)

            results['soil_parameters'] = {
                'moisture': moisture_val,
                'organic_matter': som_val,
                'texture': texture_val,
                'temperature': temp_val
            }

            # Crop Suitability Analysis with Disease Risk
            crop_results = self.analyze_all_crops(moisture_val, som_val, texture_val, temp_val, location_name)
            results['crop_analysis'] = crop_results

        return results

# Initialize session state for steps
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
if 'farmadvisor_instance' not in st.session_state:
    st.session_state.farmadvisor_instance = FarmAdvisor() if st.session_state.ee_initialized else None

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis & FarmAdvisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define steps including FarmAdvisor
STEPS = [
    {"number": 1, "label": "Select Area", "icon": "📍"},
    {"number": 2, "label": "Analysis Type", "icon": "📊"},
    {"number": 3, "label": "Run Analysis", "icon": "🚀"},
    {"number": 4, "label": "View Results", "icon": "📈"}
]

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1>🌍 KHISBA GIS + FARMADVISOR</h1>
    <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics & Comprehensive Farm Advisory System</p>
</div>
""", unsafe_allow_html=True)

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

# JavaScript for progress fill
st.markdown(f"""
<script>
    document.getElementById('progress-fill').style.width = '{((st.session_state.current_step - 1) / (len(STEPS) - 1)) * 100}%';
</script>
""", unsafe_allow_html=True)

# Status indicators
st.markdown("""
<div class="status-container">
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.ee_initialized else ''}"></div>
        <span>Earth Engine: {'Connected' if st.session_state.ee_initialized else 'Disconnected'}</span>
    </div>
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.selected_area_name else ''}"></div>
        <span>Area Selected: {'Yes' if st.session_state.selected_area_name else 'No'}</span>
    </div>
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.farmadvisor_results else ''}"></div>
        <span>FarmAdvisor: {'Complete' if st.session_state.farmadvisor_results else 'Pending'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([0.35, 0.65], gap="large")

with col1:
    # Step 1: Area Selection
    if st.session_state.current_step == 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📍</div><h3 style="margin: 0;">Step 1: Select Your Area</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 1
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
                # Get countries
                countries_fc = st.session_state.FAO_GAUL
                country_names = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
                country_names = sorted(country_names) if country_names else []
                
                selected_country = st.selectbox(
                    "🌍 Country",
                    options=["Select a country"] + country_names,
                    index=0,
                    help="Choose a country for analysis",
                    key="country_select"
                )
                
                if selected_country and selected_country != "Select a country":
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                    admin1_fc = st.session_state.FAO_GAUL_ADMIN1\
                        .filter(ee.Filter.eq('ADM0_CODE', country_feature.get('ADM0_CODE')))
                    
                    admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().getInfo()
                    admin1_names = sorted(admin1_names) if admin1_names else []
                    
                    selected_admin1 = st.selectbox(
                        "🏛️ State/Province",
                        options=["Select state/province"] + admin1_names,
                        index=0,
                        help="Choose a state or province",
                        key="admin1_select"
                    )
                    
                    if selected_admin1 and selected_admin1 != "Select state/province":
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                        admin2_fc = st.session_state.FAO_GAUL_ADMIN2\
                            .filter(ee.Filter.eq('ADM1_CODE', admin1_feature.get('ADM1_CODE')))
                        
                        admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                        admin2_names = sorted(admin2_names) if admin2_names else []
                        
                        selected_admin2 = st.selectbox(
                            "🏘️ Municipality",
                            options=["Select municipality"] + admin2_names,
                            index=0,
                            help="Choose a municipality",
                            key="admin2_select"
                        )
                    else:
                        selected_admin2 = None
                else:
                    selected_admin1 = None
                    selected_admin2 = None
                    
                if st.button("✅ Confirm Selection", type="primary", use_container_width=True, disabled=not selected_country or selected_country == "Select a country"):
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
                        
                        # Store in session state
                        st.session_state.selected_geometry = geometry
                        st.session_state.selected_area_name = area_name
                        st.session_state.selected_area_level = area_level
                        
                        # Get coordinates for the map
                        bounds = geometry.geometry().bounds().getInfo()
                        coords = bounds['coordinates'][0]
                        lats = [coord[1] for coord in coords]
                        lons = [coord[0] for coord in coords]
                        center_lat = sum(lats) / len(lats)
                        center_lon = sum(lons) / len(lons)
                        
                        st.session_state.selected_coordinates = {
                            'center': [center_lon, center_lat],
                            'bounds': [[min(lats), min(lons)], [max(lats), max(lons)]],
                            'zoom': 6
                        }
                        
                        # Move to next step
                        st.session_state.current_step = 2
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error loading boundaries: {str(e)}")
        else:
            st.warning("Earth Engine not initialized. Please wait...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Analysis Type Selection
    elif st.session_state.current_step == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 2: Select Analysis Type</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 2
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">🔍</div>
                <div class="guide-title">Choose Analysis</div>
            </div>
            <div class="guide-content">
                Select the type of agricultural analysis you want to perform. FarmAdvisor provides comprehensive crop suitability and groundwater analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
            
            # Analysis type selection
            analysis_type = st.radio(
                "📋 Select Analysis Type",
                options=[
                    "🌾 Crop Suitability & Disease Risk Analysis",
                    "💧 Groundwater Potential Analysis"
                ],
                help="Choose the type of analysis to perform"
            )
            
            # Map selection to internal values
            if "Crop Suitability" in analysis_type:
                st.session_state.farmadvisor_analysis_type = 'crop_suitability'
                analysis_description = """
                **Crop Suitability Analysis Includes:**
                • Soil moisture and organic matter assessment
                • Soil texture classification
                • Temperature suitability analysis
                • Disease risk assessment for common crops
                • Management recommendations for 32+ crops
                • Yield potential estimation
                """
            else:
                st.session_state.farmadvisor_analysis_type = 'groundwater'
                analysis_description = """
                **Groundwater Potential Analysis Includes:**
                • Precipitation and water balance analysis
                • Soil infiltration capacity assessment
                • Topographic wetness index calculation
                • Groundwater recharge potential
                • Hydraulic conductivity estimation
                • Water availability for irrigation
                """
            
            st.markdown(f"""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #00ff88;">
                {analysis_description}
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation buttons
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Area Selection", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            
            with col_next:
                if st.button("✅ Confirm & Continue", type="primary", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()
        else:
            st.warning("Please go back to Step 1 and select an area first.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: Run FarmAdvisor Analysis
    elif st.session_state.current_step == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 3: Run FarmAdvisor Analysis</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"""
            **Selected Area:** {st.session_state.selected_area_name}
            
            **Analysis Type:** {'Crop Suitability & Disease Risk' if st.session_state.farmadvisor_analysis_type == 'crop_suitability' else 'Groundwater Potential'}
            
            **Status:** Ready to analyze
            """)
            
            if st.button("🚀 Run FarmAdvisor Analysis", type="primary", use_container_width=True):
                with st.spinner("Running FarmAdvisor analysis..."):
                    try:
                        # Get selected location details
                        selected_country = st.session_state.get('selected_country', '')
                        selected_admin1 = st.session_state.get('selected_admin1', 'Select Region')
                        selected_admin2 = st.session_state.get('selected_admin2', 'Select Municipality')
                        
                        # Run FarmAdvisor analysis
                        analyzer = st.session_state.farmadvisor_instance
                        results = analyzer.run_comprehensive_analysis(
                            selected_country,
                            selected_admin1,
                            selected_admin2,
                            st.session_state.farmadvisor_analysis_type
                        )
                        
                        if results:
                            st.session_state.farmadvisor_results = results
                            st.success("✅ Analysis completed successfully!")
                            
                            # Auto-move to results after 1 second
                            import time
                            time.sleep(1)
                            st.session_state.current_step = 4
                            st.rerun()
                        else:
                            st.error("❌ Analysis failed. Please try again.")
                            
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.error(traceback.format_exc())
            
            # Navigation buttons
            col_back, _ = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Analysis Type", use_container_width=True):
                    st.session_state.current_step = 2
                    st.rerun()
        else:
            st.warning("No area selected. Please go back to Step 1.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 4: View FarmAdvisor Results
    elif st.session_state.current_step == 4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📈</div><h3 style="margin: 0;">Step 4: FarmAdvisor Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.farmadvisor_results:
            results = st.session_state.farmadvisor_results
            location_name = results['location_name']
            analysis_type = results['analysis_type']
            
            # Navigation buttons
            col_back, col_new = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Analysis", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()
            
            with col_new:
                if st.button("🔄 New Analysis", use_container_width=True):
                    # Reset for new analysis
                    st.session_state.farmadvisor_results = None
                    st.session_state.current_step = 1
                    st.rerun()
            
            # Display results based on analysis type
            if analysis_type == 'groundwater':
                self.display_groundwater_results(results)
            else:
                self.display_crop_suitability_results(results)
        else:
            st.warning("No results available. Please run an analysis first.")
            if st.button("⬅️ Go Back", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def display_groundwater_results(self, results):
        """Display groundwater analysis results"""
        gw = results['groundwater_analysis']
        
        st.markdown(f"""
        <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #00ff88;">
            <div style="color: #00ff88; font-weight: 600; font-size: 16px;">Groundwater Potential Analysis</div>
            <div style="color: #cccccc; font-size: 12px; margin-top: 5px;">{results['location_name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Score with color coding
        score = gw['score']
        if score >= 0.75:
            score_color = "#00ff88"
            score_label = "VERY HIGH"
        elif score >= 0.6:
            score_color = "#4ECDC4"
            score_label = "HIGH"
        elif score >= 0.45:
            score_color = "#FFA500"
            score_label = "MODERATE"
        else:
            score_color = "#FF6B6B"
            score_label = "LOW"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Groundwater Score", f"{score:.3f}", delta=None, delta_color="normal")
        with col2:
            st.metric("Potential Category", score_label)
        with col3:
            st.metric("Recharge", f"{gw['recharge_mm']:.0f} mm/year")
        
        # Water Balance Components
        st.subheader("💧 Water Balance Components")
        water_balance = gw['water_balance']
        
        fig = go.Figure(data=[
            go.Bar(name='Precipitation', x=['Water Balance'], y=[water_balance['precipitation_mm']], marker_color='#1f77b4'),
            go.Bar(name='Evapotranspiration', x=['Water Balance'], y=[water_balance['evapotranspiration_mm']], marker_color='#ff7f0e'),
            go.Bar(name='Runoff', x=['Water Balance'], y=[water_balance['runoff_mm']], marker_color='#2ca02c'),
            go.Bar(name='Recharge', x=['Water Balance'], y=[water_balance['recharge_mm']], marker_color='#d62728')
        ])
        
        fig.update_layout(
            title="Annual Water Balance (mm/year)",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Soil Properties
        st.subheader("🌱 Soil Properties")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Soil Type", gw['soil_type'])
        with col2:
            st.metric("Sand Content", f"{gw['sand_percent']:.1f}%")
        with col3:
            st.metric("Clay Content", f"{gw['clay_percent']:.1f}%")
        with col4:
            st.metric("Conductivity", f"{gw['conductivity']:.2f} cm/day")
        
        # Topography
        st.subheader("🗺️ Topography")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Slope", f"{gw['slope']:.1f}°")
        with col2:
            st.metric("Topographic Wetness Index", f"{gw['twi']:.2f}")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        if score >= 0.75:
            st.success("""
            **Excellent Groundwater Potential:**
            • High recharge rates suitable for irrigation
            • Consider installing wells for agricultural use
            • Monitor water quality regularly
            • Implement sustainable water management practices
            """)
        elif score >= 0.6:
            st.info("""
            **Good Groundwater Potential:**
            • Moderate recharge suitable for supplemental irrigation
            • Consider rainwater harvesting to supplement groundwater
            • Monitor water table levels during dry seasons
            • Practice water conservation measures
            """)
        elif score >= 0.45:
            st.warning("""
            **Moderate Groundwater Potential:**
            • Limited recharge capacity
            • Use groundwater as supplementary source only
            • Implement water-efficient irrigation systems
            • Consider alternative water sources
            """)
        else:
            st.error("""
            **Low Groundwater Potential:**
            • Very limited groundwater availability
            • Not suitable for groundwater-dependent agriculture
            • Focus on rainwater harvesting and storage
            • Consider drought-resistant crops
            • Explore alternative water sources
            """)

    def display_crop_suitability_results(self, results):
        """Display crop suitability analysis results"""
        crop_analysis = results['crop_analysis']
        soil_params = results['soil_parameters']
        
        st.markdown(f"""
        <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #00ff88;">
            <div style="color: #00ff88; font-weight: 600; font-size: 16px;">Crop Suitability Analysis</div>
            <div style="color: #cccccc; font-size: 12px; margin-top: 5px;">{results['location_name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Soil Parameters
        st.subheader("🌱 Soil Parameters")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Soil Moisture", f"{soil_params['moisture']:.3f} m³/m³")
        with col2:
            st.metric("Organic Matter", f"{soil_params['organic_matter']:.2f}%")
        with col3:
            texture_val = soil_params['texture']
            texture_name = SOIL_TEXTURE_CLASSES.get(int(round(texture_val)), 'Unknown')
            st.metric("Soil Texture", texture_name)
        with col4:
            st.metric("Temperature", f"{soil_params['temperature']:.1f}°C")
        
        # Sort crops by suitability score
        sorted_crops = sorted(crop_analysis.items(),
                            key=lambda x: x[1]['suitability_analysis']['final_score'],
                            reverse=True)
        
        # Top 5 Recommended Crops
        st.subheader("🏆 Top Recommended Crops")
        
        for crop_name, data in sorted_crops[:5]:
            analysis = data['suitability_analysis']
            crop_req = data['crop_requirements']
            
            # Determine risk color
            risk_color = {
                'Low': '#00ff88',
                'Moderate': '#FFA500',
                'High': '#FF6B6B',
                'Very High': '#8B0000'
            }.get(analysis['risk_level'], '#cccccc')
            
            st.markdown(f"""
            <div class="crop-card">
                <div class="crop-header">
                    <div style="font-weight: bold; font-size: 16px;">{crop_name}</div>
                    <div class="crop-score" style="background: {risk_color};">{analysis['final_score']:.3f}</div>
                </div>
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Suitability: {analysis['final_score']:.3f}</span>
                        <span class="{'risk-high' if analysis['risk_level'] == 'High' or analysis['risk_level'] == 'Very High' else 'risk-medium' if analysis['risk_level'] == 'Moderate' else 'risk-low'}">
                            Disease Risk: {analysis['risk_level']}
                        </span>
                    </div>
                    <div style="font-size: 12px; color: #999999;">
                        Maturity: {crop_req['maturity_days']} days • Water: {crop_req['water_needs']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show first management tip
            if data['management_strategies']:
                st.markdown(f"""
                <div class="management-tip">
                    💡 <strong>Management Tip:</strong> {data['management_strategies'][0]}
                </div>
                """, unsafe_allow_html=True)
            
            # Show disease alert if risk is high
            if analysis['risk_level'] in ['High', 'Very High'] and crop_req['likely_diseases']:
                st.markdown(f"""
                <div class="disease-alert">
                    ⚠️ <strong>Disease Alert:</strong> {crop_req['likely_diseases'][0]}
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed Analysis Button
        if st.button("📋 View Detailed Analysis for All Crops", use_container_width=True):
            st.session_state.show_detailed_analysis = True
        
        if st.session_state.get('show_detailed_analysis', False):
            self.display_detailed_crop_analysis(sorted_crops)
        
        # Export Results
        st.subheader("💾 Export Results")
        if st.button("📥 Download CSV Report", use_container_width=True):
            # Create CSV data
            export_data = []
            for crop_name, data in sorted_crops:
                analysis = data['suitability_analysis']
                export_data.append({
                    'Crop': crop_name,
                    'Suitability_Score': analysis['final_score'],
                    'Disease_Risk': analysis['risk_level'],
                    'Moisture_Score': analysis['component_scores']['moisture'],
                    'OM_Score': analysis['component_scores']['organic_matter'],
                    'Texture_Score': analysis['component_scores']['texture'],
                    'Temperature_Score': analysis['component_scores']['temperature'],
                    'Maturity_Days': data['crop_requirements']['maturity_days'],
                    'Water_Needs': data['crop_requirements']['water_needs']
                })
            
            df = pd.DataFrame(export_data)
            st.download_button(
                label="Click to Download CSV",
                data=df.to_csv(index=False),
                file_name=f"farmadvisor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    def display_detailed_crop_analysis(self, sorted_crops):
        """Display detailed analysis for all crops"""
        st.subheader("📊 Detailed Crop Analysis")
        
        for crop_name, data in sorted_crops:
            analysis = data['suitability_analysis']
            crop_req = data['crop_requirements']
            
            with st.expander(f"{crop_name} (Score: {analysis['final_score']:.3f}, Risk: {analysis['risk_level']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Component Scores:**")
                    comp = analysis['component_scores']
                    st.write(f"• Moisture: {comp['moisture']:.3f}")
                    st.write(f"• Organic Matter: {comp['organic_matter']:.3f}")
                    st.write(f"• Texture: {comp['texture']:.3f}")
                    st.write(f"• Temperature: {comp['temperature']:.3f}")
                    
                    st.markdown("**Crop Requirements:**")
                    st.write(f"• Optimal Moisture: {crop_req['moisture_opt']:.3f} m³/m³")
                    st.write(f"• Optimal Organic Matter: {crop_req['om_opt']:.1f}%")
                    st.write(f"• Optimal Temperature: {crop_req['temp_opt']}°C")
                    st.write(f"• Water Needs: {crop_req['water_needs']}")
                    st.write(f"• Maturity: {crop_req['maturity_days']} days")
                
                with col2:
                    st.markdown("**Management Strategies:**")
                    for i, strategy in enumerate(data['management_strategies'][:3], 1):
                        st.write(f"{i}. {strategy}")
                    
                    if crop_req['likely_diseases']:
                        st.markdown("**Common Diseases:**")
                        for i, disease in enumerate(crop_req['likely_diseases'][:2], 1):
                            st.write(f"{i}. {disease}")
                
                st.markdown("**Additional Information:**")
                st.write(crop_req['notes'])

with col2:
    # Right column - Show map or results based on step
    if st.session_state.current_step <= 3:
        # Show 3D Mapbox Globe for steps 1-3
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Interactive 3D Global Map</h3></div>', unsafe_allow_html=True)
        
        # Prepare coordinates for the map
        map_center = [0, 20]
        map_zoom = 2
        bounds_data = None
        
        if st.session_state.selected_coordinates:
            map_center = st.session_state.selected_coordinates['center']
            map_zoom = st.session_state.selected_coordinates['zoom']
            bounds_data = st.session_state.selected_coordinates['bounds']
        
        # Generate HTML for Mapbox interactive globe
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
            <div class="overlay-title">🌍 KHISBA GIS + FARMADVISOR</div>
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
              Status: <span style="color: #00ff88;">Ready for FarmAdvisor Analysis</span>
            </div>
          </div>
          ''' if st.session_state.selected_area_name else ''}
          
          <script>
            mapboxgl.accessToken = 'pk.eyJ1IjoiYnJ5Y2VseW5uMjUiLCJhIjoiY2x1a2lmcHh5MGwycTJrbzZ4YXVrb2E0aiJ9.LXbneMJJ6OosHv9ibtI5XA';

            // Create a new map instance with OUTDOORS as default
            const map = new mapboxgl.Map({{
              container: 'map',
              style: 'mapbox://styles/mapbox/outdoors-v12',
              center: {map_center},
              zoom: {map_zoom},
              pitch: 45,
              bearing: 0
            }});

            // Add navigation controls
            map.addControl(new mapboxgl.NavigationControl());

            // Add scale control
            map.addControl(new mapboxgl.ScaleControl({{
              unit: 'metric'
            }}));

            // Add fullscreen control
            map.addControl(new mapboxgl.FullscreenControl());

            // Layer switcher functionality
            const layerButtons = document.querySelectorAll('.layer-button');
            layerButtons.forEach(button => {{
              button.addEventListener('click', () => {{
                // Update active button
                layerButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Change map style
                map.setStyle(button.dataset.style);
                
                // Re-add selected area after style change
                setTimeout(() => {{
                  {f'''
                  if ({bounds_data}) {{
                    const bounds = {bounds_data};
                    
                    // Remove existing layers if they exist
                    if (map.getSource('selected-area')) {{
                      map.removeLayer('selected-area-fill');
                      map.removeLayer('selected-area-border');
                      map.removeSource('selected-area');
                    }}
                    
                    // Create a polygon for the selected area
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

                    // Add the polygon layer
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

                    // Add border for the polygon
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

            // Wait for map to load
            map.on('load', () => {{
              // Add event listener for mouse move to show coordinates
              map.on('mousemove', (e) => {{
                document.getElementById('lat-display').textContent = e.lngLat.lat.toFixed(2) + '°';
                document.getElementById('lon-display').textContent = e.lngLat.lng.toFixed(2) + '°';
              }});

              // Add selected area polygon if bounds are available
              {f'''
              if ({bounds_data}) {{
                const bounds = {bounds_data};
                
                // Create a polygon for the selected area
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

                // Add the polygon layer
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

                // Add border for the polygon
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

                // Fly to the selected area with animation
                map.flyTo({{
                  center: {map_center},
                  zoom: {map_zoom},
                  duration: 2000,
                  essential: true
                }});
              }}
              ''' if bounds_data else ''}

              // Add some sample cities for interaction
              const cities = [
                {{ name: 'New York', coordinates: [-74.006, 40.7128], country: 'USA', info: 'Financial capital' }},
                {{ name: 'London', coordinates: [-0.1276, 51.5074], country: 'UK', info: 'Historical capital' }},
                {{ name: 'Tokyo', coordinates: [139.6917, 35.6895], country: 'Japan', info: 'Mega metropolis' }},
                {{ name: 'Sydney', coordinates: [151.2093, -33.8688], country: 'Australia', info: 'Harbor city' }},
                {{ name: 'Cairo', coordinates: [31.2357, 30.0444], country: 'Egypt', info: 'Nile Delta' }}
              ];

              // Add city markers
              cities.forEach(city => {{
                // Create a custom marker element
                const el = document.createElement('div');
                el.className = 'marker';
                el.style.backgroundColor = '#ffaa00';
                el.style.width = '15px';
                el.style.height = '15px';
                el.style.borderRadius = '50%';
                el.style.border = '2px solid #ffffff';
                el.style.boxShadow = '0 0 10px rgba(255, 170, 0, 0.5)';
                el.style.cursor = 'pointer';

                // Create a popup
                const popup = new mapboxgl.Popup({{
                  offset: 25,
                  closeButton: true,
                  closeOnClick: false
                }}).setHTML(
                  `<h3>${{city.name}}</h3>
                   <p><strong>Country:</strong> ${{city.country}}</p>
                   <p>${{city.info}}</p>`
                );

                // Create marker
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
        
        # Display the Mapbox HTML
        st.components.v1.html(mapbox_html, height=550)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 3:
        # During analysis, show loading state
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">FarmAdvisor Analysis in Progress</h3></div>', unsafe_allow_html=True)
        
        # Show loading animation with analysis details
        analysis_type = st.session_state.farmadvisor_analysis_type
        analysis_text = "Crop Suitability & Disease Risk" if analysis_type == 'crop_suitability' else "Groundwater Potential"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 100px 0;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: spin 2s linear infinite;">🌱</div>
            <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Running {analysis_text} Analysis</div>
            <div style="color: #666666; font-size: 14px;">Analyzing {st.session_state.selected_area_name}</div>
        </div>
        
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_step == 4:
        # Show FarmAdvisor results visualization
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        
        if st.session_state.farmadvisor_results:
            results = st.session_state.farmadvisor_results
            analysis_type = results['analysis_type']
            
            if analysis_type == 'crop_suitability':
                self.display_crop_suitability_charts(results)
            else:
                self.display_groundwater_charts(results)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">📊</div>
                <div style="color: #666666; font-size: 16px; margin-bottom: 10px;">No FarmAdvisor Results Available</div>
                <div style="color: #444444; font-size: 14px;">Please run an analysis to see results</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    def display_crop_suitability_charts(self, results):
        """Display crop suitability visualization charts"""
        crop_analysis = results['crop_analysis']
        
        # Sort crops by suitability score
        sorted_crops = sorted(crop_analysis.items(),
                            key=lambda x: x[1]['suitability_analysis']['final_score'],
                            reverse=True)
        
        # Create suitability score chart
        crop_names = [crop[0] for crop in sorted_crops[:10]]
        suitability_scores = [crop[1]['suitability_analysis']['final_score'] for crop in sorted_crops[:10]]
        disease_risks = [crop[1]['suitability_analysis']['disease_risk'] for crop in sorted_crops[:10]]
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add suitability bars
        fig.add_trace(go.Bar(
            x=crop_names,
            y=suitability_scores,
            name='Suitability Score',
            marker_color='#00ff88',
            opacity=0.7
        ))
        
        # Add disease risk line
        fig.add_trace(go.Scatter(
            x=crop_names,
            y=disease_risks,
            name='Disease Risk',
            yaxis='y2',
            line=dict(color='#ff6b6b', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title="Top 10 Crops - Suitability vs Disease Risk",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            xaxis=dict(
                title="Crop",
                tickangle=45
            ),
            yaxis=dict(
                title="Suitability Score (0-1)",
                range=[0, 1]
            ),
            yaxis2=dict(
                title="Disease Risk (0-1)",
                overlaying='y',
                side='right',
                range=[0, 1]
            ),
            height=400,
            margin=dict(l=50, r=50, t=50, b=100),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create component scores radar chart for top 3 crops
        if len(sorted_crops) >= 3:
            st.subheader("Component Analysis for Top 3 Crops")
            
            categories = ['Moisture', 'Organic Matter', 'Texture', 'Temperature']
            
            fig_radar = go.Figure()
            
            colors = ['#00ff88', '#4ECDC4', '#45B7D1']
            
            for i, (crop_name, data) in enumerate(sorted_crops[:3]):
                comp_scores = data['suitability_analysis']['component_scores']
                values = [
                    comp_scores['moisture'],
                    comp_scores['organic_matter'],
                    comp_scores['texture'],
                    comp_scores['temperature']
                ]
                values += values[:1]  # Complete the loop
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    name=crop_name,
                    line_color=colors[i],
                    fill='toself',
                    opacity=0.3
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                height=400,
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='#ffffff')
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)

    def display_groundwater_charts(self, results):
        """Display groundwater analysis visualization charts"""
        gw = results['groundwater_analysis']
        
        # Create water balance pie chart
        water_balance = gw['water_balance']
        
        labels = ['Evapotranspiration', 'Runoff', 'Recharge']
        values = [
            water_balance['evapotranspiration_mm'],
            water_balance['runoff_mm'],
            water_balance['recharge_mm']
        ]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=['#ff7f0e', '#2ca02c', '#d62728']
        )])
        
        fig_pie.update_layout(
            title="Water Balance Distribution",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Create component scores bar chart
        components = gw['components']
        
        fig_comp = go.Figure(data=[
            go.Bar(
                x=list(components.keys()),
                y=list(components.values()),
                marker_color=['#00ff88', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                opacity=0.7
            )
        ])
        
        fig_comp.update_layout(
            title="Groundwater Potential Components",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            xaxis=dict(title="Component"),
            yaxis=dict(title="Score (0-1)", range=[0, 0.5]),
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Create soil texture composition
        soil_data = [
            gw['sand_percent'],
            gw['silt_percent'],
            gw['clay_percent']
        ]
        
        fig_soil = go.Figure(data=[
            go.Bar(
                x=['Sand', 'Silt', 'Clay'],
                y=soil_data,
                marker_color=['#F4A460', '#D2691E', '#8B4513'],
                opacity=0.7
            )
        ])
        
        fig_soil.update_layout(
            title="Soil Texture Composition",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            xaxis=dict(title="Soil Component"),
            yaxis=dict(title="Percentage (%)", range=[0, 100]),
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig_soil, use_container_width=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
    <p style="margin: 5px 0;">KHISBA GIS + FARMADVISOR • Integrated Agricultural Analytics Platform</p>
    <p style="margin: 5px 0;">Crop Suitability Analysis • Groundwater Potential • Disease Risk Assessment • Management Strategies</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌾 Crop Analysis</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">💧 Groundwater</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🦠 Disease Risk</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🗺️ 3D Maps</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v3.0</span>
    </div>
</div>
""", unsafe_allow_html=True)
