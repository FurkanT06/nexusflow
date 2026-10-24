from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../model/saved/risk_model.pkl')
try:
    model = joblib.load(MODEL_PATH)
    print("[INFO] Model loaded successfully into API.")
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    model = None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model_loaded": model is not None}), 200

@app.route('/api/predict', methods=['POST'])
def predict_delay():
    if not model:
        return jsonify({"error": "Model not available"}), 500
    data = request.get_json()
    try:
        features = np.array([[
            float(data['distance_km']),
            float(data['weight_kg']),
            float(data['weather_severity_index']),
            float(data['carrier_historic_delay_rate'])
        ]])
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        return jsonify({
            "is_delayed": prediction,
            "delay_probability": round(probability * 100, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
