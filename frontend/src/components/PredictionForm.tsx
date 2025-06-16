import React, { useState } from "react";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

interface ResponseData {
  status: string;
  message?: string;
}

const PredictionForm = () => {
  const [symbol, setSymbol] = useState("");
  const [response, setResponse] = useState<ResponseData | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post("/make_prediction", {
        symbol,
        date: selectedDate ? selectedDate.toLocaleDateString("en-CA") : null,
      });
      setResponse(res.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Axios error:", error);
        setResponse({
          status: "error",
          message: error.response?.data?.message || "Unknown Axios error",
        });
      } else {
        console.error("Unexpected error:", error);
        setResponse({
          status: "error",
          message: "An unexpected error occurred",
        });
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex items-center justify-center gap-4">
          <label>
            Stock Symbol
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              required
              className="border rounded px-2 py-1 text-gray-800"
            />
          </label>
          <label>
            Date
          </label>
          <DatePicker
            selected={selectedDate}
            onChange={(date: Date | null) => setSelectedDate(date)}
            dateFormat="yyyy-MM-dd"
            className="border rounded px-2 py-1 text-gray-800"
            placeholderText="Select a date"
            shouldCloseOnSelect={true}
          />
          <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
            Get Prediction
          </button>
        </div>
      </form>

      {/* Display error message if response status is "error" */}
      {response?.status === "error" && (
        <div className="mt-4 bg-red-500 text-white p-4 rounded">
          {response.message}
        </div>
      )}

      {/* Display the full response if available */}
      {response && response.status !== "error" && (
        <div className="mt-4">
          <h2>Response:</h2>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;