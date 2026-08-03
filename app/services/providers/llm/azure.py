"""Azure OpenAI LLM Provider."""
from typing import Any, Optional, List, Dict
from openai import AsyncAzureOpenAI
from app.services.providers.base import BaseLLM

class AzureLLM(BaseLLM):
    provider_name = "azure"

    def __init__(self, api_key: str, endpoint: str = "", deployment: str = "gpt-4", api_version: str = "2024-02-01", **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.deployment = deployment
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint or kwargs.get("endpoint", ""),
            api_version=api_version,
        )

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        return response.choices[0].message.content or ""

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        return response.choices[0].message.content or ""
