from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load the models and artifacts
with open('../models/segmented_models.pkl', 'rb') as f:
    models = pickle.load(f)

with open('../models/segmented_scalers.pkl', 'rb') as f:
    scalers = pickle.load(f)

with open('../models/feature_columns.pkl', 'rb') as f:
    feature_columns = pickle.load(f)

flagship_brands = ['Apple','Google','Asus']
premium_brands = ['Nothing', 'OnePlus']
def determine_price_segment(features):
    """Determine which price segment model to use based on features."""
    if features['brand_tier'] == 'flagship':
        return 'flagship'
    elif features['brand_tier'] == 'premium':
        return 'premium'
    elif features['rom_tier'] == 'basic':
        return 'budget'
    elif features['ram_tier'] == 'basic':
        return 'budget'
    
    # For flexible brand_tier
    elif features['brand_tier'] == 'flexible':
        # High-end combinations
        if features['ram_tier'] == 'high' and features['rom_tier'] in ['high', 'mid'] and features['cam_tier'] == 'high':
            return 'flagship'
        
        # Premium combinations
        elif features['ram_tier'] == 'mid' and features['rom_tier'] in ['high', 'mid'] and features['cam_tier'] == 'high':
            return 'premium'
        
        # Mid-range combinations
        elif (features['ram_tier'] in ['high', 'mid'] and 
            features['rom_tier'] in ['high', 'mid'] and 
            features['cam_tier'] == 'basic'):
            return 'mid'
        
        # Everything else goes to budget
        else:
            return 'budget'
    
    # Default case
    else:
        return 'budget'

def prepare_features(data):
    """Prepare features in the same way as training data."""
    features = {}
    
    # Keep original brand
    features['Brand'] = data['Brand']
    # Process brand tier
    brand = data['Brand']
    features['brand_tier'] = ('flagship' if brand in flagship_brands
                            else 'premium' if brand in premium_brands
                            else 'flexible')
    
    # Process RAM tier
    ram = float(data['RAM (GB)'])
    if ram >= 12:
        features['ram_tier'] = 'high'
    elif ram >= 6:
        features['ram_tier'] = 'mid'
    else:
        features['ram_tier'] = 'basic'
    rom = float(data['ROM (GB)'])
    if rom >= 256:
        features['rom_tier'] = 'high'
    elif rom >= 128:
        features['rom_tier'] = 'mid'
    else:
        features['rom_tier'] = 'basic'
        
    cam = float(data['Back Camera (MP)'])
    if cam > 100:
        features['cam_tier'] = 'high'
    else:
        features['cam_tier'] = 'basic'
    
    # Create interaction features
    features['storage_per_ram'] = float(data['ROM (GB)']) / float(data['RAM (GB)'])
    features['camera_total'] = (float(data['Front Camera (MP)']) + float(data['Back Camera (MP)']))
    
    # Add basic features
    features['Screen Size (in)'] = float(data['Screen Size (in)'])
    features['Front Camera (MP)'] = float(data['Front Camera (MP)'])
    features['Back Camera (MP)'] = float(data['Back Camera (MP)'])
    features['Battery (mAh)'] = float(data['Battery (mAh)'])
    features['RAM (GB)'] = float(data['RAM (GB)'])
    features['ROM (GB)'] = float(data['ROM (GB)'])
    
    return features

def create_feature_vector(features):
    """Create a feature vector matching the training data structure."""
    # Create a DataFrame with one row
    df = pd.DataFrame([features])
    
    # One-hot encode categorical features
    df_encoded = pd.get_dummies(
        df,
        columns=['Brand', 'ram_tier', 'rom_tier', 'brand_tier', 'cam_tier'],
        prefix=['Brand', 'ram_tier', 'rom_tier', 'brand_tier', 'cam_tier']
    )
    
    # Ensure all feature columns from training are present
    for col in feature_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
            
    # Reorder columns to match training data
    df_encoded = df_encoded[feature_columns]
    
    return df_encoded.values[0]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = [
            'Brand', 'Screen Size (in)', 'Front Camera (MP)', 'Back Camera (MP)',
            'Battery (mAh)', 'RAM (GB)', 'ROM (GB)'
        ]
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Prepare features
        features = prepare_features(data)
        
        # Determine price segment
        segment = determine_price_segment(features)
        
        # Create feature vector
        feature_vector = create_feature_vector(features)
        
        # Scale features
        scaled_features = scalers[segment].transform([feature_vector])
        
        # Make prediction
        log_prediction = models[segment].predict(scaled_features)
        final_prediction = np.exp(log_prediction)
        
        return jsonify({
            'price': round(float(final_prediction[0]), 2),
            'segment': segment
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid numeric value provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)