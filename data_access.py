import sqlite3
import requests
import hashlib
import os
import csv
from datetime import datetime
import csv
import json
from tkinter import messagebox

# Fetch API Keys

try:
    with open("config.json") as config_file:
        config = json.load(config_file)
        api_key = config.get("EXCHANGE_RATE_API_KEY")
except FileNotFoundError:
    print("Error: config.json file not found.")
    api_key = None

currency_pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/CHF": "USDCHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X"
}

# Contains functions to interact with the database

DB_FILE = 'main.db'

# function to create customer account
def create_account(dob, first_name, surname, username, password, email, phone):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Generate salt and hash password
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((salt + password).encode()).hexdigest()

        cursor.execute('''
        INSERT INTO customers (dob, first_name, surname, username, password, email, phone, salt) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
        (dob, first_name, surname, username, hashed_password, email, phone, salt))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error creating account: {e}")
        return False
    finally:
        conn.close()

# function to create staff account
def create_account_staff(dob, first_name, surname, username, password, email, phone):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Generate salt and hash password
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((salt + password).encode()).hexdigest()

        cursor.execute('''
        INSERT INTO staff (dob, first_name, surname, username, password, salt, email, phone) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
        (dob, first_name, surname, username, hashed_password, salt, email, phone))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error creating account: {e}")
        return False
    finally:
        conn.close()
        
