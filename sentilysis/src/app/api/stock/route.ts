import { NextRequest, NextResponse } from "next/server";
import yahooFinance from "yahoo-finance2";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker");
  if (!ticker) {
    return NextResponse.json({ error: "Ticker is required" }, { status: 400 });
  }
  try {
    const quote = await yahooFinance.quote(ticker);
    return NextResponse.json({
      symbol: quote.symbol,
      shortName: quote.shortName,
      currentPrice: quote.regularMarketPrice,
      currency: quote.currency,
      previousClose: quote.regularMarketPreviousClose,
      open: quote.regularMarketOpen,
      dayHigh: quote.regularMarketDayHigh,
      dayLow: quote.regularMarketDayLow,
    });
  } catch {
    return NextResponse.json({ error: "Failed to fetch stock data ☹️." }, { status: 500 });
  }
} 