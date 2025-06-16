import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

interface Prediction {
  id: number;
  symbol: string;
  name: string;
  date_time: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_probability: number;
  negative_probability: number;
  neutral_probability: number;
  stock_value: number;
}

interface PredictionsState {
  items: Prediction[];
  loading: boolean;
  error: string | null;
}

const initialState: PredictionsState = {
  items: [],
  loading: false,
  error: null,
};

// Async thunk for fetching predictions
export const fetchPredictions = createAsyncThunk(
  'predictions/fetchPredictions',
  async () => {
    const response = await axios.get<Prediction[]>('/predictions');
    return response.data;
  }
);

const predictionsSlice = createSlice({
  name: 'predictions',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
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
      });
  },
});

export const predictionsReducer = predictionsSlice.reducer; 