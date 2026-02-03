import streamlit as st
import json
import tempfile
import os
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ee
import traceback

# Theme Configuration
THEMES = {
    "dark": {
        "name": "Dark (Default)",
        "primary": "#00ff88",
        "accent": "#00cc6a",
        "bg": "#000000",
        "card": "#0a0a0a",
        "secondary": "#111111",
        "border": "#222222",
        "text": "#ffffff",
        "text_secondary": "#999999",
        "text_light": "#cccccc",
        "success": "#00ff88",
        "warning": "#ffaa00",
        "error": "#ff4444",
        "plot_bg": "#0a0a0a",
        "plot_grid": "#222222"
    },
    "light": {
        "name": "Light",
        "primary": "#0066ff",
        "accent": "#0052cc",
        "bg": "#f8f9fa",
        "card": "#ffffff",
        "secondary": "#f1f3f5",
        "border": "#dee2e6",
        "text": "#212529",
        "text_secondary": "#6c757d",
        "text_light": "#495057",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "plot_bg": "#ffffff",
        "plot_grid": "#e9ecef"
    },
    "blue": {
        "name": "Blue",
        "primary": "#3b82f6",
        "accent": "#2563eb",
        "bg": "#0f172a",
        "card": "#1e293b",
        "secondary": "#334155",
        "border": "#475569",
        "text": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "text_light": "#cbd5e1",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "plot_bg": "#1e293b",
        "plot_grid": "#334155"
    },
    "red": {
        "name": "Red",
        "primary": "#ef4444",
        "accent": "#dc2626",
        "bg": "#0c0a09",
        "card": "#1c1917",
        "secondary": "#292524",
        "border": "#44403c",
        "text": "#fafaf9",
        "text_secondary": "#a8a29e",
        "text_light": "#d6d3d1",
        "success": "#22c55e",
        "warning": "#eab308",
        "error": "#ef4444",
        "plot_bg": "#1c1917",
        "plot_grid": "#292524"
    },
    "purple": {
        "name": "Purple",
        "primary": "#8b5cf6",
        "accent": "#7c3aed",
        "bg": "#1e1b4b",
        "card": "#312e81",
        "secondary": "#4338ca",
        "border": "#6366f1",
        "text": "#f5f3ff",
        "text_secondary": "#c4b5fd",
        "text_light": "#ddd6fe",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "plot_bg": "#312e81",
        "plot_grid": "#4338ca"
    },
    "green": {
        "name": "Green",
        "primary": "#10b981",
        "accent": "#059669",
        "bg": "#022c22",
        "card": "#064e3b",
        "secondary": "#065f46",
        "border": "#047857",
        "text": "#ecfdf5",
        "text_secondary": "#a7f3d0",
        "text_light": "#d1fae5",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "plot_bg": "#064e3b",
        "plot_grid": "#065f46"
    },
    "orange": {
        "name": "Orange",
        "primary": "#f97316",
        "accent": "#ea580c",
        "bg": "#1c1917",
        "card": "#292524",
        "secondary": "#44403c",
        "border": "#57534e",
        "text": "#fafaf9",
        "text_secondary": "#a8a29e",
        "text_light": "#d6d3d1",
        "success": "#22c55e",
        "warning": "#eab308",
        "error": "#ef4444",
        "plot_bg": "#292524",
        "plot_grid": "#44403c"
    },
    "teal": {
        "name": "Teal",
        "primary": "#14b8a6",
        "accent": "#0d9488",
        "bg": "#134e4a",
        "card": "#0f766e",
        "secondary": "#115e59",
        "border": "#0d9488",
        "text": "#f0fdfa",
        "text_secondary": "#99f6e4",
        "text_light": "#ccfbf1",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "plot_bg": "#0f766e",
        "plot_grid": "#115e59"
    }
}

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

