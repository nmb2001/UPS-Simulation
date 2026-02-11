import mysql.connector
import random

conn = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS uld_inventory")
cursor.execute("""
    CREATE TABLE uld_inventory (
        uld_id VARCHAR(20) PRIMARY KEY,
        uld_type VARCHAR(10) NOT NULL,
        volume_cubic_ft INT,
        max_weight_lbs INT,
        current_location VARCHAR(10),
        destination VARCHAR(10),
        status VARCHAR(50) DEFAULT 'Empty',
        current_weight DECIMAL(10,2) DEFAULT 0.00,
        parent_plane INT,
        position_on_plane VARCHAR(10),
        weight DECIMAL(10,2) DEFAULT 2000.00
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

can_types = {
    "AAD": {"vol": 395, "max": 13200},
    "AAY": {"vol": 350, "max": 11000},
    "AMJ": {"vol": 510, "max": 15000},
    "AMD": {"vol": 450, "max": 17600},
    "AMP": {"vol": 509, "max": 11000}
}

airports = ["SDF", "ONT", "EWR", "PHX", "ANC"]

for can_type, specs in can_types.items():
    for i in range(20):  # Generate 20 of each type
        u_id = f"{can_type}{random.randint(10000, 99999)}"
        loc = random.choice(airports)

        cursor.execute("""
            INSERT INTO uld_inventory (uld_id, uld_type, volume_cubic_ft, max_weight_lbs, current_location, status)
            VALUES (%s, %s, %s, %s, %s, 'Empty')
        """, (u_id, can_type, specs['vol'], specs['max'], loc))

conn.commit()
print("ULD Inventory populated with valid aircraft types.")
conn.close()