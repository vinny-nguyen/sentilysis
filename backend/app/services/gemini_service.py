import google.generativeai as genai
import logging
from typing import List, Dict, Any, Optional
from ..config import settings
from ..models.sentiment import SentimentType, SentimentAnalysis, ChatResponse

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini API service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def analyze_sentiment(self, content: str, ticker: str) -> SentimentAnalysis:
        """Analyze sentiment of a single post"""
        try:
            prompt = f"""
            Analyze the sentiment of the following content related to stock ticker {ticker}.
            
            Content: {content}
            
            Please provide:
            1. Sentiment classification (positive, neutral, or negative)
            2. Confidence score (0-1)
            3. Brief summary (2-3 sentences)
            4. Key points mentioned
            5. Any geopolitical events mentioned
            6. Any macroeconomic factors mentioned
            
            Format your response as JSON:
            {{
                "sentiment": "positive|neutral|negative",
                "confidence": 0.85,
                "summary": "Brief summary here",
                "key_points": ["point1", "point2"],
                "geopolitical_events": ["event1", "event2"],
                "macroeconomic_factors": ["factor1", "factor2"]
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            result = self._parse_sentiment_response(response.text)
            
            return SentimentAnalysis(
                post_id="",  # Will be set by caller
                ticker=ticker,
                sentiment=SentimentType(result["sentiment"]),
                confidence=result["confidence"],
                summary=result["summary"],
                key_points=result["key_points"],
                geopolitical_events=result["geopolitical_events"],
                macroeconomic_factors=result["macroeconomic_factors"]
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment as fallback
            return SentimentAnalysis(
                post_id="",
                ticker=ticker,
                sentiment=SentimentType.NEUTRAL,
                confidence=0.5,
                summary="Unable to analyze sentiment due to an error.",
                key_points=[],
                geopolitical_events=[],
                macroeconomic_factors=[]
            )
    
    async def generate_summary(self, posts: List[Dict[str, Any]], ticker: str) -> Dict[str, Any]:
        """Generate overall summary from multiple posts"""
        try:
            # Prepare content for analysis
            content_summary = "\n\n".join([
                f"Source: {post.get('source', 'unknown')}\nContent: {post.get('content', '')[:500]}..."
                for post in posts[:20]  # Limit to first 20 posts
            ])
            
            prompt = f"""
            Analyze the following social media posts and news articles about stock ticker {ticker}.
            
            Posts:
            {content_summary}
            
            Please provide:
            1. Overall sentiment trend (positive, neutral, or negative)
            2. Top 5 most important headlines or key points
            3. Summary of any geopolitical events affecting this stock
            4. Summary of macroeconomic factors mentioned
            5. Key insights for investors
            
            Format your response as JSON:
            {{
                "overall_sentiment": "positive|neutral|negative",
                "top_headlines": ["headline1", "headline2", "headline3", "headline4", "headline5"],
                "geopolitical_summary": "Summary of geopolitical events",
                "macro_summary": "Summary of macroeconomic factors",
                "investor_insights": "Key insights for investors"
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            return self._parse_summary_response(response.text)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "overall_sentiment": "neutral",
                "top_headlines": [],
                "geopolitical_summary": "Unable to generate summary due to an error.",
                "macro_summary": "Unable to generate summary due to an error.",
                "investor_insights": "Unable to generate insights due to an error."
            }
    
    async def chat_response(self, message: str, ticker: str, context_data: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """Generate chatbot response with context"""
        try:
            context = ""
            if context_data:
                context = f"""
                Context about {ticker}:
                - Sentiment: {context_data.get('sentiment', 'unknown')}
                - Recent headlines: {', '.join(context_data.get('headlines', [])[:3])}
                - Geopolitical events: {context_data.get('geopolitical_events', 'none')}
                """
            
            prompt = f"""
            You are a helpful AI assistant specializing in stock market analysis and sentiment.
            
            {context}
            
            User question about {ticker}: {message}
            
            Please provide a helpful, informative response based on the context provided.
            If you don't have enough information, say so and suggest what additional data might be helpful.
            
            Keep your response concise but informative (2-4 sentences).
            """
            
            response = await self.model.generate_content_async(prompt)
            
            return ChatResponse(
                response=response.text.strip(),
                sources=["AI Analysis"],
                confidence=0.8,
                timestamp=None  # Will be set automatically
            )
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return ChatResponse(
                response="I apologize, but I'm unable to process your request at the moment. Please try again later.",
                sources=[],
                confidence=0.0,
                timestamp=None
            )
    
    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """Parse sentiment analysis response from Gemini"""
        try:
            # Extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self._fallback_sentiment_parsing(response_text)
                
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {e}")
            return self._fallback_sentiment_parsing(response_text)
    
    def _parse_summary_response(self, response_text: str) -> Dict[str, Any]:
        """Parse summary response from Gemini"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_summary_parsing(response_text)
                
        except Exception as e:
            logger.error(f"Error parsing summary response: {e}")
            return self._fallback_summary_parsing(response_text)
    
    def _fallback_sentiment_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for sentiment response"""
        # Simple keyword-based sentiment detection
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['positive', 'bullish', 'good', 'up', 'gain']):
            sentiment = "positive"
        elif any(word in text_lower for word in ['negative', 'bearish', 'bad', 'down', 'loss']):
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "confidence": 0.6,
            "summary": "Sentiment analysis completed with fallback parsing.",
            "key_points": [],
            "geopolitical_events": [],
            "macroeconomic_factors": []
        }
    
    def _fallback_summary_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for summary response"""
        return {
            "overall_sentiment": "neutral",
            "top_headlines": ["Analysis completed with fallback parsing"],
            "geopolitical_summary": "Unable to extract geopolitical events from response.",
            "macro_summary": "Unable to extract macroeconomic factors from response.",
            "investor_insights": "Please review the raw data for detailed insights."
        }

# Create global instance
gemini_service = GeminiService() 