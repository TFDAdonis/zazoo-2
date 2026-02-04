import streamlit as st
import pandas as pd
import numpy as np
import json
import traceback
import sys
import subprocess

# Check and install missing packages
required_packages = ['earthengine-api', 'plotly', 'matplotlib']

for package in required_packages:
    try:
        if package == 'earthengine-api':
            import ee
        elif package == 'plotly':
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.subplots import make_subplots
        elif package == 'matplotlib':
            import matplotlib.pyplot as plt
    except ImportError:
        st.warning(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            if package == 'earthengine-api':
                import ee
            elif package == 'plotly':
                import plotly.graph_objects as go
                import plotly.express as px
                from plotly.subplots import make_subplots
            elif package == 'matplotlib':
                import matplotlib.pyplot as plt
            st.success(f"✅ {package} installed successfully")
        except:
            st.error(f"Failed to install {package}")

# Try to import seaborn, but make it optional
try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    st.warning("⚠️ Seaborn not available. Some visualizations may be limited.")

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

# Simplified Earth Engine initialization (without credentials for now)
def initialize_earth_engine():
    """Initialize Earth Engine with fallback options"""
    try:
        # Try to initialize without credentials first
        ee.Initialize()
        return True
    except Exception as e:
        try:
            # Try to authenticate if not initialized
            ee.Authenticate()
            ee.Initialize()
            return True
        except:
            st.warning("⚠️ Earth Engine not initialized. Running in demo mode with simulated data.")
            return False

# Initialize Earth Engine
if 'ee_initialized' not in st.session_state:
    with st.spinner("Initializing Earth Engine..."):
        st.session_state.ee_initialized = initialize_earth_engine()

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
        'fertilizer': 'NPK 100-120-60 kg/ha + Zinc',
        'spacing': '20-25 cm between rows, 2-3 cm between plants'
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
        'fertilizer': 'NPK 150-80-100 kg/ha + Sulfur',
        'spacing': '75 cm between rows, 20-25 cm between plants'
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
        'fertilizer': 'NPK 120-60-60 kg/ha + Zinc',
        'spacing': '20 x 20 cm for transplanted rice'
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
        'fertilizer': 'NPK 120-80-150 kg/ha + Calcium',
        'spacing': '60-90 cm between rows, 45-60 cm between plants'
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
        'fertilizer': 'NPK 150-100-200 kg/ha',
        'spacing': '75-90 cm between rows, 25-30 cm between plants'
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
        'fertilizer': 'NPK 80-60-40 kg/ha',
        'spacing': '15-20 cm between rows'
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
        'fertilizer': 'NPK 30-80-60 kg/ha + Rhizobium inoculation',
        'spacing': '45-75 cm between rows, 3-5 cm between plants'
    }
}

# Soil texture classes
SOIL_TEXTURE_CLASSES = {
    1: 'Clay', 2: 'Sandy clay', 3: 'Silty clay', 4: 'Clay loam', 5: 'Sandy clay loam',
    6: 'Silty clay loam', 7: 'Loam', 8: 'Sandy loam', 9: 'Silt loam', 10: 'Silt',
    11: 'Loamy sand', 12: 'Sand'
}

