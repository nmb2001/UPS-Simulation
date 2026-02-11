import mysql.connector
import random

conn = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS fleet")
cursor.execute("""
    CREATE TABLE fleet (
        aircraft_id INT PRIMARY KEY,
        aircraft_type VARCHAR(50) NOT NULL,
        current_location VARCHAR(10),
        main_deck_positions INT,
        p_sec_f INT,
        p_sec_r INT,
        max_payload INT,
        fuel_capacity INT,
        max_range INT,
        cruise_speed INT,
        status VARCHAR(50) DEFAULT 'Parked',
        departure_time DATETIME,
        arrival_time DATETIME,
        origin VARCHAR(10),
        destination VARCHAR(10)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

# Starter 767-300F fleet matching your aircraft_data.json
fleet_data = [
    (7471, '767-300F', 'SDF', 24, 12, 12, 125000, 24000, 3200, 530),
    (7472, '767-300F', 'ONT', 24, 12, 12, 125000, 24000, 3200, 530),
    (7473, '767-300F', 'EWR', 24, 12, 12, 125000, 24000, 3200, 530)
]

cursor.executemany("""
    INSERT INTO fleet (aircraft_id, aircraft_type, current_location, main_deck_positions, 
    p_sec_f, p_sec_r, max_payload, fuel_capacity, max_range, cruise_speed) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", fleet_data)

conn.commit()
print("Fleet table generated with full physical specs.")
conn.close()