import psycopg2
import csv
import hashlib
from datetime import datetime
from db_setup import create_tables, create_connection
import pandas as pd
from colorama import Fore, Style, init
from db_setup import add_stall_owner
from db_setup import login_stall_owner2
from db_setup import add_product2
from db_setup import view_product2
from db_setup import search_products
from db_setup import make_sale
from db_setup import get_weekly_report
from db_setup import export_report_to_csv_db


# Initialize colorama
init(autoreset=True)

# ------------------------
# Password hashing
# ------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------------
# Stall Owner Registration/Login
# ------------------------
def register_stall_owner():
    print(Fore.CYAN + "\n🧑‍🌾 Stall Owner Registration")
    name = input("👤 Enter stall owner name: ")
    location = input("📍 Enter stall location: ")
    username = input("💻 Create a username: ")
    password = input("🔐 Create a password: ")
    hashed_pw = hash_password(password)

    try:
        conn = create_connection()
        if not conn:
            return None
        cursor = conn.cursor()

        add_stall_owner(cursor, name, location, username, hashed_pw)
        owner_id = cursor.fetchone()[0]
        conn.commit()
        print(Fore.GREEN + f"✅ Stall owner '{name}' registered successfully!")
        return owner_id
    except psycopg2.errors.UniqueViolation:
        print(Fore.RED + "❌ Username already exists.")
    except Exception as e:
        print(Fore.RED + "❌ Error registering stall owner:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()
    return None


def login_stall_owner():
    print(Fore.CYAN + "\n🔑 Stall Owner Login")
    username = input("👤 Enter your username: ")
    password = input("🔐 Enter your password: ")
    hashed_pw = hash_password(password)

    try:
        conn = create_connection()
        if not conn:
            return None
        cursor = conn.cursor()

        user = login_stall_owner2(cursor, username, hashed_pw)
        
        if user:
            print(Fore.GREEN + f"✅ Welcome back, {user[1]}!")
            return user[0]
        else:
            print(Fore.RED + "❌ Invalid username or password.")
            return None
    except Exception as e:
        print(Fore.RED + "❌ Error during login:", e)
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

# ------------------------
# Product Functions
# ------------------------
def add_product(owner_id, name, price, stock):
    try:
        conn = create_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        # cursor.execute(
            # "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;",
            # (owner_id, name, price, stock)
        add_product2(cursor, owner_id, name, price, stock)

        # )
        
        
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(Fore.GREEN + f"✅ Product '{name}' added successfully!")
        return product_id
    except Exception as e:
        print(Fore.RED + "❌ Error adding product:", e)
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def view_products():
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        view_product2(cursor, products)
        products = cursor.fetchall()
        if not products:
            print(Fore.YELLOW + "ℹ️ No products found.")
            return
        print(Fore.CYAN + "\n📦 Available Products:")
        print("-" * 45)
        for p in products:
            print(Fore.LIGHTYELLOW_EX + f"🆔 ID: {p[0]} | 🛍️ {p[1]} | 💸 R{p[2]:.2f} | 📦 Stock: {p[3]}")
        print("-" * 45)
    except Exception as e:
        print(Fore.RED + "❌ Error viewing products:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


def search_products():
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        search_products(cursor, term, pid)
        term = input(Fore.CYAN + "🔎 Enter product name or ID to search: ")
        try:
            pid = int(term)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
        except ValueError:
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name ILIKE %s;", (f"%{term}%",))
        results = cursor.fetchall()
        if not results:
            print(Fore.YELLOW + "ℹ️ No matching products found.")
            return
        print(Fore.CYAN + "\n🔍 Search Results:")
        print("-" * 45)
        for p in results:
            print(Fore.LIGHTGREEN_EX + f"🆔 ID: {p[0]} | 🛍️ {p[1]} | 💸 R{p[2]:.2f} | 📦 Stock: {p[3]}")
        print("-" * 45)
    except Exception as e:
        print(Fore.RED + "❌ Error searching products:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# ------------------------
# Sales Functions
# ------------------------
def make_sale(product_input, quantity):
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            pid = int(product_input)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
        except ValueError:
            make_sale(cursor, product_input, quantity)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name = %s;", (product_input,))
        product = cursor.fetchone()
        if not product:
            print(Fore.RED + "❌ Product not found.")
            return
        pid, pname, price, stock = product
        if stock < quantity:
            print(Fore.RED + "❌ Insufficient stock.")
            return
        total = price * quantity
        sale_date = datetime.now()
        cursor.execute("INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (%s, %s, %s, %s);",
                    (pid, quantity, total, sale_date))
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s;", (quantity, pid))
        conn.commit()
        print(Fore.GREEN + f"✅ Sale recorded: {quantity} x {pname} for R{total:.2f}")
    except Exception as e:
        print(Fore.RED + "❌ Error making sale:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()
# market_app.py

from colorama import Fore # Assuming this is used for colors


# Assuming this function exists elsewhere in market_app.py or is imported
# def create_connection(): 
#     ...

def weekly_report():
    conn = None # Initialize conn
    try:
        conn = create_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        report = get_weekly_report(cursor) 
        
        if not report:
            print(Fore.YELLOW + "ℹ️ No sales data available.")
            return
            
        print(Fore.CYAN + "\n📊 Weekly Sales Report:")
        print("-" * 55)
        
        for r in report:
            print(Fore.LIGHTGREEN_EX + f"🛍️ {r[0]} | 🧾 Sold: {r[1]} | 💰 Revenue: R{r[2]:.2f}")
            
        print("-" * 55)
        
    except Exception as e:
        print(Fore.RED + "❌ Error generating report:", e)
        
    finally:
        if conn:
            cursor.close()
            conn.close()
            
            
            
            

def export_report_to_csv():
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        # cursor.execute("""
        #     SELECT p.name, so.name, so.location, p.price, p.stock,
        #     SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
        #     FROM products p
        #     JOIN stall_owners so ON p.owner_id = so.id
        #     LEFT JOIN sales s ON s.product_id = p.id
        #     GROUP BY p.id, p.name, so.name, so.location, p.price, p.stock
        #     ORDER BY so.name, p.name;
        # """)
        
        export_report_to_csv_db(cursor)
        
    
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[
            "Product", "Owner", "Location", "Price per Item", "Current Stock", "Total Sold", "Total Revenue"
        ])
        filename = f"weekly_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False)
        print(Fore.GREEN + f"✅ Weekly report exported to {filename}")
    except Exception as e:
        print(Fore.RED + "❌ Error exporting report:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# ------------------------
# Main App
# ------------------------
def main():
    print(Fore.GREEN + "🌍 Sawubona! Welcome to Mzansi Market Tracker!")
    create_tables()

    owner_id = None
    while not owner_id:
        print(Fore.CYAN + "\n===== 👥 Stall Owner Access =====")
        print(Fore.LIGHTYELLOW_EX + "1. 🧾 Register Stall Owner")
        print("2. 🔑 Login Stall Owner")
        choice = input(Fore.LIGHTBLUE_EX + "👉 Choose an option: ")
        if choice == "1":
            owner_id = register_stall_owner()
        elif choice == "2":
            owner_id = login_stall_owner()
        else:
            print(Fore.RED + "❌ Invalid choice.")

    menu = {
        "1": "🛒 Add Product",
        "2": "📦 View Products",
        "3": "💰 Make Sale",
        "4": "📊 Weekly Report",
        "5": "📁 Export Report to CSV",
        "6": "🔍 Search Products",
        "7": "🚪 Logout",
        "8": "❌ Exit"
    }

    while True:
        print(Fore.CYAN + "\n===== 🎉 Mzansi Market Menu 🎉 =====")
        for k, v in menu.items():
            print(Fore.LIGHTYELLOW_EX + f"{k}. {v}")
        choice = input(Fore.LIGHTBLUE_EX + "\n👉 Enter your choice: ")

        if choice == "1":
            name = input("🛍️ Product name: ")
            price = float(input("💸 Price: "))
            stock = int(input("📦 Stock quantity: "))
            add_product2(owner_id, name, price, stock)
        elif choice == "2":
            view_products()
        elif choice == "3":
            pname = input("🧾 Product sold: ")
            qty = int(input("🔢 Quantity: "))
            make_sale(pname, qty)
        elif choice == "4":
            weekly_report()
        elif choice == "5":
            export_report_to_csv()
        elif choice == "6":
            search_products()
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

