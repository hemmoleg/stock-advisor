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
    return <div className="text-center text-lg text-gray-500 dark:text-gray-400">Loading predictions...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-gray-100">Predictions</h1>
      {predictions.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">No predictions available.</p>
      ) : (
        <div className="border border-gray-300 dark:border-gray-600">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-200 border-b border-gray-300 dark:border-gray-600">
                <th className="px-6 py-3 text-center">Symbol</th>
                <th className="px-6 py-3 text-center">Date</th>
                <th className="px-6 py-3 text-center">Positive</th>
                <th className="px-6 py-3 text-center">Negative</th>
                <th className="px-6 py-3 text-center">Neutral</th>
                <th className="px-6 py-3 text-center">Stock Value</th>
                <th className="px-6 py-3 text-center">1 Day</th>
                <th className="px-6 py-3 text-center">2 Day</th>
                <th className="px-6 py-3 text-center">3 Day</th>
                <th className="px-6 py-3 text-center">7 Day</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((prediction) => (
                <tr key={prediction.id} className="border-b border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700">
                  <td className="px-6 py-4">
                    <h2 className="text-xl font-semibold text-blue-600 dark:text-blue-400">{prediction.symbol}</h2>
                  </td>
                  <td className="px-6 py-4 text-gray-900 dark:text-gray-200">
                    {new Date(prediction.date_time).toLocaleDateString("de-DE")}
                  </td>
                  <td className="px-6 py-4 text-green-500">
                    &#9989; {prediction.positive_count}
                  </td>
                  <td className="px-6 py-4 text-red-500">
                    &#10060; {prediction.negative_count}
                  </td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                    &#9898; {prediction.neutral_count}
                  </td>
                  <td className="px-6 py-4 text-gray-900 dark:text-gray-200">
                    ${prediction.stock_value.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-green-500">
                    {prediction.future_prices["1_day"] ? `$${prediction.future_prices["1_day"]?.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-red-500">
                    {prediction.future_prices["2_day"] ? `$${prediction.future_prices["2_day"]?.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                    {prediction.future_prices["3_day"] ? `$${prediction.future_prices["3_day"]?.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                    {prediction.future_prices["7_day"] ? `$${prediction.future_prices["7_day"]?.toFixed(2)}` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Predictions;