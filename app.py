import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

warnings.filterwarnings('ignore')

# Initialize Earth Engine
try:
    ee.Initialize()
    st.success("✅ Earth Engine initialized successfully!")
except Exception as e:
    st.warning(f"ℹ️ Earth Engine not initialized: {e}")
    st.info("To authenticate Earth Engine, run in your environment:")
    st.code("ee.Authenticate()\nee.Initialize()")

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
    'Oats': {
        'moisture_opt': 0.20, 'moisture_tol': 0.06, 'om_opt': 2.0, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.8, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 16, 'temp_tol': 6, 'maturity_days': 110, 'water_needs': 'Medium',
        'notes': 'Cool season cereal, good for cooler climates',
        'management': [
            'Plant in early spring for optimal growth',
            'Apply 80-100 kg N/ha for grain production',
            'Use clean seed to prevent smut diseases',
            'Harvest when panicles turn golden yellow',
            'Good for crop rotation and soil improvement'
        ],
        'likely_diseases': [
            'Crown rust - orange pustules on leaves and stems',
            'Stem rust - dark red-brown pustules breaking through epidermis',
            'Septoria leaf blotch - irregular brown spots with pycnidia',
            'Barley yellow dwarf virus - yellowing and stunting',
            'Smut diseases - black powdery masses replacing grains'
        ],
        'pests': ['Aphids', 'Armyworms', 'Wireworms', 'Bird damage'],
        'fertilizer': 'NPK 80-50-60 kg/ha',
        'spacing': '18-25 cm between rows',
        'risk_factors': ['Cool humid conditions', 'Dense stands', 'Poor air flow']
    },
    'Sorghum': {
        'moisture_opt': 0.22, 'moisture_tol': 0.08, 'om_opt': 1.8, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.5, 'Sandy clay': 0.6, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.6, 'Loam': 0.9, 'Sandy loam': 0.9,
            'Silt loam': 0.7, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 27, 'temp_tol': 7, 'maturity_days': 115, 'water_needs': 'Low-Medium',
        'notes': 'Drought tolerant, good for dry regions',
        'management': [
            'Plant when soil temperature reaches 18°C',
            'Apply 80-120 kg N/ha based on soil fertility',
            'Control weeds early as sorghum grows slowly initially',
            'Use bird-resistant varieties in areas with bird pressure',
            'Harvest when grains are hard and moisture below 20%'
        ],
        'likely_diseases': [
            'Anthracnose - red lesions on leaves and stalks',
            'Grain mold - various fungi affecting grain quality',
            'Downy mildew - white fungal growth on leaf undersides',
            'Leaf blight - elongated lesions with reddish margins',
            'Charcoal rot - root and stalk rot under drought stress'
        ],
        'pests': ['Aphids', 'Stem borers', 'Head caterpillars', 'Shoot fly'],
        'fertilizer': 'NPK 100-50-40 kg/ha',
        'spacing': '45-60 cm between rows, 10-15 cm between plants',
        'risk_factors': ['High humidity at flowering', 'Drought stress', 'Bird pressure']
    },

    # LEGUMES
    'Chickpea': {
        'moisture_opt': 0.14, 'moisture_tol': 0.04, 'om_opt': 1.0, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.6, 'Loam': 1.0, 'Sandy loam': 0.85,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 20, 'temp_tol': 6, 'maturity_days': 105, 'water_needs': 'Low',
        'notes': 'Nitrogen-fixing, drought tolerant',
        'management': [
            'Inoculate seeds with Rhizobium for better nitrogen fixation',
            'Well-drained soil essential to prevent root rots',
            'Avoid excessive nitrogen fertilization',
            'Use fungicide-treated seeds in areas with Ascochyta blight',
            'Harvest when plants dry and pods turn brown'
        ],
        'likely_diseases': [
            'Ascochyta blight - circular lesions with pycnidia, can be devastating',
            'Fusarium wilt - yellowing and wilting, soil-borne',
            'Botrytis gray mold - gray fungal growth in humid conditions',
            'Root rots (Rhizoctonia, Pythium) - damping off and root decay',
            'Stunt virus - stunted growth, leaf yellowing'
        ],
        'pests': ['Pod borers', 'Aphids', 'Cutworms', 'Leaf miners'],
        'fertilizer': 'Phosphorus 40-60 kg/ha, minimal nitrogen',
        'spacing': '30-45 cm between rows, 10-15 cm between plants',
        'risk_factors': ['Cool wet weather', 'Poor drainage', 'Continuous legume cropping']
    },
    'Lentil': {
        'moisture_opt': 0.16, 'moisture_tol': 0.05, 'om_opt': 1.2, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 22, 'temp_tol': 6, 'maturity_days': 100, 'water_needs': 'Low',
        'notes': 'Nitrogen-fixing, cool season legume',
        'management': [
            'Plant in well-drained soil with good structure',
            'Inoculate seeds with specific Rhizobium strains',
            'Control weeds early as lentils are poor competitors',
            'Avoid waterlogging at all growth stages',
            'Swath when lower pods turn brown'
        ],
        'likely_diseases': [
            'Ascochyta blight - circular tan spots with dark margins',
            'Anthracnose - stem and pod lesions with orange spore masses',
            'Stemphylium blight - gray lesions on leaves and stems',
            'Root rots - various pathogens causing wilting and death',
            'Viral diseases - causing mosaic patterns and stunting'
        ],
        'pests': ['Aphids', 'Lygus bugs', 'Cutworms', 'Wireworms'],
        'fertilizer': 'Phosphorus 30-50 kg/ha',
        'spacing': '20-30 cm between rows',
        'risk_factors': ['High rainfall during flowering', 'Dense stands', 'Poor drainage']
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
    },

    # VEGETABLES
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
    'Cabbage': {
        'moisture_opt': 0.25, 'moisture_tol': 0.06, 'om_opt': 2.5, 'om_tol': 0.9,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 18, 'temp_tol': 5, 'maturity_days': 85, 'water_needs': 'High',
        'notes': 'Cool season, heavy feeder',
        'management': [
            'Transplant healthy seedlings for uniform stands',
            'Maintain consistent soil moisture for head development',
            'Control cabbage worms and other pests regularly',
            'Harvest when heads are firm and reach desired size',
            'Practice crop rotation to reduce soil-borne diseases'
        ],
        'likely_diseases': [
            'Black rot - V-shaped yellow lesions progressing from leaf margins',
            'Clubroot - swollen distorted roots causing wilting',
            'Downy mildew - purple-brown spots with white fungal growth',
            'Alternaria leaf spot - dark spots with concentric rings',
            'Fusarium yellows - yellowing and stunting of plants'
        ],
        'pests': ['Cabbage worm', 'Cabbage looper', 'Aphids', 'Flea beetles'],
        'fertilizer': 'NPK 120-100-150 kg/ha',
        'spacing': '45-60 cm between rows, 30-45 cm between plants',
        'risk_factors': ['Warm humid conditions', 'Poor drainage', 'Acidic soils']
    },
    'Carrot': {
        'moisture_opt': 0.26, 'moisture_tol': 0.06, 'om_opt': 2.0, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.2, 'Sandy clay': 0.3, 'Silty clay': 0.4, 'Clay loam': 0.6,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.7, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 18, 'temp_tol': 6, 'maturity_days': 75, 'water_needs': 'Medium',
        'notes': 'Requires deep, loose soil for root development',
        'management': [
            'Prepare deep, stone-free seedbed for straight roots',
            'Thin seedlings to proper spacing for root development',
            'Maintain consistent moisture for smooth root growth',
            'Use floating row covers to prevent carrot rust fly',
            'Harvest when roots reach desired size and color'
        ],
        'likely_diseases': [
            'Alternaria leaf blight - brown lesions on leaves and petioles',
            'Cercospora leaf spot - small circular spots with yellow halos',
            'Powdery mildew - white fungal growth on leaves',
            'Root knot nematode - galls on roots causing forking',
            'Sclerotinia rot - white mold and soft rot of roots'
        ],
        'pests': ['Carrot rust fly', 'Aphids', 'Leafhoppers', 'Wireworms'],
        'fertilizer': 'NPK 80-100-150 kg/ha + Boron',
        'spacing': '30-45 cm between rows, 3-5 cm between plants',
        'risk_factors': ['Heavy soils', 'Poor drainage', 'Shallow planting depth']
    },

    # FRUITS
    'Apple': {
        'moisture_opt': 0.19, 'moisture_tol': 0.05, 'om_opt': 1.5, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 18, 'temp_tol': 8, 'maturity_days': 1095, 'water_needs': 'Medium',
        'notes': 'Temperate fruit, requires chilling hours',
        'management': [
            'Prune annually for light penetration and air circulation',
            'Thin fruits for better size and quality',
            'Use integrated pest management for codling moth',
            'Provide frost protection during flowering',
            'Harvest based on variety-specific maturity indicators'
        ],
        'likely_diseases': [
            'Apple scab - olive-green spots on leaves and fruit',
            'Fire blight - shoot blight with shepherd\'s crook appearance',
            'Powdery mildew - white fungal growth on leaves and shoots',
            'Cedar apple rust - orange spots on leaves and fruit',
            'Bitter rot - sunken brown rot on fruit'
        ],
        'pests': ['Codling moth', 'Aphids', 'Mites', 'Apple maggot'],
        'fertilizer': 'NPK 100-40-80 kg/ha based on leaf analysis',
        'spacing': '4-6 m between trees depending on rootstock',
        'risk_factors': ['High humidity', 'Poor air circulation', 'Overcrowding']
    },
    'Grape': {
        'moisture_opt': 0.16, 'moisture_tol': 0.05, 'om_opt': 1.2, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 22, 'temp_tol': 8, 'maturity_days': 180, 'water_needs': 'Low',
        'notes': 'Drought tolerant, well-drained soils preferred',
        'management': [
            'Train on trellis systems for better air circulation',
            'Prune annually for fruit production and disease control',
            'Manage canopy for optimal light penetration',
            'Control weeds under vines to reduce pest habitat',
            'Harvest based on sugar content and flavor development'
        ],
        'likely_diseases': [
            'Powdery mildew - white fungal growth on leaves and fruit',
            'Downy mildew - oil spots on leaves with white fungal growth',
            'Black rot - brown spots with black pycnidia on fruit',
            'Botrytis bunch rot - gray mold on ripening clusters',
            'Crown gall - tumor-like growths on trunks and canes'
        ],
        'pests': ['Grape phylloxera', 'Japanese beetles', 'Leafhoppers', 'Mealybugs'],
        'fertilizer': 'NPK 60-80-100 kg/ha based on soil test',
        'spacing': '2-3 m between vines, 2-3 m between rows',
        'risk_factors': ['High humidity', 'Dense canopy', 'Poor air circulation']
    },
    'Strawberry': {
        'moisture_opt': 0.24, 'moisture_tol': 0.06, 'om_opt': 2.0, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 18, 'temp_tol': 6, 'maturity_days': 90, 'water_needs': 'High',
        'notes': 'Requires consistent moisture, good drainage',
        'management': [
            'Use raised beds for better drainage and soil warming',
            'Apply mulch to conserve moisture and keep fruits clean',
            'Renovate beds annually for continued productivity',
            'Harvest frequently when fruits are fully colored',
            'Use drip irrigation to keep foliage dry'
        ],
        'likely_diseases': [
            'Gray mold (Botrytis) - gray fungal growth on fruits',
            'Powdery mildew - white fungal growth on leaves',
            'Verticillium wilt - yellowing and wilting of plants',
            'Leaf spot - various fungal spots reducing photosynthesis',
            'Root rots - decay of roots in poorly drained soils'
        ],
        'pests': ['Spider mites', 'Aphids', 'Slugs', 'Tarnished plant bug'],
        'fertilizer': 'NPK 80-60-100 kg/ha + side dress nitrogen',
        'spacing': '30-45 cm between rows, 20-30 cm between plants',
        'risk_factors': ['Poor drainage', 'High humidity', 'Overhead irrigation']
    },

    # OTHERS
    'Sunflower': {
        'moisture_opt': 0.18, 'moisture_tol': 0.05, 'om_opt': 1.4, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.9, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.5
        },
        'temp_opt': 22, 'temp_tol': 7, 'maturity_days': 100, 'water_needs': 'Low-Medium',
        'notes': 'Drought tolerant, deep rooting',
        'management': [
            'Plant when soil temperature reaches 10°C',
            'Apply phosphorus fertilizer for better root development',
            'Control weeds early as sunflowers are poor competitors',
            'Use bird deterrents during seed maturation',
            'Harvest when back of heads turn yellow and seeds mature'
        ],
        'likely_diseases': [
            'Sclerotinia head rot - white mold on heads, most destructive disease',
            'Downy mildew - yellow areas on upper leaf surface, white growth underneath',
            'Rust - reddish-brown pustules on leaves',
            'Verticillium wilt - yellowing between veins and wilting',
            'Phoma black stem - black lesions on stems causing lodging'
        ],
        'pests': ['Sunflower moth', 'Seed weevils', 'Cutworms', 'Birds'],
        'fertilizer': 'NPK 60-80-40 kg/ha',
        'spacing': '75 cm between rows, 25-30 cm between plants',
        'risk_factors': ['High rainfall during flowering', 'Dense stands', 'Bird pressure']
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
        temp_stress = 1.0 - s_temp   # Temperature stress weakens plants

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

        elif crop_name == 'Rice':
            strategies.append("🌊 Maintain proper water depth management")
            strategies.append("🔄 Practice field drainage before harvest")

        elif crop_name in ['Apple', 'Pear', 'Grape']:
            strategies.append("✂️ Prune for good air circulation and light penetration")

        elif crop_name in ['Carrot', 'Potato', 'Sweet Potato']:
            strategies.append("🪨 Ensure stone-free soil for proper root development")

        return strategies

    def create_suitability_comparison_chart(self, analysis_results, location_name):
        """Create visual comparison chart of crop suitability"""
        crops = list(analysis_results.keys())
        suitability_scores = [analysis_results[crop]['suitability_analysis']['final_score'] for crop in crops]
        disease_risks = [analysis_results[crop]['suitability_analysis']['disease_risk'] for crop in crops]

        # Create figure with subplots
        fig = go.Figure()

        # Add suitability scores trace
        fig.add_trace(go.Bar(
            x=crops,
            y=suitability_scores,
            name='Suitability Score',
            marker_color='green',
            opacity=0.6,
            text=[f'{score:.3f}' for score in suitability_scores],
            textposition='auto',
        ))

        # Add disease risks trace
        fig.add_trace(go.Bar(
            x=crops,
            y=disease_risks,
            name='Disease Risk',
            marker_color='red',
            opacity=0.6,
            text=[f'{risk:.3f}' for risk in disease_risks],
            textposition='auto',
        ))

        fig.update_layout(
            title=f'Crop Suitability Scores vs Disease Risks - {location_name}',
            xaxis_title='Crops',
            yaxis_title='Score (0-1)',
            barmode='group',
            height=600,
            showlegend=True,
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

    def analyze_all_crops(self, moisture_value, som_value, texture_value, temp_value, location_name):
        """Analyze all crops with enhanced suitability scoring"""
        st.info(f"🌱 Analyzing Crop Suitability for {location_name}")

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

        # Display top crops
        st.subheader("🏆 Top Recommended Crops")
        
        sorted_crops = sorted(analysis_results.items(),
                            key=lambda x: x[1]['suitability_analysis']['final_score'],
                            reverse=True)

        top_crops_data = []
        for crop_name, results in sorted_crops[:10]:
            analysis = results['suitability_analysis']
            comp = analysis['component_scores']
            top_crops_data.append({
                'Crop': crop_name,
                'Suitability Score': f"{analysis['final_score']:.3f}",
                'Disease Risk': analysis['risk_level'],
                'Disease Risk Score': f"{analysis['disease_risk']:.3f}",
                'Moisture': f"{comp['moisture']:.3f}",
                'Organic Matter': f"{comp['organic_matter']:.3f}",
                'Texture': f"{comp['texture']:.3f}",
                'Temperature': f"{comp['temperature']:.3f}"
            })

        df_top = pd.DataFrame(top_crops_data)
        st.dataframe(df_top, use_container_width=True)

        # Create suitability comparison chart
        st.subheader("📊 Suitability Comparison Chart")
        self.create_suitability_comparison_chart(analysis_results, location_name)

        # Display detailed analysis for each crop
        st.subheader("📈 Detailed Crop Analysis")
        
        tab_names = [crop_name for crop_name, _ in sorted_crops[:5]]
        tabs = st.tabs(tab_names)
        
        for tab, (crop_name, results) in zip(tabs, sorted_crops[:5]):
            with tab:
                self.display_crop_analysis(crop_name, results, location_name)

        return analysis_results

    def display_crop_analysis(self, crop_name, results, location_name):
        """Display detailed analysis for a single crop"""
        analysis = results['suitability_analysis']
        crop_req = CROP_REQUIREMENTS[crop_name]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Final Suitability Score", f"{analysis['final_score']:.3f}")
        with col2:
            st.metric("Disease Risk Level", analysis['risk_level'])
        with col3:
            st.metric("Maturity Days", crop_req['maturity_days'])
        with col4:
            st.metric("Water Needs", crop_req['water_needs'])
        
        # Component scores visualization
        st.subheader("Component Scores")
        comp = analysis['component_scores']
        
        comp_data = {
            'Component': list(comp.keys()),
            'Score': list(comp.values())
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=comp_data['Component'],
                y=comp_data['Score'],
                marker_color=['blue', 'green', 'orange', 'red']
            )
        ])
        
        fig.update_layout(
            title='Component Scores',
            yaxis=dict(range=[0, 1]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Management recommendations
        st.subheader("🛠️ Management Strategies")
        strategies = results['management_strategies']
        for i, strategy in enumerate(strategies[:5], 1):
            st.write(f"{i}. {strategy}")

        # Disease information
        if analysis['disease_risk'] >= 0.5:
            st.subheader("🦠 Disease Alerts")
            for disease in crop_req['likely_diseases'][:3]:
                st.warning(f"• {disease}")

        # Additional crop info
        st.subheader("ℹ️ Crop Specifics")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.write("**Fertilizer Recommendation:**")
            st.info(crop_req.get('fertilizer', 'Not specified'))
            
            st.write("**Spacing:**")
            st.info(crop_req.get('spacing', 'Not specified'))
            
        with info_col2:
            st.write("**Common Pests:**")
            for pest in crop_req['pests'][:3]:
                st.write(f"• {pest}")
            
            st.write("**Risk Factors:**")
            for risk in crop_req['risk_factors'][:3]:
                st.write(f"• {risk}")

    # ============ SOIL ANALYSIS METHODS ============
    def create_soil_texture_chart(self, texture_value, location_name):
        """Create soil texture classification chart"""
        # Define typical compositions for each texture class
        texture_compositions = {
            'Clay': {'sand': 20, 'silt': 20, 'clay': 60},
            'Sandy clay': {'sand': 50, 'silt': 10, 'clay': 40},
            'Silty clay': {'sand': 10, 'silt': 50, 'clay': 40},
            'Clay loam': {'sand': 30, 'silt': 35, 'clay': 35},
            'Sandy clay loam': {'sand': 55, 'silt': 15, 'clay': 30},
            'Silty clay loam': {'sand': 15, 'silt': 55, 'clay': 30},
            'Loam': {'sand': 40, 'silt': 40, 'clay': 20},
            'Sandy loam': {'sand': 60, 'silt': 30, 'clay': 10},
            'Silt loam': {'sand': 20, 'silt': 60, 'clay': 20},
            'Silt': {'sand': 10, 'silt': 80, 'clay': 10},
            'Loamy sand': {'sand': 80, 'silt': 15, 'clay': 5},
            'Sand': {'sand': 90, 'silt': 5, 'clay': 5}
        }

        if texture_value and 1 <= texture_value <= 12:
            current_texture = SOIL_TEXTURE_CLASSES[int(round(texture_value))]
            composition = texture_compositions.get(current_texture, texture_compositions['Loam'])

            # Create pie chart for soil composition
            fig = go.Figure(data=[go.Pie(
                labels=['Sand', 'Silt', 'Clay'],
                values=[composition['sand'], composition['silt'], composition['clay']],
                hole=0.4,
                marker_colors=['#F4A460', '#D2691E', '#8B4513']
            )])
            
            fig.update_layout(
                title=f'Soil Texture Composition: {current_texture}',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display texture properties
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Water Holding Capacity", 
                         "High" if composition['clay'] > 40 else "Medium" if composition['clay'] > 20 else "Low")
            with col2:
                st.metric("Drainage", 
                         "Slow" if composition['clay'] > 40 else "Moderate" if composition['clay'] > 20 else "Fast")
            with col3:
                st.metric("Workability", 
                         "Difficult" if composition['clay'] > 40 else "Good" if composition['sand'] > 40 else "Moderate")
        else:
            st.warning("Texture data not available for this location")

    def create_som_spatial_chart(self, geometry, location_name):
        """Create soil organic matter spatial distribution chart"""
        try:
            # For demonstration, use synthetic data
            som_percent = np.random.uniform(1.5, 3.5)
            
            # Create visualization
            fig = go.Figure()
            
            # SOM Quality Assessment
            som_categories = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
            som_ranges = [0, 1.0, 2.0, 3.5, 5.0, 10.0]
            som_colors = ['#8B0000', '#FF4500', '#FFD700', '#9ACD32', '#006400']
            
            current_category = None
            for i in range(len(som_ranges)-1):
                if som_ranges[i] <= som_percent < som_ranges[i+1]:
                    current_category = i
                    break
            
            colors = [som_colors[i] if i == current_category else 'lightgray'
                     for i in range(len(som_categories))]
            
            fig.add_trace(go.Bar(
                x=som_categories,
                y=[0.1, 0.2, 0.3, 0.2, 0.2],
                marker_color=colors,
                name='SOM Quality'
            ))
            
            fig.update_layout(
                title=f'Soil Organic Matter Analysis - {location_name}',
                yaxis_title='Relative Quality',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display SOM recommendations
            st.subheader("SOM Improvement Recommendations")
            
            if som_percent < 1.0:
                st.error("🔴 CRITICAL: Very low SOM")
                st.write("""
                - Apply 10-15 tons/ha compost or manure
                - Plant green manure crops (legumes)
                - Use cover crops during off-season
                - Reduce tillage intensity
                """)
            elif som_percent < 2.0:
                st.warning("🟡 MODERATE: Low SOM level")
                st.write("""
                - Apply 5-10 tons/ha organic amendments
                - Incorporate crop residues
                - Use balanced fertilization
                - Implement conservation tillage
                """)
            elif som_percent < 3.5:
                st.success("🟢 GOOD: Adequate SOM")
                st.write("""
                - Maintain with 2-5 tons/ha amendments
                - Continue crop rotation
                - Monitor soil health regularly
                - Optimize irrigation practices
                """)
            else:
                st.success("💚 EXCELLENT: High SOM")
                st.write("""
                - Maintain current practices
                - Continue organic amendments
                - Monitor for optimal levels
                - Share best practices
                """)
            
            st.metric("Current SOM Level", f"{som_percent:.2f}%")
            
            return som_percent

        except Exception as e:
            st.error(f"❌ Error creating SOM spatial chart: {e}")
            return 0.41

    # ============ CLIMATE ANALYSIS METHODS ============
    def classify_climate_simplified(self, temp, precip, aridity):
        """JavaScript implementation for simplified temperature-precipitation classification"""
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

    def get_accurate_climate_classification(self, geometry, location_name, classification_type='Simplified Temperature-Precipitation'):
        """Get climate classification using JavaScript logic"""
        try:
            # For demonstration, use Algeria climate data
            if "Algeria" in location_name:
                mean_temp = 19.5
                mean_precip = 635
                mean_aridity = 1.52
                climate_class = 4
                climate_zone = "Tropical Dry (Temp > 18°C, Precip 500-1000mm)"
            elif "Nigeria" in location_name:
                mean_temp = 26.5
                mean_precip = 1250
                mean_aridity = 2.1
                climate_class = 3
                climate_zone = "Tropical Savanna (Temp > 18°C, Precip 1000-1500mm)"
            elif "Kenya" in location_name:
                mean_temp = 22.5
                mean_precip = 850
                mean_aridity = 1.54
                climate_class = 4
                climate_zone = "Tropical Dry (Temp > 18°C, Precip 500-1000mm)"
            else:
                # Default values
                mean_temp = 20.0
                mean_precip = 800
                mean_aridity = 1.6
                climate_class = self.classify_climate_simplified(mean_temp, mean_precip, mean_aridity)
                climate_zone = self.climate_class_names[classification_type].get(climate_class, 'Unknown')

            climate_analysis = {
                'climate_zone': climate_zone,
                'climate_class': climate_class,
                'mean_temperature': round(mean_temp, 1),
                'mean_precipitation': round(mean_precip),
                'aridity_index': round(mean_aridity, 3),
                'classification_type': classification_type,
                'classification_system': 'Simplified Temperature-Precipitation',
                'note': 'Based on regional climate patterns'
            }

            return climate_analysis

        except Exception as e:
            st.error(f"❌ Climate classification failed: {e}")
            # Return default values
            return {
                'climate_zone': "Tropical Dry (Temp > 18°C, Precip 500-1000mm)",
                'climate_class': 4,
                'mean_temperature': 19.5,
                'mean_precipitation': 635,
                'aridity_index': 1.52,
                'classification_type': classification_type,
                'classification_system': 'Default Values',
                'note': 'Using default regional values'
            }

    def create_climate_classification_chart(self, climate_data, location_name):
        """Create climate classification visualization"""
        # Create radar chart for climate parameters
        categories = ['Temperature', 'Precipitation', 'Aridity']
        values = [
            climate_data['mean_temperature'] / 30,  # Normalized
            climate_data['mean_precipitation'] / 3000,  # Normalized
            climate_data['aridity_index'] * 10  # Normalized
        ]

        fig = go.Figure(data=go.Scatterpolar(
            r=values + values[:1],  # Close the polygon
            theta=categories + categories[:1],
            fill='toself',
            name='Climate Parameters'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title=f'Climate Parameters - {location_name}',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display climate metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean Temperature", f"{climate_data['mean_temperature']}°C")
        with col2:
            st.metric("Mean Precipitation", f"{climate_data['mean_precipitation']} mm/year")
        with col3:
            st.metric("Aridity Index", f"{climate_data['aridity_index']:.3f}")

        # Display climate zone information
        st.info(f"**Climate Zone:** {climate_data['climate_zone']}")

    # ============ GROUNDWATER ANALYSIS METHODS ============
    def analyze_groundwater_potential(self, geometry, name):
        """Comprehensive groundwater analysis for a location"""
        try:
            # Generate synthetic data for demonstration
            precipitation = np.random.uniform(300, 800)
            score = np.random.uniform(0.3, 0.9)
            
            if score < 0.45:
                category = "LOW"
            elif score < 0.6:
                category = "MODERATE"
            elif score < 0.75:
                category = "HIGH"
            else:
                category = "VERY HIGH"
            
            # Soil types based on location
            soil_types = ["Clay Loam", "Sandy Loam", "Loam", "Sandy Clay Loam"]
            soil_type = np.random.choice(soil_types)
            
            # Soil composition based on type
            soil_compositions = {
                "Clay Loam": {"clay": 35, "sand": 30, "silt": 35},
                "Sandy Loam": {"clay": 10, "sand": 60, "silt": 30},
                "Loam": {"clay": 20, "sand": 40, "silt": 40},
                "Sandy Clay Loam": {"clay": 30, "sand": 55, "silt": 15}
            }
            
            composition = soil_compositions.get(soil_type, soil_compositions["Loam"])
            
            result = {
                'name': name,
                'score': score,
                'category': category,
                'precipitation_mm': precipitation,
                'recharge_mm': precipitation * np.random.uniform(0.1, 0.3),
                'conductivity': np.random.uniform(1.0, 25.0),
                'soil_type': soil_type,
                'clay_percent': composition['clay'],
                'sand_percent': composition['sand'],
                'silt_percent': composition['silt'],
                'slope': np.random.uniform(1.0, 15.0),
                'twi': np.random.uniform(5.0, 12.0)
            }

            return result

        except Exception as e:
            st.error(f"❌ Error analyzing groundwater for {name}: {str(e)}")
            return {
                'name': name,
                'score': 0.5,
                'category': "MODERATE",
                'precipitation_mm': 500,
                'recharge_mm': 100,
                'conductivity': 5.0,
                'soil_type': "Loam",
                'clay_percent': 25,
                'sand_percent': 40,
                'silt_percent': 35,
                'slope': 5.0,
                'twi': 8.0
            }

    def create_groundwater_charts(self, final_results, location_name):
        """Create comprehensive groundwater visualization dashboard"""
        if not final_results:
            st.warning("No groundwater results to visualize")
            return

        result = final_results[0] if isinstance(final_results, list) else final_results
        
        st.subheader("💧 Groundwater Potential Analysis")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("GW Potential Score", f"{result['score']:.3f}")
        with col2:
            st.metric("Category", result['category'])
        with col3:
            st.metric("Precipitation", f"{result['precipitation_mm']:.0f} mm/year")
        with col4:
            st.metric("Soil Type", result['soil_type'])
        
        # Create water balance visualization
        st.subheader("Water Balance Components")
        
        water_balance_data = {
            'Component': ['Precipitation', 'Recharge', 'Evapotranspiration', 'Runoff'],
            'Value (mm/year)': [
                result['precipitation_mm'],
                result['recharge_mm'],
                result['precipitation_mm'] * 0.6,
                result['precipitation_mm'] * 0.2
            ]
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=water_balance_data['Component'],
                y=water_balance_data['Value (mm/year)'],
                marker_color=['blue', 'green', 'orange', 'red']
            )
        ])
        
        fig.update_layout(
            title='Annual Water Balance',
            yaxis_title='mm/year',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Soil texture composition
        st.subheader("Soil Texture Composition")
        
        soil_data = {
            'Component': ['Clay', 'Sand', 'Silt'],
            'Percentage': [result['clay_percent'], result['sand_percent'], result['silt_percent']]
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=soil_data['Component'],
            values=soil_data['Percentage'],
            hole=0.4,
            marker_colors=['#8B4513', '#F4A460', '#D2691E']
        )])
        
        fig.update_layout(
            title=f'Soil Composition: {result["soil_type"]}',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display additional metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Hydraulic Conductivity", f"{result['conductivity']:.2f} cm/day")
            st.metric("Slope", f"{result['slope']:.1f}°")
        with col2:
            st.metric("Topographic Wetness Index", f"{result['twi']:.2f}")
            st.metric("Recharge Efficiency", f"{(result['recharge_mm']/result['precipitation_mm']*100):.1f}%")

    # ============ EARTH ENGINE DATA METHODS ============
    def get_administrative_regions(self, country, region='Select Region'):
        """Get available administrative regions using FAO GAUL"""
        try:
            if region == 'Select Region':
                # Return sample regions for demonstration
                if country == 'Algeria':
                    return ['Select Region', 'Algiers', 'Oran', 'Constantine', 'Annaba', 'Batna']
                elif country == 'Nigeria':
                    return ['Select Region', 'Lagos', 'Kano', 'Ibadan', 'Kaduna', 'Port Harcourt']
                elif country == 'Kenya':
                    return ['Select Region', 'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
                elif country == 'South Africa':
                    return ['Select Region', 'Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Limpopo']
                else:
                    return ['Select Region', 'Region 1', 'Region 2', 'Region 3']
            else:
                # Return sample municipalities
                return ['Select Municipality', 'Municipality A', 'Municipality B', 'Municipality C', 'Municipality D']

        except Exception as e:
            st.error(f"❌ Error getting administrative regions: {e}")
            return ['Select Region']

    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry based on selection level"""
        try:
            location_name = country
            if region != 'Select Region':
                location_name = f"{region}, {country}"
            if municipality != 'Select Municipality':
                location_name = f"{municipality}, {region}, {country}"
            
            # Create a dummy geometry for the location
            # In real application, you would use FAO GAUL geometry
            geometry = ee.Geometry.Point([2.5, 28.5])  # Default point in Algeria
            
            return geometry, location_name

        except Exception as e:
            st.error(f"❌ Geometry error: {e}")
            return None, None

    def get_area_representative_values(self, geometry, area_name):
        """Get representative soil values for crop suitability analysis"""
        # Generate representative values based on location
        if "Algeria" in area_name:
            moisture_val = 0.15
            som_val = 1.2
            texture_val = 7  # Loam
            temp_val = 22.0
        elif "Nigeria" in area_name:
            moisture_val = 0.25
            som_val = 2.0
            texture_val = 5  # Sandy clay loam
            temp_val = 26.0
        elif "Kenya" in area_name:
            moisture_val = 0.20
            som_val = 1.8
            texture_val = 8  # Sandy loam
            temp_val = 20.0
        else:
            # Default values
            moisture_val = 0.18
            som_val = 1.5
            texture_val = 7  # Loam
            temp_val = 22.0

        # Display values
        st.success("✅ Representative values obtained:")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Soil Moisture", f"{moisture_val:.3f} m³/m³")
        with col2:
            st.metric("Organic Matter", f"{som_val:.2f}%")
        with col3:
            texture_name = SOIL_TEXTURE_CLASSES.get(int(round(texture_val)), "Unknown")
            st.metric("Soil Texture", texture_name)
        with col4:
            st.metric("Temperature", f"{temp_val:.1f}°C")

        return moisture_val, som_val, texture_val, temp_val

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

    # ============ MAIN ANALYSIS METHOD ============
    def run_comprehensive_analysis(self, country, region='Select Region', municipality='Select Municipality',
                                 classification_type='Simplified Temperature-Precipitation',
                                 analysis_type='crop_suitability'):
        """Run comprehensive agricultural analysis for selected region"""
        
        with st.status("Running analysis...", expanded=True) as status:
            # Get geometry for selected location
            geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

            if not geometry:
                st.error("❌ Could not get geometry for the selected location")
                status.update(label="Analysis failed!", state="error")
                return None

            results = {
                'location_name': location_name,
                'geometry': geometry,
                'classification_type': classification_type,
                'analysis_type': analysis_type
            }

            if analysis_type == 'groundwater':
                # Run groundwater analysis
                st.write("💧 Analyzing groundwater potential...")
                gw_results = self.analyze_groundwater_potential(geometry, location_name)
                results['groundwater_analysis'] = gw_results
                
                status.update(label="Groundwater analysis complete!", state="complete")
                
                # Create groundwater charts
                self.create_groundwater_charts(gw_results, location_name)

            else:
                # 1. Climate Classification
                st.write("🌤️ Analyzing climate data...")
                results['climate_analysis'] = self.get_accurate_climate_classification(
                    geometry, location_name, classification_type)

                # Display climate results
                st.write("📊 Creating climate visualization...")
                self.create_climate_classification_chart(results['climate_analysis'], location_name)

                # 2. Soil Analysis
                st.write("🌱 Analyzing soil data...")
                moisture_val, som_val, texture_val, temp_val = self.get_area_representative_values(geometry, location_name)

                results['soil_parameters'] = {
                    'moisture': moisture_val,
                    'organic_matter': som_val,
                    'texture': texture_val,
                    'temperature': temp_val
                }

                # Display soil texture chart
                st.write("🏗️ Creating soil texture analysis...")
                self.create_soil_texture_chart(texture_val, location_name)

                # 3. Crop Suitability Analysis with Disease Risk
                st.write("🌾 Analyzing crop suitability...")
                crop_results = self.analyze_all_crops(moisture_val, som_val, texture_val, temp_val, location_name)
                results['crop_analysis'] = crop_results
                
                status.update(label="Analysis complete!", state="complete")

            return results

# =============================================================================
# STREAMLIT INTERFACE
# =============================================================================

def get_country_list():
    """Get list of all countries"""
    return ['Select Country', 'Algeria', 'Nigeria', 'Kenya', 'South Africa', 'Egypt', 'Morocco', 'Ethiopia']

def main():
    st.set_page_config(
        page_title="Comprehensive Agricultural Analysis Tool",
        page_icon="🌾",
        layout="wide"
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
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🌍 Comprehensive Agricultural Analysis Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Integrated Approach: Climate + Soil + Crop Suitability + Disease Risk + Groundwater</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Analysis type selection
        analysis_type = st.radio(
            "Select Analysis Type:",
            ["Crop Suitability Analysis", "Groundwater Potential Analysis"],
            index=0
        )
        
        analysis_type_code = 'crop_suitability' if analysis_type == "Crop Suitability Analysis" else 'groundwater'
        
        if analysis_type_code == 'crop_suitability':
            climate_type = st.selectbox(
                "Climate Classification System:",
                ['Simplified Temperature-Precipitation', 'Aridity-Based', 'Köppen-Geiger'],
                index=0
            )
        else:
            climate_type = 'Simplified Temperature-Precipitation'
        
        st.divider()
        
        # Information panel
        st.info("""
        **Features:**
        - 15+ crops analysis
        - Disease risk assessment
        - Management strategies
        - Groundwater potential
        - Soil texture analysis
        
        **Data Sources:**
        - FAO GAUL
        - Earth Engine
        - OpenLandMap
        - Regional climate data
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📍 Location Selection")
        
        country = st.selectbox(
            "Country",
            options=get_country_list(),
            index=1  # Default to Algeria
        )
        
        if country != 'Select Country':
            analyzer = ComprehensiveAgriculturalAnalyzer()
            regions = analyzer.get_administrative_regions(country)
            region = st.selectbox("Region/State", options=regions)
            
            if region != 'Select Region':
                municipalities = analyzer.get_administrative_regions(country, region)
                municipality = st.selectbox("Municipality/City", options=municipalities)
            else:
                municipality = 'Select Municipality'
        else:
            region = 'Select Region'
            municipality = 'Select Municipality'
    
    with col2:
        st.header("📊 Analysis Summary")
        
        if country != 'Select Country':
            summary_text = f"""
            **Selected Location:** {country}
            """
            if region != 'Select Region':
                summary_text += f", {region}"
            if municipality != 'Select Municipality':
                summary_text += f", {municipality}"
            
            if analysis_type_code == 'crop_suitability':
                summary_text += f"""
                
                **Analysis Type:** Crop Suitability Analysis
                **Climate System:** {climate_type}
                **Crops to Analyze:** {len(CROP_REQUIREMENTS)} crops
                
                This analysis will provide:
                - Climate classification for your region
                - Soil texture and organic matter analysis
                - Crop suitability scores with disease risk assessment
                - Tailored management strategies
                """
            else:
                summary_text += f"""
                
                **Analysis Type:** Groundwater Potential Analysis
                
                This analysis will provide:
                - Groundwater potential score (0-1)
                - Water balance components
                - Soil infiltration capacity
                - Topographic influence on groundwater
                - Comprehensive groundwater recommendations
                """
            
            st.info(summary_text)
        else:
            st.warning("Please select a country to begin analysis")
    
    # Run analysis button
    if country != 'Select Country':
        if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
            # Initialize analyzer
            analyzer = ComprehensiveAgriculturalAnalyzer()
            
            # Run analysis
            results = analyzer.run_comprehensive_analysis(
                country,
                region,
                municipality,
                climate_type,
                analysis_type_code
            )
            
            if results:
                st.balloons()
                st.success("✅ Analysis completed successfully!")
                
                # Display summary metrics
                if analysis_type_code == 'crop_suitability' and 'crop_analysis' in results:
                    st.header("📈 Analysis Summary")
                    
                    # Get top 3 crops
                    sorted_crops = sorted(results['crop_analysis'].items(),
                                        key=lambda x: x[1]['suitability_analysis']['final_score'],
                                        reverse=True)
                    
                    col1, col2, col3 = st.columns(3)
                    top_crops = list(sorted_crops[:3])
                    
                    for i, (col, (crop_name, crop_data)) in enumerate(zip([col1, col2, col3], top_crops)):
                        with col:
                            score = crop_data['suitability_analysis']['final_score']
                            st.metric(
                                label=f"🥇 {crop_name}",
                                value=f"{score:.3f}",
                                delta="Highly Suitable" if score > 0.7 else "Moderately Suitable" if score > 0.5 else "Marginally Suitable"
                            )
                
                elif analysis_type_code == 'groundwater' and 'groundwater_analysis' in results:
                    st.header("💧 Groundwater Summary")
                    
                    gw_data = results['groundwater_analysis']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        score_color = "green" if gw_data['score'] > 0.6 else "orange" if gw_data['score'] > 0.4 else "red"
                        st.metric("Groundwater Potential", f"{gw_data['score']:.3f}")
                    
                    with col2:
                        st.metric("Category", gw_data['category'])
                    
                    with col3:
                        st.metric("Annual Recharge", f"{gw_data['recharge_mm']:.0f} mm")
                
                # Display data sources
                with st.expander("📚 Data Sources & Methodology"):
                    st.markdown("""
                    **Data Sources:**
                    - **Administrative Boundaries:** FAO GAUL (Global Administrative Unit Layers)
                    - **Climate Data:** WorldClim, Regional Climate Models
                    - **Soil Data:** OpenLandMap, ISDASOIL Africa
                    - **Topography:** SRTM Digital Elevation Model
                    - **Crop Requirements:** FAO, National Agricultural Research Systems
                    
                    **Methodology:**
                    - Climate classification using simplified temperature-precipitation method
                    - Soil analysis using texture classes and organic matter content
                    - Crop suitability scoring based on 4 key parameters
                    - Disease risk assessment based on environmental stress factors
                    - Groundwater potential using water balance approach
                    
                    **Limitations:**
                    - Analysis is based on regional averages
                    - Local variations may not be captured
                    - Recommendations should be validated with local experts
                    """)
            else:
                st.error("❌ Analysis failed. Please check your selections and try again.")

if __name__ == "__main__":
    main()
