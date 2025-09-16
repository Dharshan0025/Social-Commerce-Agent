import logging
from typing import Dict, Any, Optional
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with Groq API."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        
    async def generate_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a completion using Groq API."""
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating Groq completion: {str(e)}")
            raise
    
    async def generate_structured_completion(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a structured completion for agent tasks."""
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

# Global instance
groq_client = GroqClient()