import asyncio
import time
from models import Job, Printer
from queue_manager import ThreadSafePriorityQueue

class Simulator:
    """
    Main 3D printing simulator 
    """
    def __init__(self, num_printers: int = 1, time_scale: float = 0.1):
        self.num_printers = num_printers
        self.time_scale = time_scale
        self.queue = ThreadSafePriorityQueue()
        self.start_time = None

    async def add_job(self, job: Job) -> None:
        """Add a job to the queue"""
        await self.queue.put(job)

    async def add_jobs(self, jobs: list[Job]) -> None:
        """Add a job to the queue"""
        for job in jobs:
            await self.queue.put(job)
    

    async def run(self,job_count: int) -> None:
        """
        Main simulator function, the heart of the simulator
        """
        self.start_time = time.time()
        processed = 0

        while processed < job_count:
            job = await self.queue.get()

            print(f"Processing {job.id} with {job.priority} priority")

            job.start_processing()
            await asyncio.sleep(job.est_time * self.time_scale)
            self.queue.mark_completed(job)

            processed +=1
        total_time =  time.time() - self.start_time
        print(f"Simulator ran for a total of {total_time:.3f} seconds")

async def basic_test():

    sim = Simulator(num_printers = 1, time_scale = 0.1)
    jobs = [
        Job("J1","PLA",10,2),
        Job("J2","PETG",10,1), 
        Job("J3","TPU",10,2),
        Job("J4","ABS",10,0), # Highest priority
        Job("J5","ABS",10,2)
    ]
    await sim.add_jobs(jobs)
    sim.queue.cancel_job("J3")
    await sim.run(job_count=4)

    print(f" Job record {sim.queue._job_records}")

if __name__ == "__main__":
    asyncio.run(basic_test())