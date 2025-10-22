import psycopg2
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

# Function to add a new stall owner
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
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Function to add a new product
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
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Function to make a sale
def make_sale(product_name, quantity):
    try:
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, stock FROM products WHERE name = %s;",
            (product_name,)
        )
        product = cursor.fetchone()

        if not product:
            print("❌ Product not found.")
            return

        product_id, stock = product
        if stock < quantity:
            print("❌ Insufficient stock.")
            return

        # Update stock
        cursor.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s;",
            (quantity, product_id)
        )
        conn.commit()
        print(f"✅ Sale made: {quantity} x {product_name}")

    except Exception as e:
        print("❌ Error making sale:", e)

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Function to generate a weekly report
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

        print("📊 Weekly Sales Report:")
        for row in report:
            print(f"Product: {row[0]}, Total Sold: {row[1]}, Total Revenue: ${row[2]:.2f}")

    except Exception as e:
        print("❌ Error generating report:", e)

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# -----------------------------
def main():
    print("🌍 Sawubona! Welcome to Mzansi Market Tracker!")

    # Step 1: Setup
    create_tables()

    # Step 2: Sample data
    owner_id = add_stall_owner("John's Fresh Produce", "Downtown Market")
    add_product(owner_id, "Apples", 0.50, 100)
    add_product(owner_id, "Bananas", 0.30, 150)

    # Step 3: Interactive menu
    menu = {
        "1": "Add Stall Owner",
        "2": "Add Product",
        "3": "View Products",
        "4": "Make Sale",
        "5": "Weekly Report",
        "6": "Exit"
    }

    while True:
        print("\n===== Mzansi Market Menu =====")
        for key, value in menu.items():
            print(f"{key}. {value}")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter stall owner name: ")
            location = input("Enter stall location: ")
            add_stall_owner(name, location)

        elif choice == "2":
            product_name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            add_product(owner_id, product_name, price, quantity)

        elif choice == "3":
            print("Viewing products... (in a real app, this would fetch from the database)")

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

# -----------------------------
if __name__ == "__main__":
    main()
