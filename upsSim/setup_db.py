import mysql.connector
from mysql.connector import errorcode


def setup_database():
    # This is tailored to be ran with XAMPP v3.3.0
    # Since I ran this on my local system I just use the default user root password blank format.
    # You will have to manully update it in the coding files though
    db_name = "ups_sim"
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
    }

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return

    # Creates db
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.database = db_name

    # Generates structure
    tables = {}

    tables['airports'] = (
        "CREATE TABLE IF NOT EXISTS `airports` ("
        "  `icao` varchar(4) NOT NULL,"
        "  `name` varchar(100) DEFAULT NULL,"
        "  `city` varchar(100) DEFAULT NULL,"
        "  `is_hub` tinyint(1) DEFAULT NULL,"
        "  `latitude` decimal(10,7) DEFAULT NULL,"
        "  `longitude` decimal(10,7) DEFAULT NULL,"
        "  `timezone_offset` int(11) DEFAULT NULL,"
        "  PRIMARY KEY (`icao`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    )

    tables['fleet'] = (
        "CREATE TABLE IF NOT EXISTS `fleet` ("
        "  `aircraft_id` int(11) NOT NULL,"
        "  `aircraft_type` varchar(50) NOT NULL,"
        "  `current_location` varchar(10) DEFAULT NULL,"
        "  `main_deck_positions` int(11) DEFAULT NULL,"
        "  `p_sec_f` int(11) DEFAULT NULL,"
        "  `p_sec_r` int(11) DEFAULT NULL,"
        "  `max_payload` int(11) DEFAULT NULL,"
        "  `fuel_capacity` int(11) DEFAULT NULL,"
        "  `max_range` int(11) DEFAULT NULL,"
        "  `cruise_speed` int(11) DEFAULT NULL,"
        "  `status` varchar(50) DEFAULT 'Parked',"
        "  `departure_time` datetime DEFAULT NULL,"
        "  `arrival_time` datetime DEFAULT NULL,"
        "  `origin` varchar(10) DEFAULT NULL,"
        "  `destination` varchar(10) DEFAULT NULL,"
        "  PRIMARY KEY (`aircraft_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    )

    tables['uld_inventory'] = (
        "CREATE TABLE IF NOT EXISTS `uld_inventory` ("
        "  `uld_id` varchar(20) NOT NULL,"
        "  `uld_type` varchar(10) NOT NULL,"
        "  `volume_cubic_ft` int(11) DEFAULT NULL,"
        "  `max_weight_lbs` int(11) DEFAULT NULL,"
        "  `current_location` varchar(10) DEFAULT NULL,"
        "  `destination` varchar(10) DEFAULT NULL,"
        "  `status` varchar(50) DEFAULT 'Empty',"
        "  `current_weight` decimal(10,2) DEFAULT 0.00,"
        "  `parent_plane` int(11) DEFAULT NULL,"
        "  `position_on_plane` varchar(10) DEFAULT NULL,"
        "  `weight` decimal(10,2) DEFAULT 2000.00,"
        "  PRIMARY KEY (`uld_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    )

    for table_name in tables:
        cursor.execute(tables[table_name])
        print(f"Table '{table_name}' verified/created.")

    # Airports
    airports_data = [
        ('SDF', 'Worldport', 'Louisville', 1, 38.1744000, -85.7360000, -5),
        ('ONT', 'Ontario International', 'Ontario', 0, 34.0560000, -117.6012000, -8),
        ('EWR', 'Newark Liberty', 'Newark', 0, 40.6895000, -74.1745000, -5),
        ('PHX', 'Phoenix Sky Harbor', 'Phoenix', 0, 33.4342000, -112.0081000, -7),
        ('ANC', 'Ted Stevens Intl', 'Anchorage', 0, 61.1743000, -149.9963000, -9)
    ]
    cursor.executemany("INSERT IGNORE INTO airports VALUES (%s, %s, %s, %s, %s, %s, %s)", airports_data)


    fleet_data = [
        (7471, '767-300F', 'SDF', 24, 12, 12, 125000, 24000, 3200, 530, 'Parked', None, None, None, None),
        (7472, '767-300F', 'ONT', 24, 12, 12, 125000, 24000, 3200, 530, 'Parked', None, None, None, None)
    ]
    cursor.executemany("INSERT IGNORE INTO fleet VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       fleet_data)

    conn.commit()
    cursor.close()
    conn.close()
    print("\nDatabase setup successful! The user can now run main.py.")


if __name__ == "__main__":
    setup_database()