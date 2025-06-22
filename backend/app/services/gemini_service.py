import google.generativeai as genai
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

gemini_model = "gemini-1.5-flash"


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
            prompt,
            generation_config={
                "max_output_tokens": max_tokens
            }
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
                f"Please analyze the following text and provide insights:\n\n{text}"
            )
            response = self.client.generate_content(prompt)

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
