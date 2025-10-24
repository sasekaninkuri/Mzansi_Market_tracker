from colorama import Fore, init
from datetime import datetime
import pandas as pd
from db_setup import (
    create_tables, register_stall_owner, login_stall_owner, add_product,
    get_all_products, make_sale, get_weekly_report, get_report_data_for_csv, search_products
)

init(autoreset=True)


def main():
    print(Fore.GREEN + "🌍 Sawubona! Welcome to mans Market Tracker!")
    create_tables()

    owner_id = None
    while not owner_id:
        print(Fore.CYAN + "\n===== 👥 Stall Owner Access =====")
        print("1. 🧾 Register Stall Owner")
        print("2. 🔑 Login Stall Owner")
        choice = input(Fore.LIGHTBLUE_EX + "👉 Choose an option: ")
        if choice == "1":
            name = input("👤 Name: ")
            location = input("📍 Location: ")
            username = input("💻 Username: ")
            password = input("🔐 Password: ")
            owner_id = register_stall_owner(name, location, username, password)
        elif choice == "2":
            username = input("💻 Username: ")
            password = input("🔐 Password: ")
            owner_id = login_stall_owner(username, password)
        else:
            print(Fore.RED + "❌ Invalid choice.")

    while True:
        print(Fore.CYAN + "\n===== 🎉 Mzansi Market Menu 🎉 =====")
        print("1. 🛒 Add Product")
        print("2. 📦 View Products")
        print("3. 💰 Make Sale")
        print("4. 📊 Weekly Report")
        print("5. 📁 Export Report to CSV")
        print("6. 🔍 Search Products")
        print("7. 🚪 Logout")
        print("8. ❌ Exit")

        choice = input(Fore.LIGHTBLUE_EX + "👉 Enter your choice: ")

        if choice == "1":
            name = input("🛍️ Product name: ")
            price = float(input("💸 Price: "))
            stock = int(input("📦 Stock quantity: "))
            add_product(owner_id, name, price, stock)
        elif choice == "2":
            products = get_all_products()
            if not products:
                print(Fore.YELLOW + "ℹ️ No products found.")
            else:
                print(Fore.CYAN + "\n📦 Available Products:")
                for p in products:
                    print(Fore.LIGHTYELLOW_EX + f"🆔 ID: {p[0]} | 🛍️ {p[1]} | 💸 R{p[2]:.2f} | 📦 Stock: {p[3]}")
        elif choice == "3":
            pname = input("🧾 Product sold: ")
            qty = int(input("🔢 Quantity: "))
            make_sale(pname, qty)
        elif choice == "4":
            report = get_weekly_report()
            if not report:
                print(Fore.YELLOW + "ℹ️ No sales data available.")
            else:
                print(Fore.CYAN + "\n📊 Weekly Sales Report:")
                for r in report:
                    print(Fore.LIGHTGREEN_EX + f"🛍️ {r[0]} | 🧾 Sold: {r[1]} | 💰 Revenue: R{r[2]:.2f}")
        elif choice == "5":
            data = get_report_data_for_csv()
            df = pd.DataFrame(data, columns=["Product", "Owner", "Location", "Price", "Stock", "Total Sold", "Total Revenue"])
            filename = f"weekly_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
            df.to_csv(filename, index=False)
            print(Fore.GREEN + f"✅ Report exported to {filename}")
        elif choice == "6":
            term = input(Fore.CYAN + "🔎 Enter product name or ID to search: ")
            results = search_products(term)
            if not results:
                print(Fore.YELLOW + "ℹ️ No matching products found.")
            else:
                for r in results:
                    print(Fore.LIGHTGREEN_EX + f"🆔 ID: {r[0]} | 🛍️ {r[1]} | 💸 R{r[2]:.2f} | 📦 Stock: {r[3]}")
        elif choice == "7":
            print(Fore.MAGENTA + "👋 Logging out...")
            main()
            break
        elif choice == "8":
            print(Fore.MAGENTA + "👋 Exiting program. Hamba kahle!")
            break
        else:
            print(Fore.RED + "❌ Invalid choice.")


if __name__ == "__main__":
    main()
