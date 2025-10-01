
import json 
import random
from pathlib import Path
from datetime import datetime


MATERIALS = ["PLA", "PETG", "ABS", "TPU"]

def create_test_job(count: int) -> list[dict]:
    jobs = []
    for i in range(count):
        jobs.append({
            "id": f"P{i}",
            "material": random.choice(MATERIALS),
            "est_time": random.randint(10,40),
            "priority": random.randint(0,5)
        })
    return jobs


def main():
    jobs = create_test_job(10)
    data = {"jobs": jobs}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_case_report_{timestamp}.json"

    dirpath = Path("test_data")
    dirpath.mkdir(exist_ok=True)

    filepath = dirpath / filename

    with open(filepath,'w', encoding='utf-8') as f:
        json.dump(data,f, indent=2)
            
if __name__ == "__main__":
    main()