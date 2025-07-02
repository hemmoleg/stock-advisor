import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { Prediction } from '../types/prediction';

const API_URL = process.env.REACT_APP_API_URL;

interface SymbolsState {
  items: string[];
  loading: boolean;
  error: string | null;
}

const initialState: SymbolsState = {
  items: [],
  loading: false,
  error: null,
};

// Async thunk for fetching predictions
export const fetchSymbols = createAsyncThunk(
  'symbols/fetchSymbols',
  async () => {
    const response = await axios.get<string[]>(`${API_URL}/symbols`);
    return response.data;
  }
);



const symbolsSlice = createSlice({
  name: 'symbols',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Handle fetch symbols
      .addCase(fetchSymbols.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSymbols.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchSymbols.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch symbols';
      })
  },
});

export const symbolsReducer = symbolsSlice.reducer; 