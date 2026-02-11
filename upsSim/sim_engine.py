import time
import threading
from dispatch import FlightDispatcher
from flight_ops import FlightOperations
import load_cargo


class SimulationEngine(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self.cycle_interval = 60  # Set your cycle time here
        self.next_run_time = time.time() + self.cycle_interval

        self.dispatcher = FlightDispatcher()
        self.ops = FlightOperations()

    def get_seconds_until_next_cycle(self):
        remaining = int(self.next_run_time - time.time())
        return max(0, remaining)

    def run(self):
        while self.running:
            print(f"--- CYCLE START: {time.strftime('%H:%M:%S')} ---")
            try:
                self.ops.process_flights()
                load_cargo.simulate_cargo_sorting()
                self.dispatcher.auto_dispatch_waves()
            except Exception as e:
                print(f"Engine Error: {e}")

            # Calculate next run time before sleeping
            self.next_run_time = time.time() + self.cycle_interval
            time.sleep(self.cycle_interval)