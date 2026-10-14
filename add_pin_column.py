import sqlite3

connection = sqlite3.connect("bank.db")
cursor = connection.cursor()

columns = [
    row[1]
    for row in cursor.execute("PRAGMA table_info(accounts)")
]

if "pin_hash" not in columns:
    cursor.execute(
        "ALTER TABLE accounts ADD COLUMN pin_hash TEXT"
    )
    print("PIN column added successfully!")
else:
    print("PIN column already exists.")

connection.commit()
connection.close()