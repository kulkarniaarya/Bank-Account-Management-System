import sqlite3
from datetime import datetime
import hashlib
import getpass 

DB_NAME = "bank.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def get_account_by_number(account_number):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE account_number = ?",
        (account_number,)
    )

    account = cursor.fetchone()
    connection.close()

    return account


def verify_pin(account_number):
    import hashlib
    import getpass

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT pin_hash FROM accounts WHERE account_number = ?",
        (account_number,)
    )

    result = cursor.fetchone()
    connection.close()

    if result is None or result[0] is None:
        print("PIN not set. Please set your PIN first.")
        return False

    for attempt in range(3):
        pin = getpass.getpass("Enter your 4-digit PIN: ")

        if len(pin) == 4 and pin.isdigit():
            pin_hash = hashlib.sha256(pin.encode()).hexdigest()

            if pin_hash == result[0]:
                print("Login successful!")
                return True

        print("Incorrect PIN.")

    print("Too many failed attempts. Access denied.")
    return False

    if result is None or result[0] is None:
        print("PIN not set. Please set your PIN first.")
        return False

    for attempt in range(3):
        pin = getpass.getpass("Enter your 4-digit PIN: ")

        if len(pin) == 4 and pin.isdigit():
            pin_hash = hashlib.sha256(pin.encode()).hexdigest()

            if pin_hash == result[0]:
                print("Login successful!")
                return True

        print("Incorrect PIN.")

    print("Too many failed attempts. Access denied.")
    return False
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE account_number = ?",
        (account_number,)
    )

    account = cursor.fetchone()
    connection.close()

    return account


def save_transaction(account_number, transaction_type, amount, balance):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (account_number, transaction_type, amount,
         transaction_date, balance_after)
        VALUES (?, ?, ?, ?, ?)
    """, (
        account_number,
        transaction_type,
        amount,
        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        balance
    ))

    connection.commit()
    connection.close()


def update_balance(account_number, new_balance):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE accounts
        SET balance = ?
        WHERE account_number = ?
    """, (new_balance, account_number))

    connection.commit()
    connection.close()


def deposit(account):
    try:
        amount = float(input("Enter deposit amount: "))
    except ValueError:
        print("Enter a valid number.")
        return

    if amount <= 0:
        print("Amount must be greater than zero.")
        return

    account_number = account[0]
    balance = account[2]
    new_balance = balance + amount

    update_balance(account_number, new_balance)
    save_transaction(
        account_number, "Deposit", amount, new_balance
    )

    print(f"Deposit successful: Rs. {amount:.2f}")
    print(f"New balance: Rs. {new_balance:.2f}")


def withdraw(account):
    try:
        amount = float(input("Enter withdrawal amount: "))
    except ValueError:
        print("Enter a valid number.")
        return

    if amount <= 0:
        print("Amount must be greater than zero.")
        return

    account_number = account[0]
    balance = account[2]
    account_type = account[3]
    overdraft_limit = account[5] or 0

    if account_type == "SavingsAccount":
        if amount > balance:
            print("Insufficient balance.")
            return
    elif amount > balance + overdraft_limit:
        print("Overdraft limit exceeded.")
        return

    new_balance = balance - amount

    update_balance(account_number, new_balance)
    save_transaction(
        account_number, "Withdrawal", -amount, new_balance
    )

    print(f"Withdrawal successful: Rs. {amount:.2f}")
    print(f"New balance: Rs. {new_balance:.2f}")


def add_interest(account):
    if account[3] != "SavingsAccount":
        print("Interest is available only for Savings Account.")
        return

    account_number = account[0]
    balance = account[2]
    interest_rate = account[4] or 4

    interest = balance * interest_rate / 100
    new_balance = balance + interest

    update_balance(account_number, new_balance)
    save_transaction(
        account_number, "Interest", interest, new_balance
    )

    print(f"Interest added: Rs. {interest:.2f}")
    print(f"New balance: Rs. {new_balance:.2f}")


def check_balance(account):
    print(f"\nAccount Holder: {account[1]}")
    print(f"Account Number: {account[0]}")
    print(f"Balance: Rs. {account[2]:.2f}")

def create_new_account():
    import hashlib
    import getpass
    import sqlite3

    name = input("Enter account holder name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    print("\n1. Savings Account")
    print("2. Current Account")

    choice = input("Select account type: ").strip()

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

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT MAX(CAST(account_number AS INTEGER)) FROM accounts"
        )
        result = cursor.fetchone()[0]
        account_number = str(max(result or 100000, 100000) + 1)

        cursor.execute("""
            INSERT INTO accounts (
                account_number, name, balance, account_type,
                interest_rate, overdraft_limit, pin_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            account_number,
            name,
            balance,
            account_type,
            interest_rate,
            overdraft_limit,
            hashlib.sha256(pin.encode()).hexdigest()
        ))

        connection.commit()

        print("\nAccount created successfully!")
        print(f"Account Holder: {name}")
        print(f"Account Number: {account_number}")
        print(f"Opening Balance: ₹{balance:.2f}")

    except sqlite3.Error as error:
        print("Could not create account:", error)

    finally:
        connection.close()

def show_transactions(account):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT transaction_date, transaction_type,
               amount, balance_after
        FROM transactions
        WHERE account_number = ?
        ORDER BY transaction_id DESC
        LIMIT 10
    """, (account[0],))

    transactions = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(CASE
                WHEN amount > 0 THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE
                WHEN amount < 0 THEN -amount ELSE 0 END), 0)
        FROM transactions
        WHERE account_number = ?
    """, (account[0],))

    summary = cursor.fetchone()
    connection.close()

    print("\n========== MINI STATEMENT ==========")
    print(f"Account Holder: {account[1]}")
    print(f"Account Number: {account[0]}")
    print(f"Current Balance: ₹{account[2]:.2f}")

    print(f"\nTotal Transactions: {summary[0]}")
    print(f"Total Deposits/Interest: ₹{summary[1]:.2f}")
    print(f"Total Withdrawals: ₹{summary[2]:.2f}")

    print("\nLast 10 Transactions:")
    print("-" * 75)

    if not transactions:
        print("No transactions found.")
    else:
        for date, transaction_type, amount, balance in transactions:
            print(
                f"{date} | {transaction_type} | "
                f"₹{amount:.2f} | Balance: ₹{balance:.2f}"
            )

    print("-" * 75)


account_number = input("Enter account number: ").strip()

if not verify_pin(account_number):
    raise SystemExit

account = get_account_by_number(account_number)

if account is None:
    print("Account not found.")
    raise SystemExit

print("\nWelcome to Bank Account Management System!")
check_balance(account)

while True:
    print("\n1. Deposit")
    print("2. Withdraw")
    print("3. Check Balance")
    print("4. Exit")
    print("5. Add Interest")
    print("6. Transaction History")
    print("7.Create New Account")

    choice = input("Enter your choice: ")

    # Reload the latest balance before every operation.
    account = get_account_by_number(account_number)
    if account is None:
        print("Account not found.")
        break

    if choice == "1":
        deposit(account)
    elif choice == "2":
        withdraw(account)
    elif choice == "3":
        check_balance(account)
    elif choice == "4":
        print("Thank you!")
        break
    elif choice == "5":
        add_interest(account)
    elif choice == "6":
        show_transactions(account)
    elif choice == "7":
        create_new_account()
    else:
        print("Invalid choice.")