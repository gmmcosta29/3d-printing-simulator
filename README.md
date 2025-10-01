# 3D Printing Simulator

## Requirements

# Install requirements:
pip install -r requirements.txt


## Time scale
To decrease simulated time the time_scale input is used in all in all processing sleeps(simulate real processing time)

## Data Models

# JobStatus
 Enum for diferent states of a job
    QUEUE = "queue"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELED = "canceled"

# Job
Represents a 3D printing job, is utilized for each job that is created
Atributtes:
    id: Job identifier
    material: Material utilized make the job (PLA, ABS, PETG, etc)
    est_time: Estimated time in Seconds
    priority: Job priority
    created_at: Timestamp when the job was created
    started_at: Timestamp when the job was started
    finished_at: Timestamp when the job was finished
    status: Current status of the job

# PrioritizedJob 
Wrapper class to ordering jobs by priority

This ensures stable ordering
    1 - Priority
    2 - FIFO Counter (When the job was inserted in the FIFO list)

# Printer
Represents a 3D Printer
Attributes:
    id: Unique printer identifier
    current_job: Job currently being processed
    total_busy_time: Total time working

# Job Record
Lightweight record of a completed job, only has the data needed for logs

## Source Files

# cli.py
Command Line Interface that manages the entire application
# database.py 
Class that manages persistance storage using SQLite3
# json_manager.py
File that has methods such as generate final processing report and reads from json file and export a list of jobs
# models.py
Dataclasses of Job, JobStatus, PrioritizedJob and Printer
# queue_manager.py
ThreadSafe queue for all jobs in
# visualizer.py
Create an image of each printer utilization

## Execution

# Simulator in Real Time
python cli.py

# Simulator processing a testcase, the simulation will continue in real time
python cli.py --input sample_jobs.json --printers --time-scale 0.01


## Testings

# Create Random Sample textes (This will create a randomized test case with 10 jobs) in /test_data 
python scripts/create_test_case.py 

# Run all tests
pytest -q 

# Run a specific test 
pytest test/simulator.py::test_load_balancing