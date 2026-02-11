import mysql.connector
from datetime import datetime, timedelta


def auto_dispatch_waves():
    db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
    cursor = db.cursor(dictionary=True)

    # 1. Identify airports that have cargo waiting but not assigned to a plane
    cursor.execute("""
        SELECT current_location, destination, COUNT(*) as qty 
        FROM uld_inventory WHERE status = 'Loaded' AND parent_plane IS NULL
        GROUP BY current_location, destination HAVING qty >= 5
    """)
    hotspots = cursor.fetchall()

    wave_offset = 0
    for spot in hotspots:
        # 2. Find a Parked plane at this location
        cursor.execute("""
            SELECT aircraft_id, aircraft_type FROM fleet 
            WHERE current_location = %s AND status = 'Parked' LIMIT 1
        """, (spot['current_location'],))

        plane = cursor.fetchone()
        if plane:
            # 3. Create the 'Wave' timing (Example: stagger flights by 15 mins)
            departure_time = datetime.now() + timedelta(minutes=wave_offset)
            arrival_time = departure_time + timedelta(minutes=120)  # 2-hour flight

            print(f"📦 Loading {spot['qty']} ULDs onto {plane['aircraft_type']} ({plane['aircraft_id']})")
            print(f"⏰ Scheduled Wave: Departure at {departure_time.strftime('%H:%M')}")

            # 4. Update the Fleet (Mark as Scheduled)
            cursor.execute("""
                UPDATE fleet SET status = 'Scheduled', destination = %s, 
                departure_time = %s, arrival_time = %s 
                WHERE aircraft_id = %s
            """, (spot['destination'], departure_time, arrival_time, plane['aircraft_id']))

            # 5. Load the ULDs (Link to this specific aircraft_id)
            cursor.execute("""
                UPDATE uld_inventory SET parent_plane = %s, status = 'Loaded'
                WHERE current_location = %s AND destination = %s AND parent_plane IS NULL
                LIMIT %s
            """, (plane['aircraft_id'], spot['current_location'], spot['destination'], spot['qty']))

            wave_offset += 15  # Next plane in the wave goes 15 mins later

    db.commit()
    db.close()