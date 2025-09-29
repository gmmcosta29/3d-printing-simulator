import asyncio
import time
from models import Job, Printer
from queue_manager import ThreadSafePriorityQueue

class Simulator:
    """
    Main 3D printing simulator 
    """
    def __init__(self, num_printers: int = 1, time_scale: float = 0.1):
        self._printers = [Printer(id=i) for i in range(num_printers)]
        self._time_scale = time_scale
        self._start_time = None
        self._queue = ThreadSafePriorityQueue()
        self._running = False
        self._workers_tasks = []

    @property
    def num_printers(self) -> int:
        return len(self._printers)
    
    @property
    def time_scale(self) -> float:
        return self._time_scale
    
    @property
    def printers(self) -> list[Printer]:
        return self._printers.copy()
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel job by name """
        return self._queue.cancel_job(job_id=job_id)
    
    def get_active_jobs(self) -> list[Job]:
        """Returns a list of the active jobs"""
        return list(self._queue._jobs.values())
    
    def get_job_records(self) -> list[Job]:
        """Return Jobs that are completed/canceled"""
        return self._queue._job_records.copy()
    
    def get_queue_stats(self) -> dict:
        records = self._queue._job_records
        return{
            "active_jobs": len(self._queue._jobs),
            "completed": sum(1 for r in records if r.status == "completed"),
            "canceled": sum(1 for r in records if r.status == "canceled"),
            "total_processed": len(records)
        }
    
    def get_global_stats(self) -> dict:
        """Final statistics"""
        total_sim_time = time.time() - self._start_time
        records = self._queue._job_records
        completed = [r for r in records if r.status == "completed"]

        wait_times = []
        for r in completed:
            if r.start_time > 0:
                wait = r.start_time - r.created_time
                wait_times.append(wait)


        if wait_times:
            sorted_wait = sorted(wait_times)
            size = len(sorted_wait)
            avg_wait = sum(wait_times) / len(wait_times)
            if size % 2 == 0:
                median_wait = (sorted_wait[size//2 -1] + sorted_wait[size//2])/2
            else:
                median_wait = sorted_wait[size//2]
        else:
            median_wait = 0.0
            avg_wait = 0.0

        total_completed = len(completed)
        if total_sim_time != 0:
            throughput = total_completed / total_sim_time
        else:
            throughput = 0.0
        
        #printer utilization
        printer_utilization = []
        for printer in self._printers:
            utiliziation = printer.get_utilization(total_sim_time)
            printer_utilization.append({
                "printer_id": printer.id,
                "utilization_percent": utiliziation
            })
        return {
            "avg_wait_time": avg_wait,
            "median_wait_time":median_wait,
            "throughput":throughput,
            "printer_utilization": printer_utilization,
            "total_simulation_time": total_sim_time,
            "total_completed": total_completed
        }
    
    async def add_job(self, job: Job) -> None:
        """Add a job to the queue"""
        await self._queue.put(job)

    async def add_jobs(self, jobs: list[Job]) -> None:
        """Add a job to the queue"""
        for job in jobs:
            await self._queue.put(job)
    
    async def run_printer(self,printer: Printer) -> None:
        """
        One coroutine per printer 
        Runs in loop until signal from CLI to stop (timeout in order to stop)
        """
        while self._running:
            try:
                job = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
                printer.start_job(job)
                await asyncio.sleep(job.est_time * self._time_scale)
                printer.finish_current_job()
                self._queue.mark_completed(job)
                print(f"Printer {printer.id} completed the job{job.id}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Printer {printer.id} as the  error:{e}")
        print(f"Printer {printer.id} stopped")
    
    async def start(self) -> None:
        """Main routine that starts all the coroutines"""
        self._running = True
        self._start_time = time.time()
        for printer in self._printers:
            task = asyncio.create_task(self.run_printer(printer=printer))
            self._workers_tasks.append(task)
        print(f"Started {len(self._printers)} printer workers")

    async def stop(self) -> None:
        """Stops all the workers safely"""
        self._running = False
        await asyncio.gather(*self._workers_tasks, return_exceptions=True) # Waits for all threads even if they raise exceptions
        print("All workers stoped")

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
    sim._queue.cancel_job("J3")
    #await sim.run(job_count=4)

    print(f" Job record {sim._queue._job_records}")

if __name__ == "__main__":
    asyncio.run(basic_test())