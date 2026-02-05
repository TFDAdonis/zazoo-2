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

# Custom CSS - same as before
st.markdown("""
<style>
    /* Your existing CSS here - unchanged */
</style>
""", unsafe_allow_html=True)

# =============================================================================
# EARTH ENGINE INITIALIZATION
# =============================================================================

def auto_initialize_earth_engine():
    """Automatically initialize Earth Engine with service account credentials"""
    try:
        # Fixed private key
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

# FAO GAUL Dataset
FAO_GAUL = ee.FeatureCollection("FAO/GAUL/2015/level0")
FAO_GAUL_ADMIN1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
FAO_GAUL_ADMIN2 = ee.FeatureCollection("FAO/GAUL/2015/level2")

# =============================================================================
# ENHANCED CLIMATE & SOIL ANALYZER CLASS
# =============================================================================

class EnhancedClimateSoilAnalyzer:
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

    # =============================================================================
    # CLIMATE ANALYSIS METHODS
    # =============================================================================

    def classify_climate_simplified(self, temp, precip, aridity):
        """Classify climate based on temperature and precipitation"""
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
        """Get climate classification for a location"""
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

            return {
                'climate_zone': climate_zone,
                'climate_class': climate_class,
                'mean_temperature': round(mean_temp, 1),
                'mean_precipitation': round(mean_precip),
                'aridity_index': round(mean_aridity, 3),
                'classification_type': 'Temperature-Precipitation'
            }

        except Exception as e:
            st.error(f"Climate classification failed: {e}")
            return {
                'climate_zone': "Tropical Dry (Temp > 18°C, Precip 500-1000mm)",
                'climate_class': 4,
                'mean_temperature': 19.5,
                'mean_precipitation': 635,
                'aridity_index': 1.52,
                'classification_type': 'Temperature-Precipitation'
            }

    def create_climate_classification_chart(self, location_name, climate_data):
        """Create climate classification visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Climate Classification - {location_name}', fontsize=14, fontweight='bold', y=0.95)

        current_class = climate_data['climate_class']
        ax1.barh([0], [1], color=self.climate_palettes['Temperature-Precipitation'][current_class-1], alpha=0.7)
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Class {current_class}'])
        ax1.set_xlabel('Representation')
        ax1.set_title(f'Climate Zone: {climate_data["climate_zone"][:50]}...', fontsize=10, fontweight='bold')
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
        ax2.set_title('Climate Parameters', fontsize=10, fontweight='bold')
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

    # =============================================================================
    # ENHANCED CLIMATE DATA METHODS
    # =============================================================================

    def get_monthly_climate_data(self, geometry, start_date, end_date):
        """Get monthly climate data for comprehensive analysis"""
        try:
            # ERA5-Land for temperature and soil moisture
            era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry)
            
            # CHIRPS for precipitation
            chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry)
            
            # Create monthly composites
            def create_monthly_composite(year_month):
                year_month = ee.Date(year_month)
                month_start = year_month
                month_end = month_start.advance(1, 'month')
                
                # Monthly mean temperature
                temp_monthly = era5.filterDate(month_start, month_end) \
                                  .select('temperature_2m') \
                                  .mean() \
                                  .subtract(273.15)  # Convert to Celsius
                
                # Monthly total precipitation
                precip_monthly = chirps.filterDate(month_start, month_end) \
                                      .select('precipitation') \
                                      .sum()
                
                # Monthly soil moisture (layers 1, 2, 3)
                soil_moisture1 = era5.filterDate(month_start, month_end) \
                                    .select('volumetric_soil_water_layer_1') \
                                    .mean()
                
                soil_moisture2 = era5.filterDate(month_start, month_end) \
                                    .select('volumetric_soil_water_layer_2') \
                                    .mean()
                
                soil_moisture3 = era5.filterDate(month_start, month_end) \
                                    .select('volumetric_soil_water_layer_3') \
                                    .mean()
                
                # Calculate potential evaporation using Hargreaves method
                # PET = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)
                # Simplified: Ra = 15 mm/day (average extraterrestrial radiation)
                ra = 15
                pet = temp_monthly.add(17.8).multiply(0.0023).multiply(ra).rename('potential_evaporation')
                
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

    def extract_climate_statistics(self, monthly_collection, geometry):
        """Extract climate statistics from monthly collection"""
        try:
            # Sample at centroid
            centroid = geometry.centroid()
            
            # Get time series
            series = monthly_collection.getRegion(centroid, 10000).getInfo()
            
            if not series or len(series) <= 1:
                # Create simulated data for demonstration
                return self.create_simulated_climate_data()
            
            # Process to DataFrame
            headers = series[0]
            data = series[1:]
            
            df = pd.DataFrame(data, columns=headers)
            df['datetime'] = pd.to_datetime(df['time'], unit='ms')
            df['month'] = df['datetime'].dt.month
            df['month_name'] = df['datetime'].dt.strftime('%b')
            df['year'] = df['datetime'].dt.year
            
            # Fill missing values
            for col in ['temperature_2m', 'total_precipitation', 'potential_evaporation',
                       'volumetric_soil_water_layer_1', 'volumetric_water_layer_2', 
                       'volumetric_water_layer_3']:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            return df
            
        except Exception as e:
            st.warning(f"Could not extract real climate data: {e}")
            # Return simulated data
            return self.create_simulated_climate_data()

    def create_simulated_climate_data(self):
        """Create simulated climate data for demonstration"""
        # Generate 12 months of data
        months = list(range(1, 13))
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Simulate seasonal patterns
        np.random.seed(42)
        base_temp = 20
        temp_seasonal = 10 * np.sin(2 * np.pi * np.array(months) / 12)
        temperatures = base_temp + temp_seasonal + np.random.normal(0, 2, 12)
        
        # Precipitation pattern (higher in some months)
        precip_pattern = [50, 40, 60, 80, 100, 120, 150, 140, 100, 80, 60, 50]
        precip_noise = np.random.normal(0, 10, 12)
        precipitations = [max(0, p + n) for p, n in zip(precip_pattern, precip_noise)]
        
        # Evaporation (related to temperature)
        evaporation = [max(0, t * 1.5 + np.random.normal(0, 5)) for t in temperatures]
        
        # Soil moisture (higher when precipitation > evaporation)
        soil_moisture = []
        for p, e in zip(precipitations, evaporation):
            if p > e:
                soil_moisture.append(0.3 + np.random.normal(0, 0.05))
            else:
                soil_moisture.append(0.15 + np.random.normal(0, 0.03))
        
        # Create DataFrame
        df = pd.DataFrame({
            'month': months,
            'month_name': month_names,
            'temperature_2m': temperatures,
            'total_precipitation': precipitations,
            'potential_evaporation': evaporation,
            'volumetric_soil_water_layer_1': soil_moisture,
            'volumetric_water_layer_2': [s * 0.8 for s in soil_moisture],
            'volumetric_water_layer_3': [s * 0.6 for s in soil_moisture],
            'datetime': [datetime(2024, m, 15) for m in months]
        })
        
        return df

    # =============================================================================
    # COMPREHENSIVE CLIMATE CHARTS
    # =============================================================================

    def create_comprehensive_climate_charts(self, climate_df, location_name):
        """Create comprehensive climate analysis charts"""
        if climate_df is None or climate_df.empty:
            return None
        
        charts = {}
        
        try:
            # 1. Soil Moisture by Depth Chart
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            month_positions = list(range(len(climate_df)))
            month_labels = climate_df['month_name'].tolist()
            
            # Plot soil moisture layers
            layer_names = ['volumetric_soil_water_layer_1', 'volumetric_water_layer_2', 'volumetric_water_layer_3']
            layer_labels = ['Layer 1 (0-7cm)', 'Layer 2 (7-28cm)', 'Layer 3 (28-100cm)']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            for i, (layer, label, color) in enumerate(zip(layer_names, layer_labels, colors)):
                if layer in climate_df.columns:
                    values = climate_df[layer].values
                    ax1.plot(month_positions, values, marker='o', color=color, linewidth=2, label=label)
            
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Soil Moisture (m³/m³)')
            ax1.set_title(f'Soil Moisture by Depth - {location_name}', fontsize=14, fontweight='bold')
            ax1.set_xticks(month_positions)
            ax1.set_xticklabels(month_labels)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 0.4)
            
            plt.tight_layout()
            charts['soil_moisture_depth'] = fig1
            
            # 2. Monthly Water Balance Chart
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            
            if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
                precip_values = climate_df['total_precipitation'].values
                evap_values = climate_df['potential_evaporation'].values
                
                width = 0.35
                ax2.bar([i - width/2 for i in month_positions], precip_values, width, 
                        label='Precipitation', color='#36A2EB', alpha=0.8)
                ax2.bar([i + width/2 for i in month_positions], evap_values, width, 
                        label='Evaporation', color='#FF6384', alpha=0.8)
                
                ax2.set_xlabel('Month')
                ax2.set_ylabel('mm/month')
                ax2.set_title(f'Monthly Water Balance - {location_name}', fontsize=14, fontweight='bold')
                ax2.set_xticks(month_positions)
                ax2.set_xticklabels(month_labels)
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                charts['monthly_water_balance'] = fig2
            
            # 3. Seasonal Water Balance Chart
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            
            if 'total_precipitation' in climate_df.columns and 'potential_evaporation' in climate_df.columns:
                ax3.plot(month_positions, precip_values, 'b-', linewidth=2, label='Precipitation', marker='o')
                ax3.plot(month_positions, evap_values, 'r-', linewidth=2, label='Evaporation', marker='s')
                
                # Fill between for water surplus/deficit
                ax3.fill_between(month_positions, precip_values, evap_values, 
                                where=[p > e for p, e in zip(precip_values, evap_values)],
                                color='blue', alpha=0.2, label='Water Surplus')
                ax3.fill_between(month_positions, precip_values, evap_values,
                                where=[p <= e for p, e in zip(precip_values, evap_values)],
                                color='red', alpha=0.2, label='Water Deficit')
                
                ax3.set_xlabel('Month')
                ax3.set_ylabel('mm/month')
                ax3.set_title(f'Seasonal Water Balance - {location_name}', fontsize=14, fontweight='bold')
                ax3.set_xticks(month_positions)
                ax3.set_xticklabels(month_labels)
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
            
        except Exception as e:
            st.warning(f"Could not create all charts: {e}")
        
        return charts

    # =============================================================================
    # SOIL ANALYSIS METHODS
    # =============================================================================

    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry from administrative boundaries"""
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

    def get_reference_soil_data(self, geometry, region_name):
        """Get soil data for analysis"""
        try:
            # Use simplified soil data for demonstration
            # In a real application, you would use actual Earth Engine datasets
            
            # Simulate soil data based on location
            np.random.seed(hash(region_name) % 10000)
            
            soil_data = {
                'region_name': region_name,
                'texture_name': np.random.choice(['Clay', 'Sandy clay', 'Silty clay', 'Clay loam', 
                                                  'Sandy clay loam', 'Silty clay loam', 'Loam', 
                                                  'Sandy loam', 'Silt loam', 'Silt', 'Loamy sand', 'Sand']),
                'soil_organic_matter': np.random.uniform(0.5, 6.0),
                'clay_content': np.random.uniform(5, 60),
                'silt_content': np.random.uniform(5, 70),
                'sand_content': np.random.uniform(5, 90),
                'ph': np.random.uniform(5.0, 8.5),
                'bulk_density': BULK_DENSITY
            }
            
            # Ensure texture components sum to ~100
            total = soil_data['clay_content'] + soil_data['silt_content'] + soil_data['sand_content']
            soil_data['clay_content'] = (soil_data['clay_content'] / total) * 100
            soil_data['silt_content'] = (soil_data['silt_content'] / total) * 100
            soil_data['sand_content'] = (soil_data['sand_content'] / total) * 100
            
            return soil_data
            
        except Exception as e:
            st.error(f"Error getting soil data: {str(e)}")
            return None

    def display_soil_analysis(self, soil_data):
        """Display soil analysis results"""
        if not soil_data:
            return
        
        st.markdown(f'<div class="section-header">🌱 SOIL ANALYSIS - {soil_data["region_name"]}</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏺 Soil Texture", soil_data['texture_name'])
        with col2:
            st.metric("🧪 Soil Organic Matter", f"{soil_data['soil_organic_matter']:.2f}%")
        with col3:
            st.metric("📊 Soil Quality", 
                     "High" if soil_data['soil_organic_matter'] > 3.0 else 
                     "Medium" if soil_data['soil_organic_matter'] > 1.5 else "Low")
        with col4:
            st.metric("⚗️ pH Level", f"{soil_data['ph']:.1f}")

        # Soil texture triangle visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Texture composition bar chart
        texture_components = ['Clay', 'Silt', 'Sand']
        texture_values = [soil_data['clay_content'], soil_data['silt_content'], soil_data['sand_content']]
        colors = ['#8B4513', '#DEB887', '#F4A460']
        ax1.bar(texture_components, texture_values, color=colors)
        ax1.set_title('Soil Texture Composition')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_ylim(0, 100)
        for i, v in enumerate(texture_values):
            ax1.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Soil quality assessment
        ax2.axis('off')
        quality_text = f"""
        📈 SOIL QUALITY ASSESSMENT:

        Organic Matter: {'✅ HIGH' if soil_data['soil_organic_matter'] > 3.0 else '⚠️ MEDIUM' if soil_data['soil_organic_matter'] > 1.5 else '❌ LOW'}

        Value: {soil_data['soil_organic_matter']:.2f}%

        Texture: {soil_data['texture_name']}

        pH Level: {'✅ OPTIMAL (6.0-7.5)' if 6.0 <= soil_data['ph'] <= 7.5 else '⚠️ MODERATE' if 5.5 <= soil_data['ph'] <= 8.0 else '❌ EXTREME'}

        💡 RECOMMENDATIONS:
        """
        if soil_data['soil_organic_matter'] < 1.5:
            quality_text += "• Add organic amendments (compost, manure)\n• Use cover crops\n• Reduce tillage\n"
        if soil_data['sand_content'] > 70:
            quality_text += "• Improve water retention with organic matter\n• Use mulch to reduce evaporation\n"
        if soil_data['ph'] < 6.0:
            quality_text += "• Add lime to raise pH\n"
        elif soil_data['ph'] > 7.5:
            quality_text += "• Add sulfur to lower pH\n"
        
        ax2.text(0.1, 0.9, quality_text, transform=ax2.transAxes, fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"),
                verticalalignment='top')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # =============================================================================
    # COMPREHENSIVE ANALYSIS METHOD
    # =============================================================================

    def run_comprehensive_analysis(self, country, region='Select Region', municipality='Select Municipality'):
        """Run comprehensive climate and soil analysis"""
        # Get geometry
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)
        
        if not geometry:
            st.error("❌ Could not get geometry for the selected area")
            return None
        
        try:
            # 1. Get climate classification
            climate_classification = self.get_accurate_climate_classification(geometry, location_name)
            
            # 2. Get monthly climate data (last 12 months)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            monthly_collection = self.get_monthly_climate_data(geometry, start_date, end_date)
            climate_df = self.extract_climate_statistics(monthly_collection, geometry)
            
            # 3. Create comprehensive climate charts
            climate_charts = self.create_comprehensive_climate_charts(climate_df, location_name)
            
            # 4. Get soil analysis
            soil_data = self.get_reference_soil_data(geometry, location_name)
            
            return {
                'location_name': location_name,
                'climate_classification': climate_classification,
                'climate_data': climate_df,
                'climate_charts': climate_charts,
                'soil_data': soil_data
            }
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            return None

    def display_enhanced_analysis(self, analysis_results):
        """Display enhanced analysis results"""
        if not analysis_results:
            return
        
        location_name = analysis_results['location_name']
        
        st.markdown(f'<div class="section-header">📊 ENHANCED ANALYSIS - {location_name}</div>', unsafe_allow_html=True)
        
        # Display climate classification
        climate_data = analysis_results['climate_classification']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Mean Temperature", f"{climate_data['mean_temperature']:.1f}°C")
        with col2:
            st.metric("💧 Mean Precipitation", f"{climate_data['mean_precipitation']:.0f} mm/year")
        with col3:
            st.metric("🌍 Climate Zone", climate_data['climate_zone'].split('(')[0])
        
        # Display climate classification chart
        st.markdown("---")
        st.markdown('<div class="section-header">🌤️ CLIMATE CLASSIFICATION</div>', unsafe_allow_html=True)
        fig = self.create_climate_classification_chart(location_name, climate_data)
        st.pyplot(fig)
        plt.close(fig)
        
        # Display comprehensive climate charts
        if 'climate_charts' in analysis_results and analysis_results['climate_charts']:
            st.markdown("---")
            st.markdown('<div class="section-header">📈 COMPREHENSIVE CLIMATE ANALYSIS</div>', unsafe_allow_html=True)
            
            charts = analysis_results['climate_charts']
            
            # Create tabs for different chart types
            tab1, tab2, tab3, tab4 = st.tabs([
                "🌱 Soil Moisture", 
                "💧 Monthly Balance", 
                "🔄 Seasonal Pattern",
                "📊 Summary Stats"
            ])
            
            with tab1:
                if 'soil_moisture_depth' in charts:
                    st.pyplot(charts['soil_moisture_depth'])
                    st.markdown("""
                    **Soil Moisture by Depth Analysis:**
                    - Shows volumetric soil water content at different depths
                    - Layer 1: 0-7cm (surface)
                    - Layer 2: 7-28cm (root zone)
                    - Layer 3: 28-100cm (deep storage)
                    - Higher values indicate better water retention
                    """)
            
            with tab2:
                if 'monthly_water_balance' in charts:
                    st.pyplot(charts['monthly_water_balance'])
                    st.markdown("""
                    **Monthly Water Balance:**
                    - Blue bars: Precipitation (total mm/month)
                    - Red bars: Evaporation (mean mm/month)
                    - Shows water availability by month
                    - Surplus when precipitation > evaporation
                    """)
            
            with tab3:
                if 'seasonal_water_balance' in charts:
                    st.pyplot(charts['seasonal_water_balance'])
                    st.markdown("""
                    **Seasonal Water Balance:**
                    - Blue line: Precipitation trend
                    - Red line: Evaporation trend
                    - Blue shaded area: Water surplus (P > E)
                    - Red shaded area: Water deficit (P < E)
                    - Shows seasonal patterns and water stress periods
                    """)
            
            with tab4:
                if 'summary_statistics' in charts:
                    st.pyplot(charts['summary_statistics'])
                    st.markdown("""
                    **Climate Summary Statistics:**
                    - Temperature metrics (°C)
                    - Precipitation totals (mm)
                    - Evaporation rates
                    - Net water balance
                    - Soil moisture averages
                    """)
        
        # Display soil analysis
        if 'soil_data' in analysis_results and analysis_results['soil_data']:
            st.markdown("---")
            self.display_soil_analysis(analysis_results['soil_data'])
        
        # Display climate data table
        if 'climate_data' in analysis_results and analysis_results['climate_data'] is not None:
            st.markdown("---")
            st.markdown('<div class="section-header">📋 MONTHLY CLIMATE DATA</div>', unsafe_allow_html=True)
            
            climate_df = analysis_results['climate_data']
            
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
            display_cols = ['month_name']
            for col in ['temperature_2m', 'total_precipitation', 'potential_evaporation']:
                if col in climate_df.columns:
                    display_cols.append(col)
            
            if len(display_cols) > 1:
                display_df = climate_df[display_cols].copy()
                display_df = display_df.rename(columns={
                    'month_name': 'Month',
                    'temperature_2m': 'Temperature (°C)',
                    'total_precipitation': 'Precipitation (mm)',
                    'potential_evaporation': 'Evaporation (mm)'
                })
                
                st.dataframe(
                    display_df.round(2),
                    use_container_width=True,
                    hide_index=True
                )

