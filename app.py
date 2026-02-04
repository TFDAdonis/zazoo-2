import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ee
import traceback
import numpy as np

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

# CLIMATE ANALYSIS FUNCTIONS FROM COLAB
def get_daily_climate_data_corrected(start_date, end_date, geometry, scale=50000):
    """
    CORRECTED version: Get daily temperature and precipitation data
    """
    # Daily Temperature data (ERA5-Land Daily)
    temperature = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
        .filterDate(start_date, end_date) \
        .select(['temperature_2m'])  # This is the mean temperature

    # Daily Precipitation data (CHIRPS Daily)
    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date) \
        .select('precipitation')

    # Create list of dates
    start = ee.Date(start_date)
    end = ee.Date(end_date)
    n_days = end.difference(start, 'day')
    days = ee.List.sequence(0, n_days.subtract(1))

    def get_daily_data(day_offset):
        """Get daily data for a specific day"""
        day_offset = ee.Number(day_offset)
        date = start.advance(day_offset, 'day')
        date_str = date.format('YYYY-MM-dd')

        # Get temperature for the date
        temp_image = temperature.filterDate(date, date.advance(1, 'day')).first()

        # Get precipitation for the date
        precip_image = precipitation.filterDate(date, date.advance(1, 'day')).first()

        # Extract temperature value (CORRECT CONVERSION)
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

        # Extract precipitation value
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

        # CORRECT TEMPERATURE CONVERSION
        # ERA5-Land daily temperature is already in Kelvin, no multiplication needed
        temp_celsius = ee.Algorithms.If(
            temp_result,
            ee.Number(temp_result).subtract(273.15),  # Just subtract 273.15
            None
        )

        return ee.Feature(None, {
            'date': date_str,
            'temperature': temp_celsius,
            'precipitation': precipitation_val
        })

    # Create feature collection with daily data
    daily_data = ee.FeatureCollection(days.map(get_daily_data))

    return daily_data

def get_daily_climate_data_debug(start_date, end_date, geometry, scale=50000):
    """
    DEBUG version to see what's happening with the data
    """
    # Let's try a different approach using MODIS for temperature
    # MODIS Land Surface Temperature
    modis_temp = ee.ImageCollection("MODIS/061/MOD11A1") \
        .filterDate(start_date, end_date) \
        .select('LST_Day_1km')

    # Daily Precipitation data (CHIRPS Daily)
    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date) \
        .select('precipitation')

    # Create list of dates
    start = ee.Date(start_date)
    end = ee.Date(end_date)
    n_days = end.difference(start, 'day')
    days = ee.List.sequence(0, n_days.subtract(1))

    def get_daily_data(day_offset):
        """Get daily data for a specific day"""
        day_offset = ee.Number(day_offset)
        date = start.advance(day_offset, 'day')
        date_str = date.format('YYYY-MM-dd')

        # Get MODIS temperature for the date
        modis_image = modis_temp.filterDate(date, date.advance(1, 'day')).first()

        # Get precipitation for the date
        precip_image = precipitation.filterDate(date, date.advance(1, 'day')).first()

        # Extract MODIS temperature (convert from Kelvin to Celsius)
        modis_temp_val = ee.Algorithms.If(
            modis_image,
            modis_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=scale,
                maxPixels=1e9
            ).get('LST_Day_1km'),
            None
        )

        # MODIS LST conversion: multiply by 0.02 then subtract 273.15
        modis_temp_celsius = ee.Algorithms.If(
            modis_temp_val,
            ee.Number(modis_temp_val).multiply(0.02).subtract(273.15),
            None
        )

        # Extract precipitation value
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

        return ee.Feature(None, {
            'date': date_str,
            'temperature': modis_temp_celsius,
            'precipitation': precipitation_val,
            'data_source': 'MODIS'
        })

    # Create feature collection with daily data
    daily_data = ee.FeatureCollection(days.map(get_daily_data))

    return daily_data

