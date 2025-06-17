import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchPredictions, makePrediction } from '../store/predictionsSlice';

interface ResponseData {
  status: string;
  message?: string;
}

const PredictionForm = () => {
  const [symbol, setSymbol] = useState("");
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  const { formLoading, error, lastPredictionResult } = useSelector((state: RootState) => state.predictions);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dispatch(makePrediction({
        symbol,
        date: selectedDate ? selectedDate.toLocaleDateString("en-CA") : null,
      })).unwrap();
      // Refresh predictions after successful submission
      await dispatch(fetchPredictions());
      // Clear the form
      setSymbol("");
      setSelectedDate(null);
    } catch (error) {
      // Error is handled by the reducer
      console.error("Error making prediction:", error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex items-center justify-center gap-4">
          <label>Stock Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              required
              className="border rounded px-2 py-1 text-gray-800"
              disabled={formLoading}
            />
          <label>
            Date
          </label>
          <DatePicker
            selected={selectedDate}
            onChange={(date: Date | null) => setSelectedDate(date)}
            dateFormat="yyyy-MM-dd"
            className="border rounded px-2 py-1 text-gray-800"
            placeholderText="Select a date"
            shouldCloseOnSelect={true}
            disabled={formLoading}
          />
          <button 
            type="submit" 
            className={`bg-blue-500 text-white px-4 py-2 rounded flex items-center gap-2 ${formLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'}`}
            disabled={formLoading}
          >
            {formLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              'Get Prediction'
            )}
          </button>
        </div>
      </form>

      {/* Display error message if there's an error */}
      {error && (
        <div className="mt-4 bg-red-500 text-white p-4 rounded">
          {error}
        </div>
      )}

      {/* Display the prediction result if available */}
      {lastPredictionResult && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold mb-2">Prediction Result:</h2>
          <div className="bg-gray-800 p-4 rounded">
            <p className="mb-2">{lastPredictionResult.message}</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-green-500">Positive: {lastPredictionResult.positive_count}</p>
                <p className="text-sm text-gray-400">Probability: {lastPredictionResult.positive_probability}</p>
              </div>
              <div>
                <p className="text-red-500">Negative: {lastPredictionResult.negative_count}</p>
                <p className="text-sm text-gray-400">Probability: {lastPredictionResult.negative_probability}</p>
              </div>
              <div>
                <p className="text-gray-300">Neutral: {lastPredictionResult.neutral_count}</p>
                <p className="text-sm text-gray-400">Probability: {lastPredictionResult.neutral_probability}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;