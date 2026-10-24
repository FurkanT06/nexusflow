import numpy as np
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
