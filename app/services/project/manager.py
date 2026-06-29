from pathlib import Path
from app.core.constants import PROJECT_STAGES
import json

class ProjectManager:

    def __init__(self):
        self.projects_folder = Path("projects")

    def slugify(self, title: str) -> str:
        return title.lower().replace(" ", "_")
    
    def create_projects_folder(self):
        self.projects_folder.mkdir(exist_ok=True)

    def create_project_folder(self, title: str):
        folder_name = self.slugify(title)
        project_path = self.projects_folder / folder_name
        project_path.mkdir(exist_ok=True)
        return project_path
    
    def create_stage_folders(self, project_path):
        for stage in PROJECT_STAGES:
            stage_path = project_path / stage
            (stage_path / "input").mkdir(parents=True, exist_ok=True)
            (stage_path / "output").mkdir(parents=True, exist_ok=True)
    
    def create_metadata(self, project_path, title):
        metadata = {
            "title": title,
            "status": "created",
            "current_stage": "narrative",
        }
        metadata_file = project_path / "metadata.json"

        with open(metadata_file, "w") as file:
            json.dump(metadata, file, indent=4)
    def create_project(self, title):
        self.create_projects_folder()
        project_path = self.create_project_folder(title)
        self.create_stage_folders(project_path)
        self.create_metadata(project_path, title)

        return project_path