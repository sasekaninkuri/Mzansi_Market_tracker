import psycopg2

# Function to create connection
def create_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mzansi_market",
            user="postgres",
            password="12345"  # <-- Replace with your actual password
        )
        return conn
    except Exception as e:
        print("❌ Error connecting to database:", e)
        return None

# Function to create the tables
def create_tables():
    conn = create_connection()
    if not conn:
        return
    with conn:
        cursor = conn.cursor()

        # Create stall_owners table with username & password
        create_stall_owners = """
        CREATE TABLE IF NOT EXISTS stall_owners (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
        """

        # Create products table
        create_products = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            owner_id INT REFERENCES stall_owners(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INT DEFAULT 0
        );
        """

        # Create sales table
        create_sales = """
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            product_id INT REFERENCES products(id) ON DELETE CASCADE,
            quantity INT DEFAULT 1,
            total_amount DECIMAL(10,2),
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        


def add_stall_owner(cursor, name, location, username, hashed_pw):
    cursor.execute(
        "INSERT INTO stall_owners (name, location, username, password) VALUES (%s, %s, %s, %s)",
        (name, location, username, hashed_pw)
    )


def login_stall_owner2(cursor, username, hashed_pw):
    cursor.execute(
        "SELECT id, name FROM stall_owners WHERE username = %s AND password = %s;",
        (username, hashed_pw)
    )

def add_product2(cursor, owner_id, name, price, stock):
        cursor.execute(
            "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s)",
            (owner_id, name, price, stock)
        )

def view_product2(cursor, products):
    cursor.execute("SELECT id, name, price, stock FROM products;")
    products = cursor.fetchall()
    

def search_products(cursor, term , pid):
    cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (pid,))
    cursor.execute("SELECT id, name, price, stock FROM products WHERE name ILIKE %s;", (f"%{term}%",))
    search_products = cursor.fetchall()


def make_sale(cursor, product_input, quantity):
    cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (quantity,))
    cursor.execute("SELECT id, name, price, stock FROM products WHERE name = %s;", (product_input,))
    product = cursor.fetchone()

# db_setup.py

def get_weekly_report(cursor, weekly_rshow): 
    """ Executes the weekly sales report query and fetches the results. """
    # 1. EXECUTE the query first (must be before fetchall)
    cursor.execute("""
        SELECT p.name, SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_revenue DESC;
    """)
    weekly_rshow = cursor.fetchall()

    return weekly_rshow


def export_report_to_csv_db(cursor):
    """ Executes the comprehensive report query and fetches the results for CSV export. """
    cursor.execute("""
        SELECT p.name, so.name, so.location, p.price, p.stock,
        COALESCE(SUM(s.quantity), 0) AS total_sold, COALESCE(SUM(s.total_amount), 0.00) AS total_revenue
        FROM products p
        JOIN stall_owners so ON p.owner_id = so.id
        LEFT JOIN sales s ON s.product_id = p.id
        GROUP BY p.id, p.name, so.name, so.location, p.price, p.stock
        ORDER BY so.name, p.name;
    """)
    return cursor.fetchall()