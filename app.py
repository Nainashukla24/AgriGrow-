import os
import json
from flask import Flask, render_template, request, jsonify

# Simple version without extra dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv is not available, we'll just continue without it
    pass

app = Flask(__name__)

# Enhanced crop recommendation system
def get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    # This is an improved model with more crops and better scoring
    crops = {
        'rice': {
            'n': (80, 120), 'p': (30, 60), 'k': (20, 40), 'temp': (22, 32), 
            'humidity': (80, 100), 'ph': (5.5, 6.5), 'rainfall': (200, 300),
            'description': 'A staple food crop that thrives in warm, humid conditions with abundant water.',
            'growing_season': '90-150 days depending on variety',
            'soil_type': 'Clay or clay loam soils that retain water well'
        },
        'wheat': {
            'n': (100, 140), 'p': (50, 80), 'k': (25, 50), 'temp': (15, 25), 
            'humidity': (60, 70), 'ph': (6.0, 7.0), 'rainfall': (75, 100),
            'description': 'A cool-season crop that is one of the world\'s most important cereal grains.',
            'growing_season': '120-150 days',
            'soil_type': 'Well-drained loamy soils'
        },
        'maize': {
            'n': (80, 160), 'p': (50, 80), 'k': (40, 90), 'temp': (20, 30), 
            'humidity': (50, 80), 'ph': (5.5, 7.0), 'rainfall': (80, 110),
            'description': 'A versatile crop used for food, feed, and industrial products.',
            'growing_season': '90-120 days',
            'soil_type': 'Well-drained, fertile soils'
        },
        'cotton': {
            'n': (120, 200), 'p': (50, 80), 'k': (50, 90), 'temp': (25, 35), 
            'humidity': (50, 70), 'ph': (5.5, 8.0), 'rainfall': (60, 100),
            'description': 'A major fiber crop that requires warm temperatures and moderate rainfall.',
            'growing_season': '150-180 days',
            'soil_type': 'Deep, well-drained soils'
        },
        'sugarcane': {
            'n': (150, 300), 'p': (60, 100), 'k': (40, 80), 'temp': (24, 35), 
            'humidity': (70, 85), 'ph': (6.0, 8.0), 'rainfall': (150, 200),
            'description': 'A tropical grass that is a major source of sugar worldwide.',
            'growing_season': '10-12 months',
            'soil_type': 'Well-drained, fertile soils with good water retention'
        },
        'tomato': {
            'n': (100, 150), 'p': (60, 90), 'k': (60, 100), 'temp': (20, 30), 
            'humidity': (50, 70), 'ph': (6.0, 7.0), 'rainfall': (60, 100),
            'description': 'A popular vegetable crop that requires warm temperatures and consistent moisture.',
            'growing_season': '70-90 days',
            'soil_type': 'Well-drained, fertile loamy soil'
        },
        'potato': {
            'n': (120, 200), 'p': (100, 150), 'k': (80, 120), 'temp': (15, 25), 
            'humidity': (60, 80), 'ph': (5.0, 6.5), 'rainfall': (50, 75),
            'description': 'A cool-season root vegetable that is a staple food in many regions.',
            'growing_season': '90-120 days',
            'soil_type': 'Loose, well-drained, slightly acidic soil'
        },
        'sunflower': {
            'n': (90, 130), 'p': (40, 70), 'k': (80, 120), 'temp': (20, 30), 
            'humidity': (40, 60), 'ph': (6.0, 7.5), 'rainfall': (40, 70),
            'description': 'An oilseed crop that is drought-tolerant and adaptable to various conditions.',
            'growing_season': '90-120 days',
            'soil_type': 'Well-drained, fertile soil with good water-holding capacity'
        }
    }
    
    # Calculate weighted scores for each crop
    scores = {}
    for crop, requirements in crops.items():
        # Base score starts at 0
        score = 0
        
        # Calculate how well each parameter matches the requirements
        # Use a weighted approach where the closer to the ideal range, the higher the score
        n_weight = 1.0
        if requirements['n'][0] <= n <= requirements['n'][1]:
            score += 1.0 * n_weight
        else:
            # Calculate distance from range and apply a penalty
            n_distance = min(abs(n - requirements['n'][0]), abs(n - requirements['n'][1]))
            n_range = requirements['n'][1] - requirements['n'][0]
            score += max(0, 1.0 - (n_distance / n_range)) * n_weight
        
        # Apply similar logic for other parameters
        p_weight = 1.0
        if requirements['p'][0] <= p <= requirements['p'][1]:
            score += 1.0 * p_weight
        else:
            p_distance = min(abs(p - requirements['p'][0]), abs(p - requirements['p'][1]))
            p_range = requirements['p'][1] - requirements['p'][0]
            score += max(0, 1.0 - (p_distance / p_range)) * p_weight
        
        k_weight = 1.0
        if requirements['k'][0] <= k <= requirements['k'][1]:
            score += 1.0 * k_weight
        else:
            k_distance = min(abs(k - requirements['k'][0]), abs(k - requirements['k'][1]))
            k_range = requirements['k'][1] - requirements['k'][0]
            score += max(0, 1.0 - (k_distance / k_range)) * k_weight
        
        # Temperature is very important for crop growth
        temp_weight = 1.5
        if requirements['temp'][0] <= temperature <= requirements['temp'][1]:
            score += 1.0 * temp_weight
        else:
            temp_distance = min(abs(temperature - requirements['temp'][0]), abs(temperature - requirements['temp'][1]))
            temp_range = requirements['temp'][1] - requirements['temp'][0]
            score += max(0, 1.0 - (temp_distance / temp_range)) * temp_weight
        
        # Humidity affects disease pressure and water requirements
        humidity_weight = 1.0
        if requirements['humidity'][0] <= humidity <= requirements['humidity'][1]:
            score += 1.0 * humidity_weight
        else:
            humidity_distance = min(abs(humidity - requirements['humidity'][0]), abs(humidity - requirements['humidity'][1]))
            humidity_range = requirements['humidity'][1] - requirements['humidity'][0]
            score += max(0, 1.0 - (humidity_distance / humidity_range)) * humidity_weight
        
        # pH is critical for nutrient availability
        ph_weight = 1.2
        if requirements['ph'][0] <= ph <= requirements['ph'][1]:
            score += 1.0 * ph_weight
        else:
            ph_distance = min(abs(ph - requirements['ph'][0]), abs(ph - requirements['ph'][1]))
            ph_range = requirements['ph'][1] - requirements['ph'][0]
            score += max(0, 1.0 - (ph_distance / ph_range)) * ph_weight
        
        # Rainfall/irrigation needs
        rainfall_weight = 1.3
        if requirements['rainfall'][0] <= rainfall <= requirements['rainfall'][1]:
            score += 1.0 * rainfall_weight
        else:
            rainfall_distance = min(abs(rainfall - requirements['rainfall'][0]), abs(rainfall - requirements['rainfall'][1]))
            rainfall_range = requirements['rainfall'][1] - requirements['rainfall'][0]
            score += max(0, 1.0 - (rainfall_distance / rainfall_range)) * rainfall_weight
        
        # Calculate normalized score (0-100%)
        max_possible_score = n_weight + p_weight + k_weight + temp_weight + humidity_weight + ph_weight + rainfall_weight
        normalized_score = (score / max_possible_score) * 100
        
        # Store the score and crop details
        scores[crop] = {
            'score': round(normalized_score, 1),
            'description': requirements['description'],
            'growing_season': requirements['growing_season'],
            'soil_type': requirements['soil_type']
        }
    
    # Return top 3 recommendations with details
    recommendations = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)[:3]
    return [{
        'crop': crop, 
        'score': details['score'],
        'description': details['description'],
        'growing_season': details['growing_season'],
        'soil_type': details['soil_type']
    } for crop, details in recommendations]

