import asyncio
import sys
from pathlib import Path

# Asegurar que app/ esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.narrative.service import NarrativeService
from app.services.project.manager import ProjectManager

async def test():
    pm = ProjectManager()
    project_id = "volcanes_040b3700"
    
    # Verificar que el proyecto existe
    try:
        meta = pm.get_project(project_id)
        print(f"✅ Proyecto encontrado: {meta['title']}")
    except FileNotFoundError:
        print(f"❌ Proyecto NO encontrado en: {pm.projects_dir / project_id}")
        return
    
    # Verificar API key
    from app.core.config import get_settings
    s = get_settings()
    print(f"🔑 OPENAI_API_KEY: {'CONFIGURADA' if s.OPENAI_API_KEY else 'VACÍA'}")
    
    # Probar narrative
    service = NarrativeService(project_id, pm.projects_dir / project_id)
    try:
        result = await service.generate(
            raw_text="Había una vez un volcán dormido...",
            style_hints="",
            provider="openai"
        )
        print(f"✅ Narrativa generada: {result['output_path']}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())