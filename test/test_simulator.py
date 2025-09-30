import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Job
from simulator import Simulator

@pytest_asyncio.fixture
async def single_printer_sim():
    sim = Simulator(num_printers=1, time_scale=0.1)
    await sim.start()
    yield sim
    await sim.stop()

@pytest.mark.asyncio
async def test_priority_ordering(single_printer_sim):
    sim = single_printer_sim

    jobs = [
        Job("J1", "PLA", 10, priority=2),
        Job("J2", "PETG", 10, priority=1),
        Job("J3", "TPU", 10, priority=0)
    ]

    await sim.add_jobs(jobs) 
    await asyncio.sleep(3.5) # 30 total secs * 0.1 time_scale = 3.0 secs 

    records = sim.get_job_records()
    order = [r.job_id for r in sorted(records, key=lambda x: x.end_time)]

    assert order == ['J3', 'J2', 'J1'], f"Expected ['J3', 'J2', 'J1'], got {order}"
    assert len(records) ==3


