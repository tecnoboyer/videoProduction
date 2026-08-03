"""DashScope (Alibaba/Qwen) LLM Provider."""
from typing import Any, Optional, List, Dict
import dashscope
from dashscope import Generation
from app.services.providers.base import BaseLLM

class DashScopeLLM(BaseLLM):
    provider_name = "dashscope"

    def __init__(self, api_key: str, model: str = "qwen-max", **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.model = model
        dashscope.api_key = api_key

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format="message",
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        raise RuntimeError(f"DashScope error: {response.code} - {response.message}")

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format="message",
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4000),
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        raise RuntimeError(f"DashScope error: {response.code} - {response.message}")
