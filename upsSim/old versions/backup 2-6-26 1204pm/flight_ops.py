import mysql.connector
from datetime import datetime

class FlightOperations:
    @staticmethod
    def process_flights():
        db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim", autocommit=True)
        cursor = db.cursor(dictionary=True)
        now = datetime.now()

        # Takeoffs
        cursor.execute("UPDATE fleet SET status = 'In-Transit' WHERE status = 'Scheduled' AND departure_time <= %s", (now,))

        # Landings
        cursor.execute("SELECT aircraft_id, destination FROM fleet WHERE status = 'In-Transit' AND arrival_time <= %s", (now,))
        for row in cursor.fetchall():
            # Reset Plane
            cursor.execute("UPDATE fleet SET current_location=%s, status='Parked', destination=NULL, departure_time=NULL, arrival_time=NULL WHERE aircraft_id=%s",
                           (row['destination'], row['aircraft_id']))
            # Reset Cargo
            cursor.execute("UPDATE uld_inventory SET current_location=%s, parent_plane=NULL, position_on_plane=NULL, status='Arrived' WHERE parent_plane=%s",
                           (row['destination'], row['aircraft_id']))
            print(f"🛬 Landed: {row['aircraft_id']} at {row['destination']}")
        db.close()