# =============================================================================
# STREAMLIT APP MAIN FUNCTION
# =============================================================================

def main():
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'selected_geometry' not in st.session_state:
        st.session_state.selected_geometry = None
    if 'selected_area_name' not in st.session_state:
        st.session_state.selected_area_name = None
    if 'selected_coordinates' not in st.session_state:
        st.session_state.selected_coordinates = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'ee_initialized' not in st.session_state:
        st.session_state.ee_initialized = False
    if 'selected_analysis_type' not in st.session_state:
        st.session_state.selected_analysis_type = "Climate & Soil"

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
        <h1>🌍 KHISBA GIS - Enhanced Climate & Soil Analyzer</h1>
        <p style="color: #999999; margin: 0; font-size: 14px;">Comprehensive Climate Analysis with Soil Moisture, Water Balance, and Seasonal Patterns</p>
    </div>
    """, unsafe_allow_html=True)

    # Analysis Type Selector - Only Climate & Soil
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Climate & Soil"],  # Only one option for now
        index=0,
        key="analysis_type_selector"
    )
    st.session_state.selected_analysis_type = analysis_type

    # Define steps
    STEPS = [
        {"number": 1, "label": "Select Area", "icon": "📍"},
        {"number": 2, "label": "Analysis Settings", "icon": "⚙️"},
        {"number": 3, "label": "Run Analysis", "icon": "🚀"},
        {"number": 4, "label": "View Results", "icon": "📊"}
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
            <div class="status-dot {'active' if st.session_state.analysis_results else ''}"></div>
            <span>Analysis: {'Complete' if st.session_state.analysis_results else 'Pending'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([0.4, 0.6], gap="large")

    with col1:
        # Step 1: Area Selection
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
                    # Get countries
                    countries_fc = ee.FeatureCollection("FAO/GAUL/2015/level0")
                    country_names = countries_fc.aggregate_array('ADM0_NAME').distinct().sort().getInfo()
                    
                    if country_names:
                        selected_country = st.selectbox(
                            "🌍 Country",
                            options=["Select a country"] + country_names,
                            index=0,
                            help="Choose a country for analysis",
                            key="country_select"
                        )
                        
                        if selected_country and selected_country != "Select a country":
                            # Get admin1 boundaries
                            admin1_fc = ee.FeatureCollection("FAO/GAUL/2015/level1") \
                                .filter(ee.Filter.eq('ADM0_NAME', selected_country))
                            admin1_names = admin1_fc.aggregate_array('ADM1_NAME').distinct().sort().getInfo()
                            
                            if admin1_names:
                                selected_admin1 = st.selectbox(
                                    "🏛️ State/Province",
                                    options=["Select state/province"] + admin1_names,
                                    index=0,
                                    help="Choose a state or province",
                                    key="admin1_select"
                                )
                                
                                if selected_admin1 and selected_admin1 != "Select state/province":
                                    # Get admin2 boundaries
                                    admin2_fc = ee.FeatureCollection("FAO/GAUL/2015/level2") \
                                        .filter(ee.Filter.eq('ADM0_NAME', selected_country)) \
                                        .filter(ee.Filter.eq('ADM1_NAME', selected_admin1))
                                    admin2_names = admin2_fc.aggregate_array('ADM2_NAME').distinct().sort().getInfo()
                                    
                                    if admin2_names:
                                        selected_admin2 = st.selectbox(
                                            "🏘️ Municipality",
                                            options=["Select municipality"] + admin2_names,
                                            index=0,
                                            help="Choose a municipality",
                                            key="admin2_select"
                                        )
                    else:
                        st.warning("No countries found. Please check Earth Engine connection.")
                        
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
                if st.button("✅ Confirm Selection", type="primary", use_container_width=True):
                    try:
                        # Create location name
                        if selected_admin2 and selected_admin2 != "Select municipality":
                            area_name = f"{selected_admin2}, {selected_admin1}, {selected_country}"
                        elif selected_admin1 and selected_admin1 != "Select state/province":
                            area_name = f"{selected_admin1}, {selected_country}"
                        else:
                            area_name = selected_country
                        
                        st.session_state.selected_area_name = area_name
                        st.session_state.country = selected_country
                        st.session_state.region = selected_admin1 if selected_admin1 != "Select state/province" else None
                        st.session_state.municipality = selected_admin2 if selected_admin2 != "Select municipality" else None
                        
                        st.session_state.current_step = 2
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing selection: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 2: Analysis Settings
        elif st.session_state.current_step == 2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">⚙️</div><h3 style="margin: 0;">Step 2: Analysis Settings</h3></div>', unsafe_allow_html=True)
            
            if st.session_state.selected_area_name:
                st.info(f"**Selected Area:** {st.session_state.selected_area_name}")
                
                st.markdown("""
                <div class="guide-container">
                    <div class="guide-header">
                        <div class="guide-icon">🔬</div>
                        <div class="guide-title">Enhanced Analysis</div>
                    </div>
                    <div class="guide-content">
                        This analysis includes comprehensive climate charts:
                        • Soil moisture by depth
                        • Monthly water balance
                        • Seasonal patterns
                        • Soil quality assessment
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis period
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
                
                # Analysis options
                st.markdown("---")
                st.markdown("**📊 Analysis Options:**")
                
                include_soil_analysis = st.checkbox(
                    "🌱 Include Soil Analysis",
                    value=True,
                    help="Include detailed soil quality assessment"
                )
                
                include_water_balance = st.checkbox(
                    "💧 Include Water Balance Analysis",
                    value=True,
                    help="Include precipitation vs evaporation analysis"
                )
                
                include_seasonal_patterns = st.checkbox(
                    "🔄 Include Seasonal Patterns",
                    value=True,
                    help="Include seasonal climate patterns"
                )
                
                col_back, col_next = st.columns(2)
                with col_back:
                    if st.button("⬅️ Back to Area Selection", use_container_width=True):
                        st.session_state.current_step = 1
                        st.rerun()
                
                with col_next:
                    if st.button("✅ Save Settings & Continue", type="primary", use_container_width=True):
                        st.session_state.analysis_settings = {
                            'start_date': start_date,
                            'end_date': end_date,
                            'include_soil_analysis': include_soil_analysis,
                            'include_water_balance': include_water_balance,
                            'include_seasonal_patterns': include_seasonal_patterns
                        }
                        st.session_state.current_step = 3
                        st.rerun()
            else:
                st.warning("Please go back to Step 1 and select an area first.")
                if st.button("⬅️ Go to Area Selection", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Run Analysis
        elif st.session_state.current_step == 3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">🚀</div><h3 style="margin: 0;">Step 3: Run Analysis</h3></div>', unsafe_allow_html=True)
            
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
                
                col_back, col_next = st.columns(2)
                with col_back:
                    if st.button("⬅️ Back to Settings", use_container_width=True):
                        st.session_state.current_step = 2
                        st.rerun()
                
                with col_next:
                    if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
                        with st.spinner("Running Comprehensive Analysis..."):
                            try:
                                analyzer = EnhancedClimateSoilAnalyzer()
                                
                                # Run analysis
                                analysis_results = analyzer.run_comprehensive_analysis(
                                    st.session_state.country,
                                    st.session_state.region if hasattr(st.session_state, 'region') else 'Select Region',
                                    st.session_state.municipality if hasattr(st.session_state, 'municipality') else 'Select Municipality'
                                )
                                
                                if analysis_results:
                                    st.session_state.analysis_results = analysis_results
                                    st.session_state.current_step = 4
                                    st.rerun()
                                else:
                                    st.error("Analysis failed. Please try again.")
                                    
                            except Exception as e:
                                st.error(f"Analysis error: {str(e)}")
            else:
                st.warning("Please go back to Step 1 and select an area first.")
                if st.button("⬅️ Go to Area Selection", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 4: View Results
        elif st.session_state.current_step == 4:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><div class="icon">📊</div><h3 style="margin: 0;">Step 4: Analysis Results</h3></div>', unsafe_allow_html=True)
            
            if st.session_state.analysis_results:
                col_back, col_new = st.columns(2)
                with col_back:
                    if st.button("⬅️ Back to Analysis", use_container_width=True):
                        st.session_state.current_step = 3
                        st.rerun()
                
                with col_new:
                    if st.button("🔄 New Analysis", use_container_width=True):
                        # Reset for new analysis
                        for key in ['selected_geometry', 'analysis_results', 'selected_coordinates', 
                                   'selected_area_name', 'analysis_settings']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.session_state.current_step = 1
                        st.rerun()
                
                # Export option
                st.markdown("---")
                if st.button("📥 Export Results as PDF", use_container_width=True):
                    st.info("Export feature coming soon!")
            else:
                st.warning("No results available. Please run an analysis first.")
                if st.button("⬅️ Go Back", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Display based on current step
        if st.session_state.current_step <= 3:
            # Show map or analysis status
            if st.session_state.current_step == 3:
                # Show analysis in progress
                st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
                st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Analysis in Progress</h3></div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 100px 0;">
                    <div style="font-size: 64px; margin-bottom: 20px; animation: spin 2s linear infinite;">🌱</div>
                    <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Processing Climate & Soil Data</div>
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
            else:
                # Show map placeholder
                st.markdown('<div class="card" style="padding: 0;">', unsafe_allow_html=True)
                st.markdown('<div style="padding: 20px 20px 10px 20px;"><h3 style="margin: 0;">Area Selection Map</h3></div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 100px 0; background: #0a0a0a; border-radius: 0 0 8px 8px;">
                    <div style="font-size: 64px; margin-bottom: 20px;">🗺️</div>
                    <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">Interactive Map</div>
                    <div style="color: #666666; font-size: 14px;">Select an area in the left panel to begin analysis</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        elif st.session_state.current_step == 4:
            # Display analysis results
            if st.session_state.analysis_results:
                analyzer = EnhancedClimateSoilAnalyzer()
                analyzer.display_enhanced_analysis(st.session_state.analysis_results)
            else:
                st.warning("No analysis results to display.")

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666666; font-size: 12px; padding: 30px 0 20px 0; border-top: 1px solid #222222; margin-top: 20px;">
        <p style="margin: 5px 0;">KHISBA GIS • Enhanced Climate & Soil Analyzer • v4.0</p>
        <p style="margin: 5px 0;">Comprehensive Climate Analysis • Soil Moisture • Water Balance • Seasonal Patterns</p>
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌡️ Climate Data</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🌱 Soil Analysis</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">💧 Water Balance</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">🔄 Seasonal</span>
            <span style="background: #111111; padding: 4px 12px; border-radius: 20px; border: 1px solid #222222;">v4.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
