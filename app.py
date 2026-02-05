import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Custom CSS for better appearance
st.set_page_config(page_title="Comprehensive Climate & Soil Analysis", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #32CD32;
        margin-top: 1.5rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E90FF;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #32CD32;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fffaf0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF8C00;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Earth Engine Initialization for Streamlit
def initialize_earth_engine():
    """Initialize Earth Engine in Streamlit"""
    try:
        # For Streamlit Cloud, you need service account credentials
        # Replace with your own service account credentials
        service_account = st.secrets.get("EE_SERVICE_ACCOUNT", None)
        private_key = st.secrets.get("EE_PRIVATE_KEY", None)
        
        if service_account and private_key:
            credentials = ee.ServiceAccountCredentials(service_account, key_data=private_key)
            ee.Initialize(credentials)
        else:
            ee.Initialize()
        
        return True
    except Exception as e:
        st.error(f"Earth Engine initialization failed: {e}")
        st.info("To use Earth Engine in Streamlit Cloud, you need to:")
        st.info("1. Create a service account in Google Cloud")
        st.info("2. Add the service account email and private key to Streamlit secrets")
        return False

# Initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    st.session_state.ee_initialized = initialize_earth_engine()

if not st.session_state.ee_initialized:
    st.error("Earth Engine not initialized. Please check your credentials.")
    st.stop()

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

    # CLIMATE ANALYSIS METHODS
    def classify_climate_simplified(self, temp, precip, aridity):
        """Climate classification"""
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

    def get_accurate_climate_classification(self, geometry, location_name, classification_type='Simplified Temperature-Precipitation'):
        """Get climate classification"""
        with st.spinner(f"Getting climate classification for {location_name}..."):
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
                mean_aridity = stats.get('bio12', 0) / (stats.get('bio01', 0) + 33) if (stats.get('bio01', 0) + 33) != 0 else 1.5

                if classification_type == 'Simplified Temperature-Precipitation':
                    climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
                elif classification_type == 'Aridity-Based':
                    if mean_aridity > 0.65:
                        climate_class = 1
                    elif mean_aridity > 0.5:
                        climate_class = 2
                    elif mean_aridity > 0.2:
                        climate_class = 3
                    elif mean_aridity > 0.03:
                        climate_class = 4
                    elif mean_aridity > 0.005:
                        climate_class = 5
                    else:
                        climate_class = 6
                else:  # Köppen-Geiger
                    if mean_temp > 18:
                        if mean_precip > 1800:
                            climate_class = 1
                        elif mean_precip > 1000:
                            climate_class = 2
                        elif mean_precip > 750:
                            climate_class = 3
                        else:
                            climate_class = 4
                    elif mean_aridity < 0.2:
                        if mean_aridity < 0.03:
                            climate_class = 4
                        else:
                            climate_class = 5
                    elif mean_temp > 0:
                        if mean_precip > 800:
                            climate_class = 6
                        elif mean_precip > 500:
                            climate_class = 7
                        else:
                            climate_class = 8
                    elif mean_temp > -10:
                        if mean_precip > 500:
                            climate_class = 9
                        else:
                            climate_class = 10
                    else:
                        climate_class = 11

                climate_zone = self.climate_class_names[classification_type].get(climate_class, 'Unknown')

                climate_analysis = {
                    'climate_zone': climate_zone,
                    'climate_class': climate_class,
                    'mean_temperature': round(mean_temp, 1),
                    'mean_precipitation': round(mean_precip),
                    'aridity_index': round(mean_aridity, 3),
                    'classification_type': classification_type,
                }

                st.success(f"Climate classification: {climate_zone}")
                return climate_analysis

            except Exception as e:
                st.error(f"Climate classification failed: {e}")
                return {
                    'climate_zone': "Tropical Dry (Temp > 18°C, Precip 500-1000mm)",
                    'climate_class': 4,
                    'mean_temperature': 19.5,
                    'mean_precipitation': 635,
                    'aridity_index': 1.52,
                    'classification_type': classification_type,
                }

    def create_climate_classification_chart(self, classification_type, location_name, climate_data):
        """Create climate classification visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Climate Classification Analysis - {location_name}\n{classification_type}',
                    fontsize=16, fontweight='bold', y=0.95)

        current_class = climate_data['climate_class']
        current_zone = climate_data['climate_zone']

        ax1.barh([0], [1], color=self.climate_palettes[classification_type][current_class-1], alpha=0.7)
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Class {current_class}'])
        ax1.set_xlabel('Representation')
        ax1.set_title(f'Current Climate Zone: {current_zone}', fontsize=12, fontweight='bold')
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
        ax2.set_title('Climate Parameters Radar Chart', fontsize=12, fontweight='bold')
        ax2.legend()

        ax3.scatter(climate_data['mean_temperature'], climate_data['mean_precipitation'],
                   c=self.climate_palettes[classification_type][current_class-1], s=200, alpha=0.7)
        ax3.set_xlabel('Mean Temperature (°C)')
        ax3.set_ylabel('Mean Precipitation (mm/year)')
        ax3.set_title('Temperature vs Precipitation', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.annotate(f'Class {current_class}',
                    (climate_data['mean_temperature'], climate_data['mean_precipitation']),
                    xytext=(10, 10), textcoords='offset points')

        ax4.axis('off')
        legend_text = "CLIMATE CLASSIFICATION LEGEND\n\n"
        for class_id, class_name in self.climate_class_names[classification_type].items():
            color = self.climate_palettes[classification_type][class_id-1]
            marker = '▶' if class_id == current_class else '○'
            legend_text += f"{marker} Class {class_id}: {class_name}\n"

        ax4.text(0.1, 0.9, legend_text, transform=ax4.transAxes, fontsize=9,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
                verticalalignment='top')

        st.pyplot(fig)
        plt.close(fig)

    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry based on selection"""
        try:
            if municipality != 'Select Municipality':
                feature = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                       .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                       .filter(ee.Filter.eq('ADM2_NAME', municipality)) \
                                       .first()
                geometry = feature.geometry()
                location_name = f"{municipality}, {region}, {country}"
                st.info(f"Selected: {location_name}")
                return geometry, location_name

            elif region != 'Select Region':
                feature = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                       .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                       .first()
                geometry = feature.geometry()
                location_name = f"{region}, {country}"
                st.info(f"Selected: {location_name}")
                return geometry, location_name

            elif country != 'Select Country':
                feature = FAO_GAUL.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                geometry = feature.geometry()
                location_name = f"{country}"
                st.info(f"Selected: {location_name}")
                return geometry, location_name

            else:
                st.warning("Please select a country")
                return None, None

        except Exception as e:
            st.error(f"Geometry error: {e}")
            return None, None

    def run_accurate_analysis(self, country, region='Select Region', municipality='Select Municipality',
                            start_date=None, end_date=None, classification_type='Simplified Temperature-Precipitation'):
        """Run climate analysis"""
        if start_date is None:
            start_date = self.config['default_start_date']
        if end_date is None:
            end_date = self.config['default_end_date']

        st.subheader(f"Climate Analysis for {country}")
        if region != 'Select Region':
            st.write(f"Region/State: {region}")
        if municipality != 'Select Municipality':
            st.write(f"Municipality/City: {municipality}")
        st.write(f"Classification: {classification_type}")
        st.write(f"Period: {start_date} to {end_date}")

        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            st.error("Could not get geometry for the selected location")
            return None

        results = {
            'location_name': location_name,
            'analysis_period': f"{start_date} to {end_date}",
            'classification_type': classification_type
        }

        # Climate Classification
        results['climate_analysis'] = self.get_accurate_climate_classification(
            geometry, location_name, classification_type)

        return results

    def plot_accurate_results(self, results):
        """Plot climate results"""
        if not results:
            st.error("No results to plot")
            return

        self.create_climate_classification_chart(
            results['classification_type'],
            results['location_name'],
            results['climate_analysis']
        )

        # Print summary
        st.subheader("Climate Analysis Summary")
        climate = results['climate_analysis']
        st.write(f"**Location:** {results['location_name']}")
        st.write(f"**Climate Zone:** {climate['climate_zone']}")
        st.write(f"**Mean Temperature:** {climate['mean_temperature']:.1f}°C")
        st.write(f"**Mean Precipitation:** {climate['mean_precipitation']:.0f} mm/year")
        st.write(f"**Aridity Index:** {climate['aridity_index']:.3f}")

    # SOIL ANALYSIS METHODS
    def get_reference_soil_data_improved(self, geometry, region_name):
        """Get reference soil data"""
        with st.spinner(f"Getting soil data for {region_name}..."):
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
                        st.warning(f"Could not get {property_name}: {str(e)}")
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
                        st.warning(f"Could not get texture: {str(e)}")
                        return 7

                soc_stock_val = get_soil_stats(soc_stock, 'soc_stock')
                texture_val = get_texture_mode(texture_clipped)

                soc_percent, som_percent = self.calculate_soc_to_som(soc_stock_val, BULK_DENSITY, depth)
                clay_val, silt_val, sand_val = self.estimate_texture_components(texture_val)

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
                    'data_sources': {
                        'soil_organic_carbon': soil_source,
                        'soil_texture': DATA_SOURCES['soil_texture']
                    }
                }

                st.success(f"Soil data retrieved for {region_name}")
                return soil_data

            except Exception as e:
                st.error(f"Error getting soil data: {str(e)}")
                return None

    def calculate_soc_to_som(self, soc_stock_t_ha, bulk_density, depth_cm):
        """Calculate SOC% and SOM% from SOC stock"""
        try:
            soc_percent = soc_stock_t_ha / (bulk_density * depth_cm * 100)
            som_percent = soc_percent * SOC_TO_SOM_FACTOR * 100
            return soc_percent * 100, som_percent
        except Exception as e:
            st.error(f"Error in SOC to SOM calculation: {e}")
            return 0, 0

    def estimate_texture_components(self, texture_class):
        """Estimate clay, silt, sand percentages"""
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

    def display_comprehensive_analysis(self, soil_data):
        """Display soil analysis results"""
        if not soil_data:
            st.error("No soil data to display")
            return

        st.subheader(f"Soil Analysis for {soil_data['region_name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Soil Properties")
            st.write(f"**Soil Texture:** {soil_data['texture_name']}")
            st.write(f"**SOC Stock:** {soil_data['soc_stock']:.1f} t/ha")
            st.write(f"**Soil Organic Matter:** {soil_data['soil_organic_matter']:.2f}%")
            st.write(f"**Bulk Density:** {soil_data['bulk_density']} g/cm³")
            st.write(f"**Depth:** {soil_data['depth_cm']} cm")

        with col2:
            st.markdown("### Texture Composition")
            texture_values = [soil_data['clay_content'], soil_data['silt_content'], soil_data['sand_content']]
            texture_labels = ['Clay', 'Silt', 'Sand']
            colors = ['#8B4513', '#DEB887', '#F4A460']

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(texture_labels, texture_values, color=colors)
            ax.set_ylabel('Percentage (%)')
            ax.set_ylim(0, 100)
            ax.set_title('Soil Texture Composition')
            
            for i, v in enumerate(texture_values):
                ax.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig)
            plt.close(fig)

        st.markdown("### Data Sources")
        for source_type, source_info in soil_data['data_sources'].items():
            if isinstance(source_info, dict):
                st.write(f"**{source_type.replace('_', ' ').title()}:** {source_info['name']}")
                st.write(f"*Citation:* {source_info['citation']}")

    def run_comprehensive_soil_analysis(self, country, region='Select Region', municipality='Select Municipality'):
        """Run soil analysis"""
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            st.error("Could not get geometry for the selected location")
            return None

        soil_data = self.get_reference_soil_data_improved(geometry, location_name)

        if soil_data:
            self.display_comprehensive_analysis(soil_data)
            return soil_data
        else:
            st.error("Failed to retrieve soil data")
            return None

