import sqlite3
import hashlib
import os

DB_FILE = 'main.db'

def master_login():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if the admin user already exists
    cursor.execute("SELECT COUNT(*) FROM staff WHERE username = 'admin'")
    exists = cursor.fetchone()[0]

    if not exists:
        # Generate a salt and hash the password
        salt = os.urandom(16).hex()
        password = '123'  # Default password for admin
        hashed_password = hashlib.sha256((salt + password).encode()).hexdigest()

        # Insert the default login with salt and hashed password
        cursor.execute('''
        INSERT INTO staff (dob, first_name, surname, email, phone, username, password, salt)
        VALUES ('2000-01-01', 'Admin', 'User', 'admin@example.com', '0000000000', 'admin', ?, ?)
        ''', (hashed_password, salt))

        print("Default admin user created.")
    else:
        print("Admin user already exists.")

    conn.commit()
    conn.close()

def create_tables():
    # Connect to the database or create it if it doesn't exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dob DATE NOT NULL,
        first_name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL,  -- Added column
        balance REAL DEFAULT 0
    )
    ''')

    # Create the staff table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dob DATE NOT NULL,
        first_name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL  -- Added column
    )
    ''')

    # Create the orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        currency_pair TEXT NOT NULL,       
        order_type TEXT NOT NULL,          
        amount REAL NOT NULL,
        balance REAL NOT NULL,             
        price REAL NOT NULL,               
        order_time DATETIME DEFAULT CURRENT_TIMESTAMP, 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    ''')

    # Create the history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        currency_pair TEXT NOT NULL,
        customer_id INTEGER, 
        order_type TEXT NOT NULL,          
        amount REAL NOT NULL,             
        price REAL NOT NULL,               
        order_time_close DATETIME DEFAULT CURRENT_TIMESTAMP, 
        pip_difference REAL NOT NULL,
        profit_loss REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    ''')

    # Create Payment Card table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payment_card (
        payment_card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cardholder_name TEXT NOT NULL,
        card_number INTEGER,
        start_date DATETIME,
        end_date DATETIME,
        card_provider_id INTEGER,
        billing_address_id INTEGER,
        password TEXT NOT NULL,
        salt TEXT NOT NULL,  -- Added column
        FOREIGN KEY (card_provider_id) REFERENCES card_provider(card_provider_id),
        FOREIGN KEY (billing_address_id) REFERENCES billing_address(billing_address_id)
    );
    ''')

    # Create Card Provider table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS card_provider (
        card_provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_provider_name TEXT NOT NULL
    );
    ''')

    # Create Customer Payment Card dummy table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_payment_card (
        customer_payment_card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_card_id INTEGER,
        customer_id INTEGER,
        FOREIGN KEY (payment_card_id) REFERENCES payment_card(payment_card_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    ''')

    # Create Customer Billing Address table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billing_address (
        billing_address_id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_number TEXT NOT NULL,
        billing_address_line_1 TEXT NOT NULL,
        billing_address_line_2 TEXT NOT NULL,
        billing_postcode TEXT NOT NULL
    );
    ''')

    # Call master_login to insert default admin login
    master_login()

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print("Database setup complete!")

