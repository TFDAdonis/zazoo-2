import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings('ignore')

# Initialize Earth Engine
try:
    ee.Initialize()
    print("✅ Earth Engine initialized successfully!")
except Exception as e:
    print(f"❌ Earth Engine initialization failed: {e}")
    print("🔐 Please authenticate Earth Engine first:")
    print("   Run: ee.Authenticate()")
    print("   Then: ee.Initialize()")

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
    'Bean': {
        'moisture_opt': 0.20, 'moisture_tol': 0.06, 'om_opt': 1.5, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 21, 'temp_tol': 6, 'maturity_days': 85, 'water_needs': 'Medium',
        'notes': 'Warm season, requires good drainage',
        'management': [
            'Plant when soil temperature reaches 16°C',
            'Provide support for pole bean varieties',
            'Water consistently during flowering and pod set',
            'Use crop rotation to reduce soil-borne diseases',
            'Harvest regularly to encourage continued production'
        ],
        'likely_diseases': [
            'Common blight - angular water-soaked lesions turning brown',
            'Halo blight - small spots with yellow halos',
            'Rust - reddish-brown pustules on leaves and pods',
            'Root rots (Fusarium, Rhizoctonia) - wilting and plant death',
            'Bean common mosaic virus - mosaic patterns and leaf distortion'
        ],
        'pests': ['Bean leaf beetle', 'Aphids', 'Spider mites', 'Thrips'],
        'fertilizer': 'NPK 40-80-60 kg/ha',
        'spacing': '45-60 cm between rows, 5-10 cm between plants',
        'risk_factors': ['Overhead irrigation', 'High humidity', 'Poor air circulation']
    },
    'Pea': {
        'moisture_opt': 0.18, 'moisture_tol': 0.05, 'om_opt': 1.4, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 18, 'temp_tol': 5, 'maturity_days': 90, 'water_needs': 'Medium',
        'notes': 'Cool season, nitrogen-fixing',
        'management': [
            'Plant early in cool season for best yields',
            'Provide support for climbing varieties',
            'Inoculate seeds with appropriate Rhizobium',
            'Harvest regularly for continuous production',
            'Cool quickly after harvest for quality preservation'
        ],
        'likely_diseases': [
            'Powdery mildew - white fungal growth on leaves and pods',
            'Fusarium wilt - yellowing and wilting of plants',
            'Root rot - damping off and root decay in wet soils',
            'Ascochyta blight - leaf spots and pod lesions',
            'Pea enation mosaic virus - leaf distortion and reduced yields'
        ],
        'pests': ['Aphids', 'Pea weevil', 'Thrips', 'Leaf miners'],
        'fertilizer': 'Phosphorus 40-50 kg/ha, low nitrogen',
        'spacing': '30-45 cm between rows, 5-8 cm between plants',
        'risk_factors': ['Warm humid conditions', 'Poor drainage', 'High nitrogen']
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
    'Onion': {
        'moisture_opt': 0.22, 'moisture_tol': 0.05, 'om_opt': 1.8, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 20, 'temp_tol': 6, 'maturity_days': 120, 'water_needs': 'Medium',
        'notes': 'Requires consistent moisture, good drainage',
        'management': [
            'Plant in well-drained soil with good organic matter',
            'Control weeds carefully as onions are poor competitors',
            'Stop irrigation when tops begin to fall over for better curing',
            'Harvest when 50-80% of tops have fallen',
            'Cure properly before storage to prevent rot'
        ],
        'likely_diseases': [
            'Purple blotch - purple lesions with yellow halos on leaves',
            'Downy mildew - grayish fungal growth on leaves',
            'Botrytis leaf blight - white lesions with green halos',
            'Fusarium basal rot - rot starting from base of bulbs',
            'Pink root - pink discoloration and decay of roots'
        ],
        'pests': ['Onion thrips', 'Onion maggot', 'Cutworms', 'Aphids'],
        'fertilizer': 'NPK 100-80-120 kg/ha + Sulfur',
        'spacing': '30-45 cm between rows, 5-8 cm between plants',
        'risk_factors': ['High humidity', 'Poor air circulation', 'Overhead irrigation']
    },
    'Pepper': {
        'moisture_opt': 0.23, 'moisture_tol': 0.05, 'om_opt': 2.2, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 25, 'temp_tol': 6, 'maturity_days': 90, 'water_needs': 'Medium',
        'notes': 'Warm season, sensitive to water stress',
        'management': [
            'Start transplants indoors for early production',
            'Use black plastic mulch for weed control and warmth',
            'Provide consistent moisture, especially during fruit set',
            'Harvest regularly to encourage continued production',
            'Handle carefully to avoid bruising fruits'
        ],
        'likely_diseases': [
            'Bacterial spot - raised scabby lesions on leaves and fruits',
            'Phytophthora blight - rapid wilting and fruit rot',
            'Powdery mildew - white fungal growth on leaves',
            'Verticillium wilt - yellowing and wilting of plants',
            'Blossom end rot - sunken leathery spots on fruit ends'
        ],
        'pests': ['Aphids', 'Thrips', 'Pepper weevil', 'Spider mites'],
        'fertilizer': 'NPK 100-80-120 kg/ha + Calcium',
        'spacing': '60-90 cm between rows, 30-45 cm between plants',
        'risk_factors': ['Temperature fluctuations', 'Water stress', 'High nitrogen']
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
    'Lettuce': {
        'moisture_opt': 0.27, 'moisture_tol': 0.06, 'om_opt': 2.2, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 16, 'temp_tol': 5, 'maturity_days': 60, 'water_needs': 'High',
        'notes': 'Cool season, requires consistent moisture',
        'management': [
            'Plant in cool seasons for best quality',
            'Maintain consistent moisture for tender leaves',
            'Use shade cloth in warm weather to prevent bolting',
            'Harvest in morning for best crispness',
            'Practice succession planting for continuous harvest'
        ],
        'likely_diseases': [
            'Bottom rot - rot of lower leaves touching soil',
            'Drop (Sclerotinia) - white mold and wilting',
            'Powdery mildew - white fungal growth on leaves',
            'Bacterial leaf spot - angular water-soaked lesions',
            'Big vein virus - yellow veins and distorted growth'
        ],
        'pests': ['Aphids', 'Slugs', 'Leaf miners', 'Cutworms'],
        'fertilizer': 'NPK 80-60-100 kg/ha + Nitrogen side dressing',
        'spacing': '30-45 cm between rows, 20-30 cm between plants',
        'risk_factors': ['Warm temperatures', 'Overhead irrigation', 'Poor air circulation']
    },
    'Garlic': {
        'moisture_opt': 0.18, 'moisture_tol': 0.05, 'om_opt': 1.8, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 18, 'temp_tol': 6, 'maturity_days': 150, 'water_needs': 'Low-Medium',
        'notes': 'Cool season, requires well-drained soil',
        'management': [
            'Plant cloves in fall for spring harvest in temperate regions',
            'Use disease-free planting stock',
            'Stop watering when leaves begin to yellow for better curing',
            'Harvest when lower leaves brown but upper leaves remain green',
            'Cure properly in well-ventilated area before storage'
        ],
        'likely_diseases': [
            'White rot - white fungal growth and yellowing leaves',
            'Basal rot - rot starting from base of bulbs',
            'Rust - orange pustules on leaves',
            'Downy mildew - pale spots with grayish fungal growth',
            'Penicillium decay - blue-green mold on stored bulbs'
        ],
        'pests': ['Thrips', 'Onion maggot', 'Nematodes', 'Bulb mites'],
        'fertilizer': 'NPK 80-100-120 kg/ha',
        'spacing': '15-20 cm between rows, 8-10 cm between plants',
        'risk_factors': ['Poor drainage', 'High humidity', 'Infected seed cloves']
    },
    'Eggplant': {
        'moisture_opt': 0.23, 'moisture_tol': 0.05, 'om_opt': 2.0, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.5, 'Sand': 0.2
        },
        'temp_opt': 25, 'temp_tol': 6, 'maturity_days': 80, 'water_needs': 'Medium',
        'notes': 'Warm season, heat loving',
        'management': [
            'Start transplants indoors for early production',
            'Use plastic mulch for weed control and soil warming',
            'Provide consistent moisture for good fruit development',
            'Harvest when fruits are glossy and reach full size',
            'Prune lower leaves to improve air circulation'
        ],
        'likely_diseases': [
            'Phomopsis blight - fruit rot with concentric rings',
            'Verticillium wilt - yellowing and wilting of plants',
            'Early blight - target-like spots on leaves',
            'Bacterial wilt - rapid wilting without yellowing',
            'Fruit rot - various fungi causing fruit decay'
        ],
        'pests': ['Flea beetles', 'Aphids', 'Spider mites', 'Colorado potato beetle'],
        'fertilizer': 'NPK 100-80-120 kg/ha',
        'spacing': '75-90 cm between rows, 45-60 cm between plants',
        'risk_factors': ['Cool temperatures', 'High humidity', 'Poor air circulation']
    },
    'Spinach': {
        'moisture_opt': 0.26, 'moisture_tol': 0.06, 'om_opt': 2.2, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.8, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.7, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 16, 'temp_tol': 5, 'maturity_days': 45, 'water_needs': 'High',
        'notes': 'Cool season, fast growing',
        'management': [
            'Plant in cool seasons for best growth',
            'Maintain high soil moisture for tender leaves',
            'Use succession planting for continuous harvest',
            'Harvest outer leaves or whole plants when mature',
            'Cool quickly after harvest to maintain quality'
        ],
        'likely_diseases': [
            'Downy mildew - yellow spots with purple fungal growth',
            'White rust - white pustules on leaves',
            'Fusarium wilt - yellowing and wilting of plants',
            'Leaf spots - various fungal and bacterial spots',
            'Damping off - seedling collapse in wet conditions'
        ],
        'pests': ['Aphids', 'Leaf miners', 'Flea beetles', 'Slugs'],
        'fertilizer': 'NPK 80-60-100 kg/ha + Nitrogen',
        'spacing': '30-45 cm between rows, 5-8 cm between plants',
        'risk_factors': ['Warm temperatures', 'High humidity', 'Overcrowding']
    },
    'Cucumber': {
        'moisture_opt': 0.25, 'moisture_tol': 0.06, 'om_opt': 2.0, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.3, 'Sandy clay': 0.4, 'Silty clay': 0.5, 'Clay loam': 0.7,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 24, 'temp_tol': 6, 'maturity_days': 60, 'water_needs': 'High',
        'notes': 'Warm season, requires consistent moisture',
        'management': [
            'Provide trellis for vertical growth and better air circulation',
            'Maintain consistent moisture for straight fruit development',
            'Harvest regularly to encourage continued production',
            'Use row covers early to protect from pests',
            'Practice crop rotation to reduce disease buildup'
        ],
        'likely_diseases': [
            'Powdery mildew - white fungal growth on leaves',
            'Downy mildew - angular yellow spots on leaves',
            'Bacterial wilt - rapid wilting transmitted by cucumber beetles',
            'Anthracnose - sunken spots on leaves and fruits',
            'Gummy stem blight - stem cankers and fruit rot'
        ],
        'pests': ['Cucumber beetles', 'Aphids', 'Spider mites', 'Whiteflies'],
        'fertilizer': 'NPK 80-60-100 kg/ha',
        'spacing': '90-120 cm between rows, 30-45 cm between plants',
        'risk_factors': ['Cool wet weather', 'Poor air circulation', 'Cucumber beetle pressure']
    },

    # FRUITS
    'Olive': {
        'moisture_opt': 0.12, 'moisture_tol': 0.06, 'om_opt': 1.0, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.6, 'Sandy clay': 0.5, 'Silty clay': 0.4, 'Clay loam': 0.9,
            'Sandy clay loam': 0.6, 'Silty clay loam': 0.5, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.7, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.5
        },
        'temp_opt': 22, 'temp_tol': 8, 'maturity_days': 1095, 'water_needs': 'Very Low',
        'notes': 'Perennial, drought resistant, long-term investment',
        'management': [
            'Prune annually to maintain open canopy for light penetration',
            'Irrigate during fruit set and development for better yield',
            'Apply balanced fertilizer based on leaf analysis',
            'Control weeds around young trees',
            'Harvest when fruits change color for optimal oil quality'
        ],
        'likely_diseases': [
            'Olive knot - bacterial galls on branches and twigs',
            'Peacock spot - circular sooty spots on leaves causing defoliation',
            'Verticillium wilt - sudden wilting and dieback of branches',
            'Root rot (Phytophthora) - in poorly drained soils',
            'Anthracnose - fruit rot causing mummification'
        ],
        'pests': ['Olive fruit fly', 'Scale insects', 'Olive moth', 'Thrips'],
        'fertilizer': 'NPK 60-40-20 kg/ha for mature trees',
        'spacing': '6-8 m between trees depending on variety',
        'risk_factors': ['High humidity', 'Poor drainage', 'Mechanical injuries']
    },
    'Orange': {
        'moisture_opt': 0.20, 'moisture_tol': 0.06, 'om_opt': 1.8, 'om_tol': 0.7,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 23, 'temp_tol': 7, 'maturity_days': 730, 'water_needs': 'Medium',
        'notes': 'Citrus, requires well-drained soil',
        'management': [
            'Protect from frost in cooler regions',
            'Apply micronutrients especially zinc and iron',
            'Prune to maintain shape and remove dead wood',
            'Irrigate regularly during fruit development',
            'Monitor for citrus greening disease symptoms'
        ],
        'likely_diseases': [
            'Citrus canker - raised corky lesions on leaves, stems and fruit',
            'Greasy spot - yellow-brown blisters on leaf undersides',
            'Melanose - small raised brown spots on leaves and fruit',
            'Root rot (Phytophthora) - gumming and decline in wet soils',
            'Huanglongbing (citrus greening) - yellow shoots and misshapen fruit'
        ],
        'pests': ['Asian citrus psyllid', 'Scale insects', 'Spider mites', 'Fruit flies'],
        'fertilizer': 'NPK 150-50-100 kg/ha + micronutrients',
        'spacing': '5-6 m between trees',
        'risk_factors': ['Poor drainage', 'Frost', 'Citrus psyllid infestation']
    },
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
    'Fig': {
        'moisture_opt': 0.15, 'moisture_tol': 0.05, 'om_opt': 1.0, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.5, 'Sandy clay': 0.6, 'Silty clay': 0.5, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.6, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.7, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.5
        },
        'temp_opt': 25, 'temp_tol': 8, 'maturity_days': 180, 'water_needs': 'Low',
        'notes': 'Drought tolerant, Mediterranean climate',
        'management': [
            'Prune to maintain open center for light penetration',
            'Irrigate during fruit development for better quality',
            'Protect from birds when fruits ripen',
            'Harvest when fruits droop and skin cracks slightly',
            'Allow proper spacing for air circulation'
        ],
        'likely_diseases': [
            'Fig rust - orange pustules on leaves causing defoliation',
            'Endosepsis - internal fruit rot',
            'Souring - fermentation of fruits by yeasts and bacteria',
            'Root knot nematode - galls on roots reducing vigor',
            'Thread blight - webbing and dieback of branches'
        ],
        'pests': ['Fig beetle', 'Scale insects', 'Mealybugs', 'Birds'],
        'fertilizer': 'NPK 50-30-40 kg/ha for mature trees',
        'spacing': '5-6 m between trees',
        'risk_factors': ['High rainfall during fruiting', 'Poor drainage', 'Bird pressure']
    },
    'Date Palm': {
        'moisture_opt': 0.14, 'moisture_tol': 0.04, 'om_opt': 0.8, 'om_tol': 0.5,
        'texture_scores': {
            'Clay': 0.6, 'Sandy clay': 0.7, 'Silty clay': 0.5, 'Clay loam': 0.8,
            'Sandy clay loam': 0.9, 'Silty clay loam': 0.6, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.7, 'Silt': 0.6, 'Loamy sand': 0.8, 'Sand': 0.6
        },
        'temp_opt': 28, 'temp_tol': 8, 'maturity_days': 1460, 'water_needs': 'Low',
        'notes': 'Extremely drought tolerant, desert adapted',
        'management': [
            'Plant in full sun with excellent drainage',
            'Irrigate deeply but infrequently',
            'Remove dead fronds and fruit stalks regularly',
            'Hand-pollinate for better fruit set if needed',
            'Harvest when fruits reach desired ripeness stage'
        ],
        'likely_diseases': [
            'Bayoud disease - vascular wilt causing rapid death',
            'Khamedj - fruit rot in humid conditions',
            'Black scorch - leaf necrosis and trunk lesions',
            'Diplodia disease - bud rot and trunk decay',
            'Graphiola leaf spot - black spots on leaves'
        ],
        'pests': ['Red palm weevil', 'Scale insects', 'Birds', 'Bats'],
        'fertilizer': 'NPK 80-40-60 kg/ha + micronutrients',
        'spacing': '8-10 m between palms',
        'risk_factors': ['Poor drainage', 'High humidity', 'Mechanical injuries']
    },
    'Lemon': {
        'moisture_opt': 0.19, 'moisture_tol': 0.05, 'om_opt': 1.6, 'om_tol': 0.6,
        'texture_scores': {
            'Clay': 0.4, 'Sandy clay': 0.5, 'Silty clay': 0.6, 'Clay loam': 0.8,
            'Sandy clay loam': 0.7, 'Silty clay loam': 0.7, 'Loam': 1.0, 'Sandy loam': 0.9,
            'Silt loam': 0.8, 'Silt': 0.6, 'Loamy sand': 0.7, 'Sand': 0.4
        },
        'temp_opt': 22, 'temp_tol': 7, 'maturity_days': 730, 'water_needs': 'Medium',
        'notes': 'Citrus, sensitive to frost',
        'management': [
            'Protect from frost with covers or irrigation',
            'Prune to maintain open canopy for light penetration',
            'Apply micronutrients especially zinc and iron',
            'Harvest based on color and juice content',
            'Monitor for citrus pests and diseases regularly'
        ],
        'likely_diseases': [
            'Citrus canker - raised lesions on leaves, stems and fruit',
            'Greasy spot - blisters on leaf undersides',
            'Melanose - raised brown spots on young growth',
            'Root rot - decline in poorly drained soils',
            'Tristeza - quick decline and stem pitting'
        ],
        'pests': ['Asian citrus psyllid', 'Scale insects', 'Spider mites', 'Fruit flies'],
        'fertilizer': 'NPK 120-40-80 kg/ha + micronutrients',
        'spacing': '4-5 m between trees',
        'risk_factors': ['Frost', 'Poor drainage', 'Citrus psyllid presence']
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
    },
    'Sugarcane': {
        'moisture_opt': 0.30, 'moisture_tol': 0.08, 'om_opt': 2.0, 'om_tol': 0.8,
        'texture_scores': {
            'Clay': 0.5, 'Sandy clay': 0.6, 'Silty clay': 0.7, 'Clay loam': 0.9,
            'Sandy clay loam': 0.8, 'Silty clay loam': 0.9, 'Loam': 1.0, 'Sandy loam': 0.8,
            'Silt loam': 0.9, 'Silt': 0.8, 'Loamy sand': 0.6, 'Sand': 0.3
        },
        'temp_opt': 26, 'temp_tol': 6, 'maturity_days': 365, 'water_needs': 'Very High',
        'notes': 'Tropical grass, high water requirement',
        'management': [
            'Use disease-free planting material',
            'Apply high nitrogen fertilizer in split applications',
            'Maintain adequate soil moisture throughout growth',
            'Control ratoon stunting disease through hot water treatment',
            'Harvest at 12-18 months depending on variety and climate'
        ],
        'likely_diseases': [
            'Red rot - reddening of internal tissues with white spots',
            'Smut - black whip-like structures instead of inflorescence',
            'Ratoon stunting - internal orange-red discoloration at nodes',
            'Leaf scald - white pencil-line streaks on leaves',
            'Yellow leaf virus - yellowing and stunting'
        ],
        'pests': ['Sugarcane borer', 'Termites', 'White grubs', 'Aphids'],
        'fertilizer': 'NPK 200-80-120 kg/ha',
        'spacing': '90-120 cm between rows',
        'risk_factors': ['Water stress', 'Poor drainage', 'Infected planting material']
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

        self.current_soil_data = None
        self.analysis_results = {}

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

        elif crop_name == 'Rice':
            strategies.append("🌊 Maintain proper water depth management")
            strategies.append("🔄 Practice field drainage before harvest")

        elif crop_name in ['Apple', 'Pear', 'Grape']:
            strategies.append("✂️ Prune for good air circulation and light penetration")

        elif crop_name in ['Carrot', 'Potato', 'Sweet Potato']:
            strategies.append("🪨 Ensure stone-free soil for proper root development")

        return strategies

    def create_crop_suitability_dashboard(self, analysis_results, location_name):
        """Create comprehensive crop suitability dashboard"""

        print(f"\n🌱 CROP SUITABILITY DASHBOARD - {location_name.upper()}")
        print("=" * 70)

        # Sort crops by suitability score
        sorted_crops = sorted(analysis_results.items(),
                            key=lambda x: x[1]['suitability_analysis']['final_score'],
                            reverse=True)

        # Display top crops
        print("\n🏆 TOP RECOMMENDED CROPS:")
        print("-" * 50)

        for crop_name, results in sorted_crops[:5]:
            analysis = results['suitability_analysis']
            print(f"\n📊 {crop_name.upper()}")
            print(f"   Overall Suitability: {analysis['final_score']:.3f}")
            print(f"   Disease Risk: {analysis['risk_level']} ({analysis['disease_risk']:.3f})")

            # Component scores
            comp = analysis['component_scores']
            print(f"   Component Scores - Moisture: {comp['moisture']:.3f}, "
                  f"OM: {comp['organic_matter']:.3f}, "
                  f"Texture: {comp['texture']:.3f}, "
                  f"Temp: {comp['temperature']:.3f}")

        # Display detailed analysis for each crop
        print(f"\n📈 DETAILED CROP ANALYSIS:")
        print("-" * 50)

        for crop_name, results in sorted_crops:
            self.display_crop_analysis(crop_name, results, location_name)

    def display_crop_analysis(self, crop_name, results, location_name):
        """Display detailed analysis for a single crop"""

        analysis = results['suitability_analysis']
        crop_req = CROP_REQUIREMENTS[crop_name]

        print(f"\n🌾 {crop_name.upper()} ANALYSIS")
        print(f"   Final Suitability Score: {analysis['final_score']:.3f}")
        print(f"   Disease Risk Level: {analysis['risk_level']}")

        # Suitability visualization
        score = analysis['final_score']
        if score >= 0.8:
            rating = "★★★★★ EXCELLENT"
        elif score >= 0.6:
            rating = "★★★★☆ GOOD"
        elif score >= 0.4:
            rating = "★★★☆☆ MODERATE"
        elif score >= 0.2:
            rating = "★★☆☆☆ POOR"
        else:
            rating = "★☆☆☆☆ VERY POOR"

        print(f"   Suitability Rating: {rating}")

        # Management recommendations
        print(f"\n   🛠️ MANAGEMENT STRATEGIES:")
        strategies = results['management_strategies']
        for i, strategy in enumerate(strategies[:5], 1):
            print(f"      {i}. {strategy}")

        # Disease information
        if analysis['disease_risk'] >= 0.5:
            print(f"\n   🦠 DISEASE ALERTS:")
            for disease in crop_req['likely_diseases'][:3]:
                print(f"      • {disease}")

        # Additional crop info
        print(f"\n   ℹ️ CROP SPECIFICS:")
        print(f"      Maturity: {crop_req['maturity_days']} days")
        print(f"      Water Needs: {crop_req['water_needs']}")
        print(f"      Fertilizer: {crop_req.get('fertilizer', 'Not specified')}")
        print(f"      Spacing: {crop_req.get('spacing', 'Not specified')}")

    def create_suitability_comparison_chart(self, analysis_results, location_name):
        """Create visual comparison chart of crop suitability"""

        crops = list(analysis_results.keys())
        suitability_scores = [analysis_results[crop]['suitability_analysis']['final_score'] for crop in crops]
        disease_risks = [analysis_results[crop]['suitability_analysis']['disease_risk'] for crop in crops]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        # Suitability scores
        bars1 = ax1.barh(crops, suitability_scores, color='green', alpha=0.6)
        ax1.set_xlabel('Suitability Score')
        ax1.set_title(f'Crop Suitability Scores - {location_name}', fontsize=14, fontweight='bold')
        ax1.set_xlim(0, 1)

        # Add value labels
        for bar, score in zip(bars1, suitability_scores):
            ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{score:.3f}', ha='left', va='center', fontsize=8)

        # Disease risks
        bars2 = ax2.barh(crops, disease_risks, color='red', alpha=0.6)
        ax2.set_xlabel('Disease Risk Index')
        ax2.set_title(f'Disease Risk Assessment - {location_name}', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 1)

        # Add value labels
        for bar, risk in zip(bars2, disease_risks):
            ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{risk:.3f}', ha='left', va='center', fontsize=8)

        plt.tight_layout()
        plt.show()

    def create_disease_risk_heatmap(self, analysis_results, location_name):
        """Create a heatmap visualization of disease risk vs suitability"""

        crops = list(analysis_results.keys())
        suitability_scores = [analysis_results[crop]['suitability_analysis']['final_score'] for crop in crops]
        disease_risks = [analysis_results[crop]['suitability_analysis']['disease_risk'] for crop in crops]

        # Create scatter plot with color coding
        fig, ax = plt.subplots(figsize=(12, 10))

        # Color points based on risk-suitability combination
        colors = []
        sizes = []
        for suit, risk in zip(suitability_scores, disease_risks):
            if suit >= 0.7 and risk <= 0.3:
                colors.append('green')  # Excellent
                sizes.append(100)
            elif suit >= 0.5 and risk <= 0.5:
                colors.append('yellow')  # Good
                sizes.append(80)
            elif suit >= 0.3:
                colors.append('orange')  # Moderate
                sizes.append(60)
            else:
                colors.append('red')  # Poor
                sizes.append(60)

        scatter = ax.scatter(suitability_scores, disease_risks, c=colors, s=sizes, alpha=0.7)

        # Add crop labels
        for i, crop in enumerate(crops):
            ax.annotate(crop, (suitability_scores[i], disease_risks[i]),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax.set_xlabel('Suitability Score', fontsize=12)
        ax.set_ylabel('Disease Risk Index', fontsize=12)
        ax.set_title(f'Crop Suitability vs Disease Risk - {location_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Add quadrant labels
        ax.text(0.8, 0.1, 'Ideal\n(High Suitability\nLow Risk)', ha='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.2))
        ax.text(0.8, 0.8, 'Risky\n(High Suitability\nHigh Risk)', ha='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.2))
        ax.text(0.2, 0.1, 'Marginal\n(Low Suitability\nLow Risk)', ha='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.2))
        ax.text(0.2, 0.8, 'Avoid\n(Low Suitability\nHigh Risk)', ha='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.2))

        plt.tight_layout()
        plt.show()

    def analyze_all_crops(self, moisture_value, som_value, texture_value, temp_value, location_name):
        """Analyze all crops with enhanced suitability scoring"""

        print(f"🌱 ANALYZING CROP SUITABILITY FOR {location_name}")
        print("=" * 60)

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

        # Create comprehensive dashboard
        self.create_crop_suitability_dashboard(analysis_results, location_name)

        # Create visual comparison
        self.create_suitability_comparison_chart(analysis_results, location_name)

        # Create disease risk heatmap
        self.create_disease_risk_heatmap(analysis_results, location_name)

        return analysis_results

    # ============ SOIL ANALYSIS METHODS ============
    def create_soil_texture_triangle(self, texture_value, location_name):
        """Create soil texture triangle showing sand-silt-clay percentages"""
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create soil texture triangle
        vertices = np.array([[0, 0], [100, 0], [50, 86.6]])

        # Draw triangle
        triangle = plt.Polygon(vertices, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(triangle)

        # Add labels
        ax.text(0, -5, '100% Clay', ha='center', fontsize=10, fontweight='bold')
        ax.text(100, -5, '100% Sand', ha='center', fontsize=10, fontweight='bold')
        ax.text(50, 90, '100% Silt', ha='center', fontsize=10, fontweight='bold')

        # Define texture classes with approximate coordinates
        texture_coords = {
            'Clay': (20, 40),
            'Sandy clay': (55, 35),
            'Silty clay': (25, 60),
            'Clay loam': (35, 30),
            'Sandy clay loam': (60, 25),
            'Silty clay loam': (30, 50),
            'Loam': (40, 40),
            'Sandy loam': (65, 20),
            'Silt loam': (25, 65),
            'Silt': (15, 70),
            'Loamy sand': (80, 10),
            'Sand': (90, 5)
        }

        # Plot texture class labels
        for texture, (x, y) in texture_coords.items():
            ax.plot(x, y, 'o', markersize=8, alpha=0.7)
            ax.text(x, y+3, texture, ha='center', fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

        # Plot current soil texture if available
        if texture_value and 1 <= texture_value <= 12:
            current_texture = SOIL_TEXTURE_CLASSES[int(round(texture_value))]
            if current_texture in texture_coords:
                x, y = texture_coords[current_texture]
                ax.plot(x, y, 'ro', markersize=12, label=f'Current: {current_texture}')
                ax.annotate(f'Your Soil\n{current_texture}',
                           (x, y), xytext=(x+10, y+10),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           bbox=dict(boxstyle="round", facecolor="red", alpha=0.1))

        ax.set_xlim(-10, 110)
        ax.set_ylim(-10, 100)
        ax.set_aspect('equal')
        ax.set_title(f'Soil Texture Triangle - {location_name}\n(Sand-Silt-Clay Composition)',
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Sand Content (%)')
        ax.set_ylabel('Clay Content (%)')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.show()

    def create_texture_composition_chart(self, texture_value, location_name):
        """Create bar chart showing sand-silt-clay percentages"""
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

        fig, ax = plt.subplots(figsize=(12, 6))

        if texture_value and 1 <= texture_value <= 12:
            current_texture = SOIL_TEXTURE_CLASSES[int(round(texture_value))]
            composition = texture_compositions.get(current_texture, texture_compositions['Loam'])

            components = ['Sand', 'Silt', 'Clay']
            percentages = [composition['sand'], composition['silt'], composition['clay']]
            colors = ['#F4D03F', '#82E0AA', '#5DADE2']

            bars = ax.bar(components, percentages, color=colors, alpha=0.7, edgecolor='black')

            ax.set_title(f'Soil Texture Composition - {location_name}\n{current_texture}',
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('Percentage (%)')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar, percentage in zip(bars, percentages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{percentage}%', ha='center', va='bottom', fontweight='bold')

            # Add texture properties
            props_text = f"Texture Properties:\n"
            props_text += f"• Water Holding: {'High' if composition['clay'] > 40 else 'Medium' if composition['clay'] > 20 else 'Low'}\n"
            props_text += f"• Drainage: {'Slow' if composition['clay'] > 40 else 'Moderate' if composition['clay'] > 20 else 'Fast'}\n"
            props_text += f"• Workability: {'Difficult' if composition['clay'] > 40 else 'Good' if composition['sand'] > 40 else 'Moderate'}"

            ax.text(0.02, 0.98, props_text, transform=ax.transAxes, fontsize=10,
                   bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
                   verticalalignment='top')

        else:
            ax.text(0.5, 0.5, 'Texture data not available',
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Soil Texture Composition', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.show()

    def create_soil_texture_chart(self, texture_value, location_name):
        """Create soil texture classification chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Soil Texture Analysis - {location_name}', fontsize=16, fontweight='bold')

        # Chart 1: Soil Texture Triangle (Simplified)
        texture_classes = list(SOIL_TEXTURE_CLASSES.values())
        texture_counts = [0.1, 0.05, 0.08, 0.12, 0.09, 0.11, 0.15, 0.08, 0.07, 0.06, 0.05, 0.04]

        # Highlight current texture
        current_texture_idx = int(round(texture_value)) - 1 if texture_value else 6
        colors = ['lightgray'] * len(texture_classes)
        if 0 <= current_texture_idx < len(colors):
            colors[current_texture_idx] = 'red'

        bars = ax1.bar(range(len(texture_classes)), texture_counts, color=colors, alpha=0.7)
        ax1.set_title('Soil Texture Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Soil Texture Class')
        ax1.set_ylabel('Relative Frequency')
        ax1.set_xticks(range(len(texture_classes)))
        ax1.set_xticklabels([cls[:8] for cls in texture_classes], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, count in zip(bars, texture_counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{count:.0%}', ha='center', va='bottom', fontsize=8)

        # Chart 2: Soil Texture Properties
        texture_properties = {
            'Clay': {'Water Holding': 0.45, 'Drainage': 0.3, 'Workability': 0.2},
            'Sandy clay': {'Water Holding': 0.35, 'Drainage': 0.4, 'Workability': 0.3},
            'Silty clay': {'Water Holding': 0.4, 'Drainage': 0.35, 'Workability': 0.25},
            'Clay loam': {'Water Holding': 0.38, 'Drainage': 0.5, 'Workability': 0.6},
            'Sandy clay loam': {'Water Holding': 0.32, 'Drainage': 0.6, 'Workability': 0.5},
            'Silty clay loam': {'Water Holding': 0.35, 'Drainage': 0.45, 'Workability': 0.4},
            'Loam': {'Water Holding': 0.42, 'Drainage': 0.7, 'Workability': 0.9},
            'Sandy loam': {'Water Holding': 0.28, 'Drainage': 0.8, 'Workability': 0.8},
            'Silt loam': {'Water Holding': 0.38, 'Drainage': 0.6, 'Workability': 0.7},
            'Silt': {'Water Holding': 0.35, 'Drainage': 0.5, 'Workability': 0.6},
            'Loamy sand': {'Water Holding': 0.25, 'Drainage': 0.9, 'Workability': 0.7},
            'Sand': {'Water Holding': 0.15, 'Drainage': 1.0, 'Workability': 0.9}
        }

        if texture_value and 1 <= texture_value <= 12:
            current_texture_name = SOIL_TEXTURE_CLASSES[int(round(texture_value))]
            properties = texture_properties.get(current_texture_name, texture_properties['Loam'])

            categories = ['Water Holding', 'Drainage', 'Workability']
            values = [properties['Water Holding'], properties['Drainage'], properties['Workability']]

            bars = ax2.bar(categories, values, color=['blue', 'green', 'orange'], alpha=0.7)
            ax2.set_title(f'Soil Properties: {current_texture_name}', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Capacity Score (0-1)')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)

            # Add value labels on bars
            for i, v in enumerate(values):
                ax2.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'Texture data not available',
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Soil Properties', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.show()

    def create_som_spatial_chart(self, geometry, location_name):
        """Create soil organic matter spatial distribution chart"""
        print("📊 Generating SOM spatial distribution...")

        try:
            # Get SOM data for the region
            is_in_africa = AFRICA_BOUNDS.intersects(geometry, 100).getInfo()
            if is_in_africa:
                som_image = ee.Image("ISDASOIL/Africa/v1/carbon_organic")
                converted_som = som_image.divide(10).exp().subtract(1)
                soc_mean = converted_som.select(0)
            else:
                gsoc = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/FAO/GSOCMAP1-5-0")
                soc_mean = gsoc.select('b1')

            # Convert SOC to SOM
            soc_stats = soc_mean.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=1000,
                maxPixels=1e9
            ).getInfo()

            soc_val = list(soc_stats.values())[0] if soc_stats else 0.41
            soc_percent = soc_val / (BULK_DENSITY * (20 if is_in_africa else 30) * 100)
            som_percent = soc_percent * SOC_TO_SOM_FACTOR * 100

            # Create visualization
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
            fig.suptitle(f'Soil Organic Matter Analysis - {location_name}', fontsize=16, fontweight='bold')

            # Chart 1: SOM Quality Assessment
            som_categories = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
            som_ranges = [0, 1.0, 2.0, 3.5, 5.0, 10.0]
            som_colors = ['#8B0000', '#FF4500', '#FFD700', '#9ACD32', '#006400']

            current_category = None
            for i in range(len(som_ranges)-1):
                if som_ranges[i] <= som_percent < som_ranges[i+1]:
                    current_category = i
                    break

            bar_heights = [0.1, 0.2, 0.3, 0.2, 0.2]
            colors = [som_colors[i] if i == current_category else 'lightgray'
                     for i in range(len(som_categories))]

            bars = ax1.bar(som_categories, bar_heights, color=colors, alpha=0.7)
            ax1.set_title('SOM Quality Assessment', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Relative Quality')
            ax1.set_ylim(0, 0.35)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)

            # Add current SOM value
            ax1.axhline(y=som_percent/30, color='red', linestyle='--', linewidth=2,
                       label=f'Current: {som_percent:.2f}%')
            ax1.legend()

            # Chart 2: SOM Improvement Recommendations
            ax2.axis('off')
            recommendations = []

            if som_percent < 1.0:
                recommendations.extend([
                    "🔴 CRITICAL: Very low SOM",
                    "• Apply 10-15 tons/ha compost or manure",
                    "• Plant green manure crops (legumes)",
                    "• Use cover crops during off-season",
                    "• Reduce tillage intensity"
                ])
            elif som_percent < 2.0:
                recommendations.extend([
                    "🟡 MODERATE: Low SOM level",
                    "• Apply 5-10 tons/ha organic amendments",
                    "• Incorporate crop residues",
                    "• Use balanced fertilization",
                    "• Implement conservation tillage"
                ])
            elif som_percent < 3.5:
                recommendations.extend([
                    "🟢 GOOD: Adequate SOM",
                    "• Maintain with 2-5 tons/ha amendments",
                    "• Continue crop rotation",
                    "• Monitor soil health regularly",
                    "• Optimize irrigation practices"
                ])
            else:
                recommendations.extend([
                    "💚 EXCELLENT: High SOM",
                    "• Maintain current practices",
                    "• Continue organic amendments",
                    "• Monitor for optimal levels",
                    "• Share best practices"
                ])

            rec_text = "SOM IMPROVEMENT RECOMMENDATIONS\n\n"
            rec_text += f"Current SOM Level: {som_percent:.2f}%\n\n"
            for rec in recommendations:
                rec_text += f"{rec}\n"

            ax2.text(0.05, 0.95, rec_text, transform=ax2.transAxes, fontsize=10,
                    bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
                    verticalalignment='top')

            # Chart 3: SOM Impact on Crop Yield
            crops = ['Wheat', 'Maize', 'Potato', 'Tomato', 'Barley']
            yield_improvement = [
                min(100, som_percent * 15),  # Wheat
                min(100, som_percent * 12),  # Maize
                min(100, som_percent * 20),  # Potato
                min(100, som_percent * 18),  # Tomato
                min(100, som_percent * 14)   # Barley
            ]

            bars = ax3.bar(crops, yield_improvement, color='green', alpha=0.6)
            ax3.set_title('Potential Yield Improvement with SOM', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Yield Improvement (%)')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='x', rotation=45)

            # Add value labels
            for bar, imp in zip(bars, yield_improvement):
                ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                        f'{imp:.0f}%', ha='center', va='bottom', fontweight='bold')

            plt.tight_layout()
            plt.show()

            return som_percent

        except Exception as e:
            print(f"❌ Error creating SOM spatial chart: {e}")

            # Fallback visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            fig.suptitle(f'Soil Organic Matter Analysis - {location_name}', fontsize=16, fontweight='bold')

            ax1.text(0.5, 0.5, 'SOM Data Not Available\nUsing Default Values',
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('SOM Distribution', fontsize=14, fontweight='bold')

            ax2.text(0.5, 0.5, 'Check Earth Engine Access\nand Data Availability',
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Recommendations', fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.show()

            return 0.41

    def create_temporal_som_analysis(self, geometry, location_name):
        """Create temporal SOM pattern analysis"""
        print("📈 Generating temporal SOM patterns...")

        try:
            # Simulate temporal SOM data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            # Base SOM with seasonal variation
            base_som = 2.0  # Default base SOM
            seasonal_variation = [0.1, 0.05, 0.0, -0.05, -0.1, -0.15,
                                 -0.1, -0.05, 0.0, 0.05, 0.1, 0.15]

            som_values = [base_som + variation for variation in seasonal_variation]

            # Management scenarios
            conventional_som = [val * 0.8 for val in som_values]  # Degrading
            improved_som = [val * 1.1 for val in som_values]      # Improving
            optimal_som = [val * 1.3 for val in som_values]       # Optimal

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle(f'Temporal SOM Analysis - {location_name}', fontsize=16, fontweight='bold')

            # Chart 1: Seasonal SOM Variation
            ax1.plot(months, som_values, 'o-', linewidth=2, label='Current', color='blue')
            ax1.plot(months, conventional_som, '--', linewidth=2, label='Conventional', color='red')
            ax1.plot(months, improved_som, '--', linewidth=2, label='Improved', color='green')
            ax1.plot(months, optimal_som, '--', linewidth=2, label='Optimal', color='purple')

            ax1.set_title('Seasonal SOM Variation Patterns', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Month')
            ax1.set_ylabel('SOM (%)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(1.0, 3.0)

            # Chart 2: SOM Management Impact
            practices = ['Current', 'Conventional', 'Improved', 'Optimal']
            annual_avg = [
                np.mean(som_values),
                np.mean(conventional_som),
                np.mean(improved_som),
                np.mean(optimal_som)
            ]
            yield_impact = [0, -15, 10, 25]  # Percentage impact on yield

            x = np.arange(len(practices))
            width = 0.35

            bars1 = ax2.bar(x - width/2, annual_avg, width, label='SOM %', alpha=0.7, color='brown')
            bars2 = ax2.bar(x + width/2, yield_impact, width, label='Yield Impact %', alpha=0.7, color='green')

            ax2.set_title('Management Practice Impact', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Management Practice')
            ax2.set_ylabel('Values')
            ax2.set_xticks(x)
            ax2.set_xticklabels(practices)
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"❌ Error creating temporal SOM analysis: {e}")

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Temporal SOM Analysis Not Available',
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Temporal SOM Analysis', fontsize=16, fontweight='bold')
            plt.show()

    def create_soil_analysis_dashboard(self, geometry, location_name, texture_value, som_value):
        """Create comprehensive soil analysis dashboard"""
        print(f"\n🌱 CREATING SOIL ANALYSIS DASHBOARD FOR {location_name}")
        print("=" * 60)

        # 1. Soil Texture Analysis
        print("\n🏗️ 1. SOIL TEXTURE ANALYSIS")
        self.create_soil_texture_chart(texture_value, location_name)

        # Soil Texture Triangle
        print("\n📐 1b. SOIL TEXTURE TRIANGLE")
        self.create_soil_texture_triangle(texture_value, location_name)

        # Texture Composition Chart
        print("\n📊 1c. SOIL COMPOSITION BREAKDOWN")
        self.create_texture_composition_chart(texture_value, location_name)

        # 2. SOM Spatial Distribution
        print("\n📊 2. SOIL ORGANIC MATTER SPATIAL ANALYSIS")
        measured_som = self.create_som_spatial_chart(geometry, location_name)

        # 3. Temporal SOM Patterns
        print("\n📈 3. TEMPORAL SOM PATTERN ANALYSIS")
        self.create_temporal_som_analysis(geometry, location_name)

        return measured_som

    # ============ CLIMATE ANALYSIS METHODS ============
    def classify_climate_simplified(self, temp, precip, aridity):
        """JavaScript implementation for simplified temperature-precipitation classification"""
        # Main temperature-precipitation classification
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

    def classify_aridity_based(self, temp, precip, aridity):
        """JavaScript implementation for aridity-based classification"""
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
        """JavaScript implementation for Köppen-Geiger classification"""
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
        """Get climate classification using JavaScript logic"""
        print(f"🌤️ Getting accurate climate classification for {location_name}...")

        try:
            # Use WorldClim like GEE JS
            worldclim = ee.Image("WORLDCLIM/V1/BIO")

            # Extract the same variables as GEE JS
            annual_mean_temp = worldclim.select('bio01').divide(10)  # °C
            annual_precip = worldclim.select('bio12')  # mm/year

            # Calculate aridity index EXACTLY like JavaScript
            aridity_index = annual_precip.divide(annual_mean_temp.add(33))

            # Get statistics for the region
            stats = ee.Image.cat([annual_mean_temp, annual_precip, aridity_index]).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry.centroid(),
                scale=10000,
                maxPixels=1e6
            ).getInfo()

            mean_temp = stats.get('bio01', 18.5)  # Default to Annaba-like temperature
            mean_precip = stats.get('bio12', 800)  # Default to Annaba-like precipitation
            mean_aridity = stats.get('bio12', 0) / (stats.get('bio01', 0) + 33) if (stats.get('bio01', 0) + 33) != 0 else 1.5

            print(f"   Raw stats - Temp: {mean_temp:.1f}°C, Precip: {mean_precip:.0f}mm, Aridity: {mean_aridity:.3f}")

            # Apply EXACT JavaScript classification logic
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

            print(f"✅ Climate classification: {climate_zone} (Class {climate_class})")
            return climate_analysis

        except Exception as e:
            print(f"❌ Climate classification failed: {e}")
            # Return GEE-compatible results for Annaba based on JavaScript output
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
        """Create comprehensive climate classification visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Climate Classification Analysis - {location_name}\n{classification_type}',
                    fontsize=16, fontweight='bold', y=0.95)

        # Chart 1: Climate Zone Distribution
        current_class = climate_data['climate_class']
        current_zone = climate_data['climate_zone']

        ax1.barh([0], [1], color=self.climate_palettes[classification_type][current_class-1], alpha=0.7)
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Class {current_class}'])
        ax1.set_xlabel('Representation')
        ax1.set_title(f'Current Climate Zone: {current_zone}', fontsize=12, fontweight='bold')
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
        ax2.set_title('Climate Parameters Radar Chart', fontsize=12, fontweight='bold')
        ax2.legend()

        # Chart 3: Temperature-Precipitation Scatter
        ax3.scatter(climate_data['mean_temperature'], climate_data['mean_precipitation'],
                   c=self.climate_palettes[classification_type][current_class-1], s=200, alpha=0.7)
        ax3.set_xlabel('Mean Temperature (°C)')
        ax3.set_ylabel('Mean Precipitation (mm/year)')
        ax3.set_title('Temperature vs Precipitation', fontsize=12, fontweight='bold')
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
            legend_text += f"{marker} Class {class_id}: {class_name}\n"

        ax4.text(0.1, 0.9, legend_text, transform=ax4.transAxes, fontsize=9,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
                verticalalignment='top')

        plt.tight_layout()
        plt.show()

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
            print(f"Error getting precipitation: {e}")
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
            print(f"Error getting soil properties: {e}")
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
            print(f"Error getting topography: {e}")
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
        print(f"💧 Analyzing Groundwater Potential for {name}...")

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

            print(f"✅ {name}: GW Score = {result['score']:.3f} ({category}) | "
                  f"Soil = {soil_props['soil_type']} | "
                  f"Recharge = {result['recharge_mm']:.0f}mm | "
                  f"Sand = {result['sand_percent']:.1f}%")
            return result

        except Exception as e:
            print(f"❌ Error analyzing groundwater for {name}: {str(e)}")
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

    def create_groundwater_charts(self, final_results, location_name):
        """Create comprehensive groundwater visualization dashboard"""
        if not final_results:
            print("No groundwater results to visualize")
            return

        df = pd.DataFrame(final_results)

        # Set professional style
        plt.style.use('default')
        sns.set_palette("viridis")
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 18,
            'axes.labelsize': 16,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'figure.titlesize': 20
        })

        # FIGURE 1: Main Scores and Water Balance
        fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 15))
        fig1.suptitle(f'GROUNDWATER POTENTIAL - {location_name.upper()}', fontsize=20, fontweight='bold', y=0.95)

        # 1. MAIN SCORE COMPARISON
        colors = ['#FF6B6B' if x < 0.45 else '#4ECDC4' if x < 0.6 else '#45B7D1' if x < 0.75 else '#96CEB4' for x in df['score']]
        bars = ax1.bar(df['name'], df['score'], color=colors, alpha=0.8, edgecolor='black', linewidth=2)

        for bar, score in zip(bars, df['score']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax1.set_ylabel('Groundwater Potential Score', fontsize=14, fontweight='bold')
        ax1.set_title('GROUNDWATER POTENTIAL SCORE', fontsize=16, fontweight='bold')
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.tick_params(axis='x', rotation=45)

        # Add category labels
        for i, (name, score, category) in enumerate(zip(df['name'], df['score'], df['category'])):
            color = 'red' if category == 'LOW' else 'orange' if category == 'MODERATE' else 'green'
            ax1.text(i, -0.15, category, ha='center', va='top', fontweight='bold',
                    fontsize=10, color=color, rotation=0,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.2))

        # 2. WATER BALANCE
        x = np.arange(len(df))
        width = 0.2

        precipitation = df['precipitation_mm']
        recharge = df['recharge_mm']
        et = [r.get('evapotranspiration_mm', 0) for r in [res.get('water_balance', {}) for res in final_results]]
        runoff = [r.get('runoff_mm', 0) for r in [res.get('water_balance', {}) for res in final_results]]

        ax2.bar(x - width*1.5, precipitation, width, label='Precipitation', color='#1f77b4', alpha=0.8)
        ax2.bar(x - width*0.5, et, width, label='Evapotranspiration', color='#ff7f0e', alpha=0.8)
        ax2.bar(x + width*0.5, runoff, width, label='Runoff', color='#2ca02c', alpha=0.8)
        bars_recharge = ax2.bar(x + width*1.5, recharge, width, label='Recharge', color='#d62728', alpha=0.9, edgecolor='darkred', linewidth=2)

        ax2.set_ylabel('Water Balance (mm/year)', fontsize=14, fontweight='bold')
        ax2.set_title('ANNUAL WATER BALANCE COMPONENTS', fontsize=16, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['name'], rotation=45)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3, axis='y')

        # Add recharge efficiency labels
        for i, (p, r, bar) in enumerate(zip(precipitation, recharge, bars_recharge)):
            if p > 0:
                percentage = (r / p) * 100
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(precipitation)*0.02,
                        f'{percentage:.1f}%', ha='center', va='bottom',
                        fontweight='bold', fontsize=10, color='darkred')

        # 3. SOIL TEXTURE
        bottom = np.zeros(len(df))
        for soil_component, color in [('sand_percent', '#F4A460'),
                                     ('silt_percent', '#D2691E'),
                                     ('clay_percent', '#8B4513')]:
            values = df[soil_component]
            ax3.bar(range(len(df)), values, bottom=bottom,
                   label=soil_component.replace('_percent', '').title(),
                   color=color, alpha=0.8, edgecolor='black')
            bottom += values

        ax3.set_ylabel('Soil Composition (%)', fontsize=14, fontweight='bold')
        ax3.set_title('SOIL TEXTURE COMPOSITION', fontsize=16, fontweight='bold')
        ax3.set_xticks(range(len(df)))
        ax3.set_xticklabels([name.split('-')[-1] if '-' in name else name for name in df['name']], rotation=45)
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim(0, 100)

        # 4. HYDRAULIC CONDUCTIVITY & SOIL TYPES
        conductivity = df['conductivity']
        soil_colors = {'Sand': '#F4A460', 'Sandy Loam': '#D2691E', 'Loam': '#8B4513', 'Clay Loam': '#A0522D', 'Clay': '#654321'}
        colors = [soil_colors.get(st, '#666666') for st in df['soil_type']]

        bars = ax4.bar(df['name'], conductivity, color=colors, alpha=0.8, edgecolor='black')
        ax4.set_ylabel('Hydraulic Conductivity (cm/day)', fontsize=14, fontweight='bold')
        ax4.set_title('SOIL TRANSMISSION CAPACITY', fontsize=16, fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3, axis='y')

        # Add soil type labels
        for i, (bar, soil_type) in enumerate(zip(bars, df['soil_type'])):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(conductivity)*0.02,
                    soil_type, ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=45)

        plt.tight_layout()
        plt.show()

        # FIGURE 2: Component Analysis and Topography
        fig2, ((ax5, ax6), (ax7, ax8)) = plt.subplots(2, 2, figsize=(20, 15))
        fig2.suptitle('COMPONENT ANALYSIS & TOPOGRAPHY', fontsize=18, fontweight='bold', y=0.95)

        # 5. COMPONENT BREAKDOWN
        categories = ['Recharge', 'Soil Infil.', 'Topography', 'Soil Texture', 'Geology']
        locations = df['name']

        component_data = []
        for result in final_results:
            components = result.get('components', {})
            scores = [
                components.get('recharge_potential', 0),
                components.get('soil_infiltration', 0),
                components.get('topographic_factors', 0),
                components.get('soil_texture', 0),
                components.get('geological_factors', 0)
            ]
            component_data.append(scores)

        # Grouped bar chart
        x = np.arange(len(categories))
        width = 0.15

        for i, location in enumerate(locations):
            offset = width * (i - len(locations)/2 + 0.5)
            bars = ax5.bar(x + offset, component_data[i], width, label=location, alpha=0.8)

            # Add value labels
            for j, value in enumerate(component_data[i]):
                if value > 0.01:
                    ax5.text(j + offset, value + 0.01, f'{value:.2f}',
                            ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax5.set_xlabel('Component Type', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Component Score', fontsize=14, fontweight='bold')
        ax5.set_title('COMPONENT SCORE BREAKDOWN', fontsize=16, fontweight='bold')
        ax5.set_xticks(x)
        ax5.set_xticklabels(categories)
        ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax5.set_ylim(0, 0.5)
        ax5.grid(True, alpha=0.3, axis='y')

        # 6. RADAR CHART
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        colors_radar = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, (location, scores) in enumerate(zip(locations, component_data)):
            values = scores + scores[:1]
            ax6.plot(angles, values, 'o-', linewidth=2, label=location, color=colors_radar[i % len(colors_radar)])
            ax6.fill(angles, values, alpha=0.1, color=colors_radar[i % len(colors_radar)])

        ax6.set_xticks(angles[:-1])
        ax6.set_xticklabels(categories, fontsize=12, fontweight='bold')
        ax6.set_ylim(0, 0.5)
        ax6.set_title('COMPONENT RADAR CHART', fontsize=16, fontweight='bold')
        ax6.legend(bbox_to_anchor=(1.1, 1), loc='upper left')
        ax6.grid(True, alpha=0.3)

        # 7. TOPOGRAPHY - SLOPE vs TWI
        x_pos = np.arange(len(df))
        width = 0.35

        # Slope bars
        bars_slope = ax7.bar(x_pos - width/2, df['slope'], width, label='Slope (°)',
                            color='lightblue', alpha=0.7, edgecolor='navy')
        ax7_twin = ax7.twinx()
        bars_twi = ax7_twin.bar(x_pos + width/2, df['twi'], width, label='TWI',
                               color='lightcoral', alpha=0.7, edgecolor='darkred')

        ax7.set_ylabel('Slope (degrees)', fontsize=14, fontweight='bold', color='navy')
        ax7_twin.set_ylabel('Topographic Wetness Index', fontsize=14, fontweight='bold', color='darkred')
        ax7.set_title('TOPOGRAPHIC ANALYSIS', fontsize=16, fontweight='bold')
        ax7.set_xticks(x_pos)
        ax7.set_xticklabels([name.split('-')[-1] if '-' in name else name for name in df['name']], rotation=45)

        # Combine legends
        lines1, labels1 = ax7.get_legend_handles_labels()
        lines2, labels2 = ax7_twin.get_legend_handles_labels()
        ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        ax7.grid(True, alpha=0.3, axis='y')

        # 8. GEOGRAPHIC DISTRIBUTION
        scatter = ax8.scatter(df['lon'], df['lat'],
                             c=df['score'],
                             s=df['recharge_mm'] * 3,
                             cmap='RdYlGn',
                             alpha=0.7,
                             edgecolor='black',
                             linewidth=1)

        # Add location labels
        for i, row in df.iterrows():
            ax8.annotate(f"{row['name']}\n{row['score']:.3f}",
                        (row['lon'], row['lat']),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", linewidth=1),
                        fontsize=9, fontweight='bold')

        ax8.set_xlabel('Longitude', fontsize=14, fontweight='bold')
        ax8.set_ylabel('Latitude', fontsize=14, fontweight='bold')
        ax8.set_title('GEOGRAPHIC DISTRIBUTION\n(Bubble size = Recharge)', fontsize=16, fontweight='bold')
        ax8.grid(True, alpha=0.3)

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax8, shrink=0.8)
        cbar.set_label('GW Potential Score', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.show()

        # Print comprehensive summary
        print("\n" + "="*80)
        print("📈 GROUNDWATER ANALYSIS SUMMARY")
        print("="*80)

        print(f"• Location Analyzed: {location_name}")
        print(f"• Average GW Score: {df['score'].mean():.3f} ± {df['score'].std():.3f}")
        print(f"• Score Range: {df['score'].min():.3f} - {df['score'].max():.3f}")
        print(f"• Categories: {', '.join(df['category'].unique())}")
        print(f"• Average Precipitation: {df['precipitation_mm'].mean():.0f} mm/year")
        print(f"• Average Recharge: {df['recharge_mm'].mean():.0f} mm/year")
        print(f"• Recharge Efficiency: {(df['recharge_mm'].sum() / df['precipitation_mm'].sum() * 100):.1f}%")
        print(f"• Soil Types: {', '.join(df['soil_type'].unique())}")
        print(f"• Average Conductivity: {df['conductivity'].mean():.2f} cm/day")
        print(f"• Topography - Avg Slope: {df['slope'].mean():.1f}°, Avg TWI: {df['twi'].mean():.2f}")

    # ============ EARTH ENGINE DATA METHODS ============
    def get_administrative_regions(self, country, region='Select Region'):
        """Get available administrative regions using FAO GAUL"""
        try:
            if region == 'Select Region':
                regions = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .aggregate_array('ADM1_NAME') \
                               .getInfo()
                return sorted(list(set(regions))) if regions else []
            else:
                municipalities = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                                     .filter(ee.Filter.eq('ADM1_NAME', region)) \
                                     .aggregate_array('ADM2_NAME') \
                                     .getInfo()
                return sorted(list(set(municipalities))) if municipalities else []

        except Exception as e:
            print(f"❌ Error getting administrative regions: {e}")
            return []

    def get_geometry_from_selection(self, country, region, municipality):
        """Get geometry based on selection level using FAO GAUL"""
        try:
            if municipality != 'Select Municipality':
                feature = FAO_GAUL_ADMIN2.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .filter(ee.Filter.eq('ADM2_NAME', municipality)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{municipality}, {region}, {country}"
                print(f"📍 Selected: {location_name}")
                return geometry, location_name

            elif region != 'Select Region':
                feature = FAO_GAUL_ADMIN1.filter(ee.Filter.eq('ADM0_NAME', country)) \
                               .filter(ee.Filter.eq('ADM1_NAME', region)) \
                               .first()
                geometry = feature.geometry()
                location_name = f"{region}, {country}"
                print(f"📍 Selected: {location_name}")
                return geometry, location_name

            elif country != 'Select Country':
                feature = FAO_GAUL.filter(ee.Filter.eq('ADM0_NAME', country)).first()
                geometry = feature.geometry()
                location_name = f"{country}"
                print(f"📍 Selected: {location_name}")
                return geometry, location_name

            else:
                print("❌ Please select a country")
                return None, None

        except Exception as e:
            print(f"❌ Geometry error: {e}")
            return None, None

    def get_area_representative_values(self, geometry, area_name):
        """Get representative soil values for crop suitability analysis"""
        print('📊 Calculating representative soil values for ' + area_name + '...')

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

        print('✅ Representative values obtained:')
        print('   Moisture: ' + self.format_number(moisture_val, 3) + ' m³/m³')
        print('   SOM: ' + self.format_number(som_val, 2) + '%')

        texture_name = 'Unknown'
        display_texture_value = 'N/A'
        if texture_val is not None:
            rounded_texture = int(round(texture_val))
            display_texture_value = str(rounded_texture)
            if 1 <= rounded_texture <= 12:
                texture_name = SOIL_TEXTURE_CLASSES[rounded_texture]
        print('   Texture: ' + texture_name + ' (Class ' + display_texture_value + ')')
        print('   Temperature: ' + self.format_number(temp_val, 1) + '°C')
        print('')

        # Create soil analysis dashboard
        self.create_soil_analysis_dashboard(geometry, area_name, texture_val, som_val)

        return moisture_val, som_val, texture_val, temp_val

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

    def get_daily_climate_data(self, start_date, end_date, geometry):
        """Get daily climate data matching GEE JavaScript implementation"""
        try:
            print("🛰️ Collecting daily climate data (GEE compatible)...")

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
            print(f"❌ Daily climate data extraction failed: {e}")
            return self._create_daily_synthetic_data(start_date, end_date, geometry)

    def _create_daily_synthetic_data(self, start_date, end_date, geometry):
        """Create synthetic daily data matching GEE patterns"""
        print("📊 Creating daily synthetic data matching GEE patterns...")

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

    # ============ UTILITY METHODS ============
    def pad_string(self, str_val, length):
        """Pad string to specified length"""
        str_val = str(str_val)
        while len(str_val) < length:
            str_val += ' '
        return str_val

    def format_number(self, num, decimals):
        """Format number with specified decimals"""
        if num is None or np.isnan(num):
            return 'N/A'
        return f"{num:.{decimals}f}"

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

        print(f"🎯 COMPREHENSIVE AGRICULTURAL ANALYSIS: {country}")
        if region != 'Select Region':
            print(f"📍 Region/State: {region}")
        if municipality != 'Select Municipality':
            print(f"🏙️ Municipality/City: {municipality}")
        print(f"🌤️ Climate Classification: {classification_type}")
        print(f"📊 Analysis Type: {analysis_type}")
        print()

        # Get geometry for selected location
        geometry, location_name = self.get_geometry_from_selection(country, region, municipality)

        if not geometry:
            print("❌ Could not get geometry for the selected location")
            return None

        results = {
            'location_name': location_name,
            'geometry': geometry,
            'classification_type': classification_type,
            'analysis_type': analysis_type
        }

        if analysis_type == 'groundwater':
            # Run groundwater analysis
            print("\n" + "="*50)
            print("💧 GROUNDWATER POTENTIAL ANALYSIS")
            print("="*50)

            gw_results = self.analyze_groundwater_potential(geometry, location_name)
            results['groundwater_analysis'] = gw_results

            # Create groundwater charts
            self.create_groundwater_charts([gw_results], location_name)

        else:
            # Run comprehensive crop suitability analysis (original functionality)
            # 1. Climate Classification
            print("\n" + "="*50)
            print("🌤️ 1. CLIMATE CLASSIFICATION ANALYSIS")
            print("="*50)
            results['climate_analysis'] = self.get_accurate_climate_classification(
                geometry, location_name, classification_type)

            # Create climate visualization
            self.create_climate_classification_chart(classification_type, location_name, results['climate_analysis'])

            # 2. Soil Analysis
            print("\n" + "="*50)
            print("🌱 2. SOIL ANALYSIS")
            print("="*50)
            moisture_val, som_val, texture_val, temp_val = self.get_area_representative_values(geometry, location_name)

            results['soil_parameters'] = {
                'moisture': moisture_val,
                'organic_matter': som_val,
                'texture': texture_val,
                'temperature': temp_val
            }

            # 3. Crop Suitability Analysis with Disease Risk
            print("\n" + "="*50)
            print("🌾 3. CROP SUITABILITY & DISEASE RISK ANALYSIS")
            print("="*50)
            crop_results = self.analyze_all_crops(moisture_val, som_val, texture_val, temp_val, location_name)
            results['crop_analysis'] = crop_results

        print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETED FOR {location_name}")
        print("="*70)
        print("📊 Analysis Includes:")
        if analysis_type == 'groundwater':
            print("   • Groundwater potential assessment")
            print("   • Water balance components analysis")
            print("   • Soil infiltration capacity")
            print("   • Topographic influence on groundwater")
            print("   • Comprehensive groundwater potential scoring")
        else:
            print("   • Climate classification and visualization")
            print("   • Soil texture and organic matter analysis")
            print("   • Crop suitability scoring for 32 crops")
            print("   • Disease risk assessment and management strategies")
            print("   • Customized recommendations for selected region")

        return results

# =============================================================================
# INTERFACE FUNCTIONS
# =============================================================================

def get_country_list():
    """Get list of all countries"""
    try:
        countries = FAO_GAUL.aggregate_array('ADM0_NAME').distinct().sort().getInfo()
        return ['Select Country'] + countries
    except Exception as e:
        print(f"Error getting country list: {e}")
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
        print(f"Error getting regions for {country}: {e}")
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
        print(f"Error getting municipalities for {region}: {e}")
        return ['Select Municipality']

def create_comprehensive_interface():
    """Create interactive selection interface"""
    print("🌍 COMPREHENSIVE AGRICULTURAL ANALYSIS TOOL")
    print("=" * 70)
    print("Integrated Approach: Climate + Soil + Crop Suitability + Disease Risk + Groundwater")
    print("Features: 32 crops analysis, Disease risk assessment, Management strategies, Groundwater potential")
    print("Data Sources: FAO GAUL, Earth Engine, OpenLandMap, ISDASOIL")

    # Initialize analyzer
    analyzer = ComprehensiveAgriculturalAnalyzer()

    # Create dropdown widgets
    country_dropdown = widgets.Dropdown(
        options=get_country_list(),
        value='Algeria',
        description='Country:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='400px')
    )

    region_dropdown = widgets.Dropdown(
        options=['Select Region'],
        value='Select Region',
        description='Region/State:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='400px')
    )

    municipality_dropdown = widgets.Dropdown(
        options=['Select Municipality'],
        value='Select Municipality',
        description='Municipality:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='400px')
    )

    # Climate classification type
    climate_classification = widgets.Dropdown(
        options=['Simplified Temperature-Precipitation', 'Aridity-Based', 'Köppen-Geiger'],
        value='Simplified Temperature-Precipitation',
        description='Climate Classification:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='400px')
    )

    # Analysis type selection
    analysis_type = widgets.Dropdown(
        options=['crop_suitability', 'groundwater'],
        value='crop_suitability',
        description='Analysis Type:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='400px')
    )

    analyze_button = widgets.Button(
        description='Run Comprehensive Analysis',
        button_style='success',
        tooltip='Click for comprehensive agricultural analysis',
        layout=widgets.Layout(width='250px')
    )

    output = widgets.Output()

    # Update functions
    def update_regions(change):
        if change['type'] == 'change' and change['name'] == 'value':
            with output:
                clear_output()
                print(f"Loading regions for {change['new']}...")
            regions = get_region_list(change['new'])
            region_dropdown.options = regions
            region_dropdown.value = 'Select Region'
            municipality_dropdown.options = ['Select Municipality']
            municipality_dropdown.value = 'Select Municipality'

    def update_municipalities(change):
        if change['type'] == 'change' and change['name'] == 'value' and change['new'] != 'Select Region':
            with output:
                clear_output()
                print(f"Loading municipalities for {change['new']}...")
            municipalities = get_municipality_list(country_dropdown.value, change['new'])
            municipality_dropdown.options = municipalities
            municipality_dropdown.value = 'Select Municipality'

    def on_analyze_click(b):
        with output:
            clear_output()
            print("🔍 Starting comprehensive agricultural analysis...")
            import time
            start_time = time.time()

            try:
                results = analyzer.run_comprehensive_analysis(
                    country_dropdown.value,
                    region_dropdown.value,
                    municipality_dropdown.value,
                    climate_classification.value,
                    analysis_type.value
                )

                if results:
                    print(f"\n🎉 ANALYSIS SUCCESSFULLY COMPLETED!")
                    print(f"📍 Location: {results['location_name']}")
                    if analysis_type.value == 'groundwater':
                        print(f"💧 Groundwater Score: {results['groundwater_analysis']['score']:.3f} ({results['groundwater_analysis']['category']})")
                    else:
                        print(f"🌤️ Climate: {results['climate_analysis']['climate_zone']}")
                        print(f"🌱 Crops Analyzed: {len(results['crop_analysis'])}")

                else:
                    print("❌ Analysis failed")

            except Exception as e:
                print(f"❌ Error during analysis: {e}")
                import traceback
                traceback.print_exc()

            end_time = time.time()
            print(f"\n⏱️ Comprehensive analysis completed in {end_time - start_time:.1f} seconds")

    # Link events
    country_dropdown.observe(update_regions, names='value')
    region_dropdown.observe(update_municipalities, names='value')
    analyze_button.on_click(on_analyze_click)

    # Initialize regions for default country
    update_regions({'type': 'change', 'name': 'value', 'new': country_dropdown.value})

    # Display interface
    display(widgets.VBox([
        widgets.HTML("<h3>Select Location for Comprehensive Agricultural Analysis:</h3>"),
        widgets.HTML("<p><em>Integrating climate analysis, soil analysis, crop suitability with disease risk assessment for 32 crops + Groundwater potential analysis</em></p>"),
        country_dropdown,
        region_dropdown,
        municipality_dropdown,
        climate_classification,
        analysis_type,
        analyze_button,
        output
    ]))

    return analyzer

# Run the application
if __name__ == "__main__":
    # Import required libraries
    try:
        from scipy.stats import linregress
    except ImportError:
        print("⚠️ scipy not available, installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
        from scipy.stats import linregress

    analyzer = create_comprehensive_interface()