# Weather API integration
def get_weather_data(city):
    api_key = os.getenv('WEATHER_API_KEY', 'demo_key')  # Replace with your API key in .env file
    if api_key == 'demo_key':
        # Return mock data if no API key is provided
        return {
            'city': city,
            'temperature': 25,
            'humidity': 65,
            'description': 'Partly cloudy',
            'forecast': [
                {'day': 'Tomorrow', 'temp': 26, 'description': 'Sunny'},
                {'day': 'Day after', 'temp': 24, 'description': 'Light rain'},
                {'day': 'In 3 days', 'temp': 23, 'description': 'Cloudy'}
            ]
        }
    
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            weather_data = {
                'city': city,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'forecast': []  # In a real app, you'd make another API call for forecast
            }
            return weather_data
        else:
            return {'error': f"Error: {data.get('message', 'Unknown error')}"}
    except Exception as e:
        return {'error': f"Error: {str(e)}"}

# Improved disease identification (no dependency on PIL)
def identify_disease(image_file):
    # This is a simplified mock function that doesn't require image processing
    # We'll simulate disease identification based on the image filename
    filename = image_file.filename.lower() if hasattr(image_file, 'filename') else ''
    
    # Define a comprehensive list of common crop diseases with detailed information
    diseases = [
        {
            'name': 'Leaf Blight',
            'confidence': 0.85,
            'description': 'A fungal disease that causes brown lesions on leaves that expand and eventually kill the tissue.',
            'treatment': 'Apply appropriate fungicide according to crop type. Ensure proper spacing between plants for air circulation. Remove and destroy infected plant parts.'
        },
        {
            'name': 'Powdery Mildew',
            'confidence': 0.78,
            'description': 'A fungal disease that appears as white powdery spots on leaves, stems, and sometimes fruit.',
            'treatment': 'Apply sulfur-based fungicide or potassium bicarbonate. Improve air circulation around plants. Avoid overhead watering.'
        },
        {
            'name': 'Bacterial Leaf Spot',
            'confidence': 0.82,
            'description': 'Caused by bacteria that create dark, water-soaked spots on leaves that may turn yellow and drop prematurely.',
            'treatment': 'Apply copper-based bactericide. Practice crop rotation. Remove infected plant debris. Avoid overhead irrigation.'
        },
        {
            'name': 'Rust',
            'confidence': 0.75,
            'description': 'A fungal disease that produces rusty-colored spots on leaves and stems, reducing photosynthesis and plant vigor.',
            'treatment': 'Apply fungicide specifically labeled for rust. Remove infected plants or plant parts. Increase spacing between plants.'
        },
        {
            'name': 'Mosaic Virus',
            'confidence': 0.88,
            'description': 'A viral disease that causes mottled patterns of yellow and green on leaves, stunted growth, and deformed fruit.',
            'treatment': 'No cure available. Remove and destroy infected plants. Control insect vectors like aphids. Use virus-resistant varieties.'
        },
        {
            'name': 'Healthy Plant',
            'confidence': 0.92,
            'description': 'No disease detected. The plant appears to be healthy with normal growth patterns.',
            'treatment': 'Continue regular care including appropriate watering, fertilization, and pest monitoring.'
        }
    ]
    
    # Simulate disease detection based on filename or return a random disease
    # In a real app, this would be based on actual image analysis
    import random
    if 'blight' in filename:
        return diseases[0]
    elif 'mildew' in filename or 'powdery' in filename:
        return diseases[1]
    elif 'spot' in filename or 'bacterial' in filename:
        return diseases[2]
    elif 'rust' in filename:
        return diseases[3]
    elif 'mosaic' in filename or 'virus' in filename:
        return diseases[4]
    elif 'healthy' in filename:
        return diseases[5]
    else:
        # Return a random disease (excluding the healthy option) for demo purposes
        return random.choice(diseases[:-1])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crop-recommendation')
def crop_recommendation_page():
    return render_template('crop_recommendation.html')

@app.route('/weather')
def weather_page():
    return render_template('weather.html')

@app.route('/disease-identification')
def disease_identification_page():
    return render_template('disease_identification.html')

@app.route('/api/recommend-crop', methods=['POST'])
def recommend_crop():
    data = request.json
    n = float(data.get('nitrogen', 0))
    p = float(data.get('phosphorus', 0))
    k = float(data.get('potassium', 0))
    temperature = float(data.get('temperature', 0))
    humidity = float(data.get('humidity', 0))
    ph = float(data.get('ph', 0))
    rainfall = float(data.get('rainfall', 0))
    
    recommendations = get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)
    return jsonify(recommendations)

@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    city = data.get('city', '')
    
    if not city:
        return jsonify({'error': 'City name is required'})
    
    weather_data = get_weather_data(city)
    return jsonify(weather_data)

@app.route('/api/identify-disease', methods=['POST'])
def disease_identification():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'})
    
    try:
        # No need to process the image with PIL, just pass the file object
        result = identify_disease(image_file)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f"Error processing image: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=8083)
