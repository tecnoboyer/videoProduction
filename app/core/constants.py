from pathlib import Path

PROJECT_STRUCTURE = {
    "narrative": {"input", "output"},
    "script": {"input", "output"},
    "audio": {"input", "output", "clips"},
    "alignment": {"input", "output"},
    "images": {"input", "output"},
    "scenes": {"input", "output"},
    "video": {"input", "output", "renders"},
    "rag": {"input", "output"},
}

class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ServiceName:
    NARRATIVE = "narrative"
    SCRIPT = "script"
    AUDIO_TTS = "audio_tts"
    AUDIO_ASSEMBLER = "audio_assembler"
    ALIGNMENT = "alignment"
    SCENES = "scenes"
    VIDEO = "video"
