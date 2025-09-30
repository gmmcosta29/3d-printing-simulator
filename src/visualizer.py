import matplotlib.pyplot as plt
from pathlib import Path

class Visualizer:
    """Manages job history persistence"""

    def __init__(self, db_path: str = "logs"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
    def plot_printer_utilization(self, stats: dict) -> None:
        printer_util = stats['printer_utilization']

        printer_ids = [p['printer_id'] for p in printer_util]
        printer_utilization = [p['utilization_percent'] for p in printer_util]

        plt.figure(figsize=(10, 6))

        bars = plt.bar(printer_ids,printer_utilization)

        plt.xlabel('Printer')
        plt.ylabel('Utilization %')
        plt.ylim(1,110)
        plt.tight_layout()
        plt.show()
