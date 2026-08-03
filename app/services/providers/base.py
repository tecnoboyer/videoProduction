"""Provider abstractions — never tie services to a single vendor."""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional, Dict, List

class BaseLLM(ABC):
    provider_name: str = "base"

    def __init__(self, api_key: str, **kwargs: Any):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        pass

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        yield await self.generate(prompt, **kwargs)

class BaseTTS(ABC):
    provider_name: str = "base"

    def __init__(self, api_key: str, **kwargs: Any):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_voice(self, text: str, voice_id: str, output_path: str, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def list_voices(self) -> List[Dict[str, Any]]:
        pass

    async def clone_voice(self, name: str, samples: List[str], **kwargs: Any) -> str:
        raise NotImplementedError("Voice cloning not supported by this provider.")

class BaseImage(ABC):
    provider_name: str = "base"

    def __init__(self, api_key: str, **kwargs: Any):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_image(self, prompt: str, output_path: str, size: str = "1024x1024", **kwargs: Any) -> str:
        pass

    async def edit_image(self, image_path: str, mask_path: str, prompt: str, output_path: str, **kwargs: Any) -> str:
        raise NotImplementedError("Image editing not supported.")

    async def upscale(self, image_path: str, output_path: str, **kwargs: Any) -> str:
        raise NotImplementedError("Upscaling not supported.")

class BaseVideo(ABC):
    provider_name: str = "base"

    def __init__(self, api_key: str = "", **kwargs: Any):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_video(self, image_path: str, prompt: str, output_path: str, **kwargs: Any) -> str:
        pass
