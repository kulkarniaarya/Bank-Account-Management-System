import sqlite3

connection = sqlite3.connect("bank.db")
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(accounts)")
columns = cursor.fetchall()

print("Accounts Table Columns:")

for column in columns:
    print(column[1])

connection.close()