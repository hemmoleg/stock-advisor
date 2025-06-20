import React from 'react';
import './App.css';
import PredictionForm from './components/PredictionForm';
import Predictions from './components/Predictions';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from './store';
import { toggleTheme } from './store/themeSlice';

function App() {
  const theme = useSelector((state: RootState) => state.theme.theme);
  const dispatch = useDispatch<AppDispatch>();

  React.useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <div className="App min-h-screen">
      <header className="App-header bg-gray-100 dark:bg-gray-800 flex items-center justify-between px-4 py-2 relative">
        <h1 className='text-4xl text-red-500'>Welcome to Stock Advisor</h1>
        <button
          onClick={() => dispatch(toggleTheme())}
          className="absolute top-3 right-3 px-2 py-1 text-sm rounded border border-gray-400 bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 transition"
          aria-label="Toggle light/dark mode"
        >
          {theme === 'dark' ? '🌙' : '☀️'}
        </button>
      </header>
      <main className="text-lg pt-2 text-gray-900 dark:text-gray-200 bg-white dark:bg-gray-900">  
        <p>Get stock predictions and insights.</p>
        <p className='mb-8'>Use the form to submit a stock symbol for analysis.</p>
        <PredictionForm />
        <Predictions />
      </main>
    </div>
  );
}

export default App;
