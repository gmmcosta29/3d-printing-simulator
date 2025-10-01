import matplotlib.pyplot as plt
from pathlib import Path

class Visualizer:
    """Create visualization of printer utilization"""

    def __init__(self, dir: str = "logs"):
        self.output_dir = Path(dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def plot_printer_utilization(self, stats: dict) -> None:
        """Plot printer utilization"""
        printer_util = stats['printer_utilization']

        printer_ids = [f"Printer {p['printer_id']}" for p in printer_util]
        printer_utilization = [p['utilization_percent'] for p in printer_util]

        plt.figure(figsize=(10, 6))

        bars = plt.bar(printer_ids,printer_utilization)

        plt.xlabel('Printer')
        plt.ylabel('Utilization %')
        plt.ylim(1,110)
        plt.tight_layout()

        filepath = self.output_dir / 'printer_utilization.png'
        plt.savefig(filepath,dpi = 150, bbox_inches= 'tight')
        plt.close()
