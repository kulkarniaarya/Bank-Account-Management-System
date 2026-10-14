import sqlite3
import hashlib
import getpass

DB_NAME = "bank.db"


def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

account_number = input("Enter account number: ").strip()

cursor.execute(
    "SELECT pin_hash FROM accounts WHERE account_number = ?",
    (account_number,)
)

account = cursor.fetchone()

if account is None:
    print("Account not found.")
else:
    pin = getpass.getpass("Create a 4-digit PIN: ")

    if not pin.isdigit() or len(pin) != 4:
        print("PIN must contain exactly 4 digits.")
    else:
        confirm_pin = getpass.getpass("Confirm your PIN: ")

        if pin != confirm_pin:
            print("PINs do not match.")
        elif account[0] is not None:
            print("PIN is already set. Use the PIN change process.")
        else:
            cursor.execute(
                "UPDATE accounts SET pin_hash = ? "
                "WHERE account_number = ?",
                (hash_pin(pin), account_number)
            )
            connection.commit()
            print("PIN set successfully!")

connection.close()