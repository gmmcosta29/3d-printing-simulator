from pathlib import Path
from models import JobRecord,Job
from datetime import datetime
import json

def generate_json_report(records: list[JobRecord]) -> None:
    output_dir = Path("logs")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"job_report_{timestamp}.json"
    filepath = output_dir / filename

    report  = {
        "jobs": [
            {
                "job_id": r.job_id,
                "status": r.status,
                "started_at": r.start_time if r.start_time > 0 else None,
                "finished_at": r.end_time
            }
            for r in records
        ]
    }
    with open(filepath,'w', encoding='utf-8') as f:
        json.dump(report,f,default=lambda o:o.__dict__, indent=4)

def load_jobs_from_json(filepath: str) -> list[Job]:
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: File {filepath} not found")
            return []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs_data = data.get("jobs", [])
        
        if not jobs_data:
            print(f"Warning: No Jobs found in {filepath}")
            return []
        
        jobs = []
        for job in jobs_data:
            jobs.append(Job(
                id = job["id"],
                material = job["material"],
                est_time = job["est_time"],
                priority = job["priority"]
            ))
        print(f"Loaded {len(jobs)} jobs in {filepath}")
        return jobs
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error: loading jobs: {e}")
        return []