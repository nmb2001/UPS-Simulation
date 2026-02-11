import time
import mysql.connector
import dispatch
import flight_ops
import load_cargo


def display_manifest(aircraft_id):
    """Displays the current load of a specific plane."""
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT uld_id, uld_type, current_weight, position_on_plane FROM uld_inventory WHERE parent_plane = %s ORDER BY position_on_plane",
        (aircraft_id,))
    rows = cursor.fetchall()

    if rows:
        print(f"\n📦 DECK MANIFEST FOR AIRCRAFT {aircraft_id}:")
        print(f"{'POS':<6} | {'ULD ID':<10} | {'TYPE':<6} | {'WEIGHT':<8}")
        print("-" * 40)
        for r in rows:
            print(f"{r['position_on_plane']:<6} | {r['uld_id']:<10} | {r['uld_type']:<6} | {r['current_weight']:<8}")
    db.close()


def run_simulation():
    dispatcher = dispatch.FlightDispatcher()
    print("🚀 UPS GLOBAL OPERATIONS SIMULATOR: OOP ENGINE ONLINE")

    while True:
        print(f"\n--- [Tick: {time.ctime()}] ---")
        try:
            # 2. CALL the sorting function to turn 'Empty' cans into 'Loaded'
            load_cargo.simulate_cargo_sorting()

            # 3. Dispatch the planes
            dispatcher.auto_dispatch_waves()

            # 4. Display the manifest for your Airbus (107) or A300 (101)
            display_manifest(121)

            # 5. Process flight movements
            flight_ops.process_flights()

        except Exception as e:
            print(f"❌ System Error: {e}")

        print("\nWaiting for next sort cycle...")
        time.sleep(120)


if __name__ == "__main__":
    run_simulation()