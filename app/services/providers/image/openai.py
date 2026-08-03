"""OpenAI Image Provider."""
import base64
from typing import Any
from openai import AsyncOpenAI
import httpx
from app.services.providers.base import BaseImage

class OpenAIImage(BaseImage):
    provider_name = "openai"

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_image(self, prompt: str, output_path: str, size: str = "1024x1024", **kwargs: Any) -> str:
        model_name = kwargs.get("model", "gpt-image-1-mini")
        
        response = await self.client.images.generate(
            model=model_name,
            prompt=prompt,
            size=size,
            n=1,
        )

        image_data = response.data[0]

        # 1. Si la API devuelve una URL accesible
        if image_data.url:
            async with httpx.AsyncClient() as client:
                r = await client.get(image_data.url)
                r.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(r.content)

        # 2. Si la API devuelve los bytes en base64 (b64_json)
        elif image_data.b64_json:
            image_bytes = base64.b64decode(image_data.b64_json)
            with open(output_path, "wb") as f:
                f.write(image_bytes)

        else:
            raise ValueError("La API de OpenAI no devolvió ni 'url' ni 'b64_json'.")

        return output_path