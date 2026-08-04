"""ElevenLabs TTS Provider — compatible with SDK v2.60.0.

Uses actual voice IDs (not names). Common voices from ElevenLabs:
  CwhRBWXzGAHq8TQ4Fs17 = Roger
  EXAVITQu4vr4xnSDxMaL = Sarah
  FGY2WhTYpPnrIDTdsKH5 = Laura
  IKne3meq5aSn9XLyUdCD = Charlie
  JBFqnCBsd6RMkjVDRZzb = George
  N2lVS1w4EtoT3dr4eOWO = Callum
  TX3AE3VoEh1EHNafE3pg = River
  XrExE9yKIg1WjnnlVkGX = Matilda
  bIHbv24MWmeRgasZH58o = Will
  cgSgspJ2msm6clMCkdW9 = Jessica
  cjVigY5qzO86Huf0OWal = Eric
  iP95p4xoKVk53GoZ742B = Chris
  nPczCjzI2devNBz1zQrb = Brian
  oWAxZDx7w5VEj9dCyTzz = Lily
  pFZP5JQG7iQjIQuC4Bku = Serena
  pMsXgVXv3BLzUgSXRplE = Sam
  pNInz6obpgDQGcFmaJgB = Adam
  piTKgcLEGmPE4e6mEKli = Nicole
  t0jbNlBVZ17f02VDIeMI = Jessie
  wViXBPUzp2ZZixB1xQaV = Rachel  <- this one might work if it exists
"""
import asyncio
from typing import Any, List, Dict
from app.services.providers.base import BaseTTS

# Map generic script voice_ids to REAL ElevenLabs voice IDs
VOICE_MAP = {
    "Rachel": "wViXBPUzp2ZZixB1xQaV",
    "v_narrator_01": "EXAVITQu4vr4xnSDxMaL",   # Sarah - Mature, Reassuring
    "v_narrator_02": "JBFqnCBsd6RMkjVDRZzb",   # George - Warm Storyteller
    "v_animal1_01": "FGY2WhTYpPnrIDTdsKH5",    # Laura - Enthusiast
    "v_animal2_01": "IKne3meq5aSn9XLyUdCD",    # Charlie - Deep, Confident
    "v_teacher_01": "XrExE9yKIg1WjnnlVkGX",    # Matilda
    "v_teacher_02": "N2lVS1w4EtoT3dr4eOWO",    # Callum
    "v_child_01": "piTKgcLEGmPE4e6mEKli",      # Nicole
    "v_child_02": "pMsXgVXv3BLzUgSXRplE",      # Sam
}

# Safe default voice ID (Sarah)
DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"


class ElevenLabsTTS(BaseTTS):
    provider_name = "elevenlabs"

    def __init__(self, api_key: str, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key
        self._client = None
        self._voice_cache: Dict[str, str] = {}  # name -> id cache

    def _get_client(self):
        if self._client is None:
            from elevenlabs import ElevenLabs
            self._client = ElevenLabs(api_key=self.api_key)
        return self._client

    def _resolve_voice(self, voice_id: str) -> str:
        """Map generic voice_id to a real ElevenLabs voice ID."""
        # Direct mapping from our table
        if voice_id in VOICE_MAP:
            return VOICE_MAP[voice_id]
        # If it looks like an ElevenLabs voice ID (22 chars alphanumeric), use as-is
        if len(voice_id) >= 20 and voice_id.replace("_", "").replace("-", "").isalnum():
            return voice_id
        return DEFAULT_VOICE_ID

    def _generate_sync(self, text: str, voice_id: str, output_path: str, **kwargs: Any) -> str:
        """Synchronous generation using ElevenLabs SDK v2.x API."""
        client = self._get_client()
        voice = self._resolve_voice(voice_id)
        model_id = kwargs.get("model", "eleven_multilingual_v2")
        output_format = kwargs.get("output_format", "mp3_44100_128")

        try:
            audio_iterator = client.text_to_speech.convert(
                voice_id=voice,
                text=text,
                model_id=model_id,
                output_format=output_format,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "voice" in error_msg or "not found" in error_msg or "invalid" in error_msg:
                print(f"[WARN] Voice '{voice}' not found, falling back to '{DEFAULT_VOICE_ID}'")
                audio_iterator = client.text_to_speech.convert(
                    voice_id=DEFAULT_VOICE_ID,
                    text=text,
                    model_id=model_id,
                    output_format=output_format,
                )
            else:
                raise

        with open(output_path, "wb") as f:
            for chunk in audio_iterator:
                f.write(chunk)
        return output_path

    async def generate_voice(self, text: str, voice_id: str, output_path: str, **kwargs: Any) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._generate_sync,
            text,
            voice_id,
            output_path,
        )

    async def list_voices(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        voices = client.voices.get_all()
        return [{"voice_id": v.voice_id, "name": v.name} for v in voices.voices]