# function to get customer login details
def get_login_details(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Retrieve stored hash and salt
        cursor.execute('''
            SELECT password, salt 
            FROM customers 
            WHERE username = ?''', (username,))
        result = cursor.fetchone()

        if result:
            stored_hash, salt = result
            input_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return input_hash == stored_hash
        return False

    except Exception as e:
        print(f"Error verifying login: {e}")
        return False
    finally:
        conn.close()

# function to get staff login details
def get_login_details_staff(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Retrieve stored hash and salt
        cursor.execute('''
            SELECT password, salt 
            FROM staff 
            WHERE username = ?''', (username,))
        result = cursor.fetchone()

        if result:
            stored_hash, salt = result
            input_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return input_hash == stored_hash
        return False

    except Exception as e:
        print(f"Error verifying login: {e}")
        return False
    finally:
        conn.close()

# function to store customer order
def store_order(customer_id, currency_pair, order_type, amount, balance, price, order_time):

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (customer_id, currency_pair, order_type, amount, balance, price, order_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, currency_pair, order_type, amount, balance, price, order_time))

        # Commit the transaction
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e  # Re-raise the exception to handle it in the caller function

# function to retreieve customer id
def get_customer_id(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Retrieve the stored hash and salt for the given username
    cursor.execute('''
        SELECT customer_id, password, salt
        FROM customers 
        WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()

    if result:
        customer_id, stored_hash, salt = result
        # Hash the input password with the stored salt
        input_hash = hashlib.sha256((salt + password).encode()).hexdigest()

        # Compare the hashed input password with the stored hash
        if input_hash == stored_hash:
            return customer_id  # Return the customer_id if the password is correct
        else:
            return
    else:
        return
    
# function to retreieve customer id
def get_staff_id(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Retrieve the stored hash and salt for the given username
    cursor.execute('''
        SELECT staff_id, password, salt
        FROM staff 
        WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()

    if result:
        staff_id, stored_hash, salt = result
        # Hash the input password with the stored salt
        input_hash = hashlib.sha256((salt + password).encode()).hexdigest()

        # Compare the hashed input password with the stored hash
        if input_hash == stored_hash:
            return staff_id  # Return the staff_id if the password is correct
        else:
            return
    else:
       return

# function to get customer balance
def get_customer_balance(order_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT balance
        FROM orders 
        WHERE order_id = ?
    ''', (order_id,)) 
    
    result = cursor.fetchone()

    if result:
    
        customer_balance = result[0]

        customer_balance = int(customer_balance) if customer_balance is not None else 0
        customer_balance = round(float(result[0]), 2)  # Fixed rounding
        return customer_balance
    else:
        raise ValueError("Invalid order_id")
    
# function to get customer balance
def get_customer_balance_display(customer_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT balance
        FROM customers 
        WHERE customer_id = ?
    ''', (customer_id,)) 
    
    result = cursor.fetchone()

    if result:
    
        customer_balance = result[0]

        customer_balance = int(customer_balance) if customer_balance is not None else 0
        round(customer_balance, 2)

        return customer_balance
    else:
        raise ValueError("Invalid customer_id")

# function to get customer name
def get_customer_name(customer_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT first_name
        FROM customers 
        WHERE customer_id = ?
    ''', (customer_id,)) 
    
    result = cursor.fetchone()

    if result:
    
        customer_name = result[0]

        return customer_name
    else:
        return
    
# function to get staff name
def get_staff_name(staff_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT first_name
        FROM staff 
        WHERE staff_id = ?
    ''', (staff_id,)) 
    
    result = cursor.fetchone()

    if result:
    
        customer_name = result[0]

        return customer_name
    else:
        return
    
    
# function to fetch orders for one customer
def fetch_orders(customer_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT currency_pair, order_type, amount, price, order_time FROM orders WHERE customer_id = ?', (customer_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

# function to fect all the orders for all customers
def fetch_all_orders():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT order_id, customer_id, currency_pair, 
               order_type, amount, price, order_time 
        FROM orders
    ''')
    orders = cursor.fetchall()
    conn.close()
    return orders

# Helper function for feteching orders
def fetch_all_orders_primary_key(customer_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE customer_id = ?', (customer_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

# Function to fetch history for one customer
def fetch_history(customer_id):
    conn = sqlite3.connect("main.db")  
    cursor = conn.cursor()
    cursor.execute("SELECT currency_pair, order_type, amount, price, order_time_close, pip_difference, profit_loss FROM history  WHERE customer_id = ?", (customer_id,))
    history_records = cursor.fetchall()
    conn.close()
    return history_records

# Function to fetc history for all customers
def fetch_all_history():
    conn = sqlite3.connect("main.db")  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ")
    history_records = cursor.fetchall()
    conn.close()
    return history_records

# function to fetch customers
def fetch_customers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT customer_id, dob, first_name, surname, email, phone, username, balance FROM customers')
    customers = cursor.fetchall()
    conn.close()
    return customers

# Function to get exchange rates using API
def get_exchange_rate(base, target):
    if not api_key:
        print("Error: API key not found in config.json.")
        return None
    
    url = f"https://api.exchangerate.host/convert?from={base}&to={target}&amount=1&access_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('result', None)
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

# Function to close and save trades to history
def close_trade(order_id, closing_price, customer_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Fetch customer balance (assuming get_customer_balance exists)
        balance = get_customer_balance(order_id)

        # Fetch order details
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found.")

        # Extract order details
        open_price = float(order[6])
        major = order[2]
        amount = round(float(order[4]), 2)  # Trade amount (in GBP)
        order_type = order[3]

        # Use currency_pairs dictionary to find the ticker
        if major not in currency_pairs:
            raise ValueError(f"Unknown currency pair: {major}")
        major_ticker = currency_pairs[major]

        # Step 1: Determine pip multiplier
        if "JPY" in major_ticker:  # If JPY pair, use 100 for pip calculation
            pip_multiplier = 100
        else:
            pip_multiplier = 10000  # For most other pairs

        # Step 2: Calculate pip difference
        pip_difference = (closing_price - open_price) * pip_multiplier

        # Step 3: Calculate profit/loss in the quote currency (USD/CHF/other)
        profit_loss_quote_currency = pip_difference * (amount / pip_multiplier)

        # Step 4: Convert to GBP for non-GBP pairs
        if major != "GBP/USD" and major != "GBP/CHF":  # Check if the pair involves GBP
            # Get exchange rates to convert profit/loss into GBP
            quote_currency = major[4:7]  # Extract the quote currency (e.g., USD or CHF)
            rate_quote_to_gbp = get_exchange_rate(quote_currency, 'GBP')  # Fetch quote to GBP rate

            # Convert the P/L from the quote currency to GBP
            if rate_quote_to_gbp:
                profit_loss_gbp = profit_loss_quote_currency * rate_quote_to_gbp
            else:
                raise ValueError(f"Failed to fetch exchange rate for {quote_currency} to GBP.")
        else:
            # If the pair involves GBP directly, profit/loss in GBP is already correct
            profit_loss_gbp = profit_loss_quote_currency

        # Adjust for SELL orders
        if order_type == 'SELL':
            profit_loss_gbp = -profit_loss_gbp

        # Round the result to 2 decimal places
        profit_loss_gbp = round(profit_loss_gbp, 2)

        # Update balance if necessary
        new_balance = balance + profit_loss_gbp

        new_balance = round(new_balance, 2)
        profit_loss_gbp = round(profit_loss_gbp, 2)
        pip_difference = round(pip_difference, 1)
        closing_price = round(closing_price, 4)
        # Insert into history
        cursor.execute('''
            INSERT INTO history (order_id, currency_pair, customer_id, order_type, 
                                 amount, price, order_time_close, pip_difference, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
        ''', (order[0], major, order[1], order_type, amount, closing_price, #was amount gbp
              pip_difference, profit_loss_gbp))

        # Delete from orders and update balance
        cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
        cursor.execute('UPDATE customers SET balance = ? WHERE customer_id = ?', 
                      (new_balance, customer_id))

        conn.commit()
        print(f"Trade closed. Old Balance: £{balance} New Balance: £{new_balance:.2f} Profit/loss: £{profit_loss_gbp}")

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


# Function to get currency pairs from db
def get_currency_pair(order_id):

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT currency_pair FROM orders WHERE order_id = ?', (order_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        raise ValueError("Currency pair not found for the given order ID.")
    except Exception as e:
        raise e

### Payment system ###

# Function to add a card provider
def add_card_provider(card_provider_name):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT card_provider_id FROM card_provider WHERE card_provider_name = ?", (card_provider_name,))

    provider_result = cursor.fetchone()

    if provider_result:
        provider_id = provider_result[0]
    else:
        cursor.execute("INSERT INTO card_provider (card_provider_name) VALUES (?)", (card_provider_name,))
        provider_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return provider_id

# Function to add a billing address
def add_billing_address(building_number, line1, line2, postcode):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO billing_address (building_number, billing_address_line_1, billing_address_line_2, billing_postcode)
    VALUES (?, ?, ?, ?)''', (building_number, line1, line2, postcode))

    address_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return address_id

# Function to add a payment card
def add_payment_card(cardholder_name, card_number, start_date, end_date, card_provider_id, billing_address_id, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Generate salt and hash the CVV
        salt = os.urandom(16).hex()
        hashed_cvv = hashlib.sha256((salt + password).encode()).hexdigest()

        cursor.execute('''
        INSERT INTO payment_card (cardholder_name, card_number, start_date, end_date, card_provider_id, billing_address_id, password, salt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (cardholder_name, card_number, start_date, end_date, card_provider_id, billing_address_id, hashed_cvv, salt))

        card_id = cursor.lastrowid
        conn.commit()
        return card_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Function to link payment card to a customer
def link_card_to_customer(payment_card_id, customer_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customer_payment_card (payment_card_id, customer_id) VALUES (?, ?)", (payment_card_id, customer_id))

    conn.commit()
    conn.close()

# function to retrieve customer cards from
def get_customer_cards(customer_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT pc.cardholder_name, pc.card_number, pc.end_date
    FROM payment_card pc
    JOIN customer_payment_card cpc ON pc.payment_card_id = cpc.payment_card_id
    WHERE cpc.customer_id = ?
    ''', (customer_id,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {"cardholder_name": row[0], "card_number": row[1], "end_date": row[2]}
        for row in rows
    ]

# Function to update cards after editing only
def update_card(card_id, cardholder_name, card_number, start_date, end_date, card_provider, 
                building_number, line1, line2, postcode, password):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 1. Handle Card Provider
        cursor.execute("SELECT card_provider_id FROM card_provider WHERE card_provider_name = ?", (card_provider,))
        provider_result = cursor.fetchone()
        
        if provider_result:
            card_provider_id = provider_result[0]
        else:
            cursor.execute("INSERT INTO card_provider (card_provider_name) VALUES (?)", (card_provider,))
            card_provider_id = cursor.lastrowid

        # 2. Update Billing Address
        cursor.execute('''
        UPDATE billing_address
        SET building_number = ?, billing_address_line_1 = ?, billing_address_line_2 = ?, billing_postcode = ?
        WHERE billing_address_id = (
            SELECT billing_address_id 
            FROM payment_card 
            WHERE payment_card_id = ?
        )
        ''', (building_number, line1, line2, postcode, card_id))

        # Generate Salt and Hash CVV
        salt = os.urandom(16).hex()
        hashed_cvv = hashlib.sha256((salt + password).encode()).hexdigest()

        #  Update Payment Card with Hashed CVV
        cursor.execute('''
        UPDATE payment_card
        SET cardholder_name = ?,
            card_number = ?,
            start_date = ?,
            end_date = ?,
            card_provider_id = ?,
            password = ?,
            salt = ?
        WHERE payment_card_id = ?
        ''', (cardholder_name, card_number, start_date, end_date, card_provider_id, hashed_cvv, salt, card_id))

        conn.commit()
        print("Card updated successfully with hashed CVV")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Error updating card: {str(e)}")
    finally:
        if conn:
            conn.close()

# function to retrive card id from db
def get_card_id(cardholder_name):

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT payment_card_id
        FROM payment_card
        WHERE cardholder_name = ?
        ''', (cardholder_name,))

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"No card found for {cardholder_name}")
    
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        raise

    finally:
        if conn:
            conn.close()

# function to delete card from db
def delete_card_from_db(card_id):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Delete the billing address first
    cursor.execute('''
    DELETE FROM billing_address
    WHERE billing_address_id = (SELECT billing_address_id FROM payment_card WHERE payment_card_id = ?)
    ''', (card_id,))

    # Then delete the payment card 
    cursor.execute('''
    DELETE FROM payment_card WHERE payment_card_id = ?
    ''', (card_id,))

    conn.commit()
    conn.close()

# function to update customer balance (add)
def update_balance_add(customer_id, amount):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE customers
    SET balance = balance + ?
    WHERE customer_id = ?
    ''', (amount, customer_id))

    conn.commit()
    conn.close()

# function to update customer balance (subtract)
def update_balance_subtract(customer_id, amount):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE customers
    SET balance = balance - ?
    WHERE customer_id = ?
    ''', (amount, customer_id))

    conn.commit()
    conn.close()

def calculate_pl(order_id, closing_price, customer_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Fetch customer balance (assuming get_customer_balance exists)
        balance = get_customer_balance(order_id)

        # Fetch order details
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found.")

        # Extract order details
        open_price = float(order[6])
        major = order[2]
        amount = round(float(order[4]), 2)  # Trade amount (in GBP)
        order_type = order[3]

        # Use currency_pairs dictionary to find the ticker
        if major not in currency_pairs:
            raise ValueError(f"Unknown currency pair: {major}")
        major_ticker = currency_pairs[major]

        # Step 1: Determine pip multiplier
        if "JPY" in major_ticker:  # If JPY pair, use 100 for pip calculation
            pip_multiplier = 100
        else:
            pip_multiplier = 10000  # For most other pairs

        # Step 2: Calculate pip difference
        pip_difference = (closing_price - open_price) * pip_multiplier

        # Step 3: Calculate profit/loss in the quote currency (USD/CHF/other)
        profit_loss_quote_currency = pip_difference * (amount / pip_multiplier)

        # Step 4: Convert to GBP for non-GBP pairs
        if major != "GBP/USD" and major != "GBP/CHF":  # Check if the pair involves GBP
            # Get exchange rates to convert profit/loss into GBP
            quote_currency = major[4:7]  # Extract the quote currency (e.g. USD or CHF)
            rate_quote_to_gbp = get_exchange_rate(quote_currency, 'GBP')  # Fetch quote to GBP rate

            # Convert the P/L from the quote currency to GBP
            if rate_quote_to_gbp:
                profit_loss_gbp = profit_loss_quote_currency * rate_quote_to_gbp
            else:
                raise ValueError(f"Failed to fetch exchange rate for {quote_currency} to GBP.")
        else:
            # If the pair involves GBP directly, profit/loss in GBP is already correct
            profit_loss_gbp = profit_loss_quote_currency

        # Adjust for SELL orders
        if order_type == 'SELL':
            profit_loss_gbp = -profit_loss_gbp

        # Round the result to 2 decimal places
        profit_loss_gbp = round(profit_loss_gbp, 2)

        # Update balance if necessary
        new_balance = balance + profit_loss_gbp

        new_balance = round(new_balance, 2)
        profit_loss_gbp = round(profit_loss_gbp, 2)
        pip_difference = round(pip_difference, 1)
        closing_price = round(closing_price, 4)

        print(f"Rate (Quote to {quote_currency} for {major}): {rate_quote_to_gbp}")
        print(f"Pip Difference: {pip_difference}")
        print(f"Profit/Loss in Quote Currency {quote_currency}: {profit_loss_quote_currency}")
        print(f"Profit/Loss in GBP: {profit_loss_gbp}")


    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

    return profit_loss_gbp

# Function to export data to csv
def export_history_to_csv(customer_id=None, filename="trade_history.csv"):
    try:
        # Fetch data
        if customer_id:
            records = fetch_history(customer_id)
        else:
            records = fetch_all_history()

        # Define CSV headers
        headers = [
            "Currency Pair", "Order Type", "Amount", 
            "Price", "Close Time", "Pip Difference", "Profit/Loss"
        ]

        # Write to CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for record in records:
                writer.writerow(record)
        return True
    except Exception as e:
        print(f"CSV Export Error: {e}")
        return False

