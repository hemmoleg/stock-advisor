import React from 'react';
import './App.css';
import PredictionForm from './components/PredictionForm';
import Predictions from './components/Predictions';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1 className='text-red-500'>Welcome to Stock Advisor</h1>
      </header>
      <main className='text-gray-200'>
        <p>Get stock predictions and insights.</p>
        <p>Use the form to submit a stock symbol for analysis.</p>
        <PredictionForm />
        <Predictions />
      </main>
    </div>
  );
}

export default App;
