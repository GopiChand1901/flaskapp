from flask import Flask, request, jsonify
import pandas as pd
from xgboost import XGBRegressor
import warnings
import os

# Initialize Flask app
app = Flask(__name__)

# Load the trained XGBoost model
xgb_model = XGBRegressor()
warnings.filterwarnings("ignore", message=".*__sklearn_tags__.*")

try:
    print("Loading model from: ./gb_model.json")  # Debug
    xgb_model.load_model('./gb_model.bst')  # Load model
    print("Model loaded successfully!")
except Exception as e:
    print("Error loading model:", str(e))

# Define categorical columns
categorical_features = [
    'brand', 'model','model_year','milage', 'fuel_type', 'engine', 'transmission', 
    'ext_col', 'int_col', 'accident', 'clean_title'
]

# Expected features in the correct order
expected_features = [
    'brand', 'model','model_year','milage', 'fuel_type', 'engine', 'transmission', 
    'ext_col', 'int_col', 'accident', 'clean_title'
]

@app.route('/', methods=['GET'])
def home():
    return "✅ XGBoost Car Price Prediction API is running! Use the /predict endpoint to make predictions."

@app.route('/predict', methods=['POST'])
def predict():
    print("📩 Request received at /predict")

    try:
        # Ensure JSON request
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400
        
        # Parse JSON input
        input_data = request.get_json()
        print("🔍 Raw input data:", input_data)

        # Convert JSON to DataFrame
        input_df = pd.DataFrame([input_data])

        # Debug: Check input DataFrame before processing
        print("📝 Input DataFrame before processing:")
        print(input_df)

        # Ensure categorical columns are converted to 'category' dtype
        for col in categorical_features:
            if col in input_df.columns:
                input_df[col] = input_df[col].astype('category')

        # Debug: Print input DataFrame after processing
        print("📊 Input DataFrame after processing:")
        print(input_df.dtypes)

        # Ensure DataFrame columns match the trained model
        for feature in expected_features:
            if feature not in input_df.columns:
                input_df[feature] = 0  # Default value for missing columns
        
        # Sort columns to match training order
        input_df = input_df[expected_features]

        # Debug: Check aligned DataFrame
        print("✅ Aligned Input DataFrame:")
        print(input_df)

        # Make prediction
        prediction = xgb_model.predict(input_df)[0]
        prediction = float(prediction)

        # Return prediction as JSON
        return jsonify({'predicted_price': prediction})

    except Exception as e:
        # Log the error
        print("❌ Error during prediction:", str(e))
        return jsonify({'error': str(e)}), 400

# Running in development only
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)