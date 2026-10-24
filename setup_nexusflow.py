import os

def create_project():
    print("[INFO] Initializing NexusFlow project structure...")
    files = {
        'requirements.txt': """pandas==2.2.0
numpy==1.26.3
scikit-learn==1.4.0
flask==3.0.1
flask-cors==4.0.0
joblib==1.3.2""",
        
        'model/train_model.py': '''import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import joblib
import os

def generate_synthetic_data():
    np.random.seed(42)
    n_samples = 1000
    data = {
        'distance_km': np.random.randint(100, 5000, n_samples),
        'weight_kg': np.random.uniform(10, 500, n_samples),
        'weather_severity_index': np.random.uniform(0, 1, n_samples),
        'carrier_historic_delay_rate': np.random.uniform(0, 0.3, n_samples),
        'is_delayed': np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
    }
    return pd.DataFrame(data)

def train_and_save_model():
    print("[INFO] Generating dataset...")
    df = generate_synthetic_data()
    X = df[['distance_km', 'weight_kg', 'weather_severity_index', 'carrier_historic_delay_rate']]
    y = df['is_delayed']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("[INFO] Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"[METRICS] Cross-Validation Accuracy: {cv_scores.mean():.4f}")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    os.makedirs('model/saved', exist_ok=True)
    joblib.dump(model, 'model/saved/risk_model.pkl')
    print("[INFO] Model saved successfully to model/saved/risk_model.pkl")

if __name__ == "__main__":
    train_and_save_model()
''',

        'api/app.py': '''from flask import Flask, request, jsonify
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
''',

        'orchestration/nexusflow_pipeline.yaml': """id: nexusflow_pipeline
namespace: company.supplychain
description: "Automated pipeline for training the NexusFlow risk prediction model."
tasks:
  - id: install_dependencies
    type: io.kestra.plugin.scripts.python.Commands
    runner: PROCESS
    beforeCommands:
      - pip install -r requirements.txt
    commands:
      - python model/train_model.py
  - id: notify_completion
    type: io.kestra.plugin.core.log.Log
    message: "NexusFlow model training pipeline executed successfully!"
triggers:
  - id: schedule_weekly
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 0 * * 0"
""",

        'frontend/App.jsx': '''import React, { useState } from 'react';

export default function App() {
  const [formData, setFormData] = useState({
    distance_km: '',
    weight_kg: '',
    weather_severity_index: '',
    carrier_historic_delay_rate: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error connecting to backend:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-6">
      <div className="max-w-xl w-full bg-gray-800 p-8 rounded-xl shadow-lg border border-gray-700">
        <h1 className="text-2xl font-bold mb-2 text-indigo-400">NexusFlow Risk Intelligence</h1>
        <p className="text-sm text-gray-400 mb-6">Predict shipment delays using machine learning and automated pipelines.</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">Distance (km)</label>
            <input type="number" name="distance_km" value={formData.distance_km} onChange={handleChange} required
              className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">Weight (kg)</label>
            <input type="number" name="weight_kg" value={formData.weight_kg} onChange={handleChange} required
              className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">Weather Severity Index (0 - 1)</label>
            <input type="number" step="0.01" name="weather_severity_index" value={formData.weather_severity_index} onChange={handleChange} required
              className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">Carrier Historic Delay Rate (0 - 1)</label>
            <input type="number" step="0.01" name="carrier_historic_delay_rate" value={formData.carrier_historic_delay_rate} onChange={handleChange} required
              className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:outline-none focus:border-indigo-500" />
          </div>
          
          <button type="submit" disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 transition-colors py-2 rounded font-semibold text-white mt-2">
            {loading ? 'Evaluating Risk...' : 'Predict Delay Risk'}
          </button>
        </form>

        {result && (
          <div className="mt-6 p-4 bg-gray-900 border border-gray-700 rounded">
            <h3 className="text-sm font-semibold text-gray-300 mb-1">Prediction Results</h3>
            <p className="text-lg font-bold">
              Status: <span className={result.is_delayed ? "text-red-400" : "text-green-400"}>
                {result.is_delayed ? "High Risk of Delay" : "On Time Expected"}
              </span>
            </p>
            <p className="text-sm text-gray-400 mt-1">Delay Probability: {result.delay_probability}%</p>
          </div>
        )}
      </div>
    </div>
  );
}
''',

        'README.md': """# NexusFlow: Predictive Supply Chain & Risk Intelligence Platform

NexusFlow is a full-stack, ML-powered logistics pipeline that predicts shipment delay risks in real-time.

## Tech Stack
- **Python 3.11+**, **Pandas**, **Scikit-learn**
- **Flask** & **React / Tailwind CSS**
- **Kestra** for workflow orchestration

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Train model: `python3 model/train_model.py`
3. Run API: `python3 api/app.py`
"""
    }

    for filepath, content in files.items():
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[CREATED] {filepath}")

    print("\n[SUCCESS] All project files generated successfully!")

if __name__ == '__main__':
    create_project()
