import mysql.connector
from mysql.connector import Error


def setup_airports():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ups_sim'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS airports")

            cursor.execute("""
                CREATE TABLE airports (
                    icao VARCHAR(4) PRIMARY KEY,
                    name VARCHAR(100),
                    city VARCHAR(100),
                    is_hub TINYINT(1),
                    latitude DECIMAL(10, 7),
                    longitude DECIMAL(10, 7),
                    timezone_offset INT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            airports = [
                ('SDF', 'Worldport', 'Louisville', 1, 38.1744, -85.7360, -5),
                ('ONT', 'Ontario International', 'Ontario', 0, 34.0560, -117.6012, -8),
                ('EWR', 'Newark Liberty', 'Newark', 0, 40.6895, -74.1745, -5),
                ('ANC', 'Ted Stevens Intl', 'Anchorage', 0, 61.1743, -149.9963, -9),
                ('PHX', 'Phoenix Sky Harbor', 'Phoenix', 0, 33.4342, -112.0081, -7)
            ]

            cursor.executemany("INSERT INTO airports VALUES (%s, %s, %s, %s, %s, %s, %s)", airports)
            connection.commit()
            print("Airports table synced with 3-letter codes.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()


if __name__ == "__main__":
    setup_airports()