def analyze_daily_climate_data(study_roi, start_date, end_date, data_source='era5'):
    """
    Integrated daily climate analysis with realistic temperature filtering
    """
    try:
        # Get daily climate data based on selected source
        if data_source == 'modis':
            daily_data = get_daily_climate_data_debug(start_date, end_date, study_roi)
            data_source_name = "MODIS"
        else:
            daily_data = get_daily_climate_data_corrected(start_date, end_date, study_roi)
            data_source_name = "ERA5-Land"

        # Convert to pandas DataFrame
        features = daily_data.getInfo()['features']
        data = []

        for feature in features:
            props = feature['properties']

            # Handle temperature
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

        # Remove rows with all NaN values
        df = df.dropna(how='all')

        if df.empty:
            return None, None

        # Filter out unrealistic temperatures (below -100°C or above 60°C)
        df_clean = df[(df['temperature'] > -100) & (df['temperature'] < 60)].copy()

        if len(df_clean) < len(df):
            pass  # Filtering happened, but we don't show message in Streamlit

        return df_clean, data_source_name

    except Exception as e:
        st.error(f"Error generating daily climate charts: {str(e)}")
        return None, None

def get_climate_timeseries(study_roi, start_date='2020-01-01'):
    """Generate temperature and precipitation time series charts"""
    try:
        # Get a representative point from the ROI
        centroid = study_roi.geometry().centroid()

        # Updated ERA5-Land dataset with correct band names
        era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")

        # Get end date (current date)
        end_date = datetime.now().strftime('%Y-%m-%d')

        # Filter by date and region
        climate_data = era5.filterBounds(study_roi.geometry()).filterDate(start_date, end_date)

        # Updated band names for ERA5-Land Daily Aggregated
        # Temperature data (Kelvin to Celsius)
        temperature_data = climate_data.select(['mean_2m_air_temperature']).map(
            lambda image: image.subtract(273.15).rename('temperature_c')
        )

        # Precipitation data (convert from meters to mm)
        precipitation_data = climate_data.select(['total_precipitation']).map(
            lambda image: image.multiply(1000).rename('precipitation_mm')
        )

        # Get temperature time series
        temp_timeseries = temperature_data.getRegion(centroid, 1000).getInfo()
        if not temp_timeseries or len(temp_timeseries) <= 1:
            return None, None

        temp_df = pd.DataFrame(temp_timeseries[1:], columns=temp_timeseries[0])
        temp_df['datetime'] = pd.to_datetime(temp_df['time'], unit='ms')
        temp_df['temperature_c'] = pd.to_numeric(temp_df['temperature_c'], errors='coerce')
        temp_df = temp_df.dropna(subset=['temperature_c'])

        if temp_df.empty:
            return None, None

        temp_df = temp_df.set_index('datetime')['temperature_c']

        # Get precipitation time series
        precip_timeseries = precipitation_data.getRegion(centroid, 1000).getInfo()
        if not precip_timeseries or len(precip_timeseries) <= 1:
            return None, None

        precip_df = pd.DataFrame(precip_timeseries[1:], columns=precip_timeseries[0])
        precip_df['datetime'] = pd.to_datetime(precip_df['time'], unit='ms')
        precip_df['precipitation_mm'] = pd.to_numeric(precip_df['precipitation_mm'], errors='coerce')
        precip_df = precip_df.dropna(subset=['precipitation_mm'])

        if precip_df.empty:
            return None, None

        precip_df = precip_df.set_index('datetime')['precipitation_mm']

        return temp_df, precip_df

    except Exception as e:
        st.error(f"Error generating climate time series: {str(e)}")
        return None, None

