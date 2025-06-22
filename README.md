# Sentilysis @ SpurHacks 2025
## 🚀 Inspiration
We wanted to make real-time stock sentiment and global event analysis accessible and visually engaging for everyone. With so much financial news and data, it’s hard to see the big picture so we built Sentilysis to combine AI, live data, and interactive visuals in a single dashboard.

## 👷‍♂️ What it does
Real-time sentiment analysis for major stocks, powered by AI and news aggregation. Interactive globe visualization showing global reach and futuristic design. Stock charting for quick price insights. Chatbot assistant for conversational Q&A about stocks and markets. Macro/global event analysis connecting world news to stock sentiment. Autocomplete search for all major stocks, with dropdown selection.

## 🛠️ How we built it
Frontend: Next.js (React), Tailwind CSS, Chart.js for charts, and Three.js for the animated globe. Backend: FastAPI for news aggregation, sentiment analysis, and AI-powered summaries. AI: Integrated with OpenAI for natural language sentiment summaries. Deployment: Vercel for frontend, backend hosted separately (e.g., Render/Railway). Features: Custom skeleton loaders for smooth UX, scrollable chat, and responsive design.

## ✅ Challenges we ran into
API integration: Handling CORS and environment variables for backend/frontend communication, especially in production. UI/UX: Making the dashboard visually appealing and responsive, with smooth loading states. Data consistency: Ensuring real-time updates and accurate sentiment aggregation from multiple sources. Globe rendering: Integrating Three.js with React and keeping performance smooth.

## 😁 Accomplishments that we're proud of
Built a full-stack, real-time dashboard with AI-powered insights. Created a modern, interactive UI with advanced features like globe visualization and chat. Implemented robust loading skeletons and autocomplete for a polished user experience.

## 🤔 What we learned
How to combine multiple frameworks (Next.js, FastAPI, Three.js) in a production-ready stack. The importance of environment variables and deployment configuration for multi-service apps. Advanced React patterns for state management, async data, and UI feedback.

## 👍 What's next for Sentilysis
Expand stock coverage beyond the initial 20 tickers. Deeper AI analysis: More granular sentiment, trend prediction, and user personalization. Mobile optimization and accessibility improvements. Live event feeds and push notifications. User accounts for saving preferences and watchlists.
