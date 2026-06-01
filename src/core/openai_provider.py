import time
import os
from typing import Dict, Any, Optional, Generator, Tuple
from openai import OpenAI
from src.core.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        # Get API key from .env or parameter
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        super().__init__(model_name, api_key)
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Tuple[str, Dict[str, int]]:
        """
        Generate response from OpenAI API.
        Returns: (response_text, usage_dict)
        """
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extract content and usage
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return content, usage

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model_name

