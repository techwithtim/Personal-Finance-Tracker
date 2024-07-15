from matplotlib import pyplot as plt
import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        """Initializes the CSV file by creating it if it doesn't exist."""
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        """Adds a new transaction entry to the CSV file."""
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully")

    @classmethod
    def update_entry(cls, index, date, amount, category, description):
        """Updates an existing transaction entry in the CSV file."""
        df = pd.read_csv(cls.CSV_FILE)
        if 0 <= index < len(df):
            df.at[index, 'date'] = date
            df.at[index, 'amount'] = amount
            df.at[index, 'category'] = category
            df.at[index, 'description'] = description
            df.to_csv(cls.CSV_FILE, index=False)
            print("Entry updated successfully")
        else:
            print("Invalid index. No entry updated.")

    @classmethod
    def delete_entry(cls, index):
        """Deletes a transaction entry from the CSV file."""
        try:
            df = pd.read_csv(cls.CSV_FILE)
            if df.empty:
                print("No data available to delete.")
                return
            if 0 <= index < len(df):
                df = df.drop(index).reset_index(drop=True)
                df.to_csv(cls.CSV_FILE, index=False)
                print("Entry deleted successfully")
            else:
                print("Invalid index. No entry deleted.")
        except FileNotFoundError:
            print("No data available to delete.")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        """Retrieves transactions within the specified date range."""
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transaction found in the given date range.")
        else:
            print(
                f"Transaction from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}"
            )
            print(
                filtered_df.to_string(
                    index=False,
                    formatters={"date": lambda x: x.strftime(CSV.FORMAT)}))

            total_income = filtered_df[filtered_df["category"] ==
                                       "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] ==
                                        "Expense"]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Saving: ${(total_income - total_expense):.2f}")
        return filtered_df


def add():
    """Prompts the user to add a new transaction."""
    CSV.initialize_csv()
    date = get_date(
        "Enter the date of the transaction (dd-mm-yyyy) or enter for today's date: ",
        allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def update():
    """Prompts the user to update an existing transaction."""
    index = int(input("Enter the index of the transaction to update: "))
    date = get_date("Enter the new date of the transaction (dd-mm-yyyy): ")
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.update_entry(index, date, amount, category, description)


def delete():
    """Prompts the user to delete an existing transaction."""
    index = int(input("Enter the index of the transaction to delete: "))
    CSV.delete_entry(index)


def plot_transaction(df):
    """Plots the income and expenses over time."""
    df.set_index("date", inplace=True)

    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(
        df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(
        df.index, fill_value=0)

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index,
             expense_df["amount"],
             label="Expense",
             color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    """Main function to run the application."""
    while True:
        print("\n1. Add a new transaction")
        print("\n2. Update an existing transaction")
        print("\n3. Delete a transaction")
        print("\n4. View transactions and summary within a date range")
        print("\n5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            add()
        elif choice == "2":
            update()
        elif choice == "3":
            delete()
        elif choice == "4":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if not df.empty and input(
                    "Do you want to see a plot? (y/n) ").lower() == "y":
                plot_transaction(df)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter 1, 2, 3, 4, or 5")


if __name__ == "__main__":
    main()
