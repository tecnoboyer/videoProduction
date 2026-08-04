"""Test ElevenLabs TTS v2.x with real voice IDs."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.providers.tts.elevenlabs import ElevenLabsTTS
from app.core.config import get_settings

async def main():
    settings = get_settings()
    print(f"API Key present: {bool(settings.ELEVENLAB_API_KEY)}")

    tts = ElevenLabsTTS(api_key=settings.ELEVENLAB_API_KEY)

    print("\nListing voices (first 10):")
    voices = await tts.list_voices()
    for v in voices[:10]:
        print(f"  {v['voice_id']}: {v['name']}")

    test_cases = [
        ("EXAVITQu4vr4xnSDxMaL", "test_direct_id.mp3"),   # Direct ID
        ("Sarah", "test_name.mp3"),                        # Name (will fallback to default)
        ("v_narrator_01", "test_mapped.mp3"),              # Mapped generic ID
        ("v_animal1_01", "test_animal.mp3"),               # Mapped generic ID
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
