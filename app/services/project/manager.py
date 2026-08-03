"""Project Manager: creates project folders with scene structure + master doc."""
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.constants import PROJECT_STRUCTURE
from app.storage.filesystem import FileStorage

class ProjectManager:
    def __init__(self, projects_dir: Path = Path("projects")):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(
        self,
        title: str,
        description: str = "",
        language: str = "es",
        voice: str = "Rachel",
        image_model: str = "dall-e-3",
        video_model: str = "ffmpeg",
        llm_provider: str = "openai",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        project_id = f"{title.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        project_path = self.projects_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        for folder, subfolders in PROJECT_STRUCTURE.items():
            for sub in subfolders:
                (project_path / folder / sub).mkdir(parents=True, exist_ok=True)

        master_doc = self._default_master_doc(title, description)
        (project_path / "rag" / "input" / "master_doc.md").write_text(master_doc, encoding="utf-8")

        meta = {
            "id": project_id,
            "title": title,
            "description": description,
            "status": "created",
            "language": language,
            "voice": voice,
            "image_model": image_model,
            "video_model": video_model,
            "llm_provider": llm_provider,
            "current_scene": None,
            "current_service": None,
            "last_job_id": None,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }
        (project_path / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        return project_path

    def get_project(self, project_id: str) -> Dict[str, Any]:
        meta_path = self.projects_dir / project_id / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        return json.loads(meta_path.read_text(encoding="utf-8"))

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        meta = self.get_project(project_id)
        meta.update(updates)
        meta_path = self.projects_dir / project_id / "metadata.json"
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        return meta

    def list_projects(self) -> list[Dict[str, Any]]:
        projects = []
        for p in sorted(self.projects_dir.iterdir()):
            if p.is_dir() and (p / "metadata.json").exists():
                projects.append(json.loads((p / "metadata.json").read_text(encoding="utf-8")))
        return projects

    def get_storage(self, project_id: str) -> FileStorage:
        path = self.projects_dir / project_id
        if not path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        return FileStorage(path)

    def _default_master_doc(self, title: str, description: str) -> str:
        return f"""# Documento Maestro: {title}

## Descripcion
{description}

## Valores y Principios Basales
- Respeto por la dignidad humana en todo el contenido generado.
- Precision tecnica y veracidad de la informacion.
- Inclusion y representacion equitativa de personajes.

## Objeciones de Conciencia
- No generar contenido que promueva violencia, odio o discriminacion.
- No utilizar estereotipos daninos en la caracterizacion de personajes.
- Evitar lenguaje excluyente o marginalizador.

## Principios de Ingenieria
- Priorizar la claridad sobre la complejidad innecesaria.
- Documentar decisiones tecnicas relevantes.
- Mantener trazabilidad de cambios y versiones.

## Directrices de Narrativa
- Tonos permitidos: educativo, inspiracional, neutral.
- Evitar: sensacionalismo, alarmismo, desinformacion.
- Preferir: ejemplos concretos, datos verificables, fuentes citadas.

## Notas Especificas del Proyecto
_Aniade aqui lineamientos particulares para este tema._

---
*Este documento fue generado automaticamente. Editlo segun las necesidades del proyecto.*
"""
