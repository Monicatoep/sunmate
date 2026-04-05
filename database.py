import sqlite3

def init_db(db_name="sunmate.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batteryData (
            timestamp TEXT NOT NULL,
            soc INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS energyConsumptionData (
            timestamp TEXT NOT NULL,
            consumption_kwh REAL NOT NULL
        )
    """)

    connect.commit()
    connect.close()

def seed_db(db_name="sunmate.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T00:00:00", 85))
    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T06:00:00", 40))
    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T12:00:00", 70))

    cursor.execute("INSERT INTO energyConsumptionData VALUES (?, ?)", ("2024-11-29T12:00:00", 1.2))
    cursor.execute("INSERT INTO energyConsumptionData VALUES (?, ?)", ("2024-11-29T13:00:00", 2.4))

    connect.commit()
    connect.close()