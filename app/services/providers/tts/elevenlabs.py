"""ElevenLabs TTS Provider."""
from typing import Any, List, Dict
from elevenlabs import ElevenLabs
from app.services.providers.base import BaseTTS

class ElevenLabsTTS(BaseTTS):
    provider_name = "elevenlabs"

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.client = ElevenLabs(api_key=api_key)

    async def generate_voice(self, text: str, voice_id: str, output_path: str, **kwargs: Any) -> str:
        audio = self.client.generate(
            text=text,
            voice=voice_id,
            model=kwargs.get("model", "eleven_multilingual_v2"),
            output_format=kwargs.get("output_format", "mp3_44100_128"),
        )
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        return output_path

    async def list_voices(self) -> List[Dict[str, Any]]:
        voices = self.client.voices.get_all()
        return [{"voice_id": v.voice_id, "name": v.name} for v in voices.voices]
