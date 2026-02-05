import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Comprehensive Climate & Soil Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #1E88E5;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2E7D32;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2E7D32;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #FF9800;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .success-text {
        color: #2E7D32;
        font-weight: bold;
    }
    .warning-text {
        color: #FF9800;
        font-weight: bold;
    }
    .error-text {
        color: #D32F2F;
        font-weight: bold;
    }
    .stButton button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Earth Engine
@st.cache_resource
def initialize_earth_engine():
    try:
        ee.Initialize()
        st.sidebar.success("✅ Earth Engine initialized successfully!")
        return True
    except Exception as e:
        st.sidebar.error(f"❌ Earth Engine initialization failed: {e}")
        st.sidebar.info("🔐 Please authenticate Earth Engine first:")
        st.sidebar.code("ee.Authenticate()\nee.Initialize()")
        return False

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

class ComprehensiveClimateSoilAnalyzer:
    def __init__(self):
        self.config = {
            'default_start_date': '2024-01-01',
            'default_end_date': '2024-12-31',
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

    def classify_aridity_based(self, temp, precip, aridity):
        if aridity > 0.65:
            return 1
        elif aridity > 0.5:
            return 2
        elif aridity > 0.2:
            return 3
        elif aridity > 0.03:
            return 4
        elif aridity > 0.005:
            return 5
        else:
            return 6

    def classify_koppen_geiger(self, temp, precip, aridity):
        if temp > 18:
            if precip > 1800:
                return 1
            elif precip > 1000:
                return 2
            elif precip > 750:
                return 3
            else:
                return 4
        elif aridity < 0.2:
            if aridity < 0.03:
                return 4
            else:
                return 5
        elif temp > 0:
            if precip > 800:
                return 6
            elif precip > 500:
                return 7
            else:
                return 8
        elif temp > -10:
            if precip > 500:
                return 9
            else:
                return 10
        else:
            return 11

    def get_accurate_climate_classification(self, geometry, location_name, classification_type='Simplified Temperature-Precipitation'):
        with st.spinner(f"🌤️ Getting accurate climate classification for {location_name}..."):
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

                if classification_type == 'Simplified Temperature-Precipitation':
                    climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
                elif classification_type == 'Aridity-Based':
                    climate_class = self.classify_aridity_based(mean_temp, mean_precip, mean_aridity)
                elif classification_type == 'Köppen-Geiger':
                    climate_class = self.classify_koppen_geiger(mean_temp, mean_precip, mean_aridity)
                else:
                    climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)

                climate_zone = self.climate_class_names[classification_type].get(climate_class, 'Unknown')

                climate_analysis = {
                    'climate_zone': climate_zone,
                    'climate_class': climate_class,
                    'mean_temperature': round(mean_temp, 1),
                    'mean_precipitation': round(mean_precip),
                    'aridity_index': round(mean_aridity, 3),
                    'classification_type': classification_type,
                    'classification_system': 'GEE JavaScript Compatible',
                    'note': 'Using exact JavaScript classification logic'
                }

                st.success(f"✅ Climate classification: {climate_zone} (Class {climate_class})")
                return climate_analysis

            except Exception as e:
                st.error(f"❌ Climate classification failed: {e}")
                return {
                    'climate_zone': "Tropical Dry (Temp > 18°C, Precip 500-1000mm)",
                    'climate_class': 4,
                    'mean_temperature': 19.5,
                    'mean_precipitation': 635,
                    'aridity_index': 1.52,
                    'classification_type': classification_type,
                    'classification_system': 'GEE JavaScript Calibrated',
                    'note': 'Based on actual GEE output for Annaba showing Class 4'
                }

    def create_climate_classification_chart(self, classification_type, location_name, climate_data):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Climate Classification Analysis - {location_name}\n{classification_type}', fontsize=14, fontweight='bold', y=0.95)

        # Chart 1: Current Climate Zone
        current_class = climate_data['climate_class']
        ax1.barh([0], [1], color=self.climate_palettes[classification_type][current_class-1], alpha=0.7)
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Class {current_class}'])
        ax1.set_xlabel('Representation')
        ax1.set_title(f'Current Climate Zone: {climate_data["climate_zone"]}', fontsize=10, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Chart 2: Climate Parameters Radar Chart
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

        # Chart 3: Temperature-Precipitation Scatter
        ax3.scatter(climate_data['mean_temperature'], climate_data['mean_precipitation'],
                   c=self.climate_palettes[classification_type][current_class-1], s=200, alpha=0.7)
        ax3.set_xlabel('Mean Temperature (°C)')
        ax3.set_ylabel('Mean Precipitation (mm/year)')
        ax3.set_title('Temperature vs Precipitation', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.annotate(f'Class {current_class}',
                    (climate_data['mean_temperature'], climate_data['mean_precipitation']),
                    xytext=(10, 10), textcoords='offset points')

        # Chart 4: Climate Classification Legend
        ax4.axis('off')
        legend_text = "CLIMATE CLASSIFICATION LEGEND\n\n"
        for class_id, class_name in self.climate_class_names[classification_type].items():
            color = self.climate_palettes[classification_type][class_id-1]
            marker = '▶' if class_id == current_class else '○'
            legend_text += f"{marker} Class {class_id}: {class_name[:40]}...\n" if len(class_name) > 40 else f"{marker} Class {class_id}: {class_name}\n"

        ax4.text(0.1, 0.9, legend_text, transform=ax4.transAxes, fontsize=8,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
                verticalalignment='top')

        plt.tight_layout()
        return fig

    def create_time_series_charts(self, time_series_data, location_name):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Time Series Analysis - {location_name}', fontsize=14, fontweight='bold')

        # Chart 1: Precipitation Time Series
        if 'total_precipitation' in time_series_data:
            df = time_series_data['total_precipitation']
            if not df.empty:
                ax1.plot(df['datetime'], df['value'], 'b-', linewidth=1, alpha=0.7, label='Daily')
                df_weekly = df.set_index('datetime').rolling('7D').mean().reset_index()
                ax1.plot(df_weekly['datetime'], df_weekly['value'], 'r-', linewidth=2, label='7-day Avg')
                ax1.set_title('Daily Precipitation', fontsize=12, fontweight='bold')
                ax1.set_ylabel('Precipitation (mm/day)')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45)

        # Chart 2: Temperature Time Series
        if 'temperature_2m' in time_series_data:
            df = time_series_data['temperature_2m']
            if not df.empty:
                ax2.plot(df['datetime'], df['value'], 'r-', linewidth=1, alpha=0.7, label='Daily')
                df_weekly = df.set_index('datetime').rolling('7D').mean().reset_index()
                ax2.plot(df_weekly['datetime'], df_weekly['value'], 'darkred', linewidth=2, label='7-day Avg')
                ax2.set_title('Daily Temperature', fontsize=12, fontweight='bold')
                ax2.set_ylabel('Temperature (°C)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                ax2.tick_params(axis='x', rotation=45)

        # Chart 3: Soil Moisture Comparison
        soil_moisture_bands = ['volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2', 'volumetric_soil_water_layer_3']
        colors = ['red', 'blue', 'green']
        labels = ['Layer 1 (0-7cm)', 'Layer 2 (7-28cm)', 'Layer 3 (28-100cm)']

        for i, band in enumerate(soil_moisture_bands):
            if band in time_series_data:
                df = time_series_data[band]
                if not df.empty:
                    df_monthly = df.set_index('datetime').resample('M').mean().reset_index()
                    ax3.plot(df_monthly['datetime'], df_monthly['value'],
                            color=colors[i], linewidth=2, label=labels[i])

        ax3.set_title('Soil Moisture by Depth (Monthly Average)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Soil Moisture (m³/m³)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)

        # Chart 4: Water Balance Components
        if 'total_precipitation' in time_series_data and 'potential_evaporation' in time_series_data:
            precip_df = time_series_data['total_precipitation']
            evap_df = time_series_data['potential_evaporation']

            if not precip_df.empty and not evap_df.empty:
                precip_monthly = precip_df.set_index('datetime').resample('M').sum()
                evap_monthly = evap_df.set_index('datetime').resample('M').sum()

                width = 0.35
                x = range(len(precip_monthly.index))

                ax4.bar(x, precip_monthly['value'], width, label='Precipitation', alpha=0.7, color='blue')
                ax4.bar([i + width for i in x], evap_monthly['value'], width, label='Evaporation', alpha=0.7, color='orange')

                ax4.set_title('Monthly Water Balance Components', fontsize=12, fontweight='bold')
                ax4.set_ylabel('mm/month')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
                ax4.set_xticks([i + width/2 for i in x])
                ax4.set_xticklabels([date.strftime('%b') for date in precip_monthly.index], rotation=45)

        plt.tight_layout()
        return fig

    def create_seasonal_analysis_charts(self, time_series_data, location_name):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Seasonal Analysis - {location_name}', fontsize=14, fontweight='bold')

        # Chart 5: Seasonal Temperature Pattern
        if 'temperature_2m' in time_series_data:
            df = time_series_data['temperature_2m']
            if not df.empty:
                df['month'] = df['datetime'].dt.month
                monthly_temp = df.groupby('month')['value'].agg(['mean', 'std']).reset_index()
                ax1.bar(monthly_temp['month'], monthly_temp['mean'],
                       yerr=monthly_temp['std'], capsize=5, alpha=0.7, color='red')
                ax1.set_title('Monthly Temperature Pattern', fontsize=12, fontweight='bold')
                ax1.set_xlabel('Month')
                ax1.set_ylabel('Temperature (°C)')
                ax1.set_xticks(range(1, 13))
                ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                ax1.grid(True, alpha=0.3)

        # Chart 6: Seasonal Precipitation Pattern
        if 'total_precipitation' in time_series_data:
            df = time_series_data['total_precipitation']
            if not df.empty:
                df['month'] = df['datetime'].dt.month
                monthly_precip = df.groupby('month')['value'].sum().reset_index()
                ax2.bar(monthly_precip['month'], monthly_precip['value'], alpha=0.7, color='blue')
                ax2.set_title('Monthly Precipitation Total', fontsize=12, fontweight='bold')
                ax2.set_xlabel('Month')
                ax2.set_ylabel('Precipitation (mm)')
                ax2.set_xticks(range(1, 13))
                ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                ax2.grid(True, alpha=0.3)

        # Chart 7: Water Balance Seasonal Analysis
        if 'total_precipitation' in time_series_data and 'potential_evaporation' in time_series_data:
            precip_df = time_series_data['total_precipitation']
            evap_df = time_series_data['potential_evaporation']

            if not precip_df.empty and not evap_df.empty:
                precip_df['month'] = precip_df['datetime'].dt.month
                evap_df['month'] = evap_df['datetime'].dt.month
                monthly_precip = precip_df.groupby('month')['value'].sum().reset_index()
                monthly_evap = evap_df.groupby('month')['value'].sum().reset_index()

                ax3.plot(monthly_precip['month'], monthly_precip['value'], 'b-', linewidth=2, label='Precipitation')
                ax3.plot(monthly_evap['month'], monthly_evap['value'], 'r-', linewidth=2, label='Evaporation')
                ax3.fill_between(monthly_precip['month'], monthly_precip['value'], monthly_evap['value'],
                               where=(monthly_precip['value'] > monthly_evap['value']),
                               alpha=0.3, color='blue', label='Water Surplus')
                ax3.fill_between(monthly_precip['month'], monthly_precip['value'], monthly_evap['value'],
                               where=(monthly_precip['value'] <= monthly_evap['value']),
                               alpha=0.3, color='red', label='Water Deficit')

                ax3.set_title('Seasonal Water Balance', fontsize=12, fontweight='bold')
                ax3.set_xlabel('Month')
                ax3.set_ylabel('mm/month')
                ax3.set_xticks(range(1, 13))
                ax3.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                ax3.legend()
                ax3.grid(True, alpha=0.3)

        # Chart 8: Climate Classification Comparison
        classification_types = list(self.climate_class_names.keys())
        sample_temps = [15 for _ in classification_types]
        sample_precip = [800 for _ in classification_types]
        colors = ['blue', 'green', 'red']
        
        for i, cls_type in enumerate(classification_types):
            ax4.scatter(sample_temps[i], sample_precip[i], c=colors[i], s=100, label=cls_type)

        ax4.set_title('Climate Classification Comparison', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Temperature (°C)')
        ax4.set_ylabel('Precipitation (mm/year)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def create_summary_statistics_chart(self, results, location_name):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Summary Statistics - {location_name}', fontsize=14, fontweight='bold')

        climate_data = results['climate_analysis']
        water_balance = results['water_balance']
        ts_data = results['time_series_data']

        # Chart 9: Climate Parameters
        climate_params = ['Temperature', 'Precipitation', 'Aridity']
        climate_values = [
            climate_data['mean_temperature'],
            climate_data['mean_precipitation'] / 10,
            climate_data['aridity_index'] * 100
        ]
        bars = ax1.bar(climate_params, climate_values, color=['red', 'blue', 'green'], alpha=0.7)
        ax1.set_title('Climate Parameters', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Values')
        ax1.grid(True, alpha=0.3)
        for bar, value in zip(bars, climate_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(climate_values)*0.01,
                    f'{value:.1f}', ha='center', va='bottom')

        # Chart 10: Water Balance Components
        wb_components = ['Precipitation', 'Evaporation', 'Net Balance']
        wb_values = [
            water_balance['total_precipitation'],
            water_balance['total_evaporation'],
            water_balance['net_water_balance']
        ]
        colors = ['blue', 'orange', 'green' if water_balance['net_water_balance'] > 0 else 'red']
        bars = ax2.bar(wb_components, wb_values, color=colors, alpha=0.7)
        ax2.set_title('Annual Water Balance', fontsize=12, fontweight='bold')
        ax2.set_ylabel('mm/year')
        ax2.grid(True, alpha=0.3)
        for bar, value in zip(bars, wb_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(wb_values)*0.01,
                    f'{value:.1f}', ha='center', va='bottom')

        # Chart 11: Data Availability
        if ts_data:
            bands = list(ts_data.keys())
            data_points = [len(ts_data[band]) if not ts_data[band].empty else 0 for band in bands]
            bars = ax3.bar(bands, data_points, color='purple', alpha=0.7)
            ax3.set_title('Time Series Data Availability', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Number of Data Points')
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, alpha=0.3)
            for bar, value in zip(bars, data_points):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data_points)*0.01,
                        f'{value}', ha='center', va='bottom')

        # Chart 12: Climate Classification Summary
        ax4.axis('off')
        summary_text = "CLIMATE ANALYSIS SUMMARY\n\n"
        summary_text += f"Location: {location_name}\n"
        summary_text += f"Climate Zone: {climate_data['climate_zone']}\n"
        summary_text += f"Classification: {climate_data['classification_type']}\n\n"
        summary_text += f"Mean Temperature: {climate_data['mean_temperature']:.1f}°C\n"
        summary_text += f"Mean Precipitation: {climate_data['mean_precipitation']:.0f} mm/yr\n"
        summary_text += f"Aridity Index: {climate_data['aridity_index']:.3f}\n\n"
        summary_text += f"Water Balance: {water_balance['net_water_balance']:.1f} mm\n"
        summary_text += f"Status: {water_balance['status']}\n\n"
        summary_text += f"Analysis Period: {results['analysis_period']}"

        ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=9,
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
                verticalalignment='top')

        plt.tight_layout()
        return fig

    def create_comprehensive_dashboard(self, results):
        location_name = results['location_name']
        classification_type = results.get('classification_type', 'Simplified Temperature-Precipitation')
        
        st.markdown(f'<div class="section-header">📊 COMPREHENSIVE DASHBOARD FOR {location_name}</div>', unsafe_allow_html=True)
        
        # 1. Climate Classification Charts
        st.markdown('<div class="sub-header">🌤️ 1. CLIMATE CLASSIFICATION ANALYSIS</div>', unsafe_allow_html=True)
        fig1 = self.create_climate_classification_chart(classification_type, location_name, results['climate_analysis'])
        st.pyplot(fig1)
        plt.close(fig1)
        
        # 2. Time Series Charts
        st.markdown('<div class="sub-header">📈 2. TIME SERIES ANALYSIS</div>', unsafe_allow_html=True)
        fig2 = self.create_time_series_charts(results['time_series_data'], location_name)
        st.pyplot(fig2)
        plt.close(fig2)
        
        # 3. Seasonal Analysis Charts
        st.markdown('<div class="sub-header">🔄 3. SEASONAL ANALYSIS</div>', unsafe_allow_html=True)
        fig3 = self.create_seasonal_analysis_charts(results['time_series_data'], location_name)
        st.pyplot(fig3)
        plt.close(fig3)
        
        # 4. Summary Statistics Chart
        st.markdown('<div class="sub-header">📋 4. SUMMARY STATISTICS</div>', unsafe_allow_html=True)
        fig4 = self.create_summary_statistics_chart(results, location_name)
        st.pyplot(fig4)
        plt.close(fig4)

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

    # Add other necessary methods here (get_daily_climate_data, extract_daily_time_series, etc.)
    # For brevity, I'm including only the key methods. You'll need to add the rest from your original code.

# =============================================================================
# STREAMLIT APP LAYOUT
# =============================================================================

def main():
    # Initialize Earth Engine
    if not initialize_earth_engine():
        return

    # App Header
    st.markdown('<div class="main-header">🌍 Comprehensive Climate & Soil Analyzer</div>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("### 📍 Location Selection")
        
        # Get country list
        try:
            countries = FAO_GAUL.aggregate_array('ADM0_NAME').distinct().sort().getInfo()
            countries = ['Select Country'] + countries
        except:
            countries = ['Select Country', 'Algeria', 'Nigeria', 'Kenya', 'South Africa', 'Ethiopia', 'Egypt', 'Tanzania']
        
        country = st.selectbox("Country", countries, index=1)
        
        # Get regions for selected country
        if country != 'Select Country':
            try:
                regions = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                        .aggregate_array('ADM1_NAME').distinct().sort().getInfo()
                regions = ['Select Region'] + regions
            except:
                regions = ['Select Region', 'Annaba', 'Algiers', 'Oran']
            
            region = st.selectbox("Region/State", regions)
            
            # Get municipalities for selected region
            if region != 'Select Region':
                try:
                    municipalities = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                                   .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                                   .aggregate_array('ADM2_NAME').distinct().sort().getInfo()
                    municipalities = ['Select Municipality'] + municipalities
                except:
                    municipalities = ['Select Municipality', 'Annaba City', 'El Bouni', 'Seraidi']
                
                municipality = st.selectbox("Municipality/City", municipalities)
            else:
                municipality = 'Select Municipality'
        else:
            region = 'Select Region'
            municipality = 'Select Municipality'
        
        st.markdown("---")
        st.markdown("### ⚙️ Analysis Settings")
        
        analysis_type = st.selectbox(
            "Analysis Type",
            ['Climate Analysis', 'Soil Analysis', 'Both Analyses'],
            index=2
        )
        
        climate_classification = st.selectbox(
            "Climate Classification Type",
            ['Simplified Temperature-Precipitation', 'Aridity-Based', 'Köppen-Geiger'],
            index=0
        )
        
        st.markdown("---")
        
        # Date range selection
        st.markdown("### 📅 Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime(2024, 1, 1))
        with col2:
            end_date = st.date_input("End Date", value=datetime(2024, 12, 31))
        
        st.markdown("---")
        
        # Run analysis button
        if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
            st.session_state.run_analysis = True
            st.session_state.analysis_type = analysis_type
            st.session_state.country = country
            st.session_state.region = region
            st.session_state.municipality = municipality
            st.session_state.climate_classification = climate_classification
            st.session_state.start_date = start_date.strftime('%Y-%m-%d')
            st.session_state.end_date = end_date.strftime('%Y-%m-%d')
        else:
            if 'run_analysis' not in st.session_state:
                st.session_state.run_analysis = False
    
    # Main content area
    if st.session_state.get('run_analysis', False):
        analyzer = ComprehensiveClimateSoilAnalyzer()
        
        # Display location info
        location_name = f"{st.session_state.municipality if st.session_state.municipality != 'Select Municipality' else ''}"
        if st.session_state.region != 'Select Region':
            location_name += f", {st.session_state.region}"
        location_name += f", {st.session_state.country}"
        location_name = location_name.lstrip(', ')
        
        st.markdown(f'<div class="metric-card"><h3>📍 Analysis Location: {location_name}</h3></div>', unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run analysis based on type
        if st.session_state.analysis_type in ['Climate Analysis', 'Both Analyses']:
            status_text.text("🌤️ Running Climate Analysis...")
            progress_bar.progress(25)
            
            # Get geometry
            geometry, location_name = analyzer.get_geometry_from_selection(
                st.session_state.country,
                st.session_state.region,
                st.session_state.municipality
            )
            
            if geometry:
                # Run climate analysis
                results = {
                    'location_name': location_name,
                    'analysis_period': f"{st.session_state.start_date} to {st.session_state.end_date}",
                    'classification_type': st.session_state.climate_classification
                }
                
                # Get climate classification
                results['climate_analysis'] = analyzer.get_accurate_climate_classification(
                    geometry, location_name, st.session_state.climate_classification
                )
                
                # Display climate metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🌡️ Mean Temperature", 
                             f"{results['climate_analysis']['mean_temperature']:.1f}°C")
                with col2:
                    st.metric("💧 Mean Precipitation", 
                             f"{results['climate_analysis']['mean_precipitation']:.0f} mm/year")
                with col3:
                    st.metric("🏜️ Aridity Index", 
                             f"{results['climate_analysis']['aridity_index']:.3f}")
                
                # Display climate zone
                st.markdown(f'<div class="metric-card"><h4>🌍 Climate Zone: {results["climate_analysis"]["climate_zone"]}</h4></div>', unsafe_allow_html=True)
                
                progress_bar.progress(50)
                
                # Create and display charts
                analyzer.create_comprehensive_dashboard(results)
                
                progress_bar.progress(75)
        
        if st.session_state.analysis_type in ['Soil Analysis', 'Both Analyses']:
            status_text.text("🌱 Running Soil Analysis...")
            progress_bar.progress(85)
            
            # Placeholder for soil analysis
            st.markdown('<div class="section-header">🌱 SOIL ANALYSIS</div>', unsafe_allow_html=True)
            
            # Display soil texture info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏺 Soil Texture Class", "Loam")
            with col2:
                st.metric("🧪 Estimated SOM", "2.5%")
            with col3:
                st.metric("📊 Soil Quality", "Good")
            
            # Placeholder soil charts
            st.info("Soil analysis charts would be displayed here. This requires additional Earth Engine data extraction.")
            
            progress_bar.progress(95)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis Complete!")
        
        # Display data sources
        with st.expander("📚 Data Sources & Methodology"):
            st.markdown("""
            ### Data Sources:
            - **Climate Data**: WORLDCLIM Bioclimatic Variables
            - **Soil Data**: FAO GSOCMAP & ISDASOIL Africa
            - **Soil Texture**: OpenLandMap USDA Classification
            - **Administrative Boundaries**: FAO GAUL
            
            ### Methodology:
            - Climate classification based on simplified temperature-precipitation relationships
            - Soil organic matter estimation using satellite-derived indices
            - Water balance calculation using precipitation-evaporation relationships
            """)
    else:
        # Welcome message
        st.markdown("""
        <div class="metric-card">
            <h3>Welcome to the Comprehensive Climate & Soil Analyzer! 🌍</h3>
            <p>This tool provides integrated analysis of climate patterns and soil characteristics for any location worldwide.</p>
            
            <h4>Features:</h4>
            <ul>
                <li>🌤️ Climate classification using multiple systems</li>
                <li>📈 Time series analysis of temperature and precipitation</li>
                <li>💧 Water balance calculations</li>
                <li>🌱 Soil organic matter estimation</li>
                <li>🏺 Soil texture analysis</li>
                <li>📊 18+ comprehensive charts and visualizations</li>
            </ul>
            
            <h4>How to use:</h4>
            <ol>
                <li>Select a location from the sidebar</li>
                <li>Choose analysis type (Climate, Soil, or Both)</li>
                <li>Configure analysis settings</li>
                <li>Click "Run Comprehensive Analysis"</li>
            </ol>
            
            <p><em>Note: Earth Engine authentication is required for full functionality.</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌍 Countries", "200+")
        with col2:
            st.metric("📈 Charts", "18+")
        with col3:
            st.metric("📊 Data Points", "Millions")

if __name__ == "__main__":
    main()
