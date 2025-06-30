import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { Prediction } from '../types/prediction';

const API_URL = process.env.REACT_APP_API_URL;

interface PredictionResponse {
  status: 'progress' | 'complete' | 'error';
  symbol?: string;
  total_news?: number;
  classified_news?: number;
  positive_count?: number;
  negative_count?: number;
  neutral_count?: number;
  positive_probability?: number;
  negative_probability?: number;
  neutral_probability?: number;
  message?: string;
}

interface PredictionsState {
  items: Prediction[];
  loading: boolean;
  formLoading: boolean;
  error: string | null;
  lastPredictionResult: PredictionResponse | null;
  classificationProgress: {
    total: number;
    classified: number;
  } | null;
}

const initialState: PredictionsState = {
  items: [],
  loading: false,
  formLoading: false,
  error: null,
  lastPredictionResult: null,
  classificationProgress: null,
};

// Async thunk for fetching predictions
export const fetchPredictions = createAsyncThunk(
  'predictions/fetchPredictions',
  async () => {
    const response = await axios.get<Prediction[]>(`${API_URL}/predictions`);
    return response.data;
  }
);

// Async thunk for making a prediction
export const makePrediction = createAsyncThunk<
  PredictionResponse,
  { symbol: string; date: string | null },
  { rejectValue: string }
>(
  'predictions/makePrediction',
  async ({ symbol, date }, { dispatch }) => {
    return new Promise((resolve, reject) => {
      const params = new URLSearchParams({ 
        symbol, 
        ...(date && { date })
      });
      
      const eventSource = new EventSource(`${API_URL}/make_prediction?${params}`);

      eventSource.onmessage = (event) => {
        const data: PredictionResponse = JSON.parse(event.data);
        
        switch (data.status) {
          case 'progress':
            dispatch(predictionsSlice.actions.updateProgress({
              total: data.total_news!,
              classified: data.classified_news!
            }));
            break;
          
          case 'complete':
            eventSource.close();
            resolve(data);
            break;
          
          case 'error':
            eventSource.close();
            reject(new Error(data.message || 'Unknown error occurred'));
            break;
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        reject(new Error('Connection error occurred'));
      };
    });
  }
);

const predictionsSlice = createSlice({
  name: 'predictions',
  initialState,
  reducers: {
    updateProgress: (state, action) => {
      state.classificationProgress = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle fetch predictions
      .addCase(fetchPredictions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPredictions.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchPredictions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch predictions';
      })
      // Handle make prediction
      .addCase(makePrediction.pending, (state) => {
        state.formLoading = true;
        state.error = null;
        state.lastPredictionResult = null;
        state.classificationProgress = null;
      })
      .addCase(makePrediction.fulfilled, (state, action) => {
        state.formLoading = false;
        state.lastPredictionResult = action.payload;
        state.classificationProgress = null;
      })
      .addCase(makePrediction.rejected, (state, action) => {
        state.formLoading = false;
        state.error = action.payload || 'Failed to make prediction';
        state.lastPredictionResult = null;
        state.classificationProgress = null;
      });
  },
});

export const predictionsReducer = predictionsSlice.reducer; 