# Function to generate CSS based on theme
def get_css_for_theme(theme_name):
    theme = THEMES[theme_name]
    
    return f"""
<style>
    /* Base styling */
    .stApp {{
        background: {theme['bg']};
        color: {theme['text']};
    }}
    
    /* Remove Streamlit default padding */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    
    /* Theme Variables */
    :root {{
        --primary-color: {theme['primary']};
        --accent-color: {theme['accent']};
        --bg-color: {theme['bg']};
        --card-color: {theme['card']};
        --secondary-color: {theme['secondary']};
        --border-color: {theme['border']};
        --text-color: {theme['text']};
        --text-secondary: {theme['text_secondary']};
        --text-light: {theme['text_light']};
        --success-color: {theme['success']};
        --warning-color: {theme['warning']};
        --error-color: {theme['error']};
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-color) !important;
    }}
    
    h1 {{
        font-size: 2rem !important;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
        color: var(--primary-color) !important;
    }}
    
    h3 {{
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Layout Container */
    .main-container {{
        display: flex;
        gap: 20px;
        max-width: 1800px;
        margin: 0 auto;
    }}
    
    .sidebar-container {{
        width: 320px;
        flex-shrink: 0;
    }}
    
    .content-container {{
        flex: 1;
        min-width: 0;
    }}
    
    /* Cards */
    .card {{
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }}
    
    .card:hover {{
        border-color: var(--primary-color);
    }}
    
    .card-title {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-color);
    }}
    
    .card-title .icon {{
        width: 32px;
        height: 32px;
        background: rgba(var(--primary-color-rgb, 0, 255, 136), 0.1);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-color);
        font-size: 16px;
    }}
    
    /* Buttons */
    .stButton > button {{
        width: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        color: {theme['bg'] if theme_name != 'light' else theme['text']} !important;
        border: none;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        margin: 5px 0;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(var(--primary-color-rgb, 0, 255, 136), 0.3);
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb, 0, 255, 136), 0.2) !important;
    }}
    
    /* Map container */
    .map-container {{
        border: 1px solid var(--border-color);
        border-radius: 10px;
        overflow: hidden;
        height: 600px;
    }}
    
    /* 3D Globe container */
    .globe-container {{
        border: 1px solid var(--border-color);
        border-radius: 10px;
        overflow: hidden;
        height: 600px;
        background: {theme['bg']};
        position: relative;
    }}
    
    /* Status badges */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        background: rgba(var(--primary-color-rgb, 0, 255, 136), 0.1);
        color: var(--primary-color);
        border: 1px solid rgba(var(--primary-color-rgb, 0, 255, 136), 0.3);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    /* Info panel */
    .info-panel {{
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
    }}
    
    .info-item {{
        margin-bottom: 10px;
    }}
    
    .info-label {{
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 2px;
    }}
    
    .info-value {{
        color: var(--text-color);
        font-size: 14px;
        font-weight: 500;
    }}
    
    /* View toggle */
    .view-toggle {{
        display: flex;
        background: var(--card-color);
        border-radius: 8px;
        padding: 4px;
        border: 1px solid var(--border-color);
        margin-bottom: 15px;
    }}
    
    .view-option {{
        flex: 1;
        padding: 8px 12px;
        text-align: center;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.2s;
        color: var(--text-secondary);
    }}
    
    .view-option.active {{
        background: var(--primary-color);
        color: var(--bg-color);
    }}
    
    /* Theme Selector */
    .theme-selector {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 8px;
        min-width: 180px;
    }}
    
    .theme-title {{
        color: var(--primary-color);
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .theme-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
    }}
    
    .theme-option {{
        width: 32px;
        height: 32px;
        border-radius: 6px;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }}
    
    .theme-option:hover {{
        transform: scale(1.1);
    }}
    
    .theme-option.active {{
        border-color: var(--text-color);
        box-shadow: 0 0 0 2px var(--primary-color);
    }}
    
    .theme-dot {{
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 10px;
    }}
    
    /* Plotly chart styling */
    .js-plotly-plot .plotly .modebar {{
        background: var(--card-color) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    .js-plotly-plot .plotly .modebar-btn path {{
        fill: var(--text-color) !important;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        background: var(--card-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    .dataframe th {{
        background: var(--secondary-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    .dataframe td {{
        background: var(--card-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--secondary-color);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--primary-color);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--accent-color);
    }}
</style>
"""

