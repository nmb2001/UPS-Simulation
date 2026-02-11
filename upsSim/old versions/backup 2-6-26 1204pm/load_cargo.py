import mysql.connector
import random


def simulate_cargo_sorting():
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
    cursor = db.cursor(dictionary=True)

    # 1. Define Hubs and Destinations
    airports = ['SDF', 'ONT', 'ATL', 'EWR', 'PHX']

    # 2. Find Empty ULDs
    cursor.execute("SELECT uld_id, uld_type, min_weight FROM uld_inventory WHERE status = 'Empty'")
    empty_ulds = cursor.fetchall()

    print(f"📦 Sorting {len(empty_ulds)} ULDs into the loading docks...")

    for uld in empty_ulds:
        # Pick a destination that isn't the current location (handled in the loop below)
        # For this simulation, let's just make everything go to a random different airport
        possible_dests = [a for a in airports if a != uld['current_location']]
        dest = random.choice(possible_dests)

        # Randomize weight based on ULD type (staying under the 5000lb aircraft floor limit)
        # We give it at least min_weight (tare) + some cargo
        cargo_weight = random.randint(2000, 4800)

        cursor.execute("""
            UPDATE uld_inventory 
            SET status = 'Loaded', 
                destination = %s, 
                current_weight = %s 
            WHERE uld_id = %s
        """, (dest, cargo_weight, uld['uld_id']))

    db.commit()
    print("✅ Sort Complete: ULDs are now 'Loaded' and staged for flight.")
    db.close()


if __name__ == "__main__":
    simulate_cargo_sorting()