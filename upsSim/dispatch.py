import mysql.connector
import json
import physics
from models import Aircraft, ULD
from datetime import datetime, timedelta

# This file loads the planes with cans that are assigned to the same
# destination as the planes and makes sure it can take off properly.
class FlightDispatcher:
    def __init__(self):
        with open('aircraft_data.json', 'r') as f:
            self.ac_configs = json.load(f)['aircraft']

    def auto_dispatch_waves(self):
        db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim", autocommit=True)
        cursor = db.cursor(dictionary=True)

        # Identify routes with cargo
        cursor.execute("""
            SELECT current_location, destination 
            FROM uld_inventory WHERE status = 'Loaded' AND parent_plane IS NULL
            GROUP BY current_location, destination
        """)
        routes = cursor.fetchall()

        for route in routes:
            # Finds all planes with destination
            cursor.execute("SELECT * FROM fleet WHERE current_location = %s AND status = 'Parked'",
                           (route['current_location'],))
            available_planes = cursor.fetchall()

            for p_row in available_planes:
                config = next((c for c in self.ac_configs if c['aircraft_type'] == p_row['aircraft_type']), None)
                if not config: continue

                plane = Aircraft(p_row, config)

                # Gathers cans that are viable
                cursor.execute("""
                    SELECT * FROM uld_inventory 
                    WHERE current_location = %s AND destination = %s 
                    AND status = 'Loaded' AND parent_plane IS NULL
                """, (route['current_location'], route['destination']))
                available_cargo = [ULD(row) for row in cursor.fetchall()]

                # Loads the plane
                for pos_id, pos_data in plane.uld_layout.items():
                    for i, uld in enumerate(available_cargo):
                        if uld.type in pos_data['allowed_cans'] and uld.current_weight <= pos_data['max_weight']:
                            plane.manifest[pos_id] = uld
                            available_cargo.pop(i)
                            break

                # Determines if plane can physically fly with this load (refers to aircraft_data.json)
                is_safe, cog = plane.calculate_balance()
                if is_safe and plane.manifest:
                    # Each flight takes 2 minutes in this simulation
                    self._dispatch_plane(plane, route['destination'], cursor, flight_minutes=2)
        db.close()

    def _dispatch_plane(self, plane, dest, cursor, flight_minutes=2):
        dep_time = datetime.now()
        arr_time = dep_time + timedelta(minutes=flight_minutes)

        cursor.execute(
            "UPDATE fleet SET status='Scheduled', destination=%s, departure_time=%s, arrival_time=%s WHERE aircraft_id=%s",
            (dest, dep_time, arr_time, plane.id))

        for pos_id, uld in plane.manifest.items():
            cursor.execute(
                "UPDATE uld_inventory SET parent_plane=%s, position_on_plane=%s, status='In-Transit' WHERE uld_id=%s",
                (plane.id, pos_id, uld.id))
        print(f"Plane Dispatched {plane.type} (#{plane.id}) to {dest} with {len(plane.manifest)} ULDs.")