import psycopg2
from db_setup import create_tables

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="12345"
    )
    return conn 
pass

# Function to add a new stall owner
def add_stall_owner(name, location):
    try:
        # Attempt to get a connection (will raise exception if fails)
        conn = get_connection()
        cursor = conn.cursor()

        # Insert new stall owner
        cursor.execute(
            "INSERT INTO stall_owners (name, location) VALUES (%s, %s) RETURNING id;",
            (name, location)
        )
        owner_id = cursor.fetchone()[0]  # Get the generated id
        conn.commit()
        print(f"✅ Stall owner '{name}' added successfully with ID {owner_id}!")
        return owner_id

    except Exception as e:
        print("❌ Error adding stall owner:", e)

    finally:
        # Close cursor and connection safely
        try:
            cursor.close()
            conn.close()
        except:
            pass

        

def add_product(owner_id, name, price, stock):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch products for the given owner_id
        cursor.execute(
            "INSERT INTO, name, price, stock FROM products WHERE owner_id = %s;",
            (owner_id,)
        )
        products = cursor.fetchall()
        return products

    except Exception as e:
        print("❌ Error fetching products:", e)
        return []

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
        
        def make_sale(product_name, quantity):
            conn = get_connection()
            if not conn:
                return

            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, stock) VALUES (%s, %s) RETURNING id;",
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
                cursor.close()
                conn.close()
                
        def weekly_report():
                    conn = get_connection()
                    if not conn:
                        return

                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO sales (product_id, quantity, total_amount, sale_date)
                            VALUES (%s, %s, %s, NOW());
                        """)
                        report = cursor.fetchall()
                        print("📊 Weekly Sales Report:")
                        for row in report:
                            print(f"Product: {row[0]}, Total Sold: {row[1]}, Total Revenue: ${row[2]:.2f}")
                    except Exception as e:
                        print("❌ Error generating report:", e)
                    finally:
                        cursor.close()
                        conn.close()
                        
# 🥭 Mzansi Market Tracker - Demo Version

def create_tables():
    print("📊 Tables created successfully!")

def add_stall_owner(name, location):
    print(f"👨‍🌾 Stall owner added: {name} at {location}")
    return 1  # Mock owner ID for testing

def add_product(owner_id, product_name, price, quantity):
    print(f"🍎 Product added: {product_name} | Owner ID: {owner_id} | Price: R{price} | Stock: {quantity}")

def make_sale(product_name, quantity):
    print(f"🛒 Sale recorded: {quantity} x {product_name}")

def weekly_report():
    print("📅 Weekly report generated successfully!")

def main():
    print("🌍 Sawubona! Welcome to Mzansi Market Tracker!")

    # Step 1: Create tables
    create_tables()

    # Step 2: Example usage
    owner_id = add_stall_owner("John's Fresh Produce", "Downtown Market")
    add_product(owner_id, "Apples", 0.50, 100)
    add_product(owner_id, "Bananas", 0.30, 150)

    # Step 3: Record a sale
    make_sale("Apples", 10)

    # Step 4: Generate weekly report
    weekly_report()

    # TODO: Add interactive menu in the future
    print("\n✅ Example data added and processed successfully!")

# Run program
if __name__ == "__main__":
    main()
