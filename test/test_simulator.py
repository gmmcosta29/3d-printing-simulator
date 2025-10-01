import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Job
from simulator import Simulator
from json_manager import load_jobs_from_json

#Tests will folow a 10%

@pytest_asyncio.fixture
async def one_printer_sim():
    """Fixture for one printer"""
    sim = Simulator(num_printers=1, time_scale=0.1)
    await sim.start()
    yield sim
    await sim.stop()

@pytest_asyncio.fixture
async def two_printer_sim():
    """Fixture for two printer"""
    sim = Simulator(num_printers=2, time_scale=0.1)
    await sim.start()
    yield sim
    await sim.stop()

@pytest_asyncio.fixture
async def three_printer_sim():
    """Fixture for three printer"""
    sim = Simulator(num_printers=3, time_scale=0.1)
    await sim.start()
    yield sim
    await sim.stop()

@pytest.mark.asyncio
async def test_priority_ordering(one_printer_sim):
    """Test: Simple sorting job with one printer"""
    sim = one_printer_sim

    jobs = [
        Job("J1", "PLA", 10, priority=2),
        Job("J2", "PETG", 10, priority=1),
        Job("J3", "TPU", 10, priority=0)
    ]

    await sim.add_jobs(jobs) 
    await asyncio.sleep(3.5) #3 jobs * 0.1 (time_scale) / 1 (printers)  = 3s + .5 tolerance

    records = sim.get_job_records()
    order = [r.job_id for r in sorted(records, key=lambda x: x.end_time)]

    assert order == ['J3', 'J2', 'J1'], f"Expected ['J3', 'J2', 'J1'], got {order}"
    assert len(records) == 3

@pytest.mark.asyncio
async def test_cancel_nonexistance_job(one_printer_sim):
    """Test: Cancelation of a job that doesnt exist"""
    sim = one_printer_sim

    assert sim.cancel_job("NonExistance") == False 

@pytest.mark.asyncio
async def test_cancel_already_cancelled(one_printer_sim):
    """Test: Cancelation of the same job"""
    sim = one_printer_sim

    job = Job("J1","PLA", 10, priority=1)
    await sim.add_job(job)

    assert sim.cancel_job("J1") == True 
    assert sim.cancel_job("J1") == False 

@pytest.mark.asyncio
async def test_load_balancing():
    """Test: balancing a load for 3 printers and FIFO order"""
    sim = Simulator(num_printers=3, time_scale=0.1)
    
    jobs = [Job(f"J{i}", "PLA", 10, priority=1) for i in range(12)]

    await sim.start()
    await sim.add_jobs(jobs)
    await asyncio.sleep(4.5) #12 jobs * 10 sec * 0.1 (time_scale) / 3 (printers)  = 4s + .5 tolerance 
    await sim.stop()

    stats = sim.get_global_stats()
    records = sorted(sim.get_job_records(), key= lambda x: x.end_time)
    order = [r.job_id for r in records]

    assert stats['throughput'] > 2 # Expected is 3, but with over head and context switching give 1 of tolerance
    assert stats['total_completed'] == 12

    utilization = [p['utilization_percent'] for p  in stats['printer_utilization']]
    assert(all(u > 50 for u in utilization))
    assert order == [f"J{i}" for i in range(12)] # Test FIFO


@pytest.mark.asyncio
async def test_mixed_priorities(two_printer_sim):
    """ Test:  Mix priorities with multiple printers """
    sim = two_printer_sim

    jobs = [
        Job("J1", "PLA", 10, priority=2),
        Job("J2", "PETG", 10, priority=2),
        Job("J3", "TPU", 10, priority=0),
        Job("J4", "ABS", 10, priority=1)
    ]
    await sim.add_jobs(jobs)
    await asyncio.sleep(4.5) # 4 jobs  * 10 sec * 0.1 (time_scale) / 2 (printers)  = 2s + .5 tolerance
    
    records = sorted(sim.get_job_records(), key=lambda x: x.end_time)

    assert 'J3' == records[0].job_id # J3 is the first job completed
    assert 'J4' == records[1].job_id # J4 is the second job completed

@pytest.mark.asyncio
async def test_job_validation(two_printer_sim):
    """Test: Data validation"""

    with pytest.raises(ValueError):
        Job("J1", "PLA", -10, priority=1) # Negative Time

    with pytest.raises(ValueError):
        Job("J1", "PLA", 0, priority=1) #Time is zero

    with pytest.raises(ValueError):
        Job("J1", "PLA", 10, priority = -1) #Negative priority

@pytest.mark.asyncio
async def test_stats_no_jobs(one_printer_sim):
    """Test: Test if stats functions still work with no jobs"""
    sim = one_printer_sim

    await asyncio.sleep(0.2) # creation overhead

    stats = sim.get_global_stats()
    records = sim.get_queue_stats()

    assert records['active_jobs'] == 0
    assert records['completed'] == 0
    assert records['canceled'] == 0

    assert stats['avg_wait_time'] == 0
    assert stats['median_wait_time'] == 0
    assert stats['throughput'] == 0
    assert stats['total_completed'] == 0

    utilization = [p['utilization_percent'] for p  in stats['printer_utilization']]
    assert(all(u == 0 for u in utilization))

@pytest.mark.asyncio
async def test_bulk_processing():
    """Test: Simulator in bulk """
    sim = Simulator(num_printers=3, time_scale=0.01)
    
    jobs = [Job(f"J{i}", "PLA", 10, priority=1) for i in range(3000)]

    await sim.start()
    await sim.add_jobs(jobs)
    await asyncio.sleep(102) #3000 jobs * 10s * 0.01 (time_scale) / 3 (printers)  = 100s + 2 sec tolerance 
    await sim.stop()
    
    stats = sim.get_global_stats()
    print(stats)
    assert stats['total_completed'] == 3000

    
@pytest.mark.asyncio
async def test_random_json_casetest(two_printer_sim):
    """Test: Random generated casetest"""
    sim = two_printer_sim

    jobs = load_jobs_from_json('test_data/sample_input.json')

    await sim.add_jobs(jobs) 
    await asyncio.sleep(14.5) #264 total_time * 0.1 (time_scale) / 2  (printers)  = 13,2s + 1,3s tolerance

    assert len(sim.get_job_records()) == 10


@pytest.mark.asyncio
async def test_cancelation(two_printer_sim):
    """ Test:  Job cancelation changes them from active jobs to records """
    sim = two_printer_sim

    jobs = [
        Job("J1", "PLA", 10, priority=2),
        Job("J2", "PETG", 10, priority=2),
        Job("J3", "TPU", 10, priority=0),
        Job("J4", "ABS", 10, priority=1)
    ]

    await sim.add_jobs(jobs)

    success = sim.cancel_job("J2")
    assert success == True

    active = sim.get_active_jobs()
    
    active_ids = [j.id for j in active]

    records = sim.get_job_records()
    record_ids = [r.job_id for r in records]

    assert "J2" not in active_ids
    assert "J2" in record_ids
    assert len([r for r in records if r.status == "canceled"]) == 1


@pytest.mark.asyncio
async def test_json_error_handling():
    """Test: JSON loading handles errors"""

    jobs = load_jobs_from_json("test.json")
    assert jobs == []
