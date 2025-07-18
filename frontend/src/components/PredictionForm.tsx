import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import { Combobox, ComboboxInput, ComboboxOptions, ComboboxOption } from '@headlessui/react';
import "react-datepicker/dist/react-datepicker.css";
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchPredictions, makePrediction } from '../store/predictionsSlice';
import { fetchSymbols } from '../store/symbols';

const PredictionForm: React.FC= () => {
  const [symbol, setSymbol] = useState("");
  const [query, setQuery] = useState("");
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  const { formLoading, error, lastPredictionResult, classificationProgress } = useSelector((state: RootState) => state.predictions);
  const { items: symbols, loading: symbolsLoading } = useSelector((state: RootState) => state.symbols);

  useEffect(() => {
    dispatch(fetchSymbols());
  }, [dispatch]);

  const filteredSymbols = !query
    ? symbols
    : symbols.filter((sym) => sym.includes(query.toUpperCase()));


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dispatch(makePrediction({
        symbol,
        date: selectedDate ? selectedDate.toLocaleDateString("en-CA") : null,
      })).unwrap();
      // Refresh predictions after successful submission
      await dispatch(fetchPredictions());
      setSymbol("");
      setSelectedDate(null);
    } catch (error) {
      // Error is handled by the reducer
      console.error("Error making prediction:", error);
    }
  };

  const getButtonContent = () => {
    if (formLoading) {
      if (classificationProgress) {
        return (
          <>
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing {classificationProgress.classified} of {classificationProgress.total} news...
          </>
        );
      }
      return (
        <>
          <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Starting prediction...
        </>
      );
    }
    return "Make Prediction";
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex items-center justify-center gap-4">
          <label>Stock Symbol</label>
          <div className="relative w-40">
            <Combobox 
              immediate 
              value={symbol} 
              onChange={(value: string) => {
                setSymbol(value);
                setQuery(value);
              }} 
            >
              <ComboboxInput 
                className="w-full border rounded px-2 py-1 text-gray-900 bg-white dark:bg-gray-800 dark:text-gray-100"
                displayValue={(symbol: unknown) => symbol ? String(symbol) : ""}
                onChange={(event) => {
                  const value = event.target.value.toUpperCase();
                  setQuery(value);
                  setSymbol(value);
                }}
                autoComplete="off"
                placeholder="Stock symbol"
              />
              {filteredSymbols.length > 0 && (
                <ComboboxOptions className="absolute z-10 w-full mt-1 overflow-auto rounded bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 max-h-60">
                  {filteredSymbols.map((symbol) => (
                    <ComboboxOption 
                      key={symbol} 
                      value={symbol} 
                      className={({ active }) =>
                        `relative cursor-pointer select-none py-2 px-4 ${
                          active ? 'bg-blue-600 text-white' : 'text-gray-900 dark:text-gray-100'
                        }`
                      }
                    >
                      {symbol}
                    </ComboboxOption>
                  ))}
                </ComboboxOptions>
              )}
            </Combobox>
          </div>
          <label>
            Date
          </label>
          <DatePicker
            selected={selectedDate}
            onChange={(date: Date | null) => setSelectedDate(date)}
            dateFormat="yyyy-MM-dd"
            className="border rounded px-2 py-1 text-gray-900 bg-white dark:bg-gray-800 dark:text-gray-100"
            placeholderText="Select a date"
            shouldCloseOnSelect={true}
            disabled={formLoading}
          />
          <button 
            type="submit" 
            className={`px-4 py-2 rounded flex items-center gap-2 ${formLoading ? 'opacity-50 cursor-not-allowed' : ''} bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 min-w-[200px] justify-center`}
            disabled={formLoading}
          >
            {getButtonContent()}
          </button>
        </div>
      </form>

      {/* Display error message if there's an error */}
      {error && (
        <div className="mt-4 p-4 rounded bg-red-200 text-red-900 dark:bg-red-500 dark:text-white">
          {error}
        </div>
      )}

      {/* Display the prediction result if available */}
      {lastPredictionResult && lastPredictionResult.status === 'complete' && (
        <div className="mt-4 pt-4">
          <div className="bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white p-4 rounded">
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