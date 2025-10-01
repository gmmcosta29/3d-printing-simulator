from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from simulator import Simulator
from models import Job

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
        return JobResponse(
            id=job.id,
            material=job.material,
            est_time=job.est_time,
            priority=job.priority,
            status=job.status.value
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/jobs", response_model=list[JobResponse], status_code=200)
async def list_jobs():
    jobs = sim.get_active_jobs()
    return [
        JobResponse(
            id=j.id,
            material=j.material,
            priority=j.priority,
            status=j.status.value
        )
        for j in jobs
    ]
