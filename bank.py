import json
import os
from datetime import datetime

FILE_NAME = "accounts.json"


def load_accounts():
    if not os.path.exists(FILE_NAME):
        return {}

    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Error reading accounts.json")
        raise SystemExit


def save_accounts(accounts):
    with open(FILE_NAME, "w") as file:
        json.dump(accounts, file, indent=4)


class BankAccount:
    def __init__(self, name, balance=0, account_number=None):
        self.name = name
        self.balance = balance
        self.account_number = account_number
        self.transactions = []

    def record_transaction(self, transaction_type, amount):
        self.transactions.append({
            "type": transaction_type,
            "amount": round(amount, 2),
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "balance": round(self.balance, 2)
        })

    def deposit(self, amount):
        if amount <= 0:
            print("Invalid amount")
            return

        self.balance += amount
        self.record_transaction("Deposit", amount)
        save_account(self)

        print(f"₹{amount:.2f} deposited successfully.")
        print(f"Updated Balance: ₹{self.balance:.2f}")

    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount > self.balance:
            print("Insufficient balance")
        else:
            self.balance -= amount
            self.record_transaction("Withdrawal", -amount)
            save_account(self)

            print(f"₹{amount:.2f} withdrawn successfully.")
            print(f"Updated Balance: ₹{self.balance:.2f}")

    def check_balance(self):
        print(f"\nAccount Holder: {self.name}")
        print(f"Account Number: {self.account_number}")
        print(f"Balance: ₹{self.balance:.2f}")

    def show_transactions(self):
        print("\n========== TRANSACTION HISTORY ==========")
        print(f"Account Holder: {self.name}")
        print(f"Account Number: {self.account_number}")

        if not self.transactions:
            print("No transactions recorded yet.")
            return

        for transaction in self.transactions:
            print(
                f"{transaction['date']} | "
                f"{transaction['type']} | "
                f"₹{transaction['amount']:.2f} | "
                f"Balance: ₹{transaction['balance']:.2f}"
            )

        print(f"\nCurrent Balance: ₹{self.balance:.2f}")


class SavingsAccount(BankAccount):
    def __init__(
        self, name, balance=0, interest_rate=4,
        account_number=None, transactions=None
    ):
        super().__init__(name, balance, account_number)
        self.interest_rate = interest_rate
        self.transactions = transactions or []

    def add_interest(self):
        interest = self.balance * self.interest_rate / 100

        if interest <= 0:
            print("No interest to add.")
            return

        self.balance += interest
        self.record_transaction("Interest", interest)
        save_account(self)

        print(f"Interest ₹{interest:.2f} added.")
        print(f"Updated Balance: ₹{self.balance:.2f}")


class CurrentAccount(BankAccount):
    def __init__(
        self, name, balance=0, overdraft_limit=5000,
        account_number=None, transactions=None
    ):
        super().__init__(name, balance, account_number)
        self.overdraft_limit = overdraft_limit
        self.transactions = transactions or []

    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount > self.balance + self.overdraft_limit:
            print("Overdraft limit exceeded")
        else:
            self.balance -= amount
            self.record_transaction("Withdrawal", -amount)
            save_account(self)

            print(f"₹{amount:.2f} withdrawn successfully.")
            print(f"Updated Balance: ₹{self.balance:.2f}")


def generate_account_number(accounts):
    used_numbers = [
        int(data["account_number"])
        for data in accounts.values()
        if data.get("account_number") is not None
    ]

    return str(max(used_numbers, default=100000) + 1)


def save_account(acc):
    accounts = load_accounts()

    accounts[acc.name] = {
        "account_number": acc.account_number,
        "balance": round(acc.balance, 2),
        "account_type": type(acc).__name__,
        "interest_rate": getattr(acc, "interest_rate", None),
        "overdraft_limit": getattr(acc, "overdraft_limit", None),
        "transactions": acc.transactions
    }

    save_accounts(accounts)


def create_account(name):
    accounts = load_accounts()

    if name in accounts:
        data = accounts[name]

        account_number = data.get("account_number")

        if account_number is None:
            account_number = generate_account_number(accounts)

        transactions = data.get("transactions", [])

        if data["account_type"] == "SavingsAccount":
            acc = SavingsAccount(
                name,
                data["balance"],
                data.get("interest_rate") or 4,
                account_number,
                transactions
            )
        else:
            acc = CurrentAccount(
                name,
                data["balance"],
                data.get("overdraft_limit") or 5000,
                account_number,
                transactions
            )

        save_account(acc)
        return acc

    account_number = generate_account_number(accounts)
    acc = SavingsAccount(name, 1000, 4, account_number)
    save_account(acc)

    return acc


name = input("Enter account holder name: ").strip()

if not name:
    print("Name cannot be empty.")
    raise SystemExit

acc = create_account(name)

print("\nWelcome to Bank Account Management System!")
print(f"Account Holder: {acc.name}")
print(f"Account Number: {acc.account_number}")
print(f"Current Balance: ₹{acc.balance:.2f}")

while True:
    print("\n1. Deposit")
    print("2. Withdraw")
    print("3. Check Balance")
    print("4. Exit")
    print("5. Add Interest")
    print("6. Transaction History")

    choice = input("Enter your choice: ")

    if choice == "1":
        try:
            amount = float(input("Enter deposit amount: "))
            acc.deposit(amount)
        except ValueError:
            print("Please enter a valid number.")

    elif choice == "2":
        try:
            amount = float(input("Enter withdrawal amount: "))
            acc.withdraw(amount)
        except ValueError:
            print("Please enter a valid number.")

    elif choice == "3":
        acc.check_balance()

    elif choice == "4":
        print("Thank you!")
        break

    elif choice == "5":
        if isinstance(acc, SavingsAccount):
            acc.add_interest()
        else:
            print("Interest is available only for Savings Account.")

    elif choice == "6":
        acc.show_transactions()

    else:
        print("Invalid choice")