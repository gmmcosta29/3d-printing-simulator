from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from simulator import Simulator
from models import Job
import logging

log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename= log_dir /'simulation.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class JobCreate(BaseModel):
    id: str
    material: str
    est_time: float = Field(gt=0)
    priority: int = Field(ge=0)

class JobResponse(BaseModel):
    id: str
    material: str
    est_time: float
    priority: int
    status: str

class StatsResponse(BaseModel):
    avg_wait_time: float
    median_wait_time: float
    throughput: float
    total_completed: int

#Global sim instance
sim: Optional[Simulator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sim
    sim = Simulator(num_printers=2,time_scale=0.1)
    await sim.start()
    print("Simulation started")
    yield
    await sim.stop()

app = FastAPI(
    title='3D Printing Queue API',
    version="1.0.0",
    lifespan=lifespan
)

#create a new job
@app.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(job_data: JobCreate):
    try:
        job = Job(
            id=job_data.id,
            material=job_data.material,
            est_time=job_data.est_time,
            priority=job_data.priority
        )
        await sim.add_job(job)
        logging.info(f"Job {job_data.id} created successfully")
        return JobResponse(
            id=job.id,
            material=job.material,
            est_time=job.est_time,
            priority=job.priority,
            status=job.status.value
        )
    except ValueError as e:
        logging.info(f"Error: Create job {job_data.id}, with error:{e}")
        raise HTTPException(status_code=400, detail=str(e))

#list all the jobs in queue    
@app.get("/jobs", response_model=list[JobResponse], status_code=200)
async def list_jobs():
    jobs = sim.get_active_jobs()
    return [
        JobResponse(
            id=j.id,
            material=j.material,
            est_time=j.est_time,
            priority=j.priority,
            status=j.status.value
        )
        for j in jobs
    ]

#get global stats
@app.get("/stats", response_model=StatsResponse, status_code=200)
async def list_stats():
    stats = sim.get_global_stats()
    return StatsResponse(
            avg_wait_time=stats['avg_wait_time'],
            median_wait_time=stats['median_wait_time'],
            throughput=stats['throughput'],
            total_completed=stats['total_completed']
        )

#get queue status
@app.get("/health")
async def health():
    stats = sim.get_queue_stats()
    return {
        "status": "healthy",
        "printers": sim.num_printers,
        "active_jobs": stats['active_jobs'],
        "completed": stats['completed'],
        "cancelled": stats['cancelled'],
        "total_processed": stats['total_processed']
    }

#cancel a job
@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    success = sim.cancel_job(job_id)
    if not success:
        logging.info(f"Error: Canceling {job_id} ")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    logging.info(f"Job {job_id} cancelled successfully")
    return {"message": f"Job {job_id} cancelled"}
