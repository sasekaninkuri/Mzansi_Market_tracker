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

    try:
        cursor = conn.cursor()

        # Create stall_owners table
        create_stall_owners = """
        CREATE TABLE IF NOT EXISTS stall_owners (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            location VARCHAR(150)
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

        # Execute SQL commands
        cursor.execute(create_stall_owners)
        cursor.execute(create_products)
        cursor.execute(create_sales)

        # Commit changes
        conn.commit()
        print("✅ Tables created successfully!")

    except Exception as e:
        print("❌ Error creating tables:", e)

    finally:
        cursor.close()
        conn.close()
        print("✅ Database setup complete.")

# Run the function
create_tables()

