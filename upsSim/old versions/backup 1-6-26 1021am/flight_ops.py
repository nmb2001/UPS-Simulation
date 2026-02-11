import mysql.connector
from datetime import datetime


def process_flights():
    db = mysql.connector.connect(
        host="localhost", user="root", password="", database="ups_sim"
    )
    cursor = db.cursor(dictionary=True)
    now = datetime.now()

    # --- STEP 1: Handle Landings ---
    # Find planes that are flying but should have arrived by now
    cursor.execute("""
        SELECT aircraft_id, destination FROM fleet 
        WHERE status = 'In-Transit' AND arrival_time <= %s
    """, (now,))

    arrived_planes = cursor.fetchall()

    for plane in arrived_planes:
        pid = plane['aircraft_id']
        dest = plane['destination']

        print(f"✈️ Flight {pid} has landed at {dest}.")

        # Update the Plane: Set location to destination, clear arrival time, set status to Parked
        cursor.execute("""
            UPDATE fleet 
            SET current_location = %s, status = 'Parked', 
                destination = NULL, arrival_time = NULL 
            WHERE aircraft_id = %s
        """, (dest, pid))

        # Update the Cargo: Move all ULDs assigned to this plane to the new airport
        cursor.execute("""
            UPDATE uld_inventory 
            SET current_location = %s, parent_plane = NULL, status = 'Arrived'
            WHERE parent_plane = %s
        """, (dest, pid))

    db.commit()
    db.close()


if __name__ == "__main__":
    process_flights()