# Streamlit Interface Functions
def get_country_list():
    """Get list of all countries"""
    try:
        countries = FAO_GAUL.aggregate_array('ADM0_NAME').distinct().sort().getInfo()
        return ['Select Country'] + countries
    except Exception as e:
        st.error(f"Error getting country list: {e}")
        return ['Select Country', 'Algeria', 'Nigeria', 'Kenya', 'South Africa']

def get_region_list(country):
    """Get list of regions/states for a country"""
    if country == 'Select Country':
        return ['Select Region']
    try:
        regions = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                .aggregate_array('ADM1_NAME').distinct().sort().getInfo()
        return ['Select Region'] + regions
    except Exception as e:
        st.error(f"Error getting regions for {country}: {e}")
        return ['Select Region']

def get_municipality_list(country, region):
    """Get list of municipalities for a region"""
    if region == 'Select Region':
        return ['Select Municipality']
    try:
        municipalities = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                       .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                       .aggregate_array('ADM2_NAME').distinct().sort().getInfo()
        return ['Select Municipality'] + municipalities
    except Exception as e:
        st.error(f"Error getting municipalities for {region}: {e}")
        return ['Select Municipality']

# Main Streamlit App
def main():
    st.markdown('<h1 class="main-header">🌍 Comprehensive Climate & Soil Analysis Tool</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Integrated Approach:</strong> Climate Analysis + Soil Organic Matter Analysis<br>
    <strong>Features:</strong> Climate classification, Soil properties analysis, Data visualization
    </div>
    """, unsafe_allow_html=True)

    analyzer = ComprehensiveClimateSoilAnalyzer()

    # Create selection interface
    col1, col2, col3 = st.columns(3)
    
    with col1:
        countries = get_country_list()
        selected_country = st.selectbox(
            "Select Country",
            options=countries,
            index=countries.index('Algeria') if 'Algeria' in countries else 0
        )
    
    with col2:
        if selected_country != 'Select Country':
            regions = get_region_list(selected_country)
            selected_region = st.selectbox(
                "Select Region/State",
                options=regions,
                index=0
            )
        else:
            selected_region = 'Select Region'
    
    with col3:
        if selected_region != 'Select Region':
            municipalities = get_municipality_list(selected_country, selected_region)
            selected_municipality = st.selectbox(
                "Select Municipality/City",
                options=municipalities,
                index=0
            )
        else:
            selected_municipality = 'Select Municipality'

    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        options=['Climate Analysis', 'Soil Analysis', 'Both Analyses'],
        index=2
    )

    if analysis_type in ['Climate Analysis', 'Both Analyses']:
        climate_classification = st.selectbox(
            "Climate Classification System",
            options=['Simplified Temperature-Precipitation', 'Aridity-Based', 'Köppen-Geiger'],
            index=0
        )

    # Run analysis button
    if st.button("Run Comprehensive Analysis", type="primary"):
        if selected_country == 'Select Country':
            st.warning("Please select a country first.")
        else:
            with st.spinner("Running analysis..."):
                results = {}

                if analysis_type in ['Climate Analysis', 'Both Analyses']:
                    st.markdown("### 🌤️ Climate Analysis Results")
                    climate_results = analyzer.run_accurate_analysis(
                        selected_country,
                        selected_region,
                        selected_municipality,
                        classification_type=climate_classification
                    )
                    if climate_results:
                        analyzer.plot_accurate_results(climate_results)
                        results['climate'] = climate_results
                    else:
                        st.error("Climate analysis failed")

                if analysis_type in ['Soil Analysis', 'Both Analyses']:
                    st.markdown("### 🌱 Soil Analysis Results")
                    soil_results = analyzer.run_comprehensive_soil_analysis(
                        selected_country,
                        selected_region,
                        selected_municipality
                    )
                    if soil_results:
                        results['soil'] = soil_results
                    else:
                        st.error("Soil analysis failed")

                if results:
                    st.success("Analysis completed successfully!")
                    
                    # Option to download results
                    if st.button("Download Results Summary"):
                        # Create summary DataFrame
                        summary_data = {}
                        if 'climate' in results:
                            climate = results['climate']['climate_analysis']
                            summary_data.update({
                                'Climate Zone': climate['climate_zone'],
                                'Mean Temperature (°C)': climate['mean_temperature'],
                                'Mean Precipitation (mm/year)': climate['mean_precipitation'],
                                'Aridity Index': climate['aridity_index']
                            })
                        
                        if 'soil' in results:
                            soil = results['soil']
                            summary_data.update({
                                'Soil Texture': soil['texture_name'],
                                'SOC Stock (t/ha)': soil['soc_stock'],
                                'Soil Organic Matter (%)': soil['soil_organic_matter'],
                                'Clay Content (%)': soil['clay_content'],
                                'Silt Content (%)': soil['silt_content'],
                                'Sand Content (%)': soil['sand_content']
                            })
                        
                        df_summary = pd.DataFrame([summary_data])
                        csv = df_summary.to_csv(index=False)
                        
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="analysis_results.csv",
                            mime="text/csv"
                        )

if __name__ == "__main__":
    main()
