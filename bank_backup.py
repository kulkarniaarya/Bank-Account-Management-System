import json
import os


FILE_NAME = "accounts.json"


class BankAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            print("Invalid amount")
        else:
            self.balance += amount
            save_account(self)
            print(f"₹{amount} deposited successfully.")
            print(f"Updated Balance: ₹{self.balance:.2f}")

    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount > self.balance:
            print("Insufficient balance")
        else:
            self.balance -= amount
            save_account(self)
            print(f"₹{amount} withdrawn successfully.")
            print(f"Updated Balance: ₹{self.balance:.2f}")

    def check_balance(self):
        print(f"{self.name}, your balance is: ₹{self.balance:.2f}")


class SavingsAccount(BankAccount):
    def __init__(self, name, balance=0, interest_rate=4):
        super().__init__(name, balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.balance * self.interest_rate / 100
        self.balance += interest

        save_account(self)

        print(f"Interest ₹{interest:.2f} added.")
        print(f"Updated Balance: ₹{self.balance:.2f}")


class CurrentAccount(BankAccount):
    def __init__(self, name, balance=0, overdraft_limit=5000):
        super().__init__(name, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount > self.balance + self.overdraft_limit:
            print("Overdraft limit exceeded")
        else:
            self.balance -= amount
            save_account(self)
            print(f"₹{amount} withdrawn successfully.")
            print(f"Updated Balance: ₹{self.balance:.2f}")


def load_accounts():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    return {}


def save_account(acc):
    accounts = load_accounts()

    accounts[acc.name] = {
        "balance": acc.balance,
        "account_type": type(acc).__name__,
        "interest_rate": getattr(acc, "interest_rate", None),
        "overdraft_limit": getattr(acc, "overdraft_limit", None)
    }

    with open(FILE_NAME, "w") as file:
        json.dump(accounts, file, indent=4)


def create_account(name):
    accounts = load_accounts()

    if name in accounts:
        data = accounts[name]

        if data["account_type"] == "SavingsAccount":
            return SavingsAccount(
                name,
                data["balance"],
                data["interest_rate"]
            )

        return CurrentAccount(
            name,
            data["balance"],
            data["overdraft_limit"]
        )

    acc = SavingsAccount(name, 1000)
    save_account(acc)
    return acc


name = input("Enter account holder name: ").strip()

if not name:
    print("Name cannot be empty.")
    raise SystemExit

acc = create_account(name)

print(f"\nWelcome, {acc.name}!")
print(f"Current Balance: ₹{acc.balance:.2f}")

while True:
    print("\n1. Deposit")
    print("2. Withdraw")
    print("3. Check Balance")
    print("4. Exit")
    print("5. Add Interest")

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

    else:
        print("Invalid choice")