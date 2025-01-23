import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [features, setFeatures] = useState({
    Brand: '',
    'Screen Size (in)': '',
    'Front Camera (MP)': '',
    'Back Camera (MP)': '',
    'Battery (mAh)': '',
    'RAM (GB)': '',
    'ROM (GB)': '',
    'Clock Speed (GHz)': ''
  });
  const [prediction, setPrediction] = useState(null); // State to hold price
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFeatures({
      ...features,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', {
        Brand: features.Brand,
        'Screen Size (in)': parseFloat(features['Screen Size (in)']),
        'Front Camera (MP)': parseFloat(features['Front Camera (MP)']),
        'Back Camera (MP)': parseFloat(features['Back Camera (MP)']),
        'Battery (mAh)': parseInt(features['Battery (mAh)']),
        'RAM (GB)': parseInt(features['RAM (GB)']),
        'ROM (GB)': parseFloat(features['ROM (GB)']),
        'Clock Speed (GHz)': parseFloat(features['Clock Speed (GHz)'])
      });
      setPrediction(response.data.price); // Update price state
    } catch (error) {
      console.error('Error fetching prediction:', error);
      setError(error.response?.data?.error || 'An error occurred while making the prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Smartphone Price Predictor</h1>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Brand</label>
            <select
              name="Brand"
              value={features.Brand}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select Brand</option>
              <option value="Samsung">Samsung</option>
              <option value="Realme">Realme</option>
              <option value="Vivo">Vivo</option>
              <option value="Xiaomi">Xiaomi</option>
              <option value="OPPO">OPPO</option>
              <option value="Motorola">Motorola</option>
              <option value="OnePlus">OnePlus</option>
              <option value="iQOO">iQOO</option>
              <option value="Poco">Poco</option>
              <option value="Apple">Apple</option>
              <option value="Honor">Honor</option>
              <option value="Nothing">Nothing</option>
              <option value="CMF">CMF</option>
              <option value="Infinix">Infinix</option>
              <option value="Google">Google</option>
              <option value="Tecno">Tecno</option>
              <option value="Lava">Lava</option>
              <option value="HMD">HMD</option>
              <option value="Ulefone">Ulefone</option>
              <option value="Oukitel">Oukitel</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Screen Size (in)</label>
            <input
              type="number"
              step="0.1"
              name="Screen Size (in)"
              value={features['Screen Size (in)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="5"
              max="8"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Clock Speed (GHz)</label>
            <input
              type="number"
              step="0.1"
              name="Clock Speed (GHz)"
              value={features['Clock Speed (GHz)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="1"
              max="8"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Front Camera (MP)</label>
            <input
              type="number"
              name="Front Camera (MP)"
              value={features['Front Camera (MP)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="1"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Back Camera (MP)</label>
            <input
              type="number"
              name="Back Camera (MP)"
              value={features['Back Camera (MP)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="1"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Battery (mAh)</label>
            <input
              type="number"
              name="Battery (mAh)"
              value={features['Battery (mAh)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="2000"
              max="12000"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">RAM (GB)</label>
            <input
              type="number"
              name="RAM (GB)"
              value={features['RAM (GB)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="1"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">ROM (GB)</label>
            <input
              type="number"
              name="ROM (GB)"
              value={features['ROM (GB)']}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              min="32"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? 'Predicting...' : 'Predict'}
        </button>
      </form>

      {prediction !== null && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold">Price: ₹{prediction}</h2>
        </div>
      )}
    </div>
  );
};

export default App;