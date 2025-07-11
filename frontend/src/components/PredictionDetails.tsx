import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DetailedPrediction } from '../types/prediction';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const PredictionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [prediction, setPrediction] = useState<DetailedPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictionDetails = async () => {
      try {
        const response = await axios.get<DetailedPrediction>(`${API_URL}/predictions/${id}`);
        setPrediction(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load prediction details');
        setLoading(false);
      }
    };

    fetchPredictionDetails();
  }, [id]);

  if (loading) {
    return <div className="text-center text-lg text-gray-500 dark:text-gray-400">Loading...</div>;
  }

  if (error || !prediction) {
    return (
      <div>
        <div className="text-red-500 mb-4">{error || 'Prediction not found'}</div>
        <button 
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Back to Predictions
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {prediction.symbol} - {prediction.name}
        </h1>
        <button 
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Back to Predictions
        </button>
      </div>

      <div className="space-y-8">
        {/* Basic Info */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Basic Information</h2>
          <div className="grid grid-cols-2 gap-4 text-gray-600 dark:text-gray-300">
            <div>Date: {new Date(prediction.date_time).toLocaleDateString("de-DE")}</div>
            <div>Stock Value: ${prediction.stock_value.toFixed(2)}</div>
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Sentiment Analysis</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-green-500">
              Positive: {prediction.positive_count} ({(prediction.positive_probability * 100).toFixed(1)}%)
            </div>
            <div className="text-red-500">
              Negative: {prediction.negative_count} ({(prediction.negative_probability * 100).toFixed(1)}%)
            </div>
            <div className="text-gray-500">
              Neutral: {prediction.neutral_count} ({(prediction.neutral_probability * 100).toFixed(1)}%)
            </div>
          </div>
        </div>

        {/* News Articles */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">News Articles</h2>
          <div className="space-y-4">
            {prediction.news_articles.map(article => (
              <div key={article.id} className="border-b border-gray-200 dark:border-gray-700 pb-4">
                <div className="flex items-start justify-between">
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    {article.title}
                  </a>
                  <span className={`ml-2 px-2 py-1 rounded text-sm ${
                    article.classification === 'Positive' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    article.classification === 'Negative' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {article.classification} ({(article.confidence_score * 100).toFixed(1)}%)
                  </span>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(article.date_time).toLocaleString("de-DE")}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Future Prices */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Price Predictions</h2>
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(prediction.future_prices).map(([key, value]) => (
              <div key={key} className="text-gray-600 dark:text-gray-300">
                <div className="font-medium">{key.replace('_', ' ')}:</div>
                {value.is_weekend ? (
                  <span className="text-gray-500">Weekend</span>
                ) : value.is_holiday ? (
                  <span className="text-gray-500">Holiday</span>
                ) : value.price ? (
                  <span className={`${value.price > prediction.stock_value ? 'text-green-500' : 'text-red-500'}`}>
                    ${value.price.toFixed(2)}
                  </span>
                ) : (
                  <span className="text-gray-500">No data</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionDetails; 