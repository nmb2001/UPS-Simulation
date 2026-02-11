import mysql.connector
import random

def reset_and_distribute_ulds():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ups_sim"
    )
    cursor = db.cursor()

    # 1. Define your active airports
    locations = ['SDF', 'ONT', 'ATL', 'EWR', 'PHX']

    # 2. Fetch all ULD IDs and their Tare weights
    cursor.execute("SELECT uld_id, min_weight FROM uld_inventory")
    ulds = cursor.fetchall()

    print(f"Distributing {len(ulds)} ULDs across network...")

    for uld_id, min_weight in ulds:
        # Assign a random starting location
        current_loc = random.choice(locations)

        # UPDATED: We now clear parent_plane and position_on_plane
        # We also set status to 'Empty' so they can be 'Loaded' later
        cursor.execute("""
            UPDATE uld_inventory 
            SET current_location = %s, 
                destination = NULL, 
                current_weight = %s,
                status = 'Empty',
                parent_plane = NULL,
                position_on_plane = NULL
            WHERE uld_id = %s
        """, (current_loc, min_weight, uld_id))

    db.commit()
    print("Redistribution Complete: All ULDs unlinked from aircraft.")
    cursor.close()
    db.close()

if __name__ == "__main__":
    reset_and_distribute_ulds()