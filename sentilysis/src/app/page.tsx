"use client";
// import { cn } from "../lib/utils";

import { useState, useMemo } from "react";
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
import dynamic from "next/dynamic";
import React from "react";

const World = dynamic(() => import("../components/globe").then(m => m.World), {ssr: false});
const tickers = [];


// List of 20 stock tickers:
const STOCKS = [
  { symbol: "AAPL", name: "Apple Inc." },
  { symbol: "TSLA", name: "Tesla Inc." },
  { symbol: "GOOG", name: "Alphabet Inc." },
  { symbol: "MSFT", name: "Microsoft Corp." },
  { symbol: "AMZN", name: "Amazon.com Inc." },
  { symbol: "NVDA", name: "NVIDIA Corp." },
  { symbol: "META", name: "Meta Platforms Inc." },
  { symbol: "NFLX", name: "Netflix Inc." },
  { symbol: "AMD", name: "Advanced Micro Devices" },
  { symbol: "INTC", name: "Intel Corp." },
  { symbol: "BABA", name: "Alibaba Group" },
  { symbol: "DIS", name: "Walt Disney Co." },
  { symbol: "V", name: "Visa Inc." },
  { symbol: "JPM", name: "JPMorgan Chase" },
  { symbol: "BAC", name: "Bank of America" },
  { symbol: "WMT", name: "Walmart Inc." },
  { symbol: "PYPL", name: "PayPal Holdings" },
  { symbol: "ADBE", name: "Adobe Inc." },
  { symbol: "CRM", name: "Salesforce Inc." },
  { symbol: "ORCL", name: "Oracle Corp." },
];

