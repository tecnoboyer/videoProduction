"""Diagnose TTS setup."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings

async def main():
    settings = get_settings()
    print(f"OPENAI_API_KEY: {'OK' if settings.OPENAI_API_KEY else 'MISSING'}")
    print(f"ELEVENLAB_API_KEY: {'OK' if settings.ELEVENLAB_API_KEY else 'MISSING'}")
    print(f"DEFAULT_TTS_PROVIDER: {settings.DEFAULT_TTS_PROVIDER}")

    # Check elevenlabs version
    try:
        import elevenlabs
        print(f"elevenlabs version: {getattr(elevenlabs, '__version__', 'unknown')}")
        try:
            from elevenlabs import ElevenLabs
            print("ElevenLabs class: AVAILABLE (modern API)")
        except ImportError:
            print("ElevenLabs class: NOT FOUND (legacy or broken install)")
    except ImportError:
        print("elevenlabs package: NOT INSTALLED")

    # Test factory
    from app.services.providers.factory import ProviderFactory
    try:
        tts = ProviderFactory.get_tts()
        print(f"TTS Provider loaded: {tts.provider_name}")
        voices = await tts.list_voices()
        print(f"Available voices: {len(voices)}")
        for v in voices[:3]:
            print(f"  - {v['voice_id']}: {v['name']}")
    except Exception as e:
        print(f"TTS Factory ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
