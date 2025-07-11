import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchPredictions } from '../store/predictionsSlice';
import { fetchLastPriceUpdate, updateClosingPrices } from '../store/lastPriceUpdateSlice';

const UpdatePricesButton: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  const { lastUpdate, loading: lastUpdateLoading, error: lastUpdateError, isUpdating } = useSelector(
    (state: RootState) => state.lastPriceUpdate
  );

  useEffect(() => {
    dispatch(fetchLastPriceUpdate());
  }, [dispatch]);

  const handleUpdatePrices = async () => {
    try {
      await dispatch(updateClosingPrices()).unwrap();
      await dispatch(fetchPredictions());
    } catch (error) {
      // Error is handled by the reducer
      console.error('Error updating prices:', error);
    }
  };

  const formatLastUpdate = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col items-center gap-4 mt-8">
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Last price update: {formatLastUpdate(lastUpdate)}
          {lastUpdateLoading && ' (Loading...)'}
        </span>
        <button
          onClick={handleUpdatePrices}
          disabled={isUpdating || lastUpdateLoading}
          className={`px-4 py-2 rounded ${
            (isUpdating || lastUpdateLoading) ? 'opacity-50 cursor-not-allowed' : ''
          } bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 flex items-center gap-2`}
        >
          {isUpdating ? (
            <>
              <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Updating...
            </>
          ) : (
            'Update Prices'
          )}
        </button>
      </div>
      {lastUpdateError && (
        <div className="p-4 rounded bg-red-200 text-red-900 dark:bg-red-500 dark:text-white">
          {lastUpdateError}
        </div>
      )}
    </div>
  );
};

export default UpdatePricesButton; 