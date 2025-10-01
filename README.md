# 3D Printing Simulator

# Requirements
Python 3.9+
pip
pytest

## Install requirements:
pip install -r requirements.txt


# Time scale
The time_scale parameter accelerates simulation:

- time_scale=1.0 -> Real-time (10s job takes 10s). 
- time_scale=0.1 -> 10x faster (10s job takes 1s). 
- time_scale=0.01 -> 100x faster (10s job takes 0.1s). 

Default: 0.1 in CLI, 0.1 in tests

# Data Models

## JobStatus
Job lifecycle states:

- QUEUE - Waiting to be processed. 
- RUNNING - Currently being printed. 
- COMPLETED - Successfully finished. 
- CANCELED - Cancelled before completion. 

## Job
Represents a 3D printing job, is utilized for each job that is created

    id: Unique job identifier
    material: Printing material (PLA, ABS, PETG, TPU, etc)
    est_time: Estimated time in seconds
    priority: Job priority (0 = highest, lower is better)
    created_at: Creation timestamp
    started_at: Start timestamp
    finished_at: Completion timestamp
    status: Current JobStatus

## PrioritizedJob 
Wrapper class to ordering jobs by priority

This ensures stable ordering.
##  
    1 - Priority 
    2 - FIFO Counter (When the job was inserted in the FIFO list)

## Printer
Represents a 3D Printer


    id: Unique printer identifier
    current_job: Job currently being processed
    total_busy_time: Total time working

## Job Record
Lightweight record of a completed job, only has the data needed for logs
    job_id: Unique job identifier
    start_time: Timestamp of job initialization 
    created_time: Timestamp of creation
    end_time: Timestamp of job completion
    duration: Diference betwen end_time and start time
    status: Job end status
    priority: Job priority

# Source Files

## cli.py
Command Line Interface that manages the entire application
## database.py 
Class that manages persistance storage using SQLite3
## json_manager.py
File that has methods such as generate final processing report and reads from json file and export a list of jobs
## models.py
Dataclasses of Job, JobStatus, PrioritizedJob and Printer
## queue_manager.py
ThreadSafe queue for all jobs in
## visualizer.py
Create an image of each printer utilization

# Execution

## Simulator in Real Time
python src/cli.py

# SImulator with a Test Case
python src/cli.py --input test_data/sample_jobs.json

## Simulator processing a testcase, with a costum configuration
python src/cli.py --input test_data/sample_jobs.json --printers 3 --time-scale 0.01

# Cli Commands
- add <id> <material> <time> <priority> - Add a job. 
- list - List all jobs in queue. 
- completed - List all completed jobs. 
- cancel <job_id> - Cancel a job. 
- status - Shows simulator status. 
- stats - Shows global summary. 
- help - Shows help. 
- stop - Stops the simulator and exits. 

# Testings

## Create Random Sample text (This will create a randomized test case with 10 jobs) in /test_data 
python scripts/create_test_case.py 

## Run all tests
pytest -q 

## Run a specific test 
pytest test/simulator.py::test_load_balancing


# OUTPUT
After simulation, files are saved on:
- job_history.db - SQLite database
- job_report_YYYYMMDD_HHMMSS.json - JSON report
- printer_utilization_YYYYMMDD_HHMMSS.png - Printer utilization chart
- simulation.log - Event Log