class AgriculturalAnalyzer:
    def __init__(self):
        self.config = {
            'default_start_date': '2020-01-01',
            'default_end_date': '2023-12-31',
            'scale': 1000,
            'max_pixels': 1e6
        }

    def calculate_crop_suitability_score(self, moisture_value, som_value, texture_value, temp_value, crop_req):
        """Calculate comprehensive crop suitability score"""
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
        disease_risk = self.calculate_disease_risk_index(s_m, s_om, s_t, s_temp)

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

    def calculate_disease_risk_index(self, s_m, s_om, s_t, s_temp):
        """Calculate disease risk index"""
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

        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        crops = list(CROP_REQUIREMENTS.keys())
        for idx, crop_name in enumerate(crops):
            crop_req = CROP_REQUIREMENTS[crop_name]
            
            # Calculate suitability with disease risk
            suitability_analysis = self.calculate_crop_suitability_score(
                moisture_value, som_value, texture_value, temp_value, crop_req)

            # Generate management strategies
            management_strategies = self.generate_management_strategies(crop_name, suitability_analysis, crop_req)

            analysis_results[crop_name] = {
                'suitability_analysis': suitability_analysis,
                'management_strategies': management_strategies,
                'crop_requirements': crop_req
            }
            
            progress_bar.progress((idx + 1) / len(crops))
        
        progress_bar.empty()
        progress_text.empty()
        
        return analysis_results

    def generate_management_strategies(self, crop_name, suitability_analysis, crop_req):
        """Generate tailored management strategies"""
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
            texture_name = "Loam"
        
        return crop_texture_scores.get(texture_name, 0.5)

    def calculate_temp_score(self, temp_meas, temp_opt, temp_tol):
        """Calculate temperature suitability score"""
        diff = abs(temp_meas - temp_opt)
        if diff <= 0:
            return 1.0
        if diff <= temp_tol:
            return max(0, 1 - (diff / temp_tol))
        return 0.0

    def get_simulated_climate_data(self, location_name):
        """Get simulated climate data for demonstration"""
        # Simulate based on location name
        if 'algeria' in location_name.lower() or 'morocco' in location_name.lower():
            return {
                'climate_zone': 'Mediterranean',
                'mean_temperature': 19.5,
                'mean_precipitation': 635,
                'aridity_index': 1.52
            }
        elif 'kenya' in location_name.lower() or 'tanzania' in location_name.lower():
            return {
                'climate_zone': 'Tropical',
                'mean_temperature': 23.0,
                'mean_precipitation': 1200,
                'aridity_index': 2.15
            }
        else:
            return {
                'climate_zone': 'Temperate',
                'mean_temperature': 18.0,
                'mean_precipitation': 800,
                'aridity_index': 1.57
            }

    def get_simulated_groundwater_data(self, location_name):
        """Get simulated groundwater data for demonstration"""
        import random
        
        categories = ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
        weights = [0.2, 0.3, 0.35, 0.15]  # Probability weights
        
        category = random.choices(categories, weights=weights, k=1)[0]
        
        if category == 'VERY HIGH':
            score = random.uniform(0.75, 0.95)
            recharge = random.uniform(200, 300)
        elif category == 'HIGH':
            score = random.uniform(0.6, 0.75)
            recharge = random.uniform(150, 200)
        elif category == 'MODERATE':
            score = random.uniform(0.45, 0.6)
            recharge = random.uniform(100, 150)
        else:  # LOW
            score = random.uniform(0.2, 0.45)
            recharge = random.uniform(50, 100)
        
        soil_types = ['Sand', 'Sandy Loam', 'Loam', 'Clay Loam', 'Clay']
        soil_type = random.choice(soil_types)
        
        return {
            'score': score,
            'category': category,
            'recharge_mm': recharge,
            'soil_type': soil_type,
            'conductivity': random.uniform(0.5, 25.0),
            'precipitation_mm': random.uniform(200, 1000)
        }

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
            st.caption("Connected to Google Earth Engine")
        else:
            st.warning("⚠️ Running in Demo Mode")
            st.caption("Using simulated data for demonstration")
        
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

    # Main content area
    st.markdown('<h2 class="section-header">📍 Location Selection</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        countries = ["Select Country", "Algeria", "Nigeria", "Kenya", "South Africa", 
                    "Ethiopia", "Egypt", "Morocco", "Tanzania", "Uganda", "Ghana"]
        country = st.selectbox("Select Country", countries)
    
    with col2:
        region_options = ["Select Region"]
        if country != "Select Country":
            # Simulate regions based on country
            if country == "Algeria":
                region_options.extend(["Annaba", "Algiers", "Oran", "Constantine"])
            elif country == "Kenya":
                region_options.extend(["Nairobi", "Mombasa", "Kisumu", "Nakuru"])
            elif country == "Nigeria":
                region_options.extend(["Lagos", "Abuja", "Kano", "Ibadan"])
            else:
                region_options.extend(["Region 1", "Region 2", "Region 3"])
        region = st.selectbox("Select Region/State", region_options)
    
    col3, col4 = st.columns(2)
    
    with col3:
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
            # Default values
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
        else:
            with st.spinner("Running analysis..."):
                # Create location name
                location_parts = []
                if municipality != "Select Municipality":
                    location_parts.append(municipality)
                if region != "Select Region":
                    location_parts.append(region)
                location_parts.append(country)
                location_name = ", ".join(location_parts)
                
                # Create analyzer instance
                analyzer = AgriculturalAnalyzer()
                
                # Store analysis results
                st.session_state['analysis_results'] = {
                    'location_name': location_name,
                    'analysis_type': analysis_type,
                    'soil_params': {
                        'moisture': moisture_val,
                        'organic_matter': som_val,
                        'texture': texture_val,
                        'temperature': temp_val
                    },
                    'analyzer': analyzer
                }
                
                st.success(f"✅ Analysis completed for {location_name}!")
                st.rerun()

    # Display results if analysis completed
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        analyzer = results['analyzer']
        location_name = results['location_name']
        analysis_type = results['analysis_type']
        soil_params = results['soil_params']
        
        st.markdown(f'<h2 class="section-header">📊 Analysis Results for {location_name}</h2>', unsafe_allow_html=True)
        
        if analysis_type == "Groundwater Potential":
            st.markdown("### 💧 Groundwater Potential Analysis")
            
            with st.spinner("Analyzing groundwater potential..."):
                gw_results = analyzer.get_simulated_groundwater_data(location_name)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                color_map = {
                    'VERY HIGH': 'green',
                    'HIGH': 'lightgreen',
                    'MODERATE': 'orange',
                    'LOW': 'red'
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
            with st.expander("📈 Detailed Analysis"):
                st.markdown(f"**Precipitation:** {gw_results['precipitation_mm']:.0f} mm/year")
                st.markdown(f"**Recharge Efficiency:** {(gw_results['recharge_mm'] / gw_results['precipitation_mm'] * 100):.1f}%")
                
                # Create a gauge chart for groundwater score
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gw_results['score'] * 100,
                    title={'text': "Groundwater Potential Score"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 45], 'color': "red"},
                            {'range': [45, 60], 'color': "orange"},
                            {'range': [60, 75], 'color': "yellow"},
                            {'range': [75, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': gw_results['score'] * 100
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
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
                
        elif analysis_type == "Crop Suitability" or analysis_type == "Comprehensive Analysis":
            # Display climate information
            st.markdown("### 🌤️ Climate Information")
            climate_data = analyzer.get_simulated_climate_data(location_name)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Climate Zone", climate_data['climate_zone'])
            with col2:
                st.metric("Mean Temperature", f"{climate_data['mean_temperature']}°C")
            with col3:
                st.metric("Annual Precipitation", f"{climate_data['mean_precipitation']} mm")
            
            # Display soil parameters
            st.markdown("### 🌱 Soil Parameters")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Moisture", f"{soil_params['moisture']:.3f} m³/m³")
            with col2:
                st.metric("Organic Matter", f"{soil_params['organic_matter']:.2f}%")
            with col3:
                st.metric("Texture", soil_params['texture'])
            with col4:
                st.metric("Temperature", f"{soil_params['temperature']}°C")
            
            # Run crop analysis
            st.markdown("### 🌾 Crop Suitability Analysis")
            
            with st.spinner("Analyzing crop suitability..."):
                crop_results = analyzer.analyze_all_crops(
                    soil_params['moisture'],
                    soil_params['organic_matter'],
                    soil_params['texture'],
                    soil_params['temperature'],
                    location_name
                )
            
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
                    
                    # Show crop requirements
                    crop_req = CROP_REQUIREMENTS[crop['Crop']]
                    management = crop_results[crop['Crop']]['management_strategies']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Crop Requirements:**")
                        st.markdown(f"- Water Needs: {crop_req['water_needs']}")
                        st.markdown(f"- Maturity Days: {crop_req['maturity_days']}")
                        st.markdown(f"- Fertilizer: {crop_req['fertilizer']}")
                        st.markdown(f"- Spacing: {crop_req['spacing']}")
                        st.markdown(f"- Notes: {crop_req['notes']}")
                    
                    with col2:
                        st.markdown("**Management Strategies:**")
                        for strategy in management:
                            st.markdown(f"- {strategy}")
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"crop_suitability_{location_name.replace(' ', '_').replace(',', '')}.csv",
                mime="text/csv"
            )
            
            # Visualizations
            st.markdown("#### 📈 Visualizations")
            
            tab1, tab2 = st.tabs(["Suitability vs Disease Risk", "Top Crops Chart"])
            
            with tab1:
                # Suitability vs Disease Risk Scatter Plot
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
            
            with tab2:
                # Bar chart of top crops
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
                fig2.update_layout(
                    height=400, 
                    yaxis_range=[0, 1],
                    title="Top 10 Crops by Suitability Score"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # If comprehensive analysis, also show groundwater
            if analysis_type == "Comprehensive Analysis":
                st.markdown("---")
                st.markdown("### 💧 Groundwater Potential (Comprehensive Analysis)")
                
                gw_results = analyzer.get_simulated_groundwater_data(location_name)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Groundwater Potential", gw_results['category'], f"Score: {gw_results['score']:.2f}")
                with col2:
                    st.metric("Annual Recharge", f"{gw_results['recharge_mm']:.0f} mm")
                
                # Overall assessment
                st.markdown("#### 📈 Overall Assessment")
                
                # Calculate overall agricultural potential
                crop_scores = df['Suitability Score'].mean()
                gw_score = gw_results['score']
                
                # Weighted average
                overall_score = (crop_scores * 0.7 + gw_score * 0.3)
                
                if overall_score > 0.7:
                    st.success(f"""
                    **Excellent Agricultural Potential** (Overall Score: {overall_score:.2f})
                    
                    This location shows strong potential for agricultural development with good crop suitability 
                    and adequate water resources. Consider diversified farming with high-value crops.
                    """)
                elif overall_score > 0.5:
                    st.warning(f"""
                    **Moderate Agricultural Potential** (Overall Score: {overall_score:.2f})
                    
                    This location has moderate potential. Focus on soil improvement and water conservation 
                    measures. Consider crops with moderate water requirements.
                    """)
                else:
                    st.error(f"""
                    **Limited Agricultural Potential** (Overall Score: {overall_score:.2f})
                    
                    Agricultural development in this area may be challenging. Consider alternative land uses 
                    or specialized drought-resistant crops with extensive irrigation infrastructure.
                    """)

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            <p>🌾 Comprehensive Agricultural Analyzer v1.0</p>
            <p>Agricultural Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)

    # Requirements info in sidebar
    with st.sidebar:
        with st.expander("📦 Installation Requirements"):
            st.code("""streamlit
pandas
numpy
plotly
matplotlib""")
            
            if st.button("Show requirements.txt"):
                requirements = """streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
matplotlib>=3.7.0"""
                st.download_button(
                    label="Download requirements.txt",
                    data=requirements,
                    file_name="requirements.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
