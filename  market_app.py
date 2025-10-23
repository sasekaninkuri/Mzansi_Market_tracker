import psycopg2
import csv
from datetime import datetime
from db_setup import create_tables

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mzansi_market",
            user="postgres",
            password="12345"
        )
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# =========================
# Function: Add Stall Owner
# =========================
def add_stall_owner(name, location):
    try:
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stall_owners (name, location) VALUES (%s, %s) RETURNING id;",
            (name, location)
        )
        owner_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Stall owner '{name}' added successfully with ID {owner_id}!")
        return owner_id

    except Exception as e:
        print("❌ Error adding stall owner:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()


# =====================
# Function: Add Product
# =====================
def add_product(owner_id, name, price, stock):
    try:
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;",
            (owner_id, name, price, stock)
        )
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Product '{name}' added successfully with ID {product_id}!")
        return product_id

    except Exception as e:
        print("❌ Error adding product:", e)
        return None

    finally:
        if conn:
            cursor.close()
            conn.close()


# ==================
# Function: View Products
# ==================
def view_products():
    try:
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products;")
        products = cursor.fetchall()

        if not products:
            print("ℹ️ No products found in the database.")
            return

        print("\n📦 Available Products:")
        print("-" * 40)
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: R{product[2]:.2f}, Stock: {product[3]}")
        print("-" * 40)

    except Exception as e:
        print("❌ Error viewing products:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()


# ==================
# Function: Make Sale
# ==================
def make_sale(product_name, quantity):
    try:
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id, price, stock FROM products WHERE name = %s;", (product_name,))
        product = cursor.fetchone()

        if not product:
            print("❌ Product not found.")
            return

        product_id, price, stock = product
        if stock < quantity:
            print("❌ Insufficient stock.")
            return

        total_amount = price * quantity

        # Record the sale
        cursor.execute(
            "INSERT INTO sales (product_id, quantity, total_amount) VALUES (%s, %s, %s);",
            (product_id, quantity, total_amount)
        )

        # Update stock
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s;", (quantity, product_id))
        conn.commit()
        print(f"✅ Sale recorded: {quantity} x {product_name} for R{total_amount:.2f}")

    except Exception as e:
        print("❌ Error making sale:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()


# =======================
# Function: Weekly Report
# =======================
def weekly_report():
    try:
        conn = get_connection()
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
            print("ℹ️ No sales data available for this week.")
            return

        print("\n📊 Weekly Sales Report:")
        print("-" * 50)
        for row in report:
            print(f"Product: {row[0]}, Total Sold: {row[1]}, Total Revenue: R{row[2]:.2f}")
        print("-" * 50)

    except Exception as e:
        print("❌ Error generating report:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()
            
            
            
            
def export_report_to_csv(filename="weekly_report.csv"):
    try:
        conn = get_connection()
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
            print("ℹ️ No sales data available to export.")
            return

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Product", "Total Sold", "Total Revenue"])
            for row in report:
                writer.writerow([row[0], row[1], f"R{row[2]:.2f}"])

        print(f"✅ Weekly report exported successfully to {filename}!")

    except Exception as e:
        print("❌ Error exporting report to CSV:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()          


# ==================
# Main Program Menu
# ==================
def main():
    print("🌍 Sawubona! Welcome to Mzansi Market Tracker!")

    # Create tables if not exist
    create_tables()

    menu = {
        "1": "Add Stall Owner",
        "2": "Add Product",
        "3": "View Products",
        "4": "Make Sale",
        "5": "Weekly Report",
        "6": "Exit"
    }

    current_owner_id = None

    while True:
        print("\n===== Mzansi Market Menu =====")
        for key, value in menu.items():
            print(f"{key}. {value}")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter stall owner name: ")
            location = input("Enter stall location: ")
            current_owner_id = add_stall_owner(name, location)

        elif choice == "2":
            if not current_owner_id:
                print("⚠️ Please add a stall owner first.")
                continue
            product_name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            add_product(current_owner_id, product_name, price, quantity)

        elif choice == "3":
            view_products()

        elif choice == "4":
            product_name = input("Enter product sold: ")
            quantity = int(input("Enter quantity sold: "))
            make_sale(product_name, quantity)

        elif choice == "5":
            weekly_report()

        elif choice == "6":
            print("Exiting the program. Hamba kahle! 👋")
            break

        else:
            print("❌ Invalid choice. Please try again.")


# Run Program
if __name__ == "__main__":
    main()

