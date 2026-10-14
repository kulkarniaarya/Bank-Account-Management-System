import sqlite3

connection = sqlite3.connect("bank.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT account_number, name, balance, account_type
    FROM accounts
    ORDER BY account_number
""")

accounts = cursor.fetchall()

print("\n===== ALL BANK ACCOUNTS =====")

for account in accounts:
    print(f"""
Account Number: {account[0]}
Name: {account[1]}
Balance: ₹{account[2]:.2f}
Account Type: {account[3]}
------------------------------
""")

connection.close()