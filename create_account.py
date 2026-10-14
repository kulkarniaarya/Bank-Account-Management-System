import sqlite3
import hashlib
import getpass

DB_NAME = "bank.db"


def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def create_account():
    name = input("Enter account holder name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    print("\nSelect Account Type:")
    print("1. Savings Account")
    print("2. Current Account")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        account_type = "SavingsAccount"
        interest_rate = 4
        overdraft_limit = 0
    elif choice == "2":
        account_type = "CurrentAccount"
        interest_rate = 0
        overdraft_limit = 5000
    else:
        print("Invalid account type.")
        return

    try:
        balance = float(input("Enter opening balance: "))
        if balance < 0:
            print("Balance cannot be negative.")
            return
    except ValueError:
        print("Enter a valid amount.")
        return

    pin = getpass.getpass("Create 4-digit PIN: ")

    if len(pin) != 4 or not pin.isdigit():
        print("PIN must contain exactly 4 digits.")
        return

    confirm_pin = getpass.getpass("Confirm PIN: ")

    if pin != confirm_pin:
        print("PINs do not match.")
        return

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT MAX(CAST(account_number AS INTEGER)) FROM accounts"
    )
    result = cursor.fetchone()[0]

    account_number = str((result or 100000) + 1)

    cursor.execute("""
        INSERT INTO accounts (
            account_number, name, balance,
            account_type, interest_rate,
            overdraft_limit, pin_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        account_number,
        name,
        balance,
        account_type,
        interest_rate,
        overdraft_limit,
        hash_pin(pin)
    ))

    connection.commit()
    connection.close()

    print("\nAccount created successfully!")
    print(f"Account Holder: {name}")
    print(f"Account Number: {account_number}")
    print(f"Account Type: {account_type}")
    print(f"Opening Balance: ₹{balance:.2f}")


create_account()