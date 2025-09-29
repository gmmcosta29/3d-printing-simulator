import asyncio
from models import Job
from simulator import Simulator

class CLI:
    def __init__(self, simulator: Simulator):
        self.sim = simulator
        self.running = False
    
    def print_help(self):
        """
        Print avaliable commands
        """
        print("Avaliable commands")
        print(" add <id> <material> <time> <priority>       - add a job")
        print("list                                         - list all the jobs in queue")
        print("cancel <job_id>                              - cancel a job")
        print("status                                       - shows simulator status")
        print("help                                         - shows help")
        print("stop                                         - stops the simulator and exit")
        print()

    async def cmd_add(self, args: list[str]) -> None:
        """Add a job to the queue"""
        if len(args) != 4:
            print("Usage add <id> <material> <time> <priority>")
            return
        
        try:
            job_id = args[0]
            material = args[1]
            estimate_time = float(args[2])
            priority = int(args[3])
            
            job = Job(job_id = job_id, material=material, est_time= estimate_time, priority=priority)
            await self.sim.add_job(job = job)

            print(f"Added Job {job_id}: {material}, {estimate_time}s with {priority} priority")
        except ValueError as e:
            print(f"Error: {e}")
    
    def cmd_list(self) -> None:
        """Print all the jobs in queue"""
        print("\n Jobs in Queue: ")
        records = self.sim.get_job_records()
        if not records:
            return
        print("\nJob Records: ")
        print(f"ID      Priority        Duration        Status      Wait Time       RunTime")
        print("-" * 50)
        for record in records:
            print(f"{record.job_id}     {record.priority}       {record.duration:.3f}       {record.status}     {(record.start_time-record.created_time):.3f}      {(record.end_time -record.start_time):.3f}")
        print()
        print("-" * 50)
    
