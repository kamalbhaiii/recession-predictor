import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart } from "chart.js/auto";
import { motion } from "framer-motion";

function App() {
  const chartCanvasRef = useRef(null);
  const [features, setFeatures] = useState(
    JSON.stringify(Array(12).fill({ gdp: 0, inflation: 0, unemployment: 0 }), null, 2)
  );
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  const chartRef = useRef(null);

  useEffect(() => {
    const eventSource = new EventSource(`${import.meta.env.VITE_BACKEND}/logs`);
    eventSource.onmessage = (event) => {
      setLogs((prevLogs) => [...prevLogs, event.data]);
    };
    return () => eventSource.close();
  }, []);

  const validateInput = (text) => {
    try {
      const parsed = JSON.parse(text);
      if (!Array.isArray(parsed) || parsed.length !== 12) return false;
      return parsed.every(
        (item) =>
          typeof item === "object" &&
          "gdp" in item && typeof item.gdp === "number" &&
          "inflation" in item && typeof item.inflation === "number" &&
          "unemployment" in item && typeof item.unemployment === "number"
      );
    } catch {
      return false;
    }
  };

  const handleInputChange = (e) => {
    setFeatures(e.target.value);
    if (validateInput(e.target.value)) setError(null);
    else setError("Invalid JSON format. Ensure it's an array of 12 objects.");
  };

  const handleSubmit = async () => {
    if (!validateInput(features)) {
      setError("Invalid data format! Please correct it before proceeding.");
      return;
    }
    
    setLoading(true);
    setLogs(["🔄 Sending request to server..."]);
  
    try {
      const res = await axios.post(`${import.meta.env.VITE_BACKEND}/predict`, {
        features: JSON.parse(features),
      });
  
      setPrediction(res.data.prediction);
      
      setHistory((prevHistory) => {
        const updatedHistory = [...prevHistory, { date: new Date().toLocaleDateString(), prob: res.data.prediction }];
        
        if (chartRef.current) {
          chartRef.current.data.labels = updatedHistory.map((h) => h.date);
          chartRef.current.data.datasets[0].data = updatedHistory.map((h) => h.prob);
          chartRef.current.update();
        } else if (chartCanvasRef.current) {
          chartRef.current = new Chart(chartCanvasRef.current, {
            type: "line",
            data: {
              labels: updatedHistory.map((h) => h.date),
              datasets: [
                {
                  label: "Recession Probability",
                  data: updatedHistory.map((h) => h.prob),
                  borderColor: "red",
                  backgroundColor: "rgba(255, 99, 132, 0.2)",
                  fill: true,
                },
              ],
            },
          });
        }
  
        return updatedHistory;
      });
    } catch (err) {
      console.log(err);
      setError("❌ Failed to fetch prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      {loading && (
        <motion.div
          className="fixed inset-0 flex flex-col items-center justify-center bg-white bg-opacity-80"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div className="w-16 h-16 border-t-4 border-blue-500 rounded-full animate-spin" />
          <div className="mt-4 text-gray-600 text-sm w-1/2 bg-gray-50 p-4 rounded shadow max-h-60 overflow-auto">
            {logs.map((log, index) => (
              <p key={index}>{log}</p>
            ))}
          </div>
        </motion.div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-lg w-1/2">
        <h1 className="text-2xl font-semibold text-center mb-4">Indian Recession Predictor</h1>

        <textarea
          rows="10"
          className="w-full p-2 border border-gray-300 rounded"
          value={features}
          onChange={handleInputChange}
        />

        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

        <button
          className={`w-full mt-4 py-2 text-white rounded ${error ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"}`}
          onClick={handleSubmit}
          disabled={!!error}
        >
          Predict
        </button>

        {prediction !== null && (
          <p className="text-center text-lg font-medium mt-4">
            Recession Probability: <span className="font-bold">{(prediction * 100).toFixed(2)}%</span>
          </p>
        )}

        {history.length > 0 && (
          <div className="mt-6">
            <canvas ref={chartCanvasRef} id="recessionChart"></canvas>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
