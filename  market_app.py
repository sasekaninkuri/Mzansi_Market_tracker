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
            "SELECT id, name, price, stock FROM products WHERE owner_id = %s;",
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
        
        