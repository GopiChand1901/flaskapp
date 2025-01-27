from flask import Flask, request, jsonify
import pandas as pd
from xgboost import XGBRegressor
import warnings


# Initialize Flask app
app = Flask(__name__)

# Load the trained XGBoost model
xgb_model = XGBRegressor()
warnings.filterwarnings("ignore", message=".*__sklearn_tags__.*")

try:
    print("Loading model from: ./gb_model.bst")  # Update path as needed
    xgb_model.load_model('./gb_model.bst')  # Use the correct model file
    print("Model loaded successfully!")
except Exception as e:
    print("Error loading model:", str(e))

# Define categorical columns
categorical_features = ['brand', 'model', 'fuel_type', 'engine', 'transmission', 'ext_col', 'int_col', 'accident', 'clean_title']

@app.route('/', methods=['GET'])
def home():
    return "XGBoost Car Price Prediction API is running! Use the /predict endpoint to make predictions."

@app.route('/predict', methods=['POST'])
def predict():
    print("request recieved")
    try:
        # Parse JSON input
        input_data = request.get_json()

        # Convert JSON to DataFrame
        input_df = pd.DataFrame([input_data])

        # Debug: Print input DataFrame before processing
        print("Input DataFrame before processing:")
        print(input_df)

        # Ensure categorical columns are converted to 'category' dtype
        for col in categorical_features:
            if col in input_df.columns:
                input_df[col] = input_df[col].astype('category')

        # Debug: Print input DataFrame after processing
        print("Input DataFrame after processing:")
        print(input_df)

        # Make prediction
        prediction = xgb_model.predict(input_df)[0]
        prediction = float(prediction)

        # Return prediction as JSON
        return jsonify({'predicted_price': prediction})

    except Exception as e:
        # Return error details
        return jsonify({'error': str(e)}), 400

# Run the API
if __name__ == '__main__':
    app.run(debug=True)
