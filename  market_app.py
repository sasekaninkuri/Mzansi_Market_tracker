import psycopg2
import csv
import hashlib
from datetime import datetime
from db_setup import create_tables, create_connection
import pandas as pd

# ------------------------
# Password hashing
# ------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------------
# Stall Owner Registration/Login
# ------------------------
def register_stall_owner():
    name = input("Enter stall owner name: ")
    location = input("Enter stall location: ")
    username = input("Create a username: ")
    password = input("Create a password: ")
    hashed_pw = hash_password(password)

    try:
        conn = create_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stall_owners (name, location, username, password) VALUES (%s, %s, %s, %s) RETURNING id;",
            (name, location, username, hashed_pw)
        )
        owner_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Stall owner '{name}' registered successfully!")
        return owner_id
    except psycopg2.errors.UniqueViolation:
        print("❌ Username already exists.")
    except Exception as e:
        print("❌ Error registering stall owner:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()
    return None

def login_stall_owner():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    hashed_pw = hash_password(password)

    try:
        conn = create_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name FROM stall_owners WHERE username = %s AND password = %s;",
            (username, hashed_pw)
        )
        user = cursor.fetchone()
        if user:
            print(f"✅ Welcome back, {user[1]}!")
            return user[0]
        else:
            print("❌ Invalid username or password.")
            return None
    except Exception as e:
        print("❌ Error during login:", e)
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
        cursor.execute(
            "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;",
            (owner_id, name, price, stock)
        )
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Product '{name}' added successfully!")
        return product_id
    except Exception as e:
        print("❌ Error adding product:", e)
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
        cursor.execute("SELECT id, name, price, stock FROM products;")
        products = cursor.fetchall()
        if not products:
            print("ℹ️ No products found.")
            return
        print("\n📦 Available Products:")
        print("-" * 40)
        for p in products:
            print(f"ID: {p[0]}, Name: {p[1]}, Price: R{p[2]:.2f}, Stock: {p[3]}")
        print("-" * 40)
    except Exception as e:
        print("❌ Error viewing products:", e)
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
        term = input("Enter product name or ID to search: ")
        try:
            pid = int(term)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
        except ValueError:
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name ILIKE %s;", (f"%{term}%",))
        results = cursor.fetchall()
        if not results:
            print("ℹ️ No matching products found.")
            return
        print("\n🔍 Search Results:")
        print("-" * 40)
        for p in results:
            print(f"ID: {p[0]}, Name: {p[1]}, Price: R{p[2]:.2f}, Stock: {p[3]}")
        print("-" * 40)
    except Exception as e:
        print("❌ Error searching products:", e)
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
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name = %s;", (product_input,))
        product = cursor.fetchone()
        if not product:
            print("❌ Product not found.")
            return
        pid, pname, price, stock = product
        if stock < quantity:
            print("❌ Insufficient stock.")
            return
        total = price * quantity
        sale_date = datetime.now()
        cursor.execute("INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (%s, %s, %s, %s);",
                       (pid, quantity, total, sale_date))
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s;", (quantity, pid))
        conn.commit()
        print(f"✅ Sale recorded: {quantity} x {pname} for R{total:.2f}")
    except Exception as e:
        print("❌ Error making sale:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def weekly_report():
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name;
        """)
        report = cursor.fetchall()
        if not report:
            print("ℹ️ No sales data available.")
            return
        print("\n📊 Weekly Sales Report:")
        print("-" * 50)
        for r in report:
            print(f"Product: {r[0]}, Total Sold: {r[1]}, Total Revenue: R{r[2]:.2f}")
        print("-" * 50)
    except Exception as e:
        print("❌ Error generating report:", e)
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
        cursor.execute("""
            SELECT p.name, so.name, so.location, p.price, p.stock,
            SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
            FROM products p
            JOIN stall_owners so ON p.owner_id = so.id
            LEFT JOIN sales s ON s.product_id = p.id
            GROUP BY p.id, p.name, so.name, so.location, p.price, p.stock
            ORDER BY so.name, p.name;
        """)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[
            "Product", "Owner", "Location", "Price per Item", "Current Stock", "Total Sold", "Total Revenue"
        ])
        filename = f"weekly_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Weekly report exported to {filename}")
    except Exception as e:
        print("❌ Error exporting report:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# ------------------------
# Main App
# ------------------------
def main():
    print("🌍 Welcome to Mzansi Market Tracker!")
    create_tables()

    owner_id = None
    while not owner_id:
        print("\n1. Register Stall Owner")
        print("2. Login Stall Owner")
        choice = input("Choose an option: ")
        if choice == "1":
            owner_id = register_stall_owner()
        elif choice == "2":
            owner_id = login_stall_owner()
        else:
            print("❌ Invalid choice.")

    menu = {
        "1": "Add Product",
        "2": "View Products",
        "3": "Make Sale",
        "4": "Weekly Report",
        "5": "Export Weekly Report to CSV",
        "6": "Search Products",
        "7": "Logout",
        "8": "Exit"
    }

    while True:
        print("\n===== Mzansi Market Menu =====")
        for k, v in menu.items():
            print(f"{k}. {v}")
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Product name: ")
            price = float(input("Price: "))
            stock = int(input("Stock quantity: "))
            add_product(owner_id, name, price, stock)
        elif choice == "2":
            view_products()
        elif choice == "3":
            pname = input("Product sold: ")
            qty = int(input("Quantity: "))
            make_sale(pname, qty)
        elif choice == "4":
            weekly_report()
        elif choice == "5":
            export_report_to_csv()
        elif choice == "6":
            search_products()
        elif choice == "7":
            print("👋 Logging out...")
            main()
            break
        elif choice == "8":
            print("👋 Exiting program. Hamba kahle!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