# Function to create theme selector
def theme_selector():
    with st.sidebar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🎨</div><h3 style="margin: 0;">Theme</h3></div>', unsafe_allow_html=True)
        
        # Create columns for theme selection
        cols = st.columns(2)
        theme_options = list(THEMES.keys())
        
        for idx, theme_key in enumerate(theme_options):
            theme = THEMES[theme_key]
            col_idx = idx % 2
            
            # Create a custom button with theme color
            button_style = f"""
            <style>
            .theme-btn-{theme_key} {{
                background: {theme['bg']} !important;
                border: 2px solid {theme['border']} !important;
                color: {theme['text']} !important;
                border-radius: 8px !important;
                padding: 10px !important;
                text-align: center !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                width: 100% !important;
            }}
            .theme-btn-{theme_key}:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            }}
            .theme-btn-{theme_key}.active {{
                border-color: {theme['primary']} !important;
                box-shadow: 0 0 0 2px {theme['primary']}20 !important;
            }}
            .theme-dot-{theme_key} {{
                width: 20px !important;
                height: 20px !important;
                border-radius: 50% !important;
                background: {theme['primary']} !important;
                display: inline-block !important;
                margin-right: 8px !important;
                vertical-align: middle !important;
            }}
            </style>
            """
            
            st.markdown(button_style, unsafe_allow_html=True)
            
            # Create button
            button_label = f'<span class="theme-dot-{theme_key}"></span> {theme["name"]}'
            is_active = "active" if st.session_state.theme == theme_key else ""
            
            if cols[col_idx].button(
                "", 
                key=f"theme_{theme_key}",
                on_click=lambda t=theme_key: setattr(st.session_state, 'theme', t)
            ):
                st.session_state.theme = theme_key
                st.rerun()
            
            # Add custom HTML for the button
            cols[col_idx].markdown(
                f'<div class="theme-btn-{theme_key} {is_active}">{button_label}</div>', 
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# Apply the selected theme CSS
st.markdown(get_css_for_theme(st.session_state.theme), unsafe_allow_html=True)

# Earth Engine Auto-Authentication with Service Account
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

# Try to auto-initialize Earth Engine on app start
if 'ee_auto_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_auto_initialized = True
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_auto_initialized = False
            st.session_state.ee_initialized = False

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
if 'ee_initialized' not in st.session_state:
    st.session_state.ee_initialized = False
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Set authenticated to True
st.session_state.authenticated = True

# Add theme selector to sidebar in a more prominent way
st.sidebar.markdown("""
<div style="padding: 10px 0; text-align: center;">
    <h3 style="color: var(--primary-color); margin: 0;">🎨 Theme</h3>
</div>
""", unsafe_allow_html=True)

# Theme selection buttons in sidebar
theme_cols = st.sidebar.columns(2)
theme_keys = list(THEMES.keys())

for i, theme_key in enumerate(theme_keys):
    theme = THEMES[theme_key]
    col_idx = i % 2
    
    # Create a colorful button for each theme
    if theme_cols[col_idx].button(
        theme["name"],
        key=f"theme_btn_{theme_key}",
        use_container_width=True,
        type="primary" if st.session_state.theme == theme_key else "secondary"
    ):
        st.session_state.theme = theme_key
        st.rerun()
    
    # Add a small color indicator
    theme_cols[col_idx].markdown(
        f'<div style="height: 4px; background: {theme["primary"]}; border-radius: 2px; margin-top: 2px;"></div>',
        unsafe_allow_html=True
    )

# Main Dashboard Layout with theme-aware colors
current_theme = THEMES[st.session_state.theme]

st.markdown(f"""
<div class="compact-header">
    <div>
        <h1>🌍 KHISBA GIS</h1>
        <p style="color: {current_theme['text_secondary']}; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation Analytics</p>
    </div>
    <div style="display: flex; gap: 10px;">
        <span class="status-badge">Connected</span>
        <span class="status-badge" style="background: rgba({int(current_theme['primary'][1:3], 16)}, {int(current_theme['primary'][3:5], 16)}, {int(current_theme['primary'][5:7], 16)}, 0.1); color: {current_theme['primary']};">Theme: {current_theme['name']}</span>
        <span class="status-badge">v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper Functions for Earth Engine (same as before)
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
        st.error(f"Error loading boundaries: {str(e)}")
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
        
    except Exception as e:
        st.error(f"Error extracting names: {str(e)}")
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
    except Exception as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return {'center': [0, 20], 'bounds': None, 'zoom': 2}

# Create main layout containers
col1, col2 = st.columns([0.25, 0.75], gap="large")

# LEFT SIDEBAR - All controls
with col1:
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="icon">🌍</div><h3 style="margin: 0;">Area Selection</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.ee_initialized:
        try:
            countries_fc = get_admin_boundaries(0)
            if countries_fc:
                country_names = get_boundary_names(countries_fc, 0)
                selected_country = st.selectbox(
                    "Country",
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
                        selected_admin1 = st.selectbox(
                            "State/Province",
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
                                selected_admin2 = st.selectbox(
                                    "Municipality",
                                    options=["Select municipality"] + admin2_names,
                                    index=0,
                                    help="Choose a municipality",
                                    key="admin2_select"
                                )
                            else:
                                selected_admin2 = None
                        else:
                            selected_admin2 = None
                    else:
                        selected_admin1 = None
                        selected_admin2 = None
                else:
                    selected_admin1 = None
                    selected_admin2 = None
            else:
                st.error("Failed to load countries. Please check Earth Engine connection.")
                selected_country = None
                selected_admin1 = None
                selected_admin2 = None
                
        except Exception as e:
            st.error(f"Error loading boundaries: {str(e)}")
            selected_country = None
            selected_admin1 = None
            selected_admin2 = None
    else:
        st.warning("Earth Engine not initialized")
        selected_country = None
        selected_admin1 = None
        selected_admin2 = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update selected geometry when area is selected
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
            
            st.session_state.selected_geometry = geometry
            st.session_state.selected_coordinates = coords_info
            st.session_state.selected_area_name = area_name
            st.session_state.selected_area_level = area_level
            
        except Exception as e:
            st.error(f"Error processing geometry: {str(e)}")
    
    # Analysis Parameters Card
    if selected_country and selected_country != "Select a country":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Analysis Settings</h3></div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2023, 1, 1),
                help="Start date for analysis",
                key="start_date"
            )
        with col_b:
            end_date = st.date_input(
                "End Date",
                value=datetime(2023, 12, 31),
                help="End date for analysis",
                key="end_date"
            )
        
        collection_choice = st.selectbox(
            "Satellite Source",
            options=["Sentinel-2", "Landsat-8"],
            help="Choose satellite collection",
            key="satellite_select"
        )
        
        cloud_cover = st.slider(
            "Max Cloud Cover (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Maximum cloud cover percentage",
            key="cloud_slider"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vegetation Indices Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🌿</div><h3 style="margin: 0;">Vegetation Indices</h3></div>', unsafe_allow_html=True)
        
        available_indices = [
            'NDVI', 'ARVI', 'ATSAVI', 'DVI', 'EVI', 'EVI2', 'GNDVI', 'MSAVI', 'MSI', 'MTVI', 'MTVI2',
            'NDTI', 'NDWI', 'OSAVI', 'RDVI', 'RI', 'RVI', 'SAVI', 'TVI', 'TSAVI', 'VARI', 'VIN', 'WDRVI',
            'GCVI', 'AWEI', 'MNDWI', 'WI', 'ANDWI', 'NDSI', 'nDDI', 'NBR', 'DBSI', 'SI', 'S3', 'BRI',
            'SSI', 'NDSI_Salinity', 'SRPI', 'MCARI', 'NDCI', 'PSSRb1', 'SIPI', 'PSRI', 'Chl_red_edge', 'MARI', 'NDMI'
        ]
        
        selected_indices = st.multiselect(
            "Select Indices",
            options=available_indices,
            default=['NDVI', 'EVI', 'SAVI', 'NDWI'],
            help="Choose vegetation indices to analyze",
            key="indices_select"
        )
        
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("Select All", use_container_width=True, key="select_all"):
                selected_indices = available_indices
                st.rerun()
        with col_d:
            if st.button("Clear All", use_container_width=True, key="clear_all"):
                selected_indices = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Run Analysis Button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True, key="run_analysis"):
            if not selected_indices:
                st.error("Please select at least one vegetation index")
            else:
                with st.spinner("Running analysis..."):
                    try:
                        if collection_choice == "Sentinel-2":
                            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                        else:
                            collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                        
                        filtered_collection = (collection
                            .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                            .filterBounds(st.session_state.selected_geometry.geometry())
                            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                        )
                        
                        try:
                            from vegetation_indices import mask_clouds, add_vegetation_indices
                            
                            if collection_choice == "Sentinel-2":
                                processed_collection = (filtered_collection
                                    .map(mask_clouds)
                                    .map(add_vegetation_indices)
                                )
                            else:
                                processed_collection = filtered_collection.map(add_vegetation_indices)
                            
                        except ImportError:
                            def simple_add_indices(image):
                                nir = image.select('B8')
                                red = image.select('B4')
                                green = image.select('B3')
                                blue = image.select('B2')
                                
                                ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
                                evi = nir.subtract(red).multiply(2.5).divide(
                                    nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
                                ).rename('EVI')
                                savi = nir.subtract(red).multiply(1.5).divide(
                                    nir.add(red).add(0.5)
                                ).rename('SAVI')
                                ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
                                
                                return image.addBands([ndvi, evi, savi, ndwi])
                            
                            processed_collection = filtered_collection.map(simple_add_indices)
                        
                        results = {}
                        for index in selected_indices:
                            try:
                                def add_date_and_reduce(image):
                                    reduced = image.select(index).reduceRegion(
                                        reducer=ee.Reducer.mean(),
                                        geometry=st.session_state.selected_geometry.geometry(),
                                        scale=30,
                                        maxPixels=1e9
                                    )
                                    return ee.Feature(None, reduced.set('date', image.date().format()))
                                
                                time_series = processed_collection.map(add_date_and_reduce)
                                time_series_list = time_series.getInfo()
                                
                                dates = []
                                values = []
                                
                                if 'features' in time_series_list:
                                    for feature in time_series_list['features']:
                                        props = feature['properties']
                                        if index in props and props[index] is not None and 'date' in props:
                                            dates.append(props['date'])
                                            values.append(props[index])
                                
                                results[index] = {'dates': dates, 'values': values}
                                
                            except Exception as e:
                                st.warning(f"Could not calculate {index}: {str(e)}")
                                results[index] = {'dates': [], 'values': []}
                        
                        st.session_state.analysis_results = results
                        st.success("✅ Analysis completed!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.error(f"Full error: {traceback.format_exc()}")

# MAIN CONTENT AREA - 3D Mapbox Globe
with col2:
    # 3D Mapbox Globe
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
    
    # Get current theme colors for the map
    current_theme = THEMES[st.session_state.theme]
    primary_color = current_theme['primary']
    card_color = current_theme['card']
    text_color = current_theme['text']
    text_secondary = current_theme['text_secondary']
    border_color = current_theme['border']
    bg_color = current_theme['bg']
    
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
          background: {bg_color};
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
          background: {card_color};
          color: {text_color};
          padding: 15px;
          border-radius: 8px;
          border: 1px solid {border_color};
          max-width: 250px;
          z-index: 1000;
          font-family: 'Inter', sans-serif;
          opacity: 0.95;
        }}
        .overlay-title {{
          color: {primary_color};
          font-weight: 600;
          margin-bottom: 10px;
          font-size: 14px;
        }}
        .overlay-text {{
          color: {text_secondary};
          font-size: 12px;
          line-height: 1.4;
        }}
        .coordinates-display {{
          position: absolute;
          bottom: 20px;
          left: 20px;
          background: {card_color};
          color: {text_color};
          padding: 10px 15px;
          border-radius: 6px;
          border: 1px solid {border_color};
          font-family: monospace;
          font-size: 12px;
          z-index: 1000;
          opacity: 0.9;
        }}
        .selected-area {{
          position: absolute;
          top: 20px;
          left: 20px;
          background: {card_color};
          color: {text_color};
          padding: 15px;
          border-radius: 8px;
          border: 1px solid {border_color};
          max-width: 300px;
          z-index: 1000;
          font-family: 'Inter', sans-serif;
          opacity: 0.95;
        }}
        .area-title {{
          color: {primary_color};
          font-weight: 600;
          margin-bottom: 10px;
          font-size: 14px;
        }}
        .area-details {{
          color: {text_secondary};
          font-size: 12px;
          line-height: 1.4;
        }}
        .layer-switcher {{
          position: absolute;
          top: 20px;
          right: 20px;
          background: {card_color};
          border: 1px solid {border_color};
          border-radius: 8px;
          overflow: hidden;
          z-index: 1000;
          opacity: 0.95;
        }}
        .layer-button {{
          display: block;
          width: 120px;
          padding: 10px;
          background: {card_color};
          color: {text_color};
          border: none;
          border-bottom: 1px solid {border_color};
          cursor: pointer;
          font-size: 12px;
          text-align: left;
          transition: all 0.2s;
        }}
        .layer-button:hover {{
          background: rgba(var(--primary-color-rgb, 0, 255, 136), 0.1);
        }}
        .layer-button.active {{
          background: {primary_color};
          color: {bg_color};
          font-weight: bold;
        }}
        .layer-button:last-child {{
          border-bottom: none;
        }}
        .mapboxgl-ctrl-group {{
          background: {card_color} !important;
          border: 1px solid {border_color} !important;
        }}
        .mapboxgl-ctrl button {{
          background-color: {card_color} !important;
          color: {text_color} !important;
        }}
        .mapboxgl-ctrl button:hover {{
          background-color: rgba(var(--primary-color-rgb, 0, 255, 136), 0.1) !important;
        }}
        .mapboxgl-popup-content {{
          background: {card_color} !important;
          color: {text_color} !important;
          border: 1px solid {border_color} !important;
          border-radius: 8px !important;
        }}
        .mapboxgl-popup-tip {{
          border-top-color: {card_color} !important;
          border-bottom-color: {card_color} !important;
        }}
        .marker {{
          background-color: {primary_color} !important;
          border: 2px solid {text_color} !important;
          box-shadow: 0 0 10px rgba(var(--primary-color-rgb, 0, 255, 136), 0.5) !important;
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
          • Selected area highlighted
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
          Status: <span style="color: {primary_color};">Ready for Analysis</span>
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
        map.addControl(new mapboxgl.ScaleControl({{
          unit: 'metric'
        }}));
        map.addControl(new mapboxgl.FullscreenControl());

        // Layer switcher functionality
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
                    'fill-color': '{primary_color}',
                    'fill-opacity': 0.2
                  }}
                }});

                map.addLayer({{
                  'id': 'selected-area-border',
                  'type': 'line',
                  'source': 'selected-area',
                  'layout': {{}},
                  'paint': {{
                    'line-color': '{primary_color}',
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
                'fill-color': '{primary_color}',
                'fill-opacity': 0.2
              }}
            }});

            map.addLayer({{
              'id': 'selected-area-border',
              'type': 'line',
              'source': 'selected-area',
              'layout': {{}},
              'paint': {{
                'line-color': '{primary_color}',
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

          // Add sample cities
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
            el.style.backgroundColor = '{primary_color}';
            el.style.width = '15px';
            el.style.height = '15px';
            el.style.borderRadius = '50%';
            el.style.border = '2px solid {text_color}';
            el.style.boxShadow = '0 0 10px {primary_color}80';
            el.style.cursor = 'pointer';

            const popup = new mapboxgl.Popup({{
              offset: 25,
              closeButton: true,
              closeOnClick: false
            }}).setHTML(
              `<h3 style="color: {primary_color}; margin: 0 0 10px 0;">${{city.name}}</h3>
               <p style="color: {text_secondary}; margin: 0 0 5px 0;"><strong>Country:</strong> ${{city.country}}</p>
               <p style="color: {text_secondary}; margin: 0;">${{city.info}}</p>`
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
    
    # Display the Mapbox HTML
    st.components.v1.html(mapbox_html, height=550)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis Results Section
    if st.session_state.analysis_results:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Results Header
        st.markdown('<div class="compact-header"><h3>Analysis Results</h3><span class="status-badge">Complete</span></div>', unsafe_allow_html=True)
        
        results = st.session_state.analysis_results
        
        # Summary Statistics
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Summary Statistics</h3></div>', unsafe_allow_html=True)
        
        summary_data = []
        for index, data in results.items():
            if data['values']:
                values = [v for v in data['values'] if v is not None]
                if values:
                    summary_data.append({
                        'Index': index,
                        'Mean': round(sum(values) / len(values), 4),
                        'Min': round(min(values), 4),
                        'Max': round(max(values), 4),
                        'Count': len(values)
                    })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts Section with theme-aware colors
        if results:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">📈</div><h3 style="margin: 0;">Vegetation Analytics</h3></div>', unsafe_allow_html=True)
            
            for index, data in results.items():
                if data['dates'] and data['values']:
                    try:
                        dates = []
                        for date_str in data['dates']:
                            try:
                                if 'T' in date_str:
                                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                else:
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                dates.append(date_obj)
                            except:
                                continue
                        
                        values = [v for v in data['values'] if v is not None]
                        
                        if dates and values and len(dates) == len(values):
                            df = pd.DataFrame({'Date': dates, 'Value': values})
                            df = df.sort_values('Date')
                            
                            # Get theme colors
                            current_theme = THEMES[st.session_state.theme]
                            primary_color = current_theme['primary']
                            plot_bg = current_theme['plot_bg']
                            plot_grid = current_theme['plot_grid']
                            text_color = current_theme['text']
                            
                            # Calculate if value is increasing or decreasing
                            current_value = df['Value'].iloc[-1] if len(df) > 0 else 0
                            prev_value = df['Value'].iloc[-2] if len(df) > 1 else current_value
                            is_increasing = current_value >= prev_value
                            
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=df['Date'], 
                                y=df['Value'],
                                mode='lines+markers',
                                name=f'{index} Index',
                                line=dict(color=primary_color if is_increasing else current_theme['error'], width=3),
                                marker=dict(
                                    size=6,
                                    color=primary_color if is_increasing else current_theme['error'],
                                    line=dict(width=1, color=text_color)
                                ),
                                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.4f}<extra></extra>'
                            ))
                            
                            if len(df) >= 5:
                                df['MA_5'] = df['Value'].rolling(window=min(5, len(df))).mean()
                                fig.add_trace(go.Scatter(
                                    x=df['Date'], 
                                    y=df['MA_5'],
                                    mode='lines',
                                    name='MA 5-day',
                                    line=dict(color=current_theme['warning'], width=2, dash='dot'),
                                    opacity=0.7
                                ))
                            
                            fig.update_layout(
                                title=f'{index} - Vegetation Analysis',
                                plot_bgcolor=plot_bg,
                                paper_bgcolor=plot_bg,
                                font=dict(color=text_color),
                                xaxis=dict(
                                    gridcolor=plot_grid,
                                    zerolinecolor=plot_grid,
                                    tickcolor=plot_grid,
                                    title_font_color=text_color,
                                    tickformat='%Y-%m-%d'
                                ),
                                yaxis=dict(
                                    gridcolor=plot_grid,
                                    zerolinecolor=plot_grid,
                                    tickcolor=plot_grid,
                                    title_font_color=text_color,
                                    title=f'{index} Value'
                                ),
                                legend=dict(
                                    bgcolor=f'{plot_bg}CC',
                                    bordercolor=current_theme['border'],
                                    borderwidth=1,
                                    x=0.01,
                                    y=0.99
                                ),
                                hovermode='x unified',
                                height=300,
                                margin=dict(t=50, b=50, l=50, r=50)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"Error creating chart for {index}: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Export Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">💾</div><h3 style="margin: 0;">Data Export</h3></div>', unsafe_allow_html=True)
        
        if st.button("📥 Download Results as CSV", type="primary", use_container_width=True, key="export_csv"):
            export_data = []
            for index, data in results.items():
                for date, value in zip(data['dates'], data['values']):
                    if value is not None:
                        export_data.append({
                            'Date': date,
                            'Index': index,
                            'Value': value
                        })
            
            if export_data:
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name=f"vegetation_indices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data available for export")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer with theme colors
current_theme = THEMES[st.session_state.theme]
st.markdown(f"""
<div class="section-divider"></div>
<div style="text-align: center; color: {current_theme['text_secondary']}; font-size: 12px; padding: 20px 0;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation Analytics Platform</p>
    <p style="margin: 5px 0;">Created by Taibi Farouk Djilali • Theme: {current_theme['name']}</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span class="status-badge">3D Mapbox</span>
        <span class="status-badge">Earth Engine</span>
        <span class="status-badge">Streamlit</span>
        <span class="status-badge">Plotly</span>
    </div>
</div>
""", unsafe_allow_html=True)
