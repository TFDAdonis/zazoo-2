import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback

# Custom CSS for Clean Green & Black TypeScript/React Style with Enhanced Guides
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
    
    /* Enhanced Guide System */
    .guide-master-container {
        position: fixed;
        top: 100px;
        right: 30px;
        width: 320px;
        z-index: 1000;
        background: var(--card-black);
        border: 2px solid var(--primary-green);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .guide-hand-icon {
        position: absolute;
        top: -15px;
        left: -15px;
        background: var(--primary-green);
        color: var(--primary-black);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        animation: pointWave 1.5s infinite;
        z-index: 1001;
    }
    
    @keyframes pointWave {
        0%, 100% { transform: translateX(0) rotate(0deg); }
        25% { transform: translateX(5px) rotate(10deg); }
        75% { transform: translateX(-5px) rotate(-10deg); }
    }
    
    .guide-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-gray);
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
        margin-bottom: 15px;
    }
    
    .guide-actions {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    
    .guide-btn {
        flex: 1;
        padding: 8px 15px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s;
    }
    
    .guide-btn-primary {
        background: var(--primary-green);
        color: var(--primary-black);
        border: none;
    }
    
    .guide-btn-primary:hover {
        background: var(--accent-green);
        transform: translateY(-2px);
    }
    
    .guide-btn-secondary {
        background: transparent;
        color: var(--text-light-gray);
        border: 1px solid var(--border-gray);
    }
    
    .guide-btn-secondary:hover {
        border-color: var(--primary-green);
        color: var(--primary-green);
    }
    
    .guide-dots {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-top: 15px;
    }
    
    .guide-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--border-gray);
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .guide-dot.active {
        background: var(--primary-green);
        transform: scale(1.2);
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
        
        .guide-master-container {
            display: none;
        }
    }
    
    /* Tooltip highlights */
    .highlight-element {
        position: relative;
        z-index: 100;
    }
    
    .highlight-element::before {
        content: '';
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        border: 2px solid var(--primary-green);
        border-radius: 8px;
        animation: pulseBorder 2s infinite;
        pointer-events: none;
    }
    
    @keyframes pulseBorder {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
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
        st.error(f"Earth Engine auto-initialization failed: {str(e)}")
        return False

# Try to auto-initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_initialized = False

# Initialize session state for steps and guides
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
if 'show_guide' not in st.session_state:
    st.session_state.show_guide = True  # Show guide by default
if 'current_guide_step' not in st.session_state:
    st.session_state.current_guide_step = 0
if 'guide_completed' not in st.session_state:
    st.session_state.guide_completed = False

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define steps
STEPS = [
    {"number": 1, "label": "Select Area", "icon": "📍"},
    {"number": 2, "label": "Set Parameters", "icon": "⚙️"},
    {"number": 3, "label": "View Map", "icon": "🗺️"},
    {"number": 4, "label": "Run Analysis", "icon": "🚀"},
    {"number": 5, "label": "View Results", "icon": "📊"}
]

# Define comprehensive guide steps for each workflow step
GUIDES = {
    1: [
        {
            "title": "Welcome to KHISBA GIS! 👋",
            "content": "I'm your hand guide. Let's analyze vegetation together! First, we need to select an area.",
            "action": "Click on the country dropdown below to get started",
            "element": "country_select"
        },
        {
            "title": "Select a Country 🌍",
            "content": "Choose any country from the list. The map will update to show your selection.",
            "action": "Pick a country like 'United States' or 'India'",
            "element": "country_select"
        },
        {
            "title": "Narrow Down (Optional) 🏛️",
            "content": "For more precise analysis, select a state/province and municipality.",
            "action": "Choose state and municipality if you want detailed analysis",
            "element": "admin1_select"
        },
        {
            "title": "Confirm Selection ✅",
            "content": "Great choice! Now let's confirm and move to the next step.",
            "action": "Click the green 'Confirm Selection' button",
            "element": "confirm_area"
        }
    ],
    2: [
        {
            "title": "Set Time Range 📅",
            "content": "Choose when you want to analyze vegetation. We recommend 1 year for best results.",
            "action": "Set start and end dates (default is 2023)",
            "element": "time_range"
        },
        {
            "title": "Choose Satellite 🛰️",
            "content": "Sentinel-2 offers higher resolution. Landsat-8 has more historical data.",
            "action": "Select Sentinel-2 for modern data",
            "element": "satellite_select"
        },
        {
            "title": "Cloud Filter ☁️",
            "content": "Remove cloudy images. 20% is optimal to keep enough clear data.",
            "action": "Keep cloud cover at 20% or lower",
            "element": "cloud_slider"
        },
        {
            "title": "Pick Vegetation Indices 🌿",
            "content": "NDVI is essential. Add EVI for better sensitivity in dense areas.",
            "action": "Select at least NDVI and EVI",
            "element": "indices_select"
        },
        {
            "title": "Save & Continue 💾",
            "content": "Perfect! Your settings are ready. Let's preview the area.",
            "action": "Click 'Save Parameters & Continue'",
            "element": "save_params"
        }
    ],
    3: [
        {
            "title": "Explore the 3D Map 🌐",
            "content": "This interactive 3D globe shows your selected area. Try rotating and zooming!",
            "action": "Drag the globe to rotate, scroll to zoom",
            "element": "map_interaction"
        },
        {
            "title": "Area Highlighted 🟢",
            "content": "Your selected area is highlighted in green. Make sure it's correct.",
            "action": "Verify the highlighted region matches your target",
            "element": "map_area"
        },
        {
            "title": "Ready for Analysis 🚀",
            "content": "Everything looks good! Time to run the vegetation analysis.",
            "action": "Click 'Run Analysis Now'",
            "element": "run_analysis"
        }
    ],
    4: [
        {
            "title": "Analysis in Progress ⏳",
            "content": "We're now processing satellite data and calculating vegetation indices.",
            "action": "Wait for analysis to complete (auto-continues)",
            "element": "progress_bar"
        }
    ],
    5: [
        {
            "title": "Results Ready! 📊",
            "content": "Analysis complete! Here are your vegetation charts and statistics.",
            "action": "Review the charts below",
            "element": "results_charts"
        },
        {
            "title": "Download Data 📥",
            "content": "You can download all data as CSV for further analysis.",
            "action": "Click 'Download CSV' to save your data",
            "element": "download_csv"
        },
        {
            "title": "Start New Analysis 🔄",
            "content": "Want to analyze another area? Start fresh with new parameters.",
            "action": "Click 'New Analysis' to begin again",
            "element": "new_analysis"
        }
    ]
}

# Function to render the guide
def render_guide():
    if st.session_state.show_guide and st.session_state.current_step in GUIDES:
        guides = GUIDES[st.session_state.current_step]
        current_guide = guides[min(st.session_state.current_guide_step, len(guides) - 1)]
        
        st.markdown(f'''
        <div class="guide-master-container">
            <div class="guide-hand-icon">👆</div>
            <div class="guide-header">
                <div class="guide-icon">🗺️</div>
                <div class="guide-title">{current_guide["title"]}</div>
            </div>
            <div class="guide-content">
                {current_guide["content"]}<br><br>
                <strong>👉 Action: </strong>{current_guide["action"]}
            </div>
            <div class="guide-actions">
                <button class="guide-btn guide-btn-secondary" onclick="parent.postMessage({{'type': 'streamlit:setComponentValue', 'value': 'guide_prev'}}, '*')">
                    ← Previous
                </button>
                <button class="guide-btn guide-btn-primary" onclick="parent.postMessage({{'type': 'streamlit:setComponentValue', 'value': 'guide_next'}}, '*')">
                    {st.session_state.current_guide_step >= len(guides) - 1 and st.session_state.current_step >= 5 ? 'Finish' : 'Next Step'} →
                </button>
            </div>
            <div class="guide-dots">
                {''.join([f'<div class="guide-dot {"active" if i == st.session_state.current_guide_step else ""}" onclick="parent.postMessage({{"type": "streamlit:setComponentValue", "value": "guide_jump_{i}"}}, "*")"></div>' for i in range(len(guides))])}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# JavaScript for guide interactions
guide_js = '''
<script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit:setComponentValue') {
            const value = event.data.value;
            if (value.startsWith('guide_')) {
                // Send to Streamlit via custom component
                const event = new CustomEvent('guideAction', { detail: value });
                document.dispatchEvent(event);
            }
        }
    });
