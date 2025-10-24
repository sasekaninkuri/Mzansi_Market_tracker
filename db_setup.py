import psycopg2
from colorama import Fore, init
from datetime import datetime
import hashlib

init(autoreset=True)

# ------------------------
# Database Setup
# ------------------------
def create_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mzansi_market",
            user="postgres",
            password="12345"  # <-- Replace with your password
        )
        return conn
    except Exception as e:
        print(Fore.RED + "❌ Error connecting to database:", str(e))
        return None


def create_tables():
    conn = create_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stall_owners (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            owner_id INT REFERENCES stall_owners(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INT DEFAULT 0
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            product_id INT REFERENCES products(id) ON DELETE CASCADE,
            quantity INT DEFAULT 1,
            total_amount DECIMAL(10,2),
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        print(Fore.GREEN + "✅ Tables created successfully!")
    except Exception as e:
        print(Fore.RED + "❌ Error creating tables:", e)
    finally:
        cursor.close()
        conn.close()


# ------------------------
# Helper Functions
# ------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------------
# Stall Owner Logic
# ------------------------
def register_stall_owner(name, location, username, password):
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


def login_stall_owner(username, password):
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
# Product Logic
# ------------------------
def add_product(owner_id, name, price, stock):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;",
            (owner_id, name, price, stock)
        )
        conn.commit()
        print(Fore.GREEN + f"✅ Product '{name}' added successfully!")
    except Exception as e:
        print(Fore.RED + "❌ Error adding product:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_all_products():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products;")
    products = cursor.fetchall()
    conn.close()
    return products


def search_products(term):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        pid = int(term)
        cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
    except ValueError:
        cursor.execute("SELECT id, name, price, stock FROM products WHERE name ILIKE %s;", (f"%{term}%",))
    results = cursor.fetchall()
    conn.close()
    return results


# ------------------------
# Sales Logic
# ------------------------
def make_sale(product_input, quantity):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        try:
            pid = int(product_input)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
        except ValueError:
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
        cursor.execute(
            "INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (%s, %s, %s, %s);",
            (pid, quantity, total, sale_date)
        )
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s;", (quantity, pid))
        conn.commit()
        print(Fore.GREEN + f"✅ Sale recorded: {quantity} x {pname} for R{total:.2f}")
    except Exception as e:
        print(Fore.RED + "❌ Error making sale:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_weekly_report():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, SUM(s.quantity), SUM(s.total_amount)
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name;
    """)
    report = cursor.fetchall()
    conn.close()
    return report


def get_report_data_for_csv():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, so.name, so.location, p.price, p.stock,
        SUM(s.quantity), SUM(s.total_amount)
        FROM products p
        JOIN stall_owners so ON p.owner_id = so.id
        LEFT JOIN sales s ON s.product_id = p.id
        GROUP BY p.id, p.name, so.name, so.location, p.price, p.stock
        ORDER BY so.name, p.name;
    """)
    data = cursor.fetchall()
    conn.close()
    return data
