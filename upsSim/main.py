import time
import mysql.connector
import dispatch
import flight_ops
import load_cargo


def display_manifest(aircraft_id):
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u_id.uld_id, u_id.uld_type, u_id.current_weight, u_id.position_on_plane, f.aircraft_type, f.destination
        FROM uld_inventory u_id
        JOIN fleet f ON u_id.parent_plane = f.aircraft_id
        WHERE f.aircraft_id = %s 
        ORDER BY u_id.position_on_plane
    """, (aircraft_id,))
    rows = cursor.fetchall()

    if rows:
        print(f"\n AIRCRAFT {aircraft_id} ({rows[0]['aircraft_type']}) bound for {rows[0]['destination']}")
        print(f"{'POS':<6} | {'ULD ID':<10} | {'TYPE':<6} | {'WEIGHT':<8}")
        print("-" * 40)
        for r in rows:
            print(f"{r['position_on_plane']:<6} | {r['uld_id']:<10} | {r['uld_type']:<6} | {r['current_weight']:<8}")
    else:
        print(f"\n Aircraft {aircraft_id} is currently empty or not in flight.")
    db.close()


def run_simulation():
    dispatcher = dispatch.FlightDispatcher()
    ops = flight_ops.FlightOperations()  # Initialize the Class
    print(" UPS GLOBAL OPERATIONS SIMULATOR: LIVE TRACKING ENABLED")

    # Resets the simulation on startup
    load_cargo.reset_and_load_inventory()

    while True:
        print(f"\n--- [TIME: {time.strftime('%H:%M:%S')}] ---")
        try:
            # Processes takeoffs and landings
            ops.process_flights()

            # Dispatches new flights
            dispatcher.auto_dispatch_waves()

            # Allows you to view manifest by typing aircraft ID (ex: 114 [airbus] 342 [767])
            print("\nEnter Aircraft ID to view manifest (or press Enter to skip):")
            user_input = input(">> ")  # This will wait for you
            if user_input.isdigit():
                display_manifest(int(user_input))

        except Exception as e:
            print(f" System Error: {e}")

        print("\nCycling in 5 seconds...")
        time.sleep(5)


if __name__ == "__main__":
    run_simulation()