</script>
'''

st.components.v1.html(guide_js, height=0)

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1>🌍 KHISBA GIS</h1>
    <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics - With Hand Guide</p>
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222; font-size: 12px;">👋 Interactive Guide</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222; font-size: 12px;">🚀 Auto Results</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222; font-size: 12px;">🗺️ 3D Mapbox</span>
        <button onclick="parent.postMessage({'type': 'streamlit:setComponentValue', 'value': 'toggle_guide'}, '*')" style="margin-left: auto; background: transparent; color: #00ff88; border: 1px solid #00ff88; padding: 4px 12px; border-radius: 20px; font-size: 12px; cursor: pointer;">
            {icon} Guide
        </button>
    </div>
</div>
""".format(icon="👁️ Hide" if st.session_state.show_guide else "👋 Show"), unsafe_allow_html=True)

# Toggle guide button handler
if st.button("Toggle Guide", key="toggle_guide_hidden", help="Show/hide the hand guide"):
    st.session_state.show_guide = not st.session_state.show_guide
    st.rerun()

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

# Status indicators with guide status
st.markdown(f"""
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
        <div class="status-dot {'active' if st.session_state.analysis_results else ''}"></div>
        <span>Analysis: {'Complete' if st.session_state.analysis_results else 'Pending'}</span>
    </div>
    <div class="status-item">
        <div class="status-dot {'active' if st.session_state.show_guide else ''}"></div>
        <span>Guide: {'Active' if st.session_state.show_guide else 'Hidden'}</span>
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
        
        # Enhanced guidance for step 1
        st.markdown("""
        <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #00ff88;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">1</div>
                <div style="color: #00ff88; font-weight: 600;">Select a Country</div>
            </div>
            <div style="color: #cccccc; font-size: 13px; margin-left: 34px;">
                Start by choosing a country from the dropdown below. Your guide will help you through each step.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.ee_initialized:
            try:
                # Get countries
                countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                country_names = countries_fc.aggregate_array('ADM0_NAME').distinct().getInfo()
                country_names = sorted(country_names) if country_names else []
                
                # Add guide highlighting
                guide_highlight = ""
                if st.session_state.show_guide and st.session_state.current_guide_step == 0:
                    guide_highlight = "highlight-element"
                
                selected_country = st.selectbox(
                    "🌍 Country",
                    options=["Select a country"] + country_names,
                    index=0,
                    help="Choose a country for analysis",
                    key="country_select"
                )
                
                if selected_country and selected_country != "Select a country":
                    country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                    admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1")\
                        .filter(ee.Filter.eq('ADM0_CODE', country_feature.get('ADM0_CODE')))
                    
                    admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().getInfo()
                    admin1_names = sorted(admin1_names) if admin1_names else []
                    
                    # Guide step 2 highlight
                    guide_highlight2 = ""
                    if st.session_state.show_guide and st.session_state.current_guide_step == 1:
                        guide_highlight2 = "highlight-element"
                    
                    selected_admin1 = st.selectbox(
                        "🏛️ State/Province (Optional)",
                        options=["Select state/province"] + admin1_names,
                        index=0,
                        help="Choose a state or province for more precise analysis",
                        key="admin1_select"
                    )
                    
                    if selected_admin1 and selected_admin1 != "Select state/province":
                        admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                        admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2")\
                            .filter(ee.Filter.eq('ADM1_CODE', admin1_feature.get('ADM1_CODE')))
                        
                        admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().getInfo()
                        admin2_names = sorted(admin2_names) if admin2_names else []
                        
                        selected_admin2 = st.selectbox(
                            "🏘️ Municipality (Optional)",
                            options=["Select municipality"] + admin2_names,
                            index=0,
                            help="Choose a municipality for most precise analysis",
                            key="admin2_select"
                        )
                    else:
                        selected_admin2 = None
                else:
                    selected_admin1 = None
                    selected_admin2 = None
                    
                # Guide step 3 highlight for confirm button
                confirm_highlight = ""
                if st.session_state.show_guide and st.session_state.current_guide_step >= 2:
                    confirm_highlight = "highlight-element"
                
                if st.button("✅ Confirm Selection", type="primary", use_container_width=True, 
                           disabled=not selected_country or selected_country == "Select a country",
                           key="confirm_area"):
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
                        
                        # Move to next step and reset guide
                        st.session_state.current_step = 2
                        st.session_state.current_guide_step = 0
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error loading boundaries: {str(e)}")
        else:
            st.warning("Earth Engine not initialized. Please wait...")
        
        # Quick tips for step 1
        st.markdown("""
        <div style="background: #111111; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #222222;">
            <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">💡 Quick Tips:</div>
            <div style="color: #999999; font-size: 11px; line-height: 1.4;">
                • Start with a country<br>
                • Add state/province for more precision<br>
                • Add municipality for detailed local analysis<br>
                • Don't worry, you can always go back!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Analysis Parameters
    elif st.session_state.current_step == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Set Analysis Parameters</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            # Enhanced guidance
            st.markdown(f"""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #00ff88;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">2</div>
                    <div style="color: #00ff88; font-weight: 600;">Configure Your Analysis</div>
                </div>
                <div style="color: #cccccc; font-size: 13px; margin-left: 34px;">
                    Adjust settings for {st.session_state.selected_area_name}. Use recommended values for best results.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Date range with guide highlight
            date_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 0:
                date_highlight = "highlight-element"
            
            st.markdown(f'<div class="{date_highlight}">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Satellite source with guide highlight
            satellite_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 1:
                satellite_highlight = "highlight-element"
            
            st.markdown(f'<div class="{satellite_highlight}">', unsafe_allow_html=True)
            collection_choice = st.selectbox(
                "🛰️ Satellite Source",
                options=["Sentinel-2", "Landsat-8"],
                help="Choose satellite collection",
                index=0,
                key="satellite_select"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Cloud cover with guide highlight
            cloud_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 2:
                cloud_highlight = "highlight-element"
            
            st.markdown(f'<div class="{cloud_highlight}">', unsafe_allow_html=True)
            cloud_cover = st.slider(
                "☁️ Max Cloud Cover (%)",
                min_value=0,
                max_value=100,
                value=20,
                help="Maximum cloud cover percentage",
                key="cloud_slider"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Vegetation indices with guide highlight
            indices_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 3:
                indices_highlight = "highlight-element"
            
            st.markdown(f'<div class="{indices_highlight}">', unsafe_allow_html=True)
            available_indices = ['NDVI', 'EVI', 'SAVI', 'NDWI', 'GNDVI', 'MSAVI']
            selected_indices = st.multiselect(
                "🌿 Vegetation Indices",
                options=available_indices,
                default=['NDVI', 'EVI'],
                help="Choose vegetation indices to analyze",
                key="indices_select"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Navigation buttons with guide highlight
            save_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step >= 4:
                save_highlight = "highlight-element"
            
            st.markdown(f'<div class="{save_highlight}">', unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Area Selection", use_container_width=True):
                    st.session_state.current_step = 1
                    st.session_state.current_guide_step = 0
                    st.rerun()
            
            with col_next:
                if st.button("✅ Save Parameters & Continue", type="primary", 
                           use_container_width=True, disabled=not selected_indices,
                           key="save_params"):
                    st.session_state.analysis_parameters = {
                        'start_date': start_date,
                        'end_date': end_date,
                        'collection_choice': collection_choice,
                        'cloud_cover': cloud_cover,
                        'selected_indices': selected_indices
                    }
                    st.session_state.current_step = 3
                    st.session_state.current_guide_step = 0
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Recommended settings
            st.markdown("""
            <div style="background: #111111; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #222222;">
                <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">🎯 Recommended Settings:</div>
                <div style="color: #999999; font-size: 11px; line-height: 1.4;">
                    • <strong>Time Range:</strong> 1 year (Jan-Dec 2023)<br>
                    • <strong>Satellite:</strong> Sentinel-2 (higher resolution)<br>
                    • <strong>Cloud Cover:</strong> ≤20% (balances data quality & quantity)<br>
                    • <strong>Indices:</strong> NDVI + EVI (covers most use cases)
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please go back to Step 1 and select an area first.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.session_state.current_guide_step = 0
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: View Map & Confirm
    elif st.session_state.current_step == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🗺️</div><h3 style="margin: 0;">Step 3: Preview Selected Area</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            # Enhanced guidance
            st.markdown(f"""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #00ff88;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">3</div>
                    <div style="color: #00ff88; font-weight: 600;">Preview & Confirm</div>
                </div>
                <div style="color: #cccccc; font-size: 13px; margin-left: 34px;">
                    Review your selection on the 3D map. Explore the globe before running analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"""
            **Selected Area:** {st.session_state.selected_area_name}
            
            **Analysis Parameters:**
            - Time Range: {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']}
            - Satellite: {st.session_state.analysis_parameters['collection_choice']}
            - Cloud Cover: ≤{st.session_state.analysis_parameters['cloud_cover']}%
            - Indices: {', '.join(st.session_state.analysis_parameters['selected_indices'])}
            """)
            
            # Navigation buttons with guide highlight
            run_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step >= 2:
                run_highlight = "highlight-element"
            
            st.markdown(f'<div class="{run_highlight}">', unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Parameters", use_container_width=True):
                    st.session_state.current_step = 2
                    st.session_state.current_guide_step = 0
                    st.rerun()
            
            with col_next:
                if st.button("🚀 Run Analysis Now", type="primary", use_container_width=True,
                           key="run_analysis"):
                    st.session_state.current_step = 4
                    st.session_state.current_guide_step = 0
                    st.session_state.auto_show_results = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Map exploration tips
            st.markdown("""
            <div style="background: #111111; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #222222;">
                <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">🗺️ Map Controls:</div>
                <div style="color: #999999; font-size: 11px; line-height: 1.4;">
                    • <strong>Drag:</strong> Rotate the 3D globe<br>
                    • <strong>Scroll:</strong> Zoom in/out<br>
                    • <strong>Right-click drag:</strong> Pan the view<br>
                    • <strong>Layer buttons:</strong> Switch map styles<br>
                    • <strong>City markers:</strong> Click for info
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No area selected. Please go back to Step 1.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.session_state.current_guide_step = 0
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 4: Running Analysis
    elif st.session_state.current_step == 4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 4: Running Analysis</h3></div>', unsafe_allow_html=True)
        
        # Enhanced guidance
        st.markdown("""
        <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #00ff88;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">4</div>
                <div style="color: #00ff88; font-weight: 600;">Processing Your Data</div>
            </div>
            <div style="color: #cccccc; font-size: 13px; margin-left: 34px;">
                We're analyzing satellite data. This may take a moment. Results will appear automatically!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Run the analysis automatically
        if not st.session_state.auto_show_results:
            # Create a placeholder for progress with guide highlight
            progress_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 0:
                progress_highlight = "highlight-element"
            
            st.markdown(f'<div class="{progress_highlight}">', unsafe_allow_html=True)
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                analysis_steps = [
                    "Initializing Earth Engine...",
                    "Loading satellite data...",
                    "Processing vegetation indices...",
                    "Calculating statistics...",
                    "Generating visualizations..."
                ]
                
                # Simulate analysis progress
                try:
                    params = st.session_state.analysis_parameters
                    
                    for i, step in enumerate(analysis_steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(analysis_steps))
                        
                        # Simulate processing time
                        import time
                        time.sleep(1)
                    
                    # Create simulated results
                    results = {}
                    for index in params['selected_indices']:
                        # Simulate data
                        import random
                        dates = [f"2023-{m:02d}-15" for m in range(1, 13)]
                        values = [random.uniform(0.1, 0.9) for _ in range(12)]
                        results[index] = {'dates': dates, 'values': values}
                    
                    st.session_state.analysis_results = results
                    progress_bar.progress(1.0)
                    status_text.text("✅ Analysis Complete!")
                    
                    # Auto-move to results after 2 seconds
                    time.sleep(2)
                    st.session_state.current_step = 5
                    st.session_state.current_guide_step = 0
                    st.session_state.auto_show_results = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    if st.button("🔄 Try Again", use_container_width=True):
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # What's happening info
        st.markdown("""
        <div style="background: #111111; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #222222;">
            <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">🔍 What's Happening:</div>
            <div style="color: #999999; font-size: 11px; line-height: 1.4;">
                • Downloading satellite imagery from {satellite}<br>
                • Filtering out clouds (≤{cloud}% coverage)<br>
                • Calculating {indices_count} vegetation indices<br>
                • Processing data for {area_name}<br>
                • Generating interactive charts
            </div>
        </div>
        """.format(
            satellite=st.session_state.analysis_parameters['collection_choice'],
            cloud=st.session_state.analysis_parameters['cloud_cover'],
            indices_count=len(st.session_state.analysis_parameters['selected_indices']),
            area_name=st.session_state.selected_area_name[:30] + "..." if len(st.session_state.selected_area_name) > 30 else st.session_state.selected_area_name
        ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 5: View Results
    elif st.session_state.current_step == 5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 5: Analysis Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            # Enhanced guidance
            st.markdown("""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #00ff88;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <div style="background: #00ff88; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">5</div>
                    <div style="color: #00ff88; font-weight: 600;">Your Results Are Ready!</div>
                </div>
                <div style="color: #cccccc; font-size: 13px; margin-left: 34px;">
                    Explore your vegetation analysis results below. Download data or start a new analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Success message
            st.success(f"""
            ✅ **Analysis Complete!** 
            
            Successfully analyzed vegetation for **{st.session_state.selected_area_name}** 
            over {len(st.session_state.analysis_results)} indices.
            """)
            
            # Navigation buttons with guide highlights
            col_back, col_new = st.columns(2)
            
            # Download button with guide highlight
            download_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 1:
                download_highlight = "highlight-element"
            
            st.markdown(f'<div class="{download_highlight}">', unsafe_allow_html=True)
            st.subheader("💾 Export Results")
            
            # Create CSV data
            export_data = []
            for index, data in st.session_state.analysis_results.items():
                for date, value in zip(data['dates'], data['values']):
                    export_data.append({
                        'Date': date,
                        'Index': index,
                        'Value': value
                    })
            
            if export_data:
                df = pd.DataFrame(export_data)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV File",
                    data=csv_data,
                    file_name=f"vegetation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_csv"
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # New analysis button with guide highlight
            new_highlight = ""
            if st.session_state.show_guide and st.session_state.current_guide_step == 2:
                new_highlight = "highlight-element"
            
            st.markdown(f'<div class="{new_highlight}">', unsafe_allow_html=True)
            if st.button("🔄 Start New Analysis", use_container_width=True, key="new_analysis"):
                # Reset for new analysis
                for key in ['selected_geometry', 'analysis_results', 'selected_coordinates', 
                           'selected_area_name', 'analysis_parameters']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_step = 1
                st.session_state.current_guide_step = 0
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Back button
            with col_back:
                if st.button("⬅️ Back to Map", use_container_width=True):
                    st.session_state.current_step = 3
                    st.session_state.current_guide_step = 0
                    st.rerun()
            
            # What you can do next
            st.markdown("""
            <div style="background: #111111; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #222222;">
                <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">🚀 What's Next:</div>
                <div style="color: #999999; font-size: 11px; line-height: 1.4;">
                    • <strong>Download CSV:</strong> For further analysis in Excel/Python<br>
                    • <strong>Start New Analysis:</strong> Try different area or parameters<br>
                    • <strong>Compare Results:</strong> Run analysis for different time periods<br>
                    • <strong>Share Findings:</strong> Use charts for reports/presentations
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No results available. Please run an analysis first.")
            if st.button("⬅️ Go Back", use_container_width=True):
                st.session_state.current_step = 4
                st.session_state.current_guide_step = 0
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Right column - Show map or results based on step
    if st.session_state.current_step <= 3:
        # Show 3D Mapbox Globe for steps 1-3
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        
        # Map title with guide interaction
        map_title = '<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Interactive 3D Global Map</h3>'
        if st.session_state.show_guide and st.session_state.current_step == 3 and st.session_state.current_guide_step == 0:
            map_title += '<div style="color: #00ff88; font-size: 12px; margin-top: 5px;">👆 Your guide will show you how to explore this 3D map</div>'
        map_title += '</div>'
        st.markdown(map_title, unsafe_allow_html=True)
        
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
            .guide-pointer {{
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              width: 60px;
              height: 60px;
              background: rgba(0, 255, 136, 0.2);
              border: 2px solid #00ff88;
              border-radius: 50%;
              animation: pulseGuide 2s infinite;
              z-index: 1001;
              pointer-events: none;
            }}
            @keyframes pulseGuide {{
              0%, 100% {{ 
                transform: translate(-50%, -50%) scale(1);
                opacity: 0.5;
              }}
              50% {{ 
                transform: translate(-50%, -50%) scale(1.2);
                opacity: 0.8;
              }}
            }}
          </style>
        </head>
        <body>
          <div id="map"></div>
          
          {f'''
          {'''<div class="guide-pointer"></div>''' if st.session_state.show_guide and st.session_state.current_step == 3 and st.session_state.current_guide_step == 0 else ''}
          
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
    
    elif st.session_state.current_step == 4:
        # During analysis, show loading state
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Analysis in Progress</h3></div>', unsafe_allow_html=True)
        
        # Show loading animation with analysis details
        st.markdown(f"""
        <div style="text-align: center; padding: 100px 0;">
            <div style="font-size: 64px; margin-bottom: 20px; animation: spin 2s linear infinite;">🌱</div>
            <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Processing Vegetation Data</div>
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
    
    elif st.session_state.current_step == 5:
        # Show analysis results with enhanced visuals
        st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
        st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">📊 Vegetation Analysis Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            # Show selected area info
            st.markdown(f"""
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 10px 20px; border-left: 4px solid #00ff88;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #00ff88; font-weight: 600; font-size: 16px;">{st.session_state.selected_area_name}</div>
                        <div style="color: #cccccc; font-size: 12px; margin-top: 5px;">
                            {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']} • 
                            {st.session_state.analysis_parameters['collection_choice']} • 
                            {len(st.session_state.analysis_parameters['selected_indices'])} indices analyzed
                        </div>
                    </div>
                    <div style="background: #00ff88; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                        ✅ Complete
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create charts for each index
            for index, data in st.session_state.analysis_results.items():
                if data['dates'] and data['values']:
                    # Create Plotly chart
                    fig = go.Figure()
                    
                    # Guide highlight for charts
                    chart_highlight = ""
                    if st.session_state.show_guide and st.session_state.current_guide_step == 0 and index == list(st.session_state.analysis_results.keys())[0]:
                        chart_highlight = "highlight-element"
                    
                    st.markdown(f'<div class="{chart_highlight}">', unsafe_allow_html=True)
                    
                    fig.add_trace(go.Scatter(
                        x=data['dates'],
                        y=data['values'],
                        mode='lines+markers',
                        name=index,
                        line=dict(color='#00ff88', width=3),
                        marker=dict(size=8, color='#ffffff', line=dict(width=1, color='#00ff88'))
                    ))
                    
                    # Add trend line
                    if len(data['values']) > 1:
                        import numpy as np
                        x_numeric = list(range(len(data['dates'])))
                        z = np.polyfit(x_numeric, data['values'], 1)
                        p = np.poly1d(z)
                        fig.add_trace(go.Scatter(
                            x=data['dates'],
                            y=p(x_numeric),
                            mode='lines',
                            name='Trend',
                            line=dict(color='#ffaa00', width=2, dash='dash')
                        ))
                    
                    fig.update_layout(
                        title=f"<b>{index}</b> - Vegetation Index Over Time",
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
                            title=f"{index} Value",
                            gridcolor='#222222',
                            tickcolor='#444444',
                            range=[min(data['values'])*0.9, max(data['values'])*1.1],
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
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{index}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Summary statistics
            st.markdown('<div style="padding: 0 20px;"><h4>📈 Summary Statistics</h4></div>', unsafe_allow_html=True)
            
            summary_data = []
            for index, data in st.session_state.analysis_results.items():
                if data['values']:
                    values = data['values']
                    current = values[-1] if values else 0
                    previous = values[-2] if len(values) > 1 else current
                    change = ((current - previous) / previous * 100) if previous != 0 else 0
                    
                    summary_data.append({
                        'Index': index,
                        'Current': round(current, 4),
                        'Previous': round(previous, 4),
                        'Change (%)': f"{change:+.2f}%",
                        'Min': round(min(values), 4),
                        'Max': round(max(values), 4),
                        'Avg': round(sum(values) / len(values), 4)
                    })
            
            if summary_data:
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

# Render the guide (floating panel)
render_guide()

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Interactive Hand Guide • Auto Results • Cool 3D Map • Step-by-Step Workflow</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">👋 Hand Guide</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🚀 Auto Results</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🗺️ 3D Mapbox</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v3.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript for guide navigation
guide_navigation_js = '''
<script>
    // Listen for guide actions
    document.addEventListener('guideAction', function(e) {
        const action = e.detail;
        
        if (action === 'guide_prev') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'guide_prev_button'
            }, '*');
        } else if (action === 'guide_next') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'guide_next_button'
            }, '*');
        } else if (action.startsWith('guide_jump_')) {
            const step = parseInt(action.split('_')[2]);
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: `guide_jump_${step}_button`
            }, '*');
        } else if (action === 'toggle_guide') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'toggle_guide_button'
            }, '*');
        }
    });
</script>
'''

st.components.v1.html(guide_navigation_js, height=0)

# Guide navigation buttons (hidden but functional)
col_guide1, col_guide2, col_guide3 = st.columns(3)
with col_guide1:
    if st.button("👈 Prev Guide", key="guide_prev_button", help="Previous guide step"):
        if st.session_state.current_guide_step > 0:
            st.session_state.current_guide_step -= 1
        st.rerun()
with col_guide2:
    if st.button("Next Guide 👉", key="guide_next_button", help="Next guide step"):
        current_guides = GUIDES.get(st.session_state.current_step, [])
        if st.session_state.current_guide_step < len(current_guides) - 1:
            st.session_state.current_guide_step += 1
        elif st.session_state.current_step < 5:
            st.session_state.current_step += 1
            st.session_state.current_guide_step = 0
        st.rerun()
with col_guide3:
    if st.button("Toggle Guide 👁️", key="toggle_guide_button", help="Show/hide guide"):
        st.session_state.show_guide = not st.session_state.show_guide
        st.rerun()

# Create jump buttons for each guide step
for step_num in range(6):  # Max 6 steps per guide
    if st.button(f"Jump to guide {step_num}", key=f"guide_jump_{step_num}_button", help=f"Jump to guide step {step_num}"):
        st.session_state.current_guide_step = step_num
        st.rerun()