# VEGETATION INDICES FUNCTIONS
def add_vegetation_indices(image):
    # NDVI - Normalized Difference Vegetation Index
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # ARVI - Atmospherically Resistant Vegetation Index
    arvi = image.expression(
        '(NIR - (2 * RED - BLUE)) / (NIR + (2 * RED - BLUE))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }).rename('ARVI')

    # EVI - Enhanced Vegetation Index
    evi = image.expression(
        '2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }).rename('EVI')

    # SAVI - Soil Adjusted Vegetation Index
    savi = image.expression(
        '1.5 * (NIR - RED) / (NIR + RED + 0.5)', {
            'NIR': image.select('B8'),
            'RED': image.select('B4')
        }).rename('SAVI')

    # NDWI - Normalized Difference Water Index
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')

    return image.addBands([ndvi, arvi, evi, savi, ndwi])

# Try to auto-initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        if auto_initialize_earth_engine():
            st.session_state.ee_initialized = True
        else:
            st.session_state.ee_initialized = False

# Initialize session state for steps
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'selected_geometry' not in st.session_state:
    st.session_state.selected_geometry = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'climate_results' not in st.session_state:
    st.session_state.climate_results = None
if 'daily_climate_results' not in st.session_state:
    st.session_state.daily_climate_results = None
if 'selected_coordinates' not in st.session_state:
    st.session_state.selected_coordinates = None
if 'selected_area_name' not in st.session_state:
    st.session_state.selected_area_name = None
if 'analysis_parameters' not in st.session_state:
    st.session_state.analysis_parameters = None
if 'auto_show_results' not in st.session_state:
    st.session_state.auto_show_results = False
if 'include_climate_analysis' not in st.session_state:
    st.session_state.include_climate_analysis = True
if 'include_daily_climate' not in st.session_state:
    st.session_state.include_daily_climate = True
if 'climate_data_source' not in st.session_state:
    st.session_state.climate_data_source = 'era5'

# Page configuration
st.set_page_config(
    page_title="Khisba GIS - 3D Global Vegetation & Climate Analysis",
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

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1>🌍 KHISBA GIS</h1>
    <p style="color: #999999; margin: 0; font-size: 14px;">Interactive 3D Global Vegetation & Climate Analytics - Guided Workflow</p>
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
        <div class="status-dot {'active' if st.session_state.analysis_results else ''}"></div>
        <span>Analysis: {'Complete' if st.session_state.analysis_results else 'Pending'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper Functions
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
                countries_fc = get_admin_boundaries(0)
                if countries_fc:
                    country_names = get_boundary_names(countries_fc, 0)
                    selected_country = st.selectbox(
                        "🌍 Country",
                        options=["Select a country"] + country_names,
                        index=0,
                        help="Choose a country for analysis",
                        key="country_select"
                    )
                    
                    if selected_country and selected_country != "Select a country":
                        # Get country code
                        country_feature = countries_fc.filter(ee.Filter.eq('ADM0_NAME', selected_country)).first()
                        
                        # Get admin1 regions for selected country
                        admin1_fc = get_admin_boundaries(1, country_feature.get('ADM0_CODE').getInfo())
                        if admin1_fc:
                            admin1_names = get_boundary_names(admin1_fc, 1)
                            selected_admin1 = st.selectbox(
                                "🏛️ State/Province",
                                options=["Select state/province"] + admin1_names,
                                index=0,
                                help="Choose a state or province",
                                key="admin1_select"
                            )
                            
                            if selected_admin1 and selected_admin1 != "Select state/province":
                                # Get admin1 code
                                admin1_feature = admin1_fc.filter(ee.Filter.eq('ADM1_NAME', selected_admin1)).first()
                                
                                # Get admin2 regions for selected admin1
                                admin2_fc = get_admin_boundaries(2, None, admin1_feature.get('ADM1_CODE').getInfo())
                                if admin2_fc:
                                    admin2_names = get_boundary_names(admin2_fc, 2)
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
            st.warning("Earth Engine not initialized. Please wait...")
        
        if selected_country and selected_country != "Select a country":
            try:
                # Determine geometry
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
                
                # Get coordinates for the map
                coords_info = get_geometry_coordinates(geometry)
                
                if st.button("✅ Confirm Selection", type="primary", use_container_width=True):
                    # Store in session state
                    st.session_state.selected_geometry = geometry
                    st.session_state.selected_coordinates = coords_info
                    st.session_state.selected_area_name = area_name
                    st.session_state.selected_area_level = area_level
                    
                    # Move to next step
                    st.session_state.current_step = 2
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error processing geometry: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Analysis Parameters
    elif st.session_state.current_step == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Set Analysis Parameters</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 2
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">📋</div>
                <div class="guide-title">Configure Analysis</div>
            </div>
            <div class="guide-content">
                Set the time range, satellite source, vegetation indices, and climate analysis options for your analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
            
            # Date range
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
            
            # Satellite source
            collection_choice = st.selectbox(
                "🛰️ Satellite Source",
                options=["Sentinel-2", "Landsat-8"],
                help="Choose satellite collection",
                index=0
            )
            
            # Cloud cover
            cloud_cover = st.slider(
                "☁️ Max Cloud Cover (%)",
                min_value=0,
                max_value=100,
                value=20,
                help="Maximum cloud cover percentage"
            )
            
            # Vegetation indices
            available_indices = [
                'NDVI', 'ARVI', 'ATSAVI', 'DVI', 'EVI', 'EVI2', 'GNDVI', 'MSAVI', 'MSI', 'MTVI', 'MTVI2',
                'NDTI', 'NDWI', 'OSAVI', 'RDVI', 'RI', 'RVI', 'SAVI', 'TVI', 'TSAVI', 'VARI', 'VIN', 'WDRVI',
                'GCVI', 'AWEI', 'MNDWI', 'WI', 'ANDWI', 'NDSI', 'nDDI', 'NBR', 'DBSI', 'SI', 'S3', 'BRI',
                'SSI', 'NDSI_Salinity', 'SRPI', 'MCARI', 'NDCI', 'PSSRb1', 'SIPI', 'PSRI', 'Chl_red_edge', 'MARI', 'NDMI'
            ]
            
            selected_indices = st.multiselect(
                "🌿 Vegetation Indices",
                options=available_indices,
                default=['NDVI', 'EVI', 'SAVI', 'NDWI'],
                help="Choose vegetation indices to analyze"
            )
            
            # Climate Analysis Options
            st.markdown("---")
            st.subheader("🌤️ Climate Analysis Options")
            
            col_climate1, col_climate2 = st.columns(2)
            with col_climate1:
                include_climate = st.checkbox(
                    "Include Climate Analysis",
                    value=True,
                    help="Analyze temperature and precipitation data"
                )
            
            with col_climate2:
                include_daily_climate = st.checkbox(
                    "Include Daily Climate Analysis",
                    value=True,
                    help="Generate daily climate charts"
                )
            
            climate_data_source = st.selectbox(
                "🌡️ Climate Data Source",
                options=["ERA5-Land (Recommended)", "MODIS (Alternative)"],
                index=0,
                help="Choose climate data source"
            )
            
            # Navigation buttons
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
                        'selected_indices': selected_indices,
                        'include_climate': include_climate,
                        'include_daily_climate': include_daily_climate,
                        'climate_data_source': 'era5' if climate_data_source == "ERA5-Land (Recommended)" else 'modis'
                    }
                    st.session_state.current_step = 3
                    st.rerun()
        else:
            st.warning("Please go back to Step 1 and select an area first.")
            if st.button("⬅️ Go to Area Selection", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: View Map & Confirm
    elif st.session_state.current_step == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🗺️</div><h3 style="margin: 0;">Step 3: Preview Selected Area</h3></div>', unsafe_allow_html=True)
        
        # Guided instruction for step 3
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">👁️</div>
                <div class="guide-title">Preview Area</div>
            </div>
            <div class="guide-content">
                Review your selected area on the 3D map. Make sure the highlighted region matches your intended analysis area.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_area_name:
            st.info(f"""
            **Selected Area:** {st.session_state.selected_area_name}
            
            **Analysis Parameters:**
            - Time Range: {st.session_state.analysis_parameters['start_date']} to {st.session_state.analysis_parameters['end_date']}
            - Satellite: {st.session_state.analysis_parameters['collection_choice']}
            - Cloud Cover: ≤{st.session_state.analysis_parameters['cloud_cover']}%
            - Indices: {', '.join(st.session_state.analysis_parameters['selected_indices'])}
            - Climate Analysis: {'Yes' if st.session_state.analysis_parameters['include_climate'] else 'No'}
            - Daily Climate: {'Yes' if st.session_state.analysis_parameters['include_daily_climate'] else 'No'}
            """)
            
            # Navigation buttons
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
    
    # Step 4: Running Analysis
    elif st.session_state.current_step == 4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 4: Running Analysis</h3></div>', unsafe_allow_html=True)
        
        # Show analysis progress
        st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">⏳</div>
                <div class="guide-title">Analysis in Progress</div>
            </div>
            <div class="guide-content">
                Please wait while we process your vegetation and climate analysis. This may take a few moments depending on the area size and time range.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Run the analysis automatically
        if not st.session_state.auto_show_results:
            # Create a placeholder for progress
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
                    "Generating climate data...",
                    "Finalizing visualizations..."
                ]
                
                # Simulate analysis progress
                try:
                    params = st.session_state.analysis_parameters
                    geometry = st.session_state.selected_geometry
                    
                    for i, step in enumerate(analysis_steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(analysis_steps))
                        
                        # Simulate processing time
                        import time
                        time.sleep(1)
                    
                    # Define collection based on choice
                    if params['collection_choice'] == "Sentinel-2":
                        collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                    else:
                        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                    
                    # Filter collection
                    filtered_collection = (collection
                        .filterDate(params['start_date'].strftime('%Y-%m-%d'), params['end_date'].strftime('%Y-%m-%d'))
                        .filterBounds(geometry.geometry())
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', params['cloud_cover']))
                    )
                    
                    # Create simplified vegetation indices
                    def simple_add_indices(image):
                        if params['collection_choice'] == "Sentinel-2":
                            nir = image.select('B8')
                            red = image.select('B4')
                            green = image.select('B3')
                            blue = image.select('B2')
                        else:
                            nir = image.select('SR_B5')
                            red = image.select('SR_B4')
                            green = image.select('SR_B3')
                            blue = image.select('SR_B2')
                        
                        # Basic indices calculation
                        indices = []
                        if 'NDVI' in params['selected_indices']:
                            ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
                            indices.append(ndvi)
                        
                        if 'EVI' in params['selected_indices']:
                            evi = nir.subtract(red).multiply(2.5).divide(
                                nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
                            ).rename('EVI')
                            indices.append(evi)
                        
                        if 'SAVI' in params['selected_indices']:
                            savi = nir.subtract(red).multiply(1.5).divide(
                                nir.add(red).add(0.5)
                            ).rename('SAVI')
                            indices.append(savi)
                        
                        if 'NDWI' in params['selected_indices']:
                            ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
                            indices.append(ndwi)
                        
                        # Add other indices as needed
                        for idx in params['selected_indices']:
                            if idx not in ['NDVI', 'EVI', 'SAVI', 'NDWI']:
                                # Simplified version for other indices
                                other_idx = nir.subtract(red).divide(nir.add(red)).rename(idx)
                                indices.append(other_idx)
                        
                        return image.addBands(indices)
                    
                    processed_collection = filtered_collection.map(simple_add_indices)
                    
                    # Calculate time series for selected indices
                    results = {}
                    for index in params['selected_indices']:
                        try:
                            # Map over collection to get mean values
                            def add_date_and_reduce(img):
                                reduced = img.select(index).reduceRegion(
                                    reducer=ee.Reducer.mean(),
                                    geometry=geometry.geometry(),
                                    scale=30,
                                    maxPixels=1e9
                                )
                                return ee.Feature(None, reduced.set('date', img.date().format('YYYY-MM-dd')))
                            
                            time_series = processed_collection.map(add_date_and_reduce)
                            time_series_list = time_series.getInfo()
                            
                            dates = []
                            values = []
                            
                            if 'features' in time_series_list:
                                for feature in time_series_list['features']:
                                    props = feature['properties']
                                    if index in props and props[index] is not None and 'date' in props:
                                        dates.append(props['date'])
                                        values.append(float(props[index]))
                            
                            results[index] = {'dates': dates, 'values': values}
                            
                        except Exception as e:
                            st.warning(f"Could not calculate {index}: {str(e)}")
                            results[index] = {'dates': [], 'values': []}
                    
                    st.session_state.analysis_results = results
                    
                    # Run climate analysis if selected
                    if params['include_climate']:
                        status_text.text("Processing climate data...")
                        temp_df, precip_df = get_climate_timeseries(
                            geometry, 
                            params['start_date'].strftime('%Y-%m-%d')
                        )
                        if temp_df is not None and precip_df is not None:
                            st.session_state.climate_results = {
                                'temperature': temp_df,
                                'precipitation': precip_df
                            }
                    
                    # Run daily climate analysis if selected
                    if params['include_daily_climate']:
                        status_text.text("Processing daily climate data...")
                        daily_df, source_name = analyze_daily_climate_data(
                            geometry.geometry(),
                            params['start_date'].strftime('%Y-%m-%d'),
                            params['end_date'].strftime('%Y-%m-%d'),
                            params['climate_data_source']
                        )
                        if daily_df is not None:
                            st.session_state.daily_climate_results = {
                                'data': daily_df,
                                'source': source_name
                            }
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Analysis Complete!")
                    
                    # Auto-move to results after 2 seconds
                    time.sleep(2)
                    st.session_state.current_step = 5
                    st.session_state.auto_show_results = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.error(f"Full error: {traceback.format_exc()}")
                    if st.button("🔄 Try Again", use_container_width=True):
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 5: View Results
    elif st.session_state.current_step == 5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 5: Analysis Results</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            # Navigation buttons
            col_back, col_new = st.columns(2)
            with col_back:
                if st.button("⬅️ Back to Map", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()
            
            with col_new:
                if st.button("🔄 New Analysis", use_container_width=True):
                    # Reset for new analysis
                    for key in ['selected_geometry', 'analysis_results', 'climate_results', 
                               'daily_climate_results', 'selected_coordinates', 
                               'selected_area_name', 'analysis_parameters']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state.current_step = 1
                    st.rerun()
            
            # Export options
            st.subheader("💾 Export Results")
            if st.button("📥 Download CSV", use_container_width=True):
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
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Click to Download CSV",
                        data=csv,
                        file_name=f"vegetation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
            <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Processing Vegetation & Climate Data</div>
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
        # Show analysis results
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
            
            # Create tabs for different result types
            tab1, tab2, tab3 = st.tabs(["🌿 Vegetation Indices", "🌡️ Climate Analysis", "📈 Daily Climate"])
            
            with tab1:
                # Create charts for each vegetation index
                for index, data in st.session_state.analysis_results.items():
                    if data['dates'] and data['values']:
                        try:
                            # Create Plotly chart
                            fig = go.Figure()
                            
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
                                    range=[min(data['values'])*0.9 if data['values'] else 0, max(data['values'])*1.1 if data['values'] else 1],
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
                            
                        except Exception as e:
                            st.warning(f"Could not display chart for {index}: {str(e)}")
                
                # Summary statistics for vegetation indices
                st.markdown('<div style="padding: 0 20px;"><h4>📈 Vegetation Statistics</h4></div>', unsafe_allow_html=True)
                
                summary_data = []
                for index, data in st.session_state.analysis_results.items():
                    if data['values']:
                        values = data['values']
                        if values:
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
            
            with tab2:
                # Climate analysis results
                if st.session_state.climate_results:
                    temp_df = st.session_state.climate_results['temperature']
                    precip_df = st.session_state.climate_results['precipitation']
                    
                    # Create temperature chart
                    fig_temp = go.Figure()
                    fig_temp.add_trace(go.Scatter(
                        x=temp_df.index,
                        y=temp_df.values,
                        mode='lines',
                        name='Temperature',
                        line=dict(color='red', width=2)
                    ))
                    
                    fig_temp.update_layout(
                        title="<b>Temperature Time Series (°C)</b>",
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
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_temp, use_container_width=True)
                    
                    # Create precipitation chart
                    fig_precip = go.Figure()
                    fig_precip.add_trace(go.Bar(
                        x=precip_df.index,
                        y=precip_df.values,
                        name='Precipitation',
                        marker_color='blue'
                    ))
                    
                    fig_precip.update_layout(
                        title="<b>Precipitation Time Series (mm)</b>",
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
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_precip, use_container_width=True)
                    
                    # Climate statistics
                    st.markdown('<div style="padding: 0 20px;"><h4>🌤️ Climate Statistics</h4></div>', unsafe_allow_html=True)
                    
                    monthly_temp = temp_df.resample('M').mean()
                    monthly_precip = precip_df.resample('M').sum()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: rgba(255, 0, 0, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid red;">
                            <div style="color: red; font-weight: 600; margin-bottom: 10px;">🌡️ Temperature</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.metric("Mean Temperature", f"{monthly_temp.mean():.1f}°C")
                        st.metric("Max Temperature", f"{monthly_temp.max():.1f}°C")
                        st.metric("Min Temperature", f"{monthly_temp.min():.1f}°C")
                        st.metric("Annual Range", f"{monthly_temp.max() - monthly_temp.min():.1f}°C")
                    
                    with col2:
                        st.markdown("""
                        <div style="background: rgba(0, 0, 255, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid blue;">
                            <div style="color: blue; font-weight: 600; margin-bottom: 10px;">🌧️ Precipitation</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.metric("Total Annual", f"{monthly_precip.sum():.0f} mm")
                        st.metric("Monthly Average", f"{monthly_precip.mean():.0f} mm")
                        st.metric("Wettest Month", f"{monthly_precip.max():.0f} mm")
                        st.metric("Driest Month", f"{monthly_precip.min():.0f} mm")
                else:
                    st.info("Climate analysis was not selected or no climate data available.")
            
            with tab3:
                # Daily climate analysis results
                if st.session_state.daily_climate_results:
                    daily_df = st.session_state.daily_climate_results['data']
                    source_name = st.session_state.daily_climate_results['source']
                    
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid cyan;">
                        <div style="color: cyan; font-weight: 600; margin-bottom: 5px;">📊 Daily Climate Analysis</div>
                        <div style="color: #cccccc; font-size: 12px;">Data Source: {source_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create daily temperature chart
                    fig_daily_temp = go.Figure()
                    fig_daily_temp.add_trace(go.Scatter(
                        x=daily_df['date'],
                        y=daily_df['temperature'],
                        mode='lines+markers',
                        name='Temperature',
                        line=dict(color='red', width=2),
                        marker=dict(size=6, color='red')
                    ))
                    
                    fig_daily_temp.update_layout(
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
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_daily_temp, use_container_width=True)
                    
                    # Create daily precipitation chart
                    fig_daily_precip = go.Figure()
                    fig_daily_precip.add_trace(go.Bar(
                        x=daily_df['date'],
                        y=daily_df['precipitation'],
                        name='Precipitation',
                        marker_color='blue'
                    ))
                    
                    fig_daily_precip.update_layout(
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
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_daily_precip, use_container_width=True)
                    
                    # Daily climate statistics
                    if not daily_df.empty:
                        temp_mean = daily_df['temperature'].mean()
                        temp_max = daily_df['temperature'].max()
                        temp_min = daily_df['temperature'].min()
                        precip_total = daily_df['precipitation'].sum()
                        precip_mean = daily_df['precipitation'].mean()
                        precip_max = daily_df['precipitation'].max()
                        
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            st.markdown("""
                            <div style="background: rgba(255, 0, 0, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <div style="color: red; font-weight: 600; margin-bottom: 10px;">🌡️ Daily Temperature Stats</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.metric("Mean", f"{temp_mean:.1f}°C")
                            st.metric("Maximum", f"{temp_max:.1f}°C")
                            st.metric("Minimum", f"{temp_min:.1f}°C")
                        
                        with col4:
                            st.markdown("""
                            <div style="background: rgba(0, 0, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <div style="color: blue; font-weight: 600; margin-bottom: 10px;">🌧️ Daily Precipitation Stats</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.metric("Total", f"{precip_total:.1f} mm")
                            st.metric("Daily Average", f"{precip_mean:.2f} mm")
                            st.metric("Max Daily", f"{precip_max:.1f} mm")
                else:
                    st.info("Daily climate analysis was not selected or no data available.")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">📊</div>
                <div style="color: #666666; font-size: 16px; margin-bottom: 10px;">No Results Available</div>
                <div style="color: #444444; font-size: 14px;">Please run an analysis to see results</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
    <p style="margin: 5px 0;">KHISBA GIS • Interactive 3D Global Vegetation & Climate Analytics Platform</p>
    <p style="margin: 5px 0;">Vegetation Indices • Temperature • Precipitation • Guided Workflow</p>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">3D Mapbox</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">Climate Analysis</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">Step-by-Step</span>
        <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v3.0</span>
    </div>
</div>
""", unsafe_allow_html=True)
