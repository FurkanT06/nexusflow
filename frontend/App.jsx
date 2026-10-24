import React, { useState } from 'react';

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
