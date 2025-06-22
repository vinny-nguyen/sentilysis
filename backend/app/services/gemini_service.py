import google.generativeai as genai
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

gemini_model = "gemini-1.5-flash"


def getSummarizePrompt(prompt: str):
    return f"""
You are an AI assistant that analyzes a Reddit post about a stock ticker and returns a structured summary.
Preserve the original message, the view of the stock (positive, negative, neutral), and the tone/emotion.
Retain the original message and information conveyed. Don't miss out on any insights, and any "whys". 

Post:
{prompt}

Return in JSON format like:
{{
    "summary": "short and clear summary of the post",
    "view": "positive, negative, or neutral",
    "tone": "emotional tone (e.g. optimistic, fearful, excited)"
}}
"""


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(gemini_model)
            logger.info("Gemini service initialized successfully")

    async def summarize_text(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text using Gemini AI"""

        try:
            if not self.client:
                return "Gemini API key not configured"

            response = self.client.generate_content(
                getSummarizePrompt(prompt),
                generation_config={"max_output_tokens": max_tokens},
            )

            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Error: {str(e)}"

    async def analyze_text(self, text: str, max_tokens: int = 200) -> Dict[str, Any]:
        """Analyze text using Gemini AI"""
        try:
            if not self.client:
                return {"error": "Gemini API key not configured"}

            prompt = (
                f"""
                    You will analyze the following text about a stock and its sentiment.
                    Please provide a short description summarizing the overall sentiment.
                    Then, list reasons found in the text that support positive sentiment, neutral sentiment, and negative sentiment.
                    Return ONLY a JSON object with these fields:

                    {{
                    "description": string,          // brief summary of overall sentiment
                    "positive": string[],           // reasons supporting positive sentiment
                    "neutral": string[],            // reasons supporting neutral sentiment
                    "negative": string[]            // reasons supporting negative sentiment
                    }}

                    Input text:
                    {text}"""
            )
            response = self.client.generate_content(
                prompt, generation_config={"max_output_tokens": max_tokens}
            )

            return {
                "analysis": response.text,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"Error analyzing text with Gemini: {e}")
            return {"error": str(e), "status": "error"}

    def is_configured(self) -> bool:
        """Check if Gemini service is properly configured"""
        return self.client is not None and self.api_key is not None


# Create a singleton instance
gemini_service = GeminiService()
