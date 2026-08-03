"""Job Manager: every generation creates a Job."""
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.core.constants import JobStatus

class JobManager:
    def __init__(self, projects_dir: Path = Path("projects")):
        self.projects_dir = Path(projects_dir)

    def _job_dir(self, project_id: str) -> Path:
        path = self.projects_dir / project_id / "jobs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_job(
        self,
        project_id: str,
        service_name: str,
        provider: Optional[str] = None,
        input_folder: Optional[str] = None,
        output_folder: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job_data = {
            "job_id": job_id,
            "project_id": project_id,
            "service_name": service_name,
            "provider": provider,
            "status": JobStatus.PENDING,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "started_at": None,
            "finished_at": None,
            "input_folder": input_folder,
            "output_folder": output_folder,
            "result_path": None,
            "error_message": None,
            "metadata": metadata or {},
        }
        job_path = self._job_dir(project_id) / f"{job_id}.json"
        job_path.write_text(json.dumps(job_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return job_id

    def get_job(self, project_id: str, job_id: str) -> Dict[str, Any]:
        job_path = self._job_dir(project_id) / f"{job_id}.json"
        if not job_path.exists():
            raise FileNotFoundError(f"Job {job_id} not found in project {project_id}")
        return json.loads(job_path.read_text(encoding="utf-8"))

    def list_jobs(self, project_id: str, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        job_dir = self._job_dir(project_id)
        jobs = []
        for f in sorted(job_dir.glob("job_*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            if service_name is None or data.get("service_name") == service_name:
                jobs.append(data)
        return jobs

    def update_status(
        self,
        project_id: str,
        job_id: str,
        status: str,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        job = self.get_job(project_id, job_id)
        job["status"] = status
        if status == JobStatus.RUNNING and job["started_at"] is None:
            job["started_at"] = datetime.utcnow().isoformat() + "Z"
        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job["finished_at"] = datetime.utcnow().isoformat() + "Z"
        if result_path:
            job["result_path"] = result_path
        if error_message:
            job["error_message"] = error_message
        job_path = self._job_dir(project_id) / f"{job_id}.json"
        job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False), encoding="utf-8")
        return job

    def get_latest_job(self, project_id: str, service_name: str) -> Optional[Dict[str, Any]]:
        jobs = self.list_jobs(project_id, service_name)
        if not jobs:
            return None
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jobs[0]
