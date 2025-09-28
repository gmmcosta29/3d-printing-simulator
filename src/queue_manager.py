from models import Job, JobStatus, PrioritizedJob
import asyncio


class ThreadSafePriorityQueue:
    """
    ThreadSafe priority queue for managin printing jobs
    """
    def __init__(self):
        self._queue = asyncio.PriorityQueue()
        self._counter = 0
        self._jobs: dict[str,Job] = {}
    
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
        prioritized = await self._queue.get()
        return prioritized.job
    
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
            Job("J4","ABS",10,0) # Highest priority
        ]

        print("Adding Job")
        for job in jobs:
            await queue.put(job)
            print(f"Added Job {job.id} with priority {job.priority}")

        while True:
            job = await queue.get()
            if job is None:
                break
            print(f"Got Job {job.id} with the {job.priority} priority")
            job.start_processing()
            await asyncio.sleep(job.est_time / time_speedup)
            job.completed_processing()

    asyncio.run(test_queue())

    