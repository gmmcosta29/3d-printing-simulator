import asyncio
from models import Job
from simulator import Simulator
import sys
from json_manager import load_jobs_from_json

class CLI:
    def __init__(self, simulator: Simulator):
        self.sim = simulator
        self.running = False
    
    def cmd_help(self):
        """
        Print avaliable commands
        """
        print("Avaliable commands")
        print(" add <id> <material> <time> <priority>       - add a job")
        print("list                                         - list all the jobs in queue")
        print("completed                                    - list all the jobs completed")
        print("cancel <job_id>                              - cancel a job")
        print("status                                       - shows simulator status")
        print("stats                                        - shows global summary")
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
            
            job = Job(id = job_id, material=material, est_time= estimate_time, priority=priority)
            await self.sim.add_job(job = job)

            print(f"Added Job {job_id}: {material}, {estimate_time}s with {priority} priority")
        except ValueError as e:
            print(f"Error: {e}")
    
    def cmd_completed(self) -> None:
        """Print all the jobs completed"""

        print("\n Jobs in Queue: ")
        records = self.sim.get_job_records()
        records = sorted(records, key=lambda r:r.end_time)
        if not records:
            return
        print("\nJob Records: ")
        print(f"ID      Priority        Duration        Status      Wait Time       RunTime")
        print("-" * 80)
        for record in records:
            print(f"{record.job_id}     {record.priority}       {record.duration:.3f}       {record.status}     {(record.start_time-record.created_time):.3f}      {(record.end_time -record.start_time):.3f}")
        print()
        print("-" * 80)

    def cmd_list(self) -> None:
        """Print all the jobs in queue"""
        print("\n Jobs in Queue: ")
        active_jobs = self.sim.get_active_jobs()
        if not active_jobs:
            return
        print("\nJob Records: ")
        print(f"ID      Material        Estimated Time        Status")
        print("-" * 50)
        for job in active_jobs:
            print(f"{job.id}     {job.material}       {job.est_time:.3f}       {job.status}")
        print()
        print("-" * 50)
    
    def cmd_cancel(self, args: list[str]) -> None:
        if len(args) != 1:
            print("Usage: cancel <job_id>")
            return
        
        sucess = self.sim.cancel_job(args[0])
        if sucess:
            print(f"Sucess canceling the job {args[0]}")
        else:
            print(f"Was not possible to cancel {args[0]}")

    def cmd_records(self) -> None:
        """Shows global statistics"""
        stats = self.sim.get_global_stats()
        
        print("\n" + "=" * 60)
        print("GLOBAL SUMMARY")
        print("=" * 60 + "\n")
        print(f"Simulated Time: {stats['total_simulation_time']:.3f}")
        print(f"Jobs Completed: {stats['total_completed']}")
        print("\nWait Metrics")
        print(f"Average Wait Time: {stats['avg_wait_time']}")
        print(f"Median Wait Time: {stats['median_wait_time']}")
        print(f"\nThroughput: {stats['throughput']:.3f} jobs/sec")

        print("\nPRINTER UTILIZATION")
        print("=" * 60 + "\n")
        for p in stats['printer_utilization']:
            print(f"Printer {p['printer_id']}: {p['utilization_percent']} %")
        print("="*60 + "\n")
    
    def cmd_status(self) -> None:
        """Shows current simulation status including the queue current status"""
        stats = self.sim.get_queue_stats()
        print("\nCurrent Status:")
        print(f" Number of Printers: {self.sim.num_printers}")
        print(f" Time Scale: {self.sim.time_scale}")
        print(f" Jobs in queue: {stats['active_jobs']}")
        print(f" Jobs Completed: {stats['completed']}")
        print(f" Jobs Cancelled: {stats['canceled']}")
    
    async def run(self) -> None:
        """ Main CLI Loop"""
        self.running = True
        print("=" * 60)
        print("3D Printing Queue Simulator")
        print("=" * 60)
        self.cmd_help()

        while self.running:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "> "
                )
                parts = user_input.strip().split()
                if not parts:
                    continue
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd == "add":
                    await self.cmd_add(args)
                elif cmd == "list":
                    self.cmd_list()
                elif cmd == "completed":
                    self.cmd_completed()
                elif cmd == "cancel":
                    self.cmd_cancel(args)
                elif cmd == "status":
                    self.cmd_status()
                elif cmd == "stats":
                    self.cmd_records()
                elif cmd == "help":
                    self.cmd_help()
                elif cmd == "stop":
                    print("\nStopping...")
                    self.running = False
                else:
                    print(f"Unknown: {cmd}")

            except KeyboardInterrupt:
                print("Use stop to exit")
            except Exception as e:
                print(f"Error: {e}")

async def main():
    if len(sys.argv) > 1:
        """Process json file only"""
        json_file = sys.argv[1]
        sim = Simulator(num_printers=3, time_scale=0.1)
        await sim.start()

        jobs = load_jobs_from_json(json_file)
        if jobs:
            await sim.add_jobs(jobs)
            print(f"Simulator running with {sim.num_printers} printers")

            cli = CLI(sim)
            await cli.run()

        await sim.stop()
    else:
        """Process input data"""
        sim = Simulator(num_printers=2, time_scale=0.1)
        print(f"Simulator running with {sim.num_printers} printers")
        await sim.start()

        cli = CLI(sim)
        await cli.run()

        await sim.stop()

if __name__ == "__main__":
    asyncio.run(main())




