import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

interface LastPriceUpdateState {
  lastUpdate: string | null;
  loading: boolean;
  error: string | null;
  isUpdating: boolean;
}

const initialState: LastPriceUpdateState = {
  lastUpdate: null,
  loading: false,
  error: null,
  isUpdating: false,
};

const API_URL = process.env.REACT_APP_API_URL;

export const fetchLastPriceUpdate = createAsyncThunk(
  'lastPriceUpdate/fetch',
  async () => {
    const response = await fetch(`${API_URL}/last_price_update`);
    if (!response.ok) {
      throw new Error('Failed to fetch last update time');
    }
    const data = await response.json();
    return data.last_update;
  }
);

export const updateClosingPrices = createAsyncThunk(
  'lastPriceUpdate/update',
  async (_, { dispatch }) => {
    const response = await fetch(`${API_URL}/update_closing_prices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lookback_days: 31 }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update prices');
    }

    const result = await response.json();
    if (result.status === 'success') {
      await dispatch(fetchLastPriceUpdate());
      return result;
    } else {
      throw new Error(result.message || 'Failed to update prices');
    }
  }
);

const lastPriceUpdateSlice = createSlice({
  name: 'lastPriceUpdate',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchLastPriceUpdate.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLastPriceUpdate.fulfilled, (state, action) => {
        state.loading = false;
        state.lastUpdate = action.payload;
        state.error = null;
      })
      .addCase(fetchLastPriceUpdate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch last update time';
      })
      .addCase(updateClosingPrices.pending, (state) => {
        state.isUpdating = true;
        state.error = null;
      })
      .addCase(updateClosingPrices.fulfilled, (state) => {
        state.isUpdating = false;
        state.error = null;
      })
      .addCase(updateClosingPrices.rejected, (state, action) => {
        state.isUpdating = false;
        state.error = action.error.message || 'Failed to update prices';
      });
  },
});

export default lastPriceUpdateSlice.reducer; 