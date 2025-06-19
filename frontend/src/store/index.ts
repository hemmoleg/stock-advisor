import { configureStore } from '@reduxjs/toolkit';
import { predictionsReducer } from './predictionsSlice';
import themeReducer from './themeSlice';

export const store = configureStore({
  reducer: {
    predictions: predictionsReducer,
    theme: themeReducer,
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 