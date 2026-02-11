import mysql.connector
import random

def reset_and_load_inventory():
    """
    This is the entry point called by main.py.
    It links the two existing processes together.
    """
    print("Resetting and Loading Inventory...")
    fix_uld_type_mismatches()
    simulate_cargo_sorting()

def fix_uld_type_mismatches():
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim", autocommit=True)
    cursor = db.cursor()

    # Makes sure uld_type matches uld_id
    query = """
        UPDATE uld_inventory 
        SET uld_type = SUBSTRING(uld_id, 1, 3)
    """
    cursor.execute(query)
    print("Database Refreshed: ULD Types now match their ID prefixes.")
    db.close()


def simulate_cargo_sorting():
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim", autocommit=True)
    cursor = db.cursor(dictionary=True)

    airports = ['SDF', 'ONT', 'ATL', 'EWR', 'PHX']

    # Gets empty or arrived ULD
    cursor.execute("SELECT uld_id, current_location FROM uld_inventory WHERE status IN ('Empty', 'Arrived')")
    ulds = cursor.fetchall()

    if not ulds:
        db.close()
        return

    print(f"Sorting {len(ulds)} ULDs into the loading docks...")

    for uld in ulds:
        loc = uld['current_location'] if uld['current_location'] else random.choice(airports)
        dest = random.choice([a for a in airports if a != loc])

        # Prevents uld_type from being incorrect (ex: uld_id=AAD, uld_type=AAY)
        u_type = uld['uld_id'][:3]
        weight = random.randint(1500, 4500)

        cursor.execute("""
            UPDATE uld_inventory 
            SET current_location = %s, destination = %s, current_weight = %s, 
                uld_type = %s, status = 'Loaded', parent_plane = NULL, position_on_plane = NULL
            WHERE uld_id = %s
        """, (loc, dest, weight, u_type, uld['uld_id']))

    print(f"Sort Complete: {len(ulds)} ULDs ready for departure.")
    db.close()