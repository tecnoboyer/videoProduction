"""Factory to instantiate providers without services knowing which one."""
from typing import Any
from app.core.config import get_settings
from app.services.providers.base import BaseLLM, BaseTTS, BaseImage, BaseVideo

class ProviderFactory:
    _llm_instances = {}
    _tts_instances = {}
    _image_instances = {}
    _video_instances = {}

    @classmethod
    def get_llm(cls, provider: str = None) -> BaseLLM:
        settings = get_settings()
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        if provider in cls._llm_instances:
            return cls._llm_instances[provider]
        if provider == "openai":
            from app.services.providers.llm.openai import OpenAILLM
            inst = OpenAILLM(api_key=settings.OPENAI_API_KEY)
        elif provider == "azure":
            from app.services.providers.llm.azure import AzureLLM
            inst = AzureLLM(api_key=settings.AZURE_ID)
        elif provider == "dashscope":
            from app.services.providers.llm.dashscope import DashScopeLLM
            inst = DashScopeLLM(api_key=settings.DASHSCOPE_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
        cls._llm_instances[provider] = inst
        return inst

    @classmethod
    def get_tts(cls, provider: str = None) -> BaseTTS:
        settings = get_settings()
        provider = provider or settings.DEFAULT_TTS_PROVIDER
        if provider in cls._tts_instances:
            return cls._tts_instances[provider]
        if provider == "elevenlabs":
            from app.services.providers.tts.elevenlabs import ElevenLabsTTS
            inst = ElevenLabsTTS(api_key=settings.ELEVENLAB_API_KEY)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")
        cls._tts_instances[provider] = inst
        return inst

    @classmethod
    def get_image(cls, provider: str = None) -> BaseImage:
        settings = get_settings()
        provider = provider or settings.DEFAULT_IMAGE_PROVIDER
        if provider in cls._image_instances:
            return cls._image_instances[provider]
        if provider == "openai":
            from app.services.providers.image.openai import OpenAIImage
            inst = OpenAIImage(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown Image provider: {provider}")
        cls._image_instances[provider] = inst
        return inst

    @classmethod
    def get_video(cls, provider: str = None) -> BaseVideo:
        settings = get_settings()
        provider = provider or settings.DEFAULT_VIDEO_PROVIDER
        if provider in cls._video_instances:
            return cls._video_instances[provider]
        if provider == "ffmpeg":
            from app.services.providers.video.placeholder import FFmpegVideo
            inst = FFmpegVideo()
        else:
            raise ValueError(f"Unknown Video provider: {provider}")
        cls._video_instances[provider] = inst
        return inst
