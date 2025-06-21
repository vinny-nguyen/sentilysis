"use client";
import { useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { sender: "bot", text: "Hi! Ask me about any stock or market event." },
  ]);

  const sentiment = { positive: 60, neutral: 25, negative: 15 };
  const headlines = {
    positive: [
      "TSLA surges after earnings beat expectations.",
      "AAPL announces innovative new product line.",
    ],
    neutral: ["Fed signals possible rate hike pause."],
    negative: [
      "$AAPL faces supply chain issues in China.",
      "Market volatility increases amid global tensions.",
    ],
  };
  const sentimentSummary =
    "Recent sentiment trends suggest a generally positive outlook for TSLA. Concerns linger around AAPL's supply chain and global market uncertainty.";
  // const macroLinks = [
  //   { text: "AAPL faces supply chain issues in China, causes investors to worry.", url: "#" },
  //   { text: "Fed signals possible rate hike pause, impacting tech stock sentiment.", url: "#" },
  //   { text: "Ongoing US-China tensions are affecting global supply chains.", url: "#" },
  // ];
  const chartData = stockData
    ? {
        labels: ["Current", "Open", "High", "Low", "Prev Close"],
        datasets: [
          {
            label: `Stock Price (${stockData.currency || "$"})`,
            data: [
              stockData.currentPrice,
              stockData.open,
              stockData.dayHigh,
              stockData.dayLow,
              stockData.previousClose,
            ],
            borderColor: "#2563eb",
            backgroundColor: "#2563eb33",
            tension: 0.4,
          },
        ],
      }
    : {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        datasets: [
          {
            label: "Stock Price ($)",
            data: [180, 185, 182, 188, 192],
            borderColor: "#2563eb",
            backgroundColor: "#2563eb33",
            tension: 0.4,
          },
        ],
      };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setStockData(null);
    try {
      const res = await fetch(`/api/stock?ticker=${ticker}`);
      const data = await res.json();
      if (res.ok) {
        setStockData(data);
      } else {
        setError(data.error || "Failed to fetch stock data");
      }
    } catch (err) {
      setError("Failed to fetch stock data");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setChatHistory((prev) => [
      ...prev,
      { sender: "user", text: chatInput },
      { sender: "bot", text: "(Mock) Here's a smart answer about: " + chatInput },
    ]);
    setChatInput("");
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 px-4 py-6 flex flex-col items-center">
      {/* Search Bar */}
      <form
        onSubmit={handleSearch}
        className="w-full max-w-3xl flex items-center gap-3 mb-6"
      >
        <input
          type="text"
          placeholder="Enter stock ticker (e.g., TSLA, AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          className="flex-1 px-4 py-2 rounded-lg border border-gray-300 bg-white dark:bg-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition shadow-sm"
        >
          Search
        </button>
      </form>

      {/* Dashboard */}
      <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sentiment Analysis */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-5 flex flex-col gap-3">
          <h2 className="text-xl font-bold">📊 Sentiment Analysis</h2>
          <div className="flex justify-around">
            <Stat label="Positive" value={sentiment.positive} color="green" />
            <Stat label="Neutral" value={sentiment.neutral} color="gray" />
            <Stat label="Negative" value={sentiment.negative} color="red" />
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300">{sentimentSummary}</p>
          <div className="text-sm space-y-2">
            {["positive", "neutral", "negative"].map((category) => (
              <div key={category}>
                <h3
                  className={`font-semibold ${
                    category === "positive"
                      ? "text-green-600 dark:text-green-400"
                      : category === "neutral"
                      ? "text-gray-600 dark:text-gray-300"
                      : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </h3>
                <ul className="list-disc ml-5">
                  {headlines[category as keyof typeof headlines].map((h, i) => (
                    <li key={i} className="text-gray-800 dark:text-gray-200">{h}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Stock Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-5 flex flex-col">
          <h2 className="text-lg font-semibold mb-3 self-center">📈 Stock Chart</h2>
          <div className="w-full h-56">
            {loading ? (
              <div className="flex items-center justify-center h-full">Loading...</div>
            ) : error ? (
              <div className="flex items-center justify-center h-full text-red-500 text-center">
                {error}
              </div>
            ) : (
              <Line
                data={chartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                }}
              />
            )}
          </div>
          {!loading && !error && stockData && (
            <div className="mt-4 text-sm text-gray-700 dark:text-gray-200 w-full">
              <div>
                <strong>
                  {stockData.shortName} ({stockData.symbol})
                </strong>
              </div>
              <div>
                Current Price: {stockData.currentPrice} {stockData.currency}
              </div>
              <div>Open: {stockData.open}</div>
              <div>High: {stockData.dayHigh}</div>
              <div>Low: {stockData.dayLow}</div>
              <div>Previous Close: {stockData.previousClose}</div>
            </div>
          )}
        </div>

        {/* Chatbot Assistant */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-5 flex flex-col">
          <h2 className="text-lg font-semibold mb-3">🤖 Chatbot Assistant</h2>
          <div className="flex-1 overflow-y-auto mb-3 border border-gray-200 dark:border-gray-700 rounded-lg p-3 bg-gray-50 dark:bg-gray-900/40 space-y-2 text-sm">
            {chatHistory.map((msg, i) => (
              <div
                key={i}
                className={`${
                  msg.sender === "bot"
                    ? "text-blue-700 dark:text-blue-300"
                    : "text-right text-gray-800 dark:text-white"
                }`}
              >
                <div className="text-xs font-medium">
                  {msg.sender === "bot" ? "Assistant" : "You"}
                </div>
                <div>{msg.text}</div>
              </div>
            ))}
          </div>
          <form onSubmit={handleChat} className="flex gap-2">
            <input
              type="text"
              placeholder="Ask a follow-up..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 px-4 py-2 rounded-full border border-gray-300 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-full hover:bg-blue-700 font-semibold transition"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Macro Events */}
      <div className="w-full max-w-7xl bg-white dark:bg-gray-800 rounded-2xl shadow p-6 mt-6 space-y-4">
  <h2 className="text-lg font-semibold tracking-tight">🌐 Connecting Global Events to Stock Sentiment</h2>
  
  <div className="space-y-3 text-sm text-gray-800 dark:text-gray-300 leading-relaxed">
    <p>
      📦 <strong>AAPL&apos;s supply chain issues</strong> in China could disrupt product deliveries and revenue forecasts. This creates uncertainty, which may lead to investor hesitation and short-term dips in stock price.
    </p>
    <p>
      🏦 The <strong>Federal Reserve&apos;s potential pause on rate hikes</strong> could signal economic stability. This might boost tech stocks like TSLA and AAPL as lower interest rates improve borrowing conditions and investor sentiment.
    </p>
    <p>
      🌏 <strong>Ongoing US-China tensions</strong> are straining global logistics networks. Companies relying on overseas manufacturing — like AAPL — may face cost increases, delayed launches, and risk of negative media coverage affecting stock valuation.
    </p>
  </div>

  <div className="mt-4">
    <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-2">🔗 References</h3>
    <ul className="list-disc ml-5 space-y-1 text-sm text-blue-700 dark:text-blue-400">
      <li><a href="#" target="_blank" rel="noopener noreferrer">AAPL Supply Chain Report – Source</a></li>
      <li><a href="#" target="_blank" rel="noopener noreferrer">Federal Reserve Interest Rate News – Source</a></li>
      <li><a href="#" target="_blank" rel="noopener noreferrer">US-China Trade Tensions Coverage – Source</a></li>
    </ul>
  </div>
  </div>
  </div>
  );
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  const colorMap: Record<string, string> = {
    green: "text-green-500",
    gray: "text-gray-400",
    red: "text-red-500",
  };
  return (
    <div className="flex flex-col items-center">
      <span className={`text-xl font-bold ${colorMap[color]}`}>{value}%</span>
      <span className="text-xs text-gray-500">{label}</span>
    </div>
  );
}
