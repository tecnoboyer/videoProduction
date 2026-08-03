"""OpenAI LLM Provider."""
from typing import Any, Optional, List, Dict
from openai import AsyncOpenAI
from app.services.providers.base import BaseLLM

class OpenAILLM(BaseLLM):
    provider_name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        return response.choices[0].message.content or ""

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        return response.choices[0].message.content or ""
