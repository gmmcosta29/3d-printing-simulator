# 3D Printing Simulator

> Async job scheduler built with Python asyncio for managing multiple 3D printer processing jobs by priority

# Features
- **Priority Queue with FIFO** - Lower number = higher priority, FIFO with the same priority
- **Concurrent Processing** - N printers running async worker pool with asyncio, one coroutine per printer
- **REST API** - FastAPI endpoints for job management
- **Persistence** - SQLite database for job history tracking and a log file with event info
- **Graphical data** - Creates a graph of printer utilization

# Requirements
- Python 3.9+
- fastapi, uvicorn
- pytest, pytest-asyncio, pytest-cov
- matplotlib

## Install requirements:
pip install -r requirements.txt

# Quick Start

# CLI
    # Simulator in Real Time
    python src/cli.py

    # Simulator with a Test Case
    python src/cli.py --input test_data/sample_jobs.json

    # Simulator processing a testcase, with a custom configuration
    python src/cli.py --input test_data/sample_jobs.json --printers 3 --time-scale 0.01

## REST API
    cd src
    uvicorn api:app --reload

### API Endpoints
    POST /jobs            # Add new job
    GET /jobs             # List active jobs
    DELETE /jobs/{id}     # Cancel Job
    GET /stats            # Global statistics
    GET /health           # System status

# Key Design 
1. Async over Threads
- Used asyncio instead of threading for better I/O efficiency and lower overhead
- Each printer is an async task that pulls from shared queue
- Graceful shutdown with asyncio.gather(return_exceptions=True)

2. Priority Queue Implementation
- Counter ensures FIFO ordering with the same priority
- field(compare=False) on Job to avoid Job comparison issues

3. Job cancellation
- Only queue jobs can be cancelled(not running jobs)
- Cancelled jobs moved to records with status tracking
- No locks needed - single threaded API/CLI context

# Time scale
The time_scale parameter accelerates simulation:
- **time_scale=1.0** -> Real-time (10s job takes 10s). 
- **time_scale=0.1** -> 10x faster (10s job takes 1s). 
- **time_scale=0.01** -> 100x faster (10s job takes 0.1s). 

Default: 0.1 in CLI, 0.1 in tests

# Project Structure

## SRC
- **api.py**            -> FastAPI REST endpoints with lifespan management
- **database.py**       -> Class that manages persistence storage using SQLite3
- **cli.py**            -> Command Line Interface that manages the entire application
- **simulator.py**      -> Core async engine with worker pool pattern
- **queue_manager.py**  -> Thread-Safe queue for all jobs in
- **json_manager.py**   -> File that has methods such as generate final processing report and reads from json file and export a list of jobs
- **models.py**         -> Dataclasses of Job, JobStatus, PrioritizedJob and Printer
- **visualizer.py**     ->Create an image of each printer utilization



# CLI Commands
- add <id> <material> <time> <priority>     - Add a job
- list                                      - List all jobs in queue
- completed                                 - List all completed jobs
- cancel <job_id>                           - Cancel a job
- status                                    - Shows simulator status
- stats                                     - Shows global summary
- help                                      - Shows help
- stop                                      - Stops the simulator and exits

# Testings

**Coverage**: 18 tests, 92% code coverage on core logic

    # Run all tests
    pytest -q 

    # With coverage report
    pytest test/ --cov=src --cov-report=html

    # Create Random Sample text (This will create a randomized test case with 10 jobs) in /test_data 
    python scripts/create_test_case.py 

    # Run a specific test 
    pytest test/simulator.py::test_load_balancing


# Output Files
After simulation, files are saved on logs/:
- job_history.db - SQLite database
- job_report_YYYYMMDD_HHMMSS.json - JSON report
- printer_utilization_YYYYMMDD_HHMMSS.png - Printer utilization chart
- simulation.log - Event Log