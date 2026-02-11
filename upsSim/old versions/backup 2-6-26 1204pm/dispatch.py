import mysql.connector
import json
import physics
from models import Aircraft, ULD
from datetime import datetime, timedelta


class FlightDispatcher:
    def __init__(self):
        # Load the physical aircraft layouts (arms, allowed types, max floor weights)
        with open('aircraft_data.json', 'r') as f:
            self.ac_configs = json.load(f)['aircraft']

    def auto_dispatch_waves(self):
        db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim", autocommit=True)
        cursor = db.cursor(dictionary=True)

        # 1. Identify valid Routes (Hotspots)
        cursor.execute("""
            SELECT current_location, destination, COUNT(*) as qty
            FROM uld_inventory WHERE status = 'Loaded' AND parent_plane IS NULL
            GROUP BY current_location, destination
        """)
        routes = cursor.fetchall()

        if not routes:
            print("🔍 Dispatcher: No 'Loaded' cargo found in uld_inventory.")
            db.close()
            return

        for route in routes:
            print(f"📍 Route Found: {route['current_location']} -> {route['destination']} ({route['qty']} cans)")

            # 2. Find an available plane at the origin
            cursor.execute("SELECT * FROM fleet WHERE current_location = %s AND status = 'Parked' LIMIT 1",
                           (route['current_location'],))
            p_row = cursor.fetchone()

            if not p_row:
                print(f"❌ No 'Parked' aircraft available at {route['current_location']}")
                continue

            config = next((c for c in self.ac_configs if c['aircraft_type'] == p_row['aircraft_type']), None)
            if not config:
                print(f"❌ Critical: No JSON config found for {p_row['aircraft_type']}")
                continue

            plane = Aircraft(p_row, config)

            # 3. Fetch all cargo for this route
            cursor.execute("""
                SELECT * FROM uld_inventory 
                WHERE current_location = %s AND destination = %s 
                AND status = 'Loaded' AND parent_plane IS NULL
            """, (route['current_location'], route['destination']))
            available_cargo = [ULD(row) for row in cursor.fetchall()]

            # 4. Fill positions
            for pos_id, pos_data in plane.uld_layout.items():
                for i, uld in enumerate(available_cargo):
                    if uld.type in pos_data['allowed_cans'] and uld.current_weight <= pos_data['max_weight']:
                        plane.manifest[pos_id] = uld
                        available_cargo.pop(i)
                        break

            # 5. Physics Check and DB Update
            is_safe, cog = plane.calculate_balance()
            if is_safe and plane.manifest:
                self._dispatch_plane(plane, route['destination'], cursor)
            else:
                print(f"⚠️ {plane.type} #{plane.id} rejected. Safe: {is_safe}, Load count: {len(plane.manifest)}")

        db.close()

    def _dispatch_plane(self, plane, dest, cursor):
        """Finalizes the flight in the database."""
        travel_time = physics.calculate_flight_time(plane.location, dest, plane.cruise_speed)
        arr_time = datetime.now() + timedelta(hours=travel_time)

        # Update the Aircraft status
        cursor.execute(
            "UPDATE fleet SET status='Scheduled', destination=%s, departure_time=%s, arrival_time=%s WHERE aircraft_id=%s",
            (dest, datetime.now(), arr_time, plane.id))

        # Link the ULDs to the plane and record their position (1L, 2R, etc.)
        for pos_id, uld in plane.manifest.items():
            cursor.execute(
                "UPDATE uld_inventory SET parent_plane=%s, position_on_plane=%s, status='In-Transit' WHERE uld_id=%s",
                (plane.id, pos_id, uld.id))

        print(
            f"✈️ Dispatched {plane.type} (#{plane.id}) to {dest} with {len(plane.manifest)} ULDs. CoG: {plane.calculate_balance()[1]}")