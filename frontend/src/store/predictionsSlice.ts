import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { Prediction } from '../types/prediction';

interface PredictionResponse {
  symbol: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_probability: number;
  negative_probability: number;
  neutral_probability: number;
  message: string;
}

interface PredictionsState {
  items: Prediction[];
  loading: boolean;
  formLoading: boolean;
  error: string | null;
  lastPredictionResult: PredictionResponse | null;
}

const initialState: PredictionsState = {
  items: [],
  loading: false,
  formLoading: false,
  error: null,
  lastPredictionResult: null,
};

// Async thunk for fetching predictions
export const fetchPredictions = createAsyncThunk(
  'predictions/fetchPredictions',
  async () => {
    const response = await axios.get<Prediction[]>('/predictions');
    return response.data;
  }
);

// Async thunk for making a prediction
export const makePrediction = createAsyncThunk(
  'predictions/makePrediction',
  async ({ symbol, date }: { symbol: string; date: string | null }, { rejectWithValue }) => {
    try {
      const response = await axios.post<PredictionResponse>('/make_prediction', { symbol, date });
      return response.data;
    } catch (error: any) {
      // If the error has response data, return it with rejectWithValue
      if (error.response && error.response.data) {
        return rejectWithValue(error.response.data);
      }
      // Otherwise, throw the original error
      throw error;
    }
  }
);

const predictionsSlice = createSlice({
  name: 'predictions',
  initialState,
  reducers: {},
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
      })
      .addCase(makePrediction.fulfilled, (state, action) => {
        state.formLoading = false;
        state.lastPredictionResult = action.payload;
      })
      .addCase(makePrediction.rejected, (state, action) => {
        state.formLoading = false;
        let errorMessage = 'Failed to make prediction';
        
        // Check if we have payload from rejectWithValue
        if (action.payload && typeof action.payload === 'object' && 'message' in action.payload) {
          errorMessage = (action.payload as any).message;
        }
        
        state.error = errorMessage;
        state.lastPredictionResult = null;
      });
  },
});

export const predictionsReducer = predictionsSlice.reducer; 