interface StockData {
  symbol: string;
  shortName: string;
  currentPrice: string;
  currency: string;
  previousClose: number;
  open: number;
  dayHigh: number;
  dayLow: number;
}

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// SentimentAnalysisSkeleton:
function SentimentAnalysisSkeleton() {
  return (
    <div
      role="status"
      className="w-full p-4 border border-gray-200 rounded-2xl shadow animate-pulse md:p-6 dark:border-gray-700 bg-white dark:bg-gray-800"
    >
      <div className="h-4 bg-gray-200 rounded-full dark:bg-gray-700 w-40 mb-4"></div>
      <div className="w-60 h-3 mb-6 bg-gray-200 rounded-full dark:bg-gray-700"></div>
      <div className="flex items-baseline gap-2 mt-4">
        <div className="w-10 bg-gray-200 rounded-t-lg h-24 dark:bg-gray-700"></div>
        <div className="w-10 h-20 bg-gray-200 rounded-t-lg dark:bg-gray-700"></div>
        <div className="w-10 bg-gray-200 rounded-t-lg h-28 dark:bg-gray-700"></div>
        <div className="w-10 h-24 bg-gray-200 rounded-t-lg dark:bg-gray-700"></div>
        <div className="w-10 bg-gray-200 rounded-t-lg h-32 dark:bg-gray-700"></div>
        <div className="w-10 bg-gray-200 rounded-t-lg h-28 dark:bg-gray-700"></div>
        <div className="w-10 bg-gray-200 rounded-t-lg h-32 dark:bg-gray-700"></div>
      </div>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

// GlobalEventsSkeleton
function GlobalEventsSkeleton() {
  return (
    <div
      role="status"
      className="space-y-2.5 animate-pulse max-w-2xl w-full bg-white dark:bg-gray-800 rounded-2xl shadow p-6"
    >
      {[...Array(6)].map((_, i) => (
        <div key={i} className="flex items-center w-full gap-2">
          <div className="h-2.5 bg-gray-200 rounded-full dark:bg-gray-700 w-32"></div>
          <div className="h-2.5 bg-gray-300 rounded-full dark:bg-gray-600 w-24"></div>
          <div className="h-2.5 bg-gray-300 rounded-full dark:bg-gray-600 flex-1"></div>
        </div>
      ))}
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState<StockData | null >(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { sender: "bot", text: "Hi! Ask me about any stock or market event." },
  ]);
  const [sentimentSummary, setSentimentSummary] = useState<string | null>(null);
  const [sentimentStats, setSentimentStats] = useState<{positive: number, neutral: number, negative: number, total: number}>({positive: 0, neutral: 0, negative: 0, total: 0});
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredStocks, setFilteredStocks] = useState(STOCKS);

  const globeConfig = {
    pointSize: 4,
    globeColor: "#0a0a23",
    showAtmosphere: true,
    atmosphereColor: "#ffffff",
    atmosphereAltitude: 0.1,
    emissive: "#1e293b",
    emissiveIntensity: 0.1,
    shininess: 0.9,
    polygonColor: "rgba(255,255,255,0.7)",
    ambientLight: "#38bdf8",
    directionalLeftLight: "#ffffff",
    directionalTopLight: "#ffffff",
    pointLight: "#ffffff",
    arcTime: 1000,
    arcLength: 0.9,
    rings: 1,
    maxRings: 3,
    initialPosition: { lat: 30, lng: 120 }, // cool angle, adjust as you like
    autoRotate: true,
    autoRotateSpeed: 0.5,
  };

  const memoizedGlobe = useMemo(() => (
  <div
    className="fixed bottom-[-30vw] right-[-20vw] z-0 pointer-events-none select-none"
    style={{
      width: "90vw",
      height: "90vw",
      minWidth: 1000,
      minHeight: 500,
      maxWidth: 2000,
      maxHeight: 1200,
      opacity: 0.18,
      filter: "blur(0px)",
    }}
  >
    <World globeConfig={globeConfig} data={[]} />
  </div>
 ), []);


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
  // const sentimentSummary =
    // "Recent sentiment trends suggest a generally positive outlook for TSLA. Concerns linger around AAPL's supply chain and global market uncertainty.";
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

async function fetchSentimentRecords(ticker: string) {
  const res = await fetch(`http://localhost:8000/overview/ticker/${ticker}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ limit: 100, skip: 0 }),
  });
  if (!res.ok) throw new Error("Failed to fetch sentiment records");
  const data = await res.json();
  return data.records; // Array of records
}

function recordsToText(records: any[]) {
  // You can customize this aggregation as needed
  return records.map(
    (r: any) => `${r.title}: ${r.sentiment?.summary || ""}`
  ).join("\n");
}

async function getSentimentSummary(ticker: string) {
  // Fetch records from DB
  const records = await fetchSentimentRecords(ticker);

  // Count sentiment types
  let positive = 0, neutral = 0, negative = 0;
  for (const r of records) {
    const s = r.sentiment?.label || r.sentiment?.type || r.sentiment;
    if (s.view === "positive") positive++;
    else if (s.view === "neutral") neutral++;
    else if (s.view === "negative") negative++;
  }

  // Collect titles + source links
  const sourceLinks = records
    .filter((r: { title: string; source_link: string }) => r.title && r.source_link)
    .map((r: { title: string; source_link: string }) => ({
      title: r.title,
      url: r.source_link
    }));

  // Aggregate records into a single text string
  const text = recordsToText(records);

  // Step 3: Send to AI for analysis
  const aiRes = await fetch(`http://localhost:8000/ai/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text, max_tokens: 200 }),
  });
  if (!aiRes.ok) throw new Error("Failed to get sentiment summary");

  const sentimentHTML = (await aiRes.json()).analysis;

  return {
    summaryHTML: sentimentHTML,
    stats: {
      positive,
      neutral,
      negative,
      total: records.length,
    },
    sourceLinks,
  };
}

const [sourceLinks, setSourceLinks] = useState<{ title: string; url: string }[]>([]);

const handleSearch = async (e: React.FormEvent | null, tickerOverride?: string) => {
  if (e) e.preventDefault();
  const searchTicker = tickerOverride || ticker;
  setLoading(true);
  setError("");
  setStockData(null);
  setSentimentSummary(null);
  setSentimentStats({positive: 0, neutral: 0, negative: 0, total: 0});
  try {
    // Fetch stock data
    const res = await fetch(`/api/stock?ticker=${searchTicker}`);
    const data = await res.json();
    if (res.ok) {
      setStockData(data);
    } else {
      setError(data.error || "Failed to fetch stock data ☹️.");
    }

    // Get both sentiment summary + stats in one go
    const { summaryHTML, stats, sourceLinks } = await getSentimentSummary(searchTicker);
    setSentimentStats(stats);
    setSentimentSummary(summaryHTML);
    setSourceLinks(sourceLinks);
  } catch {
    setError("Failed to fetch stock data or sentiment ☹️.");
  } finally {
    setLoading(false);
  }
};


const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const handleChat = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!chatInput.trim()) return;

  const userMessage = chatInput;
  setChatHistory((prev) => [...prev, { sender: "user", text: userMessage }]);
  setChatInput("");

  if (!GEMINI_API_KEY) {
    setChatHistory((prev) => [
      ...prev,
      { sender: "bot", text: "Error: Gemini API key is not set. Please set NEXT_PUBLIC_GEMINI_API_KEY in your .env.local file." },
    ]);
    return;
  }

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `You are a chatbot on a sentiment analysis web app. The user will query you information related to ${ticker}. Answer in less than 100 words and give a neurtal, grounded, professional answer. User Query:  ${userMessage}`
          }] }],
        }),
      }
    );

    const data = await res.json();
    const botReply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, no response.";

    setChatHistory((prev) => [...prev, { sender: "bot", text: botReply }]);
  } catch (err) {
    console.error("Error calling Gemini API:", err);
    setChatHistory((prev) => [
      ...prev,
      { sender: "bot", text: "Error fetching response from Gemini." },
    ]);
  }
};


  // Helper to parse sentiment summary JSON (even if wrapped in code block)
  function parseSentimentSummary(summary: string | null) {
    if (!summary) return null;
    let clean = summary.trim();
    // Remove code block markers and 'json' if present
    if (clean.startsWith('```')) {
      clean = clean.replace(/^```json|^```/i, '').replace(/```$/, '').trim();
    }
    try {
      return JSON.parse(clean);
    } catch {
      return null;
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 px-4 py-6 flex flex-col items-center">
      {/* Header */}
      <header className="w-full max-w-7xl flex items-center justify-between mb-8 px-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-extrabold tracking-tight text-blue-700 dark:text-blue-400">🌇 Sentilysis.co</span>
          <span className="text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded ml-2">AI Real Time Stocks Insights</span>
        </div>
        {/* Optionally, add a placeholder for nav or logo */}
      </header>
      {/* Globe Background */}
      {memoizedGlobe}
      <div className="relative z-0 w-full flex flex-col items-center">

      {/* Search Bar */}
      <form
        onSubmit={handleSearch}
        className="w-full max-w-3xl flex flex-col gap-1 mb-6 relative"
        autoComplete="off"
      >
        <input
          type="text"
          placeholder="Enter stock ticker (e.g., TSLA, AAPL)"
          value={ticker}
          onChange={(e) => {
            const val = e.target.value.toUpperCase();
            setTicker(val);
            if (val.length === 0) {
              setShowDropdown(false);
              setFilteredStocks(STOCKS);
            } else {
              const filtered = STOCKS.filter(
                (s) =>
                  s.symbol.startsWith(val) ||
                  s.name.toUpperCase().startsWith(val)
              );
              setFilteredStocks(filtered);
              setShowDropdown(filtered.length > 0);
            }
          }}
          onFocus={() => setShowDropdown(ticker.length > 0 && filteredStocks.length > 0)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 100)} // delay to allow click
          className="flex-1 px-4 py-2 rounded-lg border border-gray-300 bg-white dark:bg-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {showDropdown && (
          <div className="absolute top-full left-0 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-b-lg shadow z-10 max-h-56 overflow-y-auto">
            {filteredStocks.map((stock) => (
              <div
                key={stock.symbol}
                role="button"
                tabIndex={0}
                className="px-4 py-2 cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900"
                onMouseDown={async (e) => {
                  e.preventDefault();
                  setTicker(stock.symbol);
                  setShowDropdown(false);
                  setTimeout(() => {
                    handleSearch(null, stock.symbol);
                  }, 0);
                }}
              >
                <span className="font-semibold">{stock.symbol}</span>
                <span className="ml-2 text-gray-500">{stock.name}</span>
              </div>
            ))}
          </div>
        )}
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition shadow-sm mt-2"
        >
          Search 🔍
        </button>
      </form>

      {/* Dashboard */}
      <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sentiment Analysis */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-5 flex flex-col gap-3">
          <h2 className="text-xl font-bold">📊 Sentiment Analysis</h2>
          {loading && <SentimentAnalysisSkeleton />}
          {!loading && sentimentSummary && (
            <>
              {sentimentStats.total > 0 && (
                <div className="flex gap-6 mt-4 justify-center">
                  <Stat
                    label="Positive"
                    value={Math.round((sentimentStats.positive / sentimentStats.total) * 100)}
                    color="green"
                  />
                  <Stat
                    label="Neutral"
                    value={Math.round((sentimentStats.neutral / sentimentStats.total) * 100)}
                    color="gray"
                  />
                  <Stat
                    label="Negative"
                    value={Math.round((sentimentStats.negative / sentimentStats.total) * 100)}
                    color="red"
                  />
                </div>
              )}
              {/* Render parsed sentiment summary if possible */}
              {(() => {
                const parsed = parseSentimentSummary(sentimentSummary);
                if (parsed) {
                  return (
                    <div className="mt-4 text-sm text-gray-700 dark:text-gray-300">
                      <div className="font-semibold mb-1">{parsed.description}</div>
                      {parsed.positive && parsed.positive.length > 0 && (
                        <div className="mb-1">
                          <span className="font-medium text-green-600">Positive:</span>
                          <ul className="list-disc ml-6">
                            {parsed.positive.map((item: string, idx: number) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {parsed.neutral && parsed.neutral.length > 0 && (
                        <div className="mb-1">
                          <span className="font-medium text-gray-500">Neutral:</span>
                          <ul className="list-disc ml-6">
                            {parsed.neutral.map((item: string, idx: number) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {parsed.negative && parsed.negative.length > 0 && (
                        <div className="mb-1">
                          <span className="font-medium text-red-600">Negative:</span>
                          <ul className="list-disc ml-6">
                            {parsed.negative.map((item: string, idx: number) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  );
                } else {
                  // fallback to raw string if not JSON
                  return <p className="text-sm text-gray-700 dark:text-gray-300">{sentimentSummary}</p>;
                }
              })()}
            </>
          )}
          {!loading && !sentimentSummary && (
            <div className="text-gray-400 text-sm">No sentiment data available.</div>
          )}
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

        {/* To do: Make chatbot assistant scrollable instead of expanding + Make search bar support 20 tickers */}

        {/* Chatbot Assistant */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-5 flex flex-col h-full min-h-[340px]">
          <h2 className="text-lg font-semibold mb-3">🤖 Chatbot Assistant</h2>
          <div 
            className="mb-3 border border-gray-200 dark:border-gray-700 rounded-lg p-3 bg-gray-50 dark:bg-gray-900/40 space-y-2 text-sm flex-1 min-h-0 overflow-y-auto"
          >
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
    {sourceLinks.map((link, index) => (
      <li key={index}>
        <a href={link.url} target="_blank" rel="noopener noreferrer">
          {link.title}
        </a>
      </li>
    ))}
  </ul>
</div>

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
