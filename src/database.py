import sqlite3
from pathlib import Path
from queue_manager import JobRecord

class JobDatabase:
    """Manages job history persistence"""

    def __init__(self, db_path: str = "logs/job_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()

    def init_db(self) -> None:
        """Checks if database exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id  TEXT NOT NULL,
                    priority INTEGER,
                    status TEXT,
                    created_time REAL,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    wait_time REAL,
                    run_time REAL ,
                    simulation_timestamp REAL
                    )
                '''
        cursor.execute(query)
        conn.commit()
        conn.close()

    def save_jobs(self, records: list[JobRecord], simulation_time: float) -> int: 
        """Saves records to the SQL database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for record in records:
            if record.start_time > 0:
                wait_time = record.start_time - record.created_time
                run_time = record.end_time - record.start_time
            else:
                wait_time = 0
                run_time = 0
            query = '''
                    INSERT INTO job_history
                    (job_id, priority, status, created_time, start_time, end_time,
                    duration, wait_time, run_time, simulation_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            cursor.execute(query,(record.job_id,
                                  record.priority,
                                  record.status,
                                  record.created_time,
                                  record.start_time,
                                  record.end_time,
                                  record.duration,
                                  wait_time,
                                  run_time,
                                  simulation_time
                                  )
                            ) 
        conn.commit()
        conn.close()
        return len(records)