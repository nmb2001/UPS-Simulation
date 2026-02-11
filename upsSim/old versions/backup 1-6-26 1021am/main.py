import time
import dispatch  # This is the script above
import flight_ops  # This is the landing script from earlier


def run_simulation():
    while True:
        print(f"--- [SYSTEM TICK: {time.ctime()}] ---")

        # Look for cargo and launch planes automatically
        dispatch.auto_dispatch()

        # Check if any flying planes have arrived
        flight_ops.process_flights()

        time.sleep(60)  # Run the check every minute


if __name__ == "__main__":
    run_simulation()