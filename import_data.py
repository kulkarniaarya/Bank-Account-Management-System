import json
import sqlite3

# Read existing JSON data
with open("accounts.json", "r") as file:
    accounts = json.load(file)

# Connect to SQLite database
connection = sqlite3.connect("bank.db")
cursor = connection.cursor()

# Import accounts
for name, data in accounts.items():
    account_number = data.get("account_number")

    if account_number is None:
        print(f"Skipping {name}: account number missing.")
        continue

    cursor.execute("""
        INSERT INTO accounts (
            account_number, name, balance,
            account_type, interest_rate, overdraft_limit
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(account_number) DO UPDATE SET
            name = excluded.name,
            balance = excluded.balance,
            account_type = excluded.account_type,
            interest_rate = excluded.interest_rate,
            overdraft_limit = excluded.overdraft_limit
    """, (
        str(account_number),
        name,
        data["balance"],
        data["account_type"],
        data.get("interest_rate"),
        data.get("overdraft_limit")
    ))

    # Import transaction history
    for transaction in data.get("transactions", []):
        cursor.execute("""
            SELECT 1 FROM transactions
            WHERE account_number = ?
              AND transaction_type = ?
              AND amount = ?
              AND transaction_date = ?
              AND balance_after = ?
            LIMIT 1
        """, (
            str(account_number),
            transaction["type"],
            transaction["amount"],
            transaction["date"],
            transaction["balance"]
        ))

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO transactions (
                    account_number, transaction_type,
                    amount, transaction_date, balance_after
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(account_number),
                transaction["type"],
                transaction["amount"],
                transaction["date"],
                transaction["balance"]
            ))

connection.commit()
connection.close()

print("Data imported successfully!")