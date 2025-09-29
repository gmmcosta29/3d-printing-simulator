from models import Job, JobStatus, PrioritizedJob
import asyncio
from dataclasses import dataclass

@dataclass
class JobRecord:
    """
    Lightweight record of a completed job, only has the data needed for logs
    """
    job_id: str
    start_time: float
    created_time: float
    end_time: float
    duration: float
    status: str
    priority: int

    


class ThreadSafePriorityQueue:
    """
    ThreadSafe priority queue for managin printing jobs
    """
    def __init__(self):
        self._queue = asyncio.PriorityQueue()
        self._counter = 0
        self._jobs: dict[str,Job] = {}
        self._job_records: list[JobRecord] = []     #Jobs terminated
    
    async def put(self, job: Job) -> None:
        """Add a job to the queue"""
        self._counter +=1
        prioritized = PrioritizedJob(
            priority=job.priority,
            counter=self._counter,
            job=job
        )
        self._jobs[job.id] = job
        await self._queue.put(prioritized)
    
    async def get(self) -> Job:
        """Get the highest priority job from the queue"""
        while True:
            prioritized = await self._queue.get()
            job = prioritized.job
            if job.status == JobStatus.QUEUE:
                return job
    
    def cancel_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            job = self._jobs[job_id]
            if job.status == JobStatus.QUEUE:
                job.cancel()
                record = JobRecord(
                    job_id = job.id,
                    start_time = 0,
                    end_time = job.finished_at ,
                    created_time=job.created_at,
                    duration = 0.00,
                    status = job.status.value,
                    priority = job.priority
                )
                self._job_records.append(record)
                del self._jobs[job_id]
                return True
        return False
    
    def mark_completed(self,job: Job) -> None:
        """
        Complete a job and create a lightweight record to save memory
        """
        job.completed_processing()
        record = JobRecord(
            job_id = job.id,
            start_time = job.started_at,
            end_time = job.finished_at ,
            created_time=job.created_at,
            duration = job.finished_at - job.started_at,
            status = job.status.value,
            priority = job.priority
        )
        self._job_records.append(record)
        del self._jobs[job.id]

    

if __name__ == "__main__":
    import asyncio
    import time

    async def test_queue():
        queue = ThreadSafePriorityQueue()
        time_speedup = 10.0
        jobs = [
            Job("J1","PLA",10,2),
            Job("J2","PETG",10,1), 
            Job("J3","TPU",10,2),
            Job("J4","ABS",10,0), # Highest priority
            Job("J5","ABS",10,2)
        ]
        print("Adding Job")
        for job in jobs:
            await queue.put(job)
            print(f"Added Job {job.id} with priority {job.priority}")

        queue.cancel_job("J5")
        while True:
            job = await queue.get()
            if job is None:
                break
            print(f"Got Job {job.id} with the {job.priority} priority")
            job.start_processing()
            await asyncio.sleep(job.est_time / time_speedup)
            queue.mark_completed(job = job)

    asyncio.run(test_queue())

    