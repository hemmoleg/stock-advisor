import React, { useEffect } from "react";
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchPredictions } from '../store/predictionsSlice';

const Predictions: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items: predictions, loading } = useSelector((state: RootState) => state.predictions);

  useEffect(() => {
    dispatch(fetchPredictions());
  }, [dispatch]);

  if (loading) {
    return <div className="text-center text-lg text-gray-500">Loading predictions...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Predictions</h1>
      {predictions.length === 0 ? (
        <p className="text-center text-gray-500">No predictions available.</p>
      ) : (
        <div className="border grid">
          {predictions.map((prediction) => (
            <div
              key={prediction.id}
              className="flex gap-6 px-6 py-4"
            >
              <h2 className="text-xl font-semibold text-blue-600">{prediction.symbol}</h2>
              <p className="text-gray-200">Date: {new Date(prediction.date_time).toLocaleDateString("de-DE")}</p>
              <p className="text-gray-200">Stock Value: ${prediction.stock_value.toFixed(2)}</p>
              <div className="flex gap-4">
                <p className="text-green-500">&#9989; Positive: {prediction.positive_count}</p>
                <p className="text-red-500">&#10060; Negative: {prediction.negative_count}</p>
                <p className="text-gray-300">&#9898; Neutral: {prediction.neutral_count}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Predictions;