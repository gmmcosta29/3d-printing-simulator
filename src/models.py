from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Optional

class JobStatus(Enum):
    "Represents the diferent states of each job"
    QUEUE = "queue"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELED = "canceled"

@dataclass
class Job:
    """
    Represents a 3D priting Job
    Atributtes:
        id: Job identifier
        material: Material utilized make the job (PLA, ABS, PETG, etc)
        est_time: Estimated time in Seconds
        priority: Job priority
        created_at: Timestamp when the job was created
        started_at: Timestamp when the job was started
        finished_at: Timestamp when the job was finished
        status: Current status of the job
    """
    id: str
    material: str
    est_time: float
    priority: int = 0 #lower means higher priority
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    status: JobStatus = JobStatus.QUEUE

    def __post_init__(self):
        """Data validation"""
        if self.est_time <= 0:
            raise ValueError("Estimated time must be positive")
        if self.priority < 0 :
            raise ValueError("Priority must be positive")
    
    @property
    def wait_time(self) -> Optional[float]:
        "Calculate the time waiting after start processing"
        if self.started_at is not None:
            return self.started_at - self.created_at
        return None
    
    @property
    def run_time(self) -> Optional[float]:
        """Calculate job running time"""
        if self.finished_at is not None and self.started_at is not None:
            return self.finished_at - self.started_at

    def start_processing(self) -> None:
        """Begining of the Job"""
        self.status = JobStatus.RUNNING
        self.started_at = time.time()
    
    def completed_processing(self) -> None:
        """Job Completion"""
        self.status = JobStatus.COMPLETED
        self.finished_at = time.time()
    
    def cancel(self) -> None:
        """Cancel the Job"""
        self.status = JobStatus.CANCELED
        if self.finished_at is None:
            self.finished_at = time.time()

@dataclass(order=True)
class PrioritizedJob:
    """
    Wrapper class to ordering jobs by priority

    This ensures stable ordering
        1 - Priority
        2 - FIFO Counter (When the job was inserted in the FIFO list)
    """
    priority: int
    counter: int 
    job: Job = field(compare=False) #Dont compare the job object

@dataclass
class Printer:
    """
    Represents a 3D Printer
    Attributes:
        id: Unique printer identifier
        current_job: Job currently being processed
        total_busy_time: Total time working
    """
    
    id: int
    current_job: Optional[Job] = None
    total_busy_time: float = 0.0

    @property
    def is_busy(self) -> bool:
        """Check to see if the printer is being used"""
        return self.current_job is not None
    
    def start_job(self, job: Job) -> None:
        """ Start Processing job for printer"""
        self.current_job = job
        self.start_job_time = time.time()
        job.start_processing()
    
    def finish_current_job(self) -> Optional[Job]:
        """ Complete a printing job sucessfully"""
        job = self.current_job
        job.completed_processing()

        self.total_busy_time += time.time() - job.finished_at
        self.current_job = None
        return job
    
    def get_utilization(self, total_simulation_time: float) -> float:
        """ Calculate printer utilization"""
        if total_simulation_time <= 0:
            return 0.0
        return (self.total_busy_time / total_simulation_time) * 100
    

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

if __name__ == "__main__":
    #Test Job creating and processing
    time_speedup = 0.01
    job = Job(
        id="test-job-1",
        est_time=120.0,
        priority=1,
        material="PLA",
    )
    print(f"Created job: {job.id}")
    print(f"Job Material: {job.material}")
    print(f"Status: {job.status}")
    print(f"Estimateed time job: {job.est_time}")
    print(f"Job Started at: {job.started_at}")

    job.start_processing()
    print(f"Job started status : {job.status}")
    time.sleep(job.est_time/time_speedup)
    job.completed_processing()
    print(f"Job Finished status : {job.status}")
    print(f"Job Finished Timestamp : {job.finished_at:.3f} seconds")
    print(f"Job Processing Time : {job.run_time:.3f} seconds Estimated: {job.est_time:.3f} seconds")

    #Test printer 
    start_sim = time.time()
    printer = Printer(id=1)

    job1 = Job("J1", "PLA", 10,priority=2)
    job2 = Job("J2", "PLA", 15,priority=1) # Higher priority

    #Test PrioritizedJob for queue ordering
    pjob1 = PrioritizedJob(priority=job1.priority, counter=1, job=job1)
    pjob2 = PrioritizedJob(priority=job2.priority, counter=2, job=job2)

    jobs = sorted([pjob1,pjob2])

    print(f"First Job: {jobs[0].job.id}, Priority: {jobs[0].job.priority}")
    print(f"Second Job: {jobs[1].job.id}, Priority: {jobs[1].job.priority}")

    printer.start_job(jobs[0].job)
    time.sleep(jobs[0].job.est_time * time_speedup)
    printer.finish_current_job()

    printer.start_job(jobs[1].job)
    print(f"Printing status: {printer.is_busy}")
    time.sleep(jobs[1].job.est_time * time_speedup)
    printer.finish_current_job()
    
    total_sim_time = time.time() - start_sim
    print(f"Printer : {printer.id}, Total time processing: {printer.total_busy_time} seconds")
    print(f"Expected Time Processing: {jobs[0].job.est_time/time_speedup + jobs[1].job.est_time/time_speedup} seconds")
    print(f"Printer Utilization : {printer.get_utilization(total_simulation_time=total_sim_time):.3f} %")