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

# Define brand tiers
premium_brands = ['Apple', 'Google', 'OnePlus']
mid_brands = ['Nothing', 'Samsung']

def determine_price_segment(features):
    """Determine which price segment model to use based on features."""
    if features['brand_tier'] == 'premium' or features['RAM (GB)'] >= 12:
        return 'premium'
    elif features['brand_tier'] == 'budget' and features['RAM (GB)'] <= 6:
        return 'budget'
    else:
        return 'mid'

def prepare_features(data):
    """Prepare features in the same way as training data."""
    features = {}
    
    # Keep original brand
    features['Brand'] = data['Brand']
    
    # Process brand tier
    brand = data['Brand']
    features['brand_tier'] = ('premium' if brand in premium_brands 
                            else 'mid' if brand in mid_brands 
                            else 'budget')
    
    # Process RAM tier
    ram = float(data['RAM (GB)'])
    if ram <= 4:
        features['ram_tier'] = 'basic'
    elif ram <= 8:
        features['ram_tier'] = 'mid'
    elif ram <= 12:
        features['ram_tier'] = 'high'
    else:
        features['ram_tier'] = 'ultra'
    
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
    features['Clock Speed (GHz)'] = float(data['Clock Speed (GHz)'])
    
    return features

def create_feature_vector(features):
    """Create a feature vector matching the training data structure."""
    # Create a DataFrame with one row
    df = pd.DataFrame([features])
    
    # One-hot encode categorical features
    df_encoded = pd.get_dummies(
        df,
        columns=['Brand', 'brand_tier', 'ram_tier'],
        prefix=['Brand', 'brand_tier', 'ram_tier']
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
            'Battery (mAh)', 'RAM (GB)', 'ROM (GB)', 'Clock Speed (GHz)'
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