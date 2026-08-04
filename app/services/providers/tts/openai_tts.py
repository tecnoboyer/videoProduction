"""OpenAI TTS Provider — stable fallback using OpenAI API."""
from typing import Any, List, Dict
from pathlib import Path
from openai import AsyncOpenAI
from app.services.providers.base import BaseTTS

class OpenAITTS(BaseTTS):
    provider_name = "openai"

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_voice(self, text: str, voice_id: str, output_path: str, **kwargs: Any) -> str:
        # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
        # Map generic names to OpenAI voices
        voice_map = {
            "Rachel": "nova",
            "v_narrator_01": "onyx",
            "v_animal1_01": "echo",
            "v_animal2_01": "alloy",
            "v_teacher_01": "shimmer",
        }
        openai_voice = voice_map.get(voice_id, voice_id)
        if openai_voice not in ("alloy", "echo", "fable", "onyx", "nova", "shimmer"):
            openai_voice = "nova"

        response = await self.client.audio.speech.create(
            model=kwargs.get("model", "tts-1"),
            voice=openai_voice,
            input=text,
            response_format="mp3",
        )
        response.stream_to_file(Path(output_path))
        return output_path

    async def list_voices(self) -> List[Dict[str, Any]]:
        return [
            {"voice_id": "alloy", "name": "Alloy"},
            {"voice_id": "echo", "name": "Echo"},
            {"voice_id": "fable", "name": "Fable"},
            {"voice_id": "onyx", "name": "Onyx"},
            {"voice_id": "nova", "name": "Nova"},
            {"voice_id": "shimmer", "name": "Shimmer"},
        ]
