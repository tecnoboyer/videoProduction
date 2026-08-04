"""Test ElevenLabs TTS v2.x directly."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.providers.tts.elevenlabs import ElevenLabsTTS

async def main():
    from app.core.config import get_settings
    settings = get_settings()

    print(f"API Key present: {bool(settings.ELEVENLAB_API_KEY)}")

    tts = ElevenLabsTTS(api_key=settings.ELEVENLAB_API_KEY)

    print("\nListing voices (first 5):")
    voices = await tts.list_voices()
    for v in voices[:5]:
        print(f"  {v['voice_id']}: {v['name']}")

    test_cases = [
        ("Rachel", "test_rachel.mp3"),
        ("v_narrator_01", "test_narrator.mp3"),
        ("v_animal1_01", "test_animal.mp3"),
    ]

    for vid, out in test_cases:
        try:
            path = await tts.generate_voice(
                text="Habia una vez un volcan dormido en las montanas.",
                voice_id=vid,
                output_path=out,
            )
            size = Path(path).stat().st_size
            print(f"✅ {vid} -> {path} ({size} bytes)")
        except Exception as e:
            print(f"❌ {vid} -> {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
