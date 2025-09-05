import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
import yfinance as yf 
import mplfinance as mpf
import sv_ttk
from data_access import *
from datetime import datetime
import re
import warnings
import pandas as pd
import os
import sqlite3
import subprocess
import sys
from tkinter import filedialog
from dateutil.relativedelta import relativedelta  

DB_PATH = "main.db"
SETUP_SCRIPT = "db_setup.py"

# Function to check if database exists already
def database_exists():
    if not os.path.exists(DB_PATH):
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Try to find 2 tables that should be there
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff';")
        table_exists = cursor.fetchone() is not None
        conn.close()
        return table_exists
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

# Function to only run the GUI if the databse access file is present
def run_setup_script():
    if not os.path.exists(SETUP_SCRIPT):
        print(f"Setup script {SETUP_SCRIPT} not found.")
        sys.exit(1)
    
    try:
        subprocess.run(["python", SETUP_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {SETUP_SCRIPT}: {e}")
        sys.exit(1)

if not database_exists():
    print("Database not set up. Running setup script...")
    run_setup_script()
else:
    print("Database already set up.")

# Ignore warnings for compatability with future versions of yfinance
warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")

# Function to handle login
def login():
    global customer_id, staff_id

    # get username from entry
    username = entry_username.get()
    password = entry_password.get()

    # Check if fields are filled
    if not username or not password:
        messagebox.showerror("Login Error", "All fields must be filled.")
        return

    # Check customer login
    if get_login_details(username, password):
        customer_id = get_customer_id(username, password)
        if customer_id is not None:
            customer_name = get_customer_name(customer_id)
            messagebox.showinfo("Login Successful", f"Welcome, {customer_name}.")
            open_home(customer_id)
            return

    # Check staff login
    if get_login_details_staff(username, password):
        staff_id = get_staff_id(username, password)
        if staff_id is not None:
            staff_name = get_staff_name(staff_id)
            messagebox.showinfo("Login Successful", f"Welcome, {staff_name}.")
            open_home_staff(staff_id)
            return

    # If neither customer nor staff
    messagebox.showerror("Login Error", "Invalid username or password.")

# Function to open homepage
def open_home(customer_id):

    # Get customer name
    customer_name = get_customer_name(customer_id)
    
    # Ensure name is formatted
    customer_name = customer_name.capitalize()

    # Hide the main login window
    root.withdraw()
    
    # Create a new window
    new_window = tk.Toplevel(root)
    new_window.title("Welcome")
    new_window.geometry("400x600")
    sv_ttk.set_theme("light")
    new_window.resizable(False, False) 
    
    # Add content to the home page
    home_label = tk.Label(new_window, text='Home', font=("Helvetica", 20))
    home_label.pack(padx=10, pady=20)

    welcome_label = tk.Label(new_window, text=f"Welcome {customer_name}", font=("Helvetica", 14))
    welcome_label.pack(padx=10, pady=20)
   
    # Chart button to bring up the chart configurer
    chart_button = ttk.Button(new_window, text="Chart 📊", command=chart, width=11)
    chart_button.pack(padx=10, pady=20)

    # Manage orders button to bring up the order menu
    order_button = ttk.Button(new_window, text="Orders 📝", command=lambda: [new_window.destroy(), manage_orders_window()], width=11)
    order_button.pack(padx=10, pady=20)

    # Button to add customer balance
    balance_button = ttk.Button(new_window, text="Balance 💵",command=lambda: (new_window.destroy(), balance_window()), width=11)
    balance_button.pack(padx=10, pady=20)

    # Button to view trade history
    history_button = ttk.Button(new_window, text="History ⏰", command=lambda: (new_window.destroy(), history_window()), width=11)
    history_button.pack(padx=10, pady=20)

     # Button to close the new window and bring back the login window
    close_button = ttk.Button(new_window, text="Logout", command=lambda: (new_window.destroy(), root.deiconify()), width=11)
    close_button.pack(padx=10, pady=20)

    centre_window(new_window, 400, 600) # Centre window

# function to open home page as an admin
def open_home_staff(staff_id):

    staff_name = get_staff_name(staff_id)

    # Hide the main login window
    root.withdraw()
    
    # Create a new window
    new_window = tk.Toplevel(root)
    new_window.title("Welcome")
    new_window.geometry("400x600")
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)  
    
    # Add some content to the home page
    home_label = tk.Label(new_window, text='Home', font=("Helvetica", 20))
    home_label.pack(padx=10, pady=20)

    welcome_label = tk.Label(new_window, text=f"Welcome Admin: {staff_name}", font=("Helvetica", 14))
    welcome_label.pack(padx=10, pady=20)

     # Button to close the new window and bring back the login window
    create_admin_button = ttk.Button(new_window, text="Create Staff ➕", command=lambda: (new_window.destroy(), createAccountWindowStaff()), width=11)
    create_admin_button.pack(padx=10, pady=20)
   
    # Chart button to bring up the chart configurer
    chart_button = ttk.Button(new_window, text="Chart 📊", command=chart, width=11)
    chart_button.pack(padx=10, pady=20)

    # Button to add customer balance
    balance_button = ttk.Button(new_window, text="Customers 👤", command=lambda: (new_window.destroy(), view_customers_window()), width=11)
    balance_button.pack(padx=10, pady=20)

    # Button to view customer history
    history_button = ttk.Button(new_window, text="All history ⏰", command=lambda: (new_window.destroy(), history_window_staff()), width=11)
    history_button.pack(padx=10, pady=20)

    # Button to view all current orders
    history_button = ttk.Button(new_window, text="All orders 📝", command=lambda: (new_window.destroy(), all_current_orders_window()), width=11)
    history_button.pack(padx=10, pady=20)

    # Button to close the new window and bring back the login window
    close_button = ttk.Button(new_window, text="Logout", command=lambda: (new_window.destroy(), root.deiconify()), width=11)
    close_button.pack(padx=10, pady=20)

    centre_window(new_window, 400, 600)

def chart():
    
    # Helper function to validate period-interval combinations
    def is_valid_combination(period, interval):
        short_periods = ['1d', '5d', '1mo']
        medium_periods = ['3mo', '6mo']
        long_periods = ['1y', '2y', '5y', '10y', 'ytd', 'max']

        if interval == '1m' and period not in ['1d', '5d']:
            return False
        if interval in ['5m', '15m', '30m', '60m', '1h'] and period not in short_periods + medium_periods:
            return False
        if interval in ['5d'] and period in ['1d', '5d']:
            return False
        return True

    # Function to plot graphs
    def plot_graph(major_ticker, timePeriod, timeInterval, major):
        # Destroy config window
        new_window.destroy()

        try:
            # Download yfinance data
            data = yf.download(major_ticker, period=timePeriod, interval=timeInterval)
            data.index.name = 'Date'

            # Rename columns
            column_names = ["Open", "High", "Low", "Close", "Volume"]
            data.columns = column_names[:len(data.columns)]

            # Check required columns
            required_columns = ["Open", "High", "Low", "Close", "Volume"]
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                print(f"Error: Missing required columns - {missing_columns}")
                return

            # Clean data
            for col in required_columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")
            data.dropna(subset=required_columns, inplace=True)

            # Plot candlestick chart
            mpf.plot(
                data, 
                type='candle', 
                style=custom_style, 
                title=major,
                ylabel='Price', 
                xlabel='Time', 
                datetime_format='%H:%M', 
                figsize=(10, 6),  
                scale_padding={'left': 0.11, 'top': 0.33, 'right': 0.8, 'bottom': 0.58},
            )

        except Exception as e:
            messagebox.showerror('Chart Error', 'The requested range or interval is invalid or not available for this currency pair.')

    # Function to save and plot settings
    def save_options():
        period = selected_period.get()
        interval = selected_interval.get()
        major = selected_major.get()
        major_ticker = currency_pairs[major]

        print(f"Selected Pair: {major}")
        print(f"Selected Period: {period}")
        print(f"Selected Interval: {interval}")
        print(f'Ticker value for download: {major_ticker}')

        # Validate selections
        if not period or not interval or not major:
            tk.messagebox.showerror("Input Error", "Please make sure all selections are made.")
            return

        if period not in period_options:
            tk.messagebox.showerror("Input Error", f"Invalid Period '{period}'. Please select a valid one.")
            return

        if interval not in interval_options:
            tk.messagebox.showerror("Input Error", f"Invalid Interval '{interval}'. Please select a valid one.")
            return

        if major not in major_options:
            tk.messagebox.showerror("Input Error", f"Invalid Currency Pair '{major}'.")
            return

        # Check for valid period-interval combinations
        if not is_valid_combination(period, interval):
            tk.messagebox.showerror("Invalid Range", f"The combination of Period '{period}' and Interval '{interval}' is not supported.")
            return

        # Call plot function
        plot_graph(major_ticker, period, interval, major)

    # Style
    custom_style = mpf.make_mpf_style(
        base_mpl_style='seaborn-v0_8-white',
        marketcolors=mpf.make_marketcolors(
            up='blue', down='black', 
            wick={'up': 'blue', 'down': 'black'}, 
            edge={'up': 'blue', 'down': 'black'}, 
            volume={'up': 'blue', 'down': 'black'}
        ),
        rc={'font.size': 12},
        y_on_right=True
    )

    # Options
    period_options = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    interval_options = ['1m', '5m', '15m', '30m', '60m', '1h', '1d', '5d']
    major_options = list(currency_pairs.keys())

    # Window setup
    new_window = tk.Toplevel()
    new_window.title("Configure Chart")
    new_window.geometry('300x330')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)

    # Dropdown variables
    selected_period = tk.StringVar(value=period_options[0])
    selected_interval = tk.StringVar(value=interval_options[1])
    selected_major = tk.StringVar(value=major_options[0])

    # Dropdown widgets
    tk.Label(new_window, text="Select Pair:").pack(pady=5)
    ttk.Combobox(new_window, textvariable=selected_major, values=major_options).pack(pady=5)

    tk.Label(new_window, text="Select Period:").pack(pady=5)
    ttk.Combobox(new_window, textvariable=selected_period, values=period_options).pack(pady=5)

    tk.Label(new_window, text="Select Interval:").pack(pady=5)
    ttk.Combobox(new_window, textvariable=selected_interval, values=interval_options).pack(pady=5)

    # Buttons
    ttk.Button(new_window, text="Save & Plot", command=save_options, width=10).pack(pady=10)
    ttk.Button(new_window, text="← Back", command=new_window.destroy, width=10).pack(pady=10)

    centre_window(new_window, 300, 330)


# Function to bring up account creation window
def create_account_window():
    # Create the account window
    new_window = tk.Toplevel()
    new_window.title("Create Account")
    new_window.geometry('430x520')
    sv_ttk.set_theme("light") 
    new_window.resizable(False, False)

    # Define padding and styles
    padding = {'padx': 15, 'pady': 10}

    # Add a title label
    title_label = ttk.Label(new_window, text="Create Account", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

    # First name label and entry
    label_first = ttk.Label(new_window, text="First Name:")
    label_first.grid(row=1, column=0, sticky="w", **padding)
    entry_first = ttk.Entry(new_window)
    entry_first.grid(row=1, column=1, **padding)

    # Surname label and entry
    label_second = ttk.Label(new_window, text="Surname:")
    label_second.grid(row=2, column=0, sticky="w", **padding)
    entry_second = ttk.Entry(new_window)
    entry_second.grid(row=2, column=1, **padding)

    # DOB label and entry
    label_dob = ttk.Label(new_window, text="Date of Birth (xx/xx/xxxx):")
    label_dob.grid(row=3, column=0, sticky="w", **padding)
    entry_dob = ttk.Entry(new_window)
    entry_dob.grid(row=3, column=1, **padding)

    # Email label and entry
    label_email = ttk.Label(new_window, text="Email:")
    label_email.grid(row=4, column=0, sticky="w", **padding)
    entry_email = ttk.Entry(new_window)
    entry_email.grid(row=4, column=1, **padding)

    # Phone number label and entry
    label_phone = ttk.Label(new_window, text="Phone Number:")
    label_phone.grid(row=5, column=0, sticky="w", **padding)
    entry_phone = ttk.Entry(new_window)
    entry_phone.grid(row=5, column=1, **padding)

    # Username label and entry
    label_user = ttk.Label(new_window, text="Username:")
    label_user.grid(row=6, column=0, sticky="w", **padding)
    entry_user = ttk.Entry(new_window)
    entry_user.grid(row=6, column=1, **padding)

    # Password label and entry
    label_pass = ttk.Label(new_window, text="Password:")
    label_pass.grid(row=7, column=0, sticky="w", **padding)
    entry_pass = ttk.Entry(new_window, show="*")  
    entry_pass.grid(row=7, column=1, **padding)

    # Password reentry label and entry
    reentry_label_pass = ttk.Label(new_window, text="Re-enter password:")
    reentry_label_pass.grid(row=8, column=0, sticky="w", **padding)
    reentry_pass = ttk.Entry(new_window, show="*")  
    reentry_pass.grid(row=8, column=1, **padding)

    # Create account button
    create_button = ttk.Button(new_window, text="Create Account", command=lambda: [create_new_account()], width=12)
    create_button.grid(row=9, column=1, columnspan=1, pady=(20, 10))

    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: [new_window.destroy(), root.deiconify()], width=11)
    close_button.grid(row=9, column=0, columnspan=1, pady=(20, 10))

    centre_window(new_window, 430, 520) 

    # Function to handle account creation
    def create_new_account():

        # Validation patterns
        dob_pattern = r'^\d{2}/\d{2}/\d{4}$'
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^\d{11}$'

        # Get user input from the form fields
        dob = entry_dob.get()
        first = entry_first.get()
        surname = entry_second.get()
        username = entry_user.get()
        password = entry_pass.get()
        email = entry_email.get()
        phone = entry_phone.get()
        reentry = reentry_pass.get()
        
        # Validate inputs (add your validation logic here)
        if not dob or not first or not surname or not username or not password or not email or not phone:
                messagebox.showerror("Error", "All fields must be filled.")
                return
        if not re.match(dob_pattern, dob):
            messagebox.showerror("Error", "Date of Birth must be in DD/MM/YYYY format.")
            return
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if not re.match(phone_pattern, phone):
            messagebox.showerror("Error", "Phone number must be 11 digits.")
            return
        elif password != reentry:
            messagebox.showerror("Error", 'Passwords do not match.')
            return
        
        # Try to create the account
        success = create_account(dob, first, surname, username, password, email, phone)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            new_window.destroy()
            
            # Get customer_id using the provided username/password from the form
            global customer_id  # Declare global
            customer_id = get_customer_id(username, password)  # Pass credentials
            
            if customer_id:
                open_home(customer_id)
            else:
                messagebox.showerror("Error", "Auto-login failed after account creation")



# Function to open staff account creation window
def createAccountWindowStaff():

    # Create the account window
    new_window = tk.Toplevel()
    new_window.title("Create Staff Account")
    new_window.geometry('430x520')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)   

    # Define padding and styles
    padding = {'padx': 15, 'pady': 10}

    # Add a title label
    title_label = ttk.Label(new_window, text="Create Account", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

    # First name label and entry
    label_first = ttk.Label(new_window, text="First Name:")
    label_first.grid(row=1, column=0, sticky="w", **padding)
    entry_first = ttk.Entry(new_window)
    entry_first.grid(row=1, column=1, **padding)

    # Surname label and entry
    label_second = ttk.Label(new_window, text="Surname:")
    label_second.grid(row=2, column=0, sticky="w", **padding)
    entry_second = ttk.Entry(new_window)
    entry_second.grid(row=2, column=1, **padding)

    # DOB label and entry
    label_dob = ttk.Label(new_window, text="Date of Birth (xx/xx/xxxx):")
    label_dob.grid(row=3, column=0, sticky="w", **padding)
    entry_dob = ttk.Entry(new_window)
    entry_dob.grid(row=3, column=1, **padding)

    # Email label and entry
    label_email = ttk.Label(new_window, text="Email:")
    label_email.grid(row=4, column=0, sticky="w", **padding)
    entry_email = ttk.Entry(new_window)
    entry_email.grid(row=4, column=1, **padding)

    # Phone number label and entry
    label_phone = ttk.Label(new_window, text="Phone Number:")
    label_phone.grid(row=5, column=0, sticky="w", **padding)
    entry_phone = ttk.Entry(new_window)
    entry_phone.grid(row=5, column=1, **padding)

    # Username label and entry
    label_user = ttk.Label(new_window, text="Username:")
    label_user.grid(row=6, column=0, sticky="w", **padding)
    entry_user = ttk.Entry(new_window)
    entry_user.grid(row=6, column=1, **padding)

    # Password label and entry
    label_pass = ttk.Label(new_window, text="Password:")
    label_pass.grid(row=7, column=0, sticky="w", **padding)
    entry_pass = ttk.Entry(new_window, show="*")  
    entry_pass.grid(row=7, column=1, **padding)

    # Password reentry label and entry
    reentry_label_pass = ttk.Label(new_window, text="Re-enter password:")
    reentry_label_pass.grid(row=8, column=0, sticky="w", **padding)
    reentry_pass = ttk.Entry(new_window, show="*")  
    reentry_pass.grid(row=8, column=1, **padding)

    # Create account button
    create_button = ttk.Button(new_window, text="Create Account", command=lambda: create_new_account_staff(), width=12)
    create_button.grid(row=9, column=1, columnspan=1, pady=(20, 10))

    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: [new_window.destroy(), open_home_staff(staff_id)], width=11)
    close_button.grid(row=9, column=0, columnspan=1, pady=(20, 10))

    centre_window(new_window, 430, 520) 

    def create_new_account_staff():
        dob = entry_dob.get()
        first = entry_first.get()
        surname = entry_second.get()
        username = entry_user.get()
        password = entry_pass.get()
        email = entry_email.get()
        phone = entry_phone.get()
        reentry = reentry_pass.get()

        # Validation patterns
        dob_pattern = r'^\d{2}/\d{2}/\d{4}$'
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^\d{11}$'

        # Validate fields
        if not dob or not first or not surname or not username or not password or not email or not phone:
            messagebox.showerror("Error", "All fields must be filled.")
            return
        if not re.match(dob_pattern, dob):
            messagebox.showerror("Error", "Date of Birth must be in DD/MM/YYYY format.")
            return
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if not re.match(phone_pattern, phone):
            messagebox.showerror("Error", "Phone number must be 11 digits.")
            return
        elif password != reentry:
            messagebox.showerror("Error", 'Passwords do not match.')
            return
        
        # Try to create the account
        success = create_account_staff(dob, first, surname, username, password, email, phone)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            new_window.destroy()  # Close the registration window
            
            # Get the staff_id for the newly created account
            try:
                # Retrieve the staff ID using the login credentials
                new_staff_id = get_staff_id(username, password)
                # Open the home screen with the new customer ID
                open_home_staff(new_staff_id)
            except Exception as e:
                messagebox.showerror("Error", f"Login failed after account creation: {str(e)}")
        else:
            messagebox.showerror("Error", "Username already exists or there was an error creating the account.")

# Function to open a window to manage orders
def manage_orders_window():

    # Function to create a confirmation window
    def create_confirmation_window(major, gbp_value, order_type, old_balance):
        confirm_win = tk.Toplevel()
        confirm_win.title(f"{major[:6]} Order Confirmation")
        confirm_win.geometry('300x320')
        confirm_win.resizable(False, False)
        sv_ttk.set_theme("light")
        centre_window(confirm_win, 300, 320)

        main_frame = ttk.Frame(confirm_win)
        main_frame.pack(pady=15, padx=15, fill='both', expand=True)

        style = ttk.Style()
        style.configure('Bold.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Price.TLabel', font=('Arial', 10), foreground='#2c3e50')

        # Fetch live data
        try:
            major_ticker = currency_pairs[major]
            forex_data_minute = yf.download(major_ticker, period='1d', interval='1m')
            open_price = round(forex_data_minute['Open'].iloc[-1].item(), 4)
        except Exception as e:
            open_price = "N/A"
            print(f'Error fetching data: {e}')
            messagebox.showerror("Error", "Failed to get current price")
            confirm_win.destroy()
            return

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Header
        ttk.Label(main_frame, text="ORDER CONFIRMATION", font=('Arial', 12, 'bold'), anchor='center').pack(pady=(0, 15))

        # Details grid
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill='x')

        # Function to display details
        def create_detail_row(parent, label, value):
            row = ttk.Frame(parent)
            row.pack(fill='x', pady=3)
            ttk.Label(row, text=label, style='Bold.TLabel', width=12, anchor='w').pack(side='left')
            ttk.Label(row, text=value, style='Price.TLabel', anchor='w').pack(side='left')
            return row

        create_detail_row(details_frame, "Time:", time)
        create_detail_row(details_frame, "Type:", order_type)
        create_detail_row(details_frame, "Currency Pair:", major)
        create_detail_row(details_frame, "Price:", f"{open_price:.4f}")
        create_detail_row(details_frame, "Amount:", f"£{gbp_value:,.2f}")

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        # Function to confirm a trade
        def confirm_action():
            try:
                # Store the order in database
                store_order(
                    customer_id=customer_id,
                    currency_pair=major,
                    order_type=order_type,
                    amount=gbp_value,
                    balance=old_balance, 
                    price=open_price,
                    order_time=time
                )
                
                # Show success message
                success_label = ttk.Label(main_frame, text="Order placed successfully!", 
                                        foreground="green")
                success_label.pack(pady=5)
                
                # Refresh after 2 seconds
                def refresh_orders():
                    confirm_win.destroy()  # Close confirmation window
                    new_window.destroy()   # Close current orders window
                    manage_orders_window() # Reopen new orders window
                
                confirm_win.after(2000, refresh_orders)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to store order: {e}")
                confirm_win.destroy()

        ttk.Button(button_frame,text="✓ Confirm", command=confirm_action, width=12).pack(side='right', padx=5)

        ttk.Button(button_frame,text="✗ Cancel", command=confirm_win.destroy, width=12).pack(side='right')

        ttk.Label(main_frame, text="Investor Centre Ltd", foreground='#95a5a6', font=('Arial', 8)).pack(side='bottom', pady=5)

    def handle_order(order_type):
        try:
            gbp_value = int(amount_entry.get())
            if gbp_value <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter a valid positive amount in GBP.")
            return
        
        customer_balance = get_customer_balance_display(customer_id)
        if gbp_value > customer_balance:
            messagebox.showerror("Error", "Insufficient funds")
            return
         
        major = major_dropdown.get()
        if major not in major_options:
            messagebox.showerror("Error", f"Invalid Currency Pair '{major}'")
            return
        
        try:
            update_balance_subtract(customer_id, gbp_value)
            create_confirmation_window(major, gbp_value, order_type, customer_balance)
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {e}")

    def manage_orders_buy():
        handle_order('BUY')

    def manage_orders_sell():
        handle_order('SELL')

    # Real-time price update function
    def update_price_display():
        selected_pair = selected_major.get()
        ticker = currency_pairs[selected_pair]
        try:
            data = yf.download(ticker, period='1d', interval='1m')
            current_price = data['Open'].iloc[-1].item()
            current_price = round(current_price, 4)
            price_label.config(text=f"  {current_price}", foreground="#27ae60")
        except Exception as e:
            price_label.config(text="Price Unavailable", foreground="#e74c3c")
        new_window.after(30000, update_price_display)  # Update every 30 seconds

    # Input validation
    def validate_amount():
        try:
            amount = float(amount_entry.get())
            balance = get_customer_balance_display(customer_id)
            if amount <= 0:
                amount_error.config(text="Amount must be positive")
                return False
            if amount > balance:
                amount_error.config(text="Insufficient balance")
                return False
            amount_error.config(text="")
            return True
        except ValueError:
            amount_error.config(text="Invalid amount")
            return False
            
    # Custom styling
    style = ttk.Style()
    style.configure('Trade.TFrame', background='#fafafa', font=("Helvetica", 14, "bold"))

    style.configure('Trade.TLabelframe', background='#fafafa')  
    style.configure('Trade.TLabelframe.Label', font=("Helvetica", 14, "bold"))  
    style.configure('Header.TLabel', font=('Helvetica', 14))
    style.configure('Price.TLabel', font=('Helvetica', 16))
    style.configure('Error.TLabel', font=('Helvetica', 10), foreground='#e74c3c')
    style.configure('Buy.TButton', foreground='green', background='#27ae60', font=('Helvetica', 12, 'bold'))
    style.configure('Sell.TButton', foreground='red', background='#c0392b', font=('Helvetica', 12, 'bold'))
    
    # Create main window
    new_window = tk.Toplevel()
    new_window.title("Trade Manager")
    new_window.geometry('500x600')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)  
    
    # Main container
    main_frame = ttk.Frame(new_window, padding=20, style='Trade.TFrame')
    main_frame.pack(fill='both', expand=True)

    # Header Section
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill='x', pady=(0, 20))
    
    header_label = ttk.Label(main_frame, text="Trade Manager", font=("Helvetica", 18, "bold"), foreground="#2c3e50")
    header_label.pack()

    # Balance Display
    balance_frame = ttk.LabelFrame(main_frame, text=" Account Balance ", padding=15, style='Trade.TLabelframe') 
    balance_frame.pack(fill='x', pady=10)

    current_balance = get_customer_balance_display(customer_id) 

    balance_label = ttk.Label(balance_frame, text="Available:", style='Header.TLabel')
    balance_label.pack(side='left')

    balance_label_2 = ttk.Label(balance_frame, text=f"£{current_balance:.2f}", font=('Helvetica', 20, 'bold'), foreground="#27ae60")
    balance_label_2.pack(side='right')

    # Currency Pair Section
    pair_frame = ttk.LabelFrame(main_frame, text=" Currency Pair Selection ", padding=15, style='Trade.TLabelframe') 
    pair_frame.pack(fill='x', pady=10)
    
    major_options = list(currency_pairs.keys())
    selected_major = tk.StringVar(value=major_options[0])
    
    pair_label = ttk.Label(pair_frame, text="Select Pair:", style='Header.TLabel')
    pair_label.grid(row=0, column=0, sticky='w')
    
    major_dropdown = ttk.Combobox(pair_frame, textvariable=selected_major, values=major_options, font=('Helvetica', 12))
    major_dropdown.grid(row=0, column=1, padx=10, sticky='ew')

    # Price Display
    price_frame = ttk.Frame(pair_frame)
    price_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
    
    current_price_label = ttk.Label(price_frame, text="Current Price:",style='Header.TLabel')
    current_price_label.pack(side='left')

    price_label = ttk.Label(price_frame, text="Loading...", style='Price.TLabel')
    price_label.pack(side='right')

    # Amount Entry Section
    amount_frame = ttk.LabelFrame(main_frame, text=" Trade Amount ", padding=15, style='Trade.TFrame')
    amount_frame.pack(fill='x', pady=10)
    
    amount_entry = ttk.Entry(amount_frame, font=('Helvetica', 14), justify='center')
    amount_entry.pack(pady=5, fill='x')
    
    amount_error = ttk.Label(amount_frame, text="", style='Error.TLabel')
    amount_error.pack()

    # Trading Buttons
    button_frame = ttk.Frame(main_frame, style='Trade.TFrame')
    button_frame.pack(fill='x', pady=20)
    
    buy_btn = ttk.Button(button_frame, text="BUY ↗",  style='Buy.TButton', command=manage_orders_buy, width=12)
    buy_btn.pack(side='left', padx=5, expand=True)
    
    sell_btn = ttk.Button(button_frame, text="SELL ↘",  style='Sell.TButton', command=manage_orders_sell, width=12)
    sell_btn.pack(side='right', padx=5, expand=True)

    # Navigation Section
    nav_frame = ttk.Frame(main_frame)
    nav_frame.pack(fill='x', pady=10)
    
    open_trades_button = ttk.Button(nav_frame, text="Open Trades", command=lambda: [new_window.destroy(), current_orders_window()])
    open_trades_button.pack(side='left')
    
    close_button = ttk.Button(nav_frame, text="← Back", command=lambda: [new_window.destroy(), open_home(customer_id)])
    close_button.pack(side='right')

    # Event bindings
    major_dropdown.bind("<<ComboboxSelected>>", lambda e: update_price_display())
    amount_entry.bind("<KeyRelease>", lambda e: validate_amount())
    
    # Initial updates
    centre_window(new_window, 500, 600) 
    update_price_display()
    validate_amount()

# Function to open balance window
def balance_window():

    global customer_id

    # Retrieve customer balance
    customer_balance = get_customer_balance_display(customer_id)

    # Create the new window
    new_window = tk.Toplevel()
    new_window.title("Account Balance")
    new_window.geometry('400x400')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)  
    
    # Main container frame
    main_frame = ttk.Frame(new_window)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Header
    header_label = ttk.Label(main_frame, 
                           text="Account Balance",
                           font=("Helvetica", 16, "bold"),
                           foreground="#2c3e50")
    header_label.pack(pady=(0, 20))

    # Balance display frame
    balance_frame = ttk.LabelFrame(main_frame, text=" Current Balance ", padding=20)
    balance_frame.pack(fill='x', pady=10)
    
    # Balance amount display
    balance_label = ttk.Label(balance_frame,
                            text=f"£ {customer_balance:.2f}",
                            font=("Helvetica", 24, "bold"),
                            foreground="#27ae60")
    balance_label.pack()

    # Buttons container
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=20)

    # Button styling
    style = ttk.Style()
    style.configure('TopUp.TButton', foreground='green', background='#27ae60')
    style.configure('Withdraw.TButton', foreground='red', background='#c0392b')
    style.configure('Payment.TButton', foreground='blue', background='#2980b9')

    # Action buttons
    topup_btn = ttk.Button(buttons_frame, text="➕ Add Funds", command=lambda: [add_money(), new_window.destroy()], style='TopUp.TButton', width=15)
    topup_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    withdraw_btn = ttk.Button(buttons_frame, text="➖ Withdraw Funds", command=lambda: [withdraw_money(), new_window.destroy()], style='Withdraw.TButton', width=15)
    withdraw_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    payments_btn = ttk.Button(buttons_frame, text="💳 Payment Methods", command=lambda: [new_window.destroy(), payment_methods_window()], style='Payment.TButton', width=15)
    payments_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

    # Close button
    close_btn = ttk.Button(main_frame, text="← Back ", command=lambda: (new_window.destroy(), open_home(customer_id)), width=15)
    close_btn.pack(pady=(10, 0))

    # Configure grid columns
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    # Add consistent padding to all buttons
    for child in buttons_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    centre_window(new_window, 400, 400) 

# Function to view customers
def view_customers_window():
    
    # Create the new window
    new_window = tk.Toplevel()
    new_window.title("View Customers")
    new_window.geometry('870x440')  # Initial size
    new_window.resizable(True, True)  # Allow window resizing
    sv_ttk.set_theme("light") 

    # Create a style for the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"),
                    background="#f3f3f3",
                    foreground="#333333")

    # Create Treeview 
    tree = ttk.Treeview(new_window, columns=("Customer ID", "First Name", "Surname", "Email", "Phone", "Username", "Balance"), show="headings", style="Treeview")

    # Define column headings 
    tree.heading("Customer ID", text="Customer ID", command=lambda: sortby(tree, "Customer ID", False))
    tree.heading("First Name", text="First Name", command=lambda: sortby(tree, "First Name", False))
    tree.heading("Surname", text="Surname", command=lambda: sortby(tree, "Surname", False))
    tree.heading("Email", text="Email", command=lambda: sortby(tree, "Email", False))
    tree.heading("Phone", text="Phone", command=lambda: sortby(tree, "Phone", False))
    tree.heading("Username", text="Username", command=lambda: sortby(tree, "Username", False))
    tree.heading("Balance", text="Balance", command=lambda: sortby(tree, "Balance", False))

    tree.column("Customer ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("First Name", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Surname", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Email", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Phone", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Username", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Balance", anchor=tk.CENTER, stretch=tk.YES)

    # Add scrollbars
    y_scroll = ttk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(new_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Add alternating row tags
    tree.tag_configure("oddrow", background="#f9f9f9")
    tree.tag_configure("evenrow", background="#e8e8e8")

    # Search function
    def search_customers():
        query = search_entry.get().strip().lower()
        for row in tree.get_children():
            tree.delete(row)
        filtered_customers = [customer for customer in customers if query in " ".join(map(str, customer)).lower()]
        for index, customer in enumerate(filtered_customers):
            tag = "oddrow" if index % 2 == 0 else "evenrow"
            tree.insert("", tk.END, values=(customer[0], customer[2], customer[3], customer[4], customer[5], customer[6], round(customer[7], 2)), tags=(tag,))

    # Search bar and button
    search_frame = ttk.Frame(new_window)
    search_frame.pack(pady=10, padx=10, fill=tk.X)

    search_label = ttk.Label(search_frame, text="Search:")
    search_label.pack(side=tk.LEFT, padx=(0, 5))

    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    search_button = ttk.Button(search_frame, text="Search", command=search_customers)
    search_button.pack(side=tk.LEFT)

    # Pack Treeview to fill available space
    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the Treeview with customer data
    customers = fetch_customers() 
    for index, customer in enumerate(customers):
        tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=(customer[0], customer[2], customer[3], customer[4], customer[5], customer[6], round(customer[7], 2)), tags=(tag,))

    # Buttons
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: (new_window.destroy(), open_home_staff(staff_id)), width=10)
    close_button.pack(padx=10, pady=10)

    centre_window(new_window, 870, 440) 

    new_window.mainloop()

# function to withdaraw money
def withdraw_money():
    # Create the withdraw money window
    new_window = tk.Toplevel()
    new_window.title("Withdraw Money")
    new_window.geometry('400x400')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)  

    # Main container frame
    main_frame = ttk.Frame(new_window)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Withdraw Money", font=("Helvetica", 16, "bold"), foreground="#2c3e50")
    header_label.pack(pady=(0, 20))

    # Fetch cards for the dropdown
    cards = get_customer_cards(customer_id)
    customer_balance = get_customer_balance_display(customer_id)
    
    if not cards:
        messagebox.showerror("Error", "No cards found for this customer.")
        new_window.destroy()
        balance_window()
        return
    
    if customer_balance <= 0:
        messagebox.showerror("Error", "You have no money to withdraw.")
        new_window.destroy()
        balance_window()
        return
    
    # Card selection frame
    card_frame = ttk.LabelFrame(main_frame, text=" Select Card ", padding=10)
    card_frame.pack(fill='x', pady=10)
    
    card_dropdown = ttk.Combobox(card_frame, width=40, state="readonly")
    card_dropdown['values'] = [
        f"{card['cardholder_name']} | {card['card_number']} | Expires: {card['end_date']}"
        for card in cards
    ]
    card_dropdown.pack(pady=5)
    card_dropdown.current(0)

    # Amount input frame
    amount_frame = ttk.LabelFrame(main_frame, text=" Amount to Withdraw (£) ", padding=10)
    amount_frame.pack(fill='x', pady=10)
    
    entry_amount = ttk.Entry(amount_frame, width=30)
    entry_amount.pack(pady=5)
    
    # Create a style object
    style = ttk.Style()
    
    # Configure the style for the Withdraw Money button
    style.configure("RedButton.TButton", background="white", foreground="red", font=("Arial", 12, "bold"), width=18)

    # Buttons container
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=20)
    
    submit_money_button = ttk.Button(buttons_frame, text="➖ Withdraw Money", command=lambda: submit_withdraw_money(entry_amount, new_window), style="RedButton.TButton")
    submit_money_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    close_button = ttk.Button(buttons_frame, text="← Back", command=lambda: (new_window.destroy(), balance_window()), width=15)
    close_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    # Configure grid columns
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    centre_window(new_window, 400, 400) 

# Function to submit money withdraw
def submit_withdraw_money(entry_amount, new_window):

    balance = get_customer_balance_display(customer_id)

    # Fetch the amount entered by the user
    input_value = entry_amount.get().strip()

    # Validate that the input is numeric and not empty
    if not input_value or not input_value.replace('.', '', 1).isdigit():
        messagebox.showerror("Input Error", "Please enter a valid number.")
        return

    # Convert the input to a float
    amount = float(input_value)

    # Validate amount
    if amount <= 0:
        messagebox.showerror("Input Error", "Amount must be greater than 0.")
        return

    elif amount >= balance:
        messagebox.showerror("Input Error", "Insufficient funds.")
        return

    # Update the balance
    update_balance_subtract(customer_id, amount)

    # Close the window
    new_window.destroy()

    # Show a success message
    messagebox.showinfo("Success", f"Successfully withdrew £{amount} from your account.")

    # Reopen the balance window
    balance_window()

# function to top up money
def add_money():

    # Create the add money window
    new_window = tk.Toplevel()
    new_window.title("Add Money")
    new_window.geometry('400x400')
    sv_ttk.set_theme("light")
    new_window.resizable(False, False)  

    # Main container frame
    main_frame = ttk.Frame(new_window)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Add Money", font=("Helvetica", 16, "bold"), foreground="#2c3e50")
    header_label.pack(pady=(0, 20))

    # Fetch cards for the dropdown
    cards = get_customer_cards(customer_id)
    if not cards:
        messagebox.showerror("Error", "No cards found for this customer.")
        new_window.destroy()
        balance_window()
        return

    # Card selection frame
    card_frame = ttk.LabelFrame(main_frame, text=" Select Card ", padding=10)
    card_frame.pack(fill='x', pady=10)

    card_dropdown = ttk.Combobox(card_frame, width=40, state="readonly")
    card_dropdown['values'] = [
        f"{card['cardholder_name']} | {card['card_number']} | Expires: {card['end_date']}" 
        for card in cards
    ]
    card_dropdown.pack(pady=5)
    card_dropdown.current(0)

    # Amount input frame
    amount_frame = ttk.LabelFrame(main_frame, text=" Amount to Add (£) ", padding=10)
    amount_frame.pack(fill='x', pady=10)

    entry_amount = ttk.Entry(amount_frame, width=30)
    entry_amount.pack(pady=5)

    # Create a style object
    style = ttk.Style()

    # Configure the style for the Add Money button
    style.configure("GreenButton.TButton", background="white", foreground="green", font=("Arial", 12, "bold"), width=18)

    # Buttons container
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=20)

    submit_money_button = ttk.Button(buttons_frame, text="➕ Add Money", command=lambda: submit_add_money(entry_amount, new_window), style="GreenButton.TButton")
    submit_money_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    close_button = ttk.Button(buttons_frame, text="← Back", command=lambda: (new_window.destroy(), balance_window()), width=15)
    close_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    # Configure grid columns
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    centre_window(new_window, 400, 400) 


def submit_add_money(entry_amount, new_window):
    # Fetch the amount entered by the user
    input_value = entry_amount.get().strip()

    # Validate that the input is numeric and not empty
    if not input_value or not input_value.replace('.', '', 1).isdigit():
        messagebox.showerror("Input Error", "Please enter a valid number.")
        return

    # Convert the input to a float
    amount = float(input_value)

    # Validate amount
    if amount <= 0:
        messagebox.showerror("Input Error", "Amount must be greater than 0.")
        return

    # Update the balance
    update_balance_add(customer_id, amount)

    # Close the window
    new_window.destroy()

    # Show a success message
    messagebox.showinfo("Success", f"Successfully added £{amount} to your account.")

    # Reopen the balance window
    balance_window()


# Function to open payment methods window
def payment_methods_window():

    # Function to load all the cards in db
    def load_cards():

        # Fetch all cards for the customer
        cards = get_customer_cards(customer_id) 
        for widget in card_frame.winfo_children():

            # Delete cards before adding them in to prevent duplicates
            widget.destroy()

        # If no cards in db 
        if not cards:
            no_cards_label = ttk.Label(card_frame, text="No cards found.", font=("Arial", 12))
            no_cards_label.pack(pady=10)
        else:
            for card in cards:
                card_display = f"{card['cardholder_name']} - **** **** **** {str(card['card_number'])[-4:]} ({card['end_date']})"
                card_label = ttk.Label(card_frame, text=card_display, font=("Arial", 14), anchor="w")
                card_label.pack(fill="x", padx=10, pady=5)

    # Create the new window
    new_window = tk.Toplevel()
    new_window.title("Payment Methods")
    new_window.geometry('400x400')
    sv_ttk.set_theme("light")  # Set theme 
    new_window.resizable(False, False)  

    # Main container frame
    main_frame = ttk.Frame(new_window)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Payment Methods", font=("Helvetica", 16, "bold"), foreground="#2c3e50")
    header_label.pack(pady=(0, 20))

    # Frame to display current cards
    card_frame = ttk.LabelFrame(main_frame, text=" Saved Cards ", padding=10)
    card_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Buttons container
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=20)

    # Create a style object
    style = ttk.Style()
    
    # Configure button styles
    style.configure("Red.TButton", background="white", foreground="red", font=("Arial", 12, "bold"), width=18)
    style.configure("Green.TButton", background="white", foreground="green", font=("Arial", 12, "bold"), width=18)
    style.configure("Blue.TButton", background="white", foreground="blue", font=("Arial", 12, "bold"), width=18)

    # Buttons with styled appearance
    add_card_button = ttk.Button(buttons_frame, text="➕ Add Card", command=lambda: [add_card(), new_window.destroy()], style="Green.TButton")
    add_card_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    edit_card_button = ttk.Button(buttons_frame, text="✏️ Edit Card", command=lambda: [edit_card(), new_window.destroy()], style="Blue.TButton")
    edit_card_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
    
    delete_card_button = ttk.Button(buttons_frame, text="🗑️ Delete Card", command=lambda: [delete_card(), new_window.destroy()], style="Red.TButton")
    delete_card_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
    
    close_button = ttk.Button(buttons_frame, text="← Back", command=lambda: [new_window.destroy(), balance_window()], width=18)
    close_button.grid(row=3, column=0, padx=5, pady=20, sticky='ew')
    
    # Configure grid columns
    buttons_frame.columnconfigure(0, weight=1)

    # Load and display customer cards
    load_cards()

    centre_window(new_window, 400, 400) 

# Function to add card
def add_card():

    # Function to handle new data

    def submit_card():
        # Fetch user input
        cardholder_name = entry_cardholder_name.get()
        card_number = entry_card_number.get()
        start_date = entry_start_date.get()
        end_date = entry_end_date.get()
        card_provider = combo_card_provider.get()
        building_number = entry_building_number.get()
        line1 = entry_line1.get()
        line2 = entry_line2.get()
        postcode = entry_postcode.get()
        password = entry_password.get()

        # Check if all required fields are filled
        if not (cardholder_name and card_number and start_date and end_date and card_provider and building_number and line1 and postcode and password):
            tk.messagebox.showerror("Input Error", "All fields are required except Address Line 2!")
            return

        # Validate Cardholder Name alphabetic with spaces
        if not all(x.isalpha() or x.isspace() for x in cardholder_name):
            tk.messagebox.showerror("Input Error", "Cardholder Name should contain only letters and spaces!")
            return

        # Validate Card Number (16 digits)
        if not card_number.isdigit() or len(card_number) != 16:
            tk.messagebox.showerror("Input Error", "Card Number must be exactly 16 digits!")
            return

        # Validate Start Date and End Date (MM/YY format)
        date_pattern = r"^(0[1-9]|1[0-2])/[0-9]{2}$"  # Validates MM/YY format
        if not re.match(date_pattern, start_date):
            tk.messagebox.showerror("Input Error", "Start Date must be in MM/YY format!")
            return
        if not re.match(date_pattern, end_date):
            tk.messagebox.showerror("Input Error", "End Date must be in MM/YY format!")
            return

        # Validate Card Provider (non-empty)
        if not card_provider:
            tk.messagebox.showerror("Input Error", "Card Provider is required!")
            return

        # Validate Building Number (only digits)
        if not building_number.isdigit():
            tk.messagebox.showerror("Input Error", "Building Number must contain only digits!")
            return

        # Validate Address Line 1 (non-empty)
        if not line1:
            tk.messagebox.showerror("Input Error", "Address Line 1 is required!")
            return
        
        # Validate Postcode 
        postcode_pattern = r"^BT[0-9]{1,4}[A-Z]{2}$"
        if not re.match(postcode_pattern, postcode):
            tk.messagebox.showerror("Input Error", "Postcode is not valid! Must match format like BT440AY.")
            return

        # Validate Password (CVV) - exactly 3 digits
        if len(password) != 3 or not password.isdigit():  # Modified
            tk.messagebox.showerror("Input Error", "CVV must be exactly 3 digits!")
            return

        # Validate Expiry Date is in the future - New validation
        try:
            expiry_month, expiry_year = map(int, end_date.split('/'))
            expiry_date = datetime(2000 + expiry_year, expiry_month, 1) + relativedelta(day=31)
            if expiry_date < datetime.now():
                tk.messagebox.showerror("Input Error", "Card has expired!")
                return
        except ValueError:
            tk.messagebox.showerror("Input Error", "Invalid expiration date format!")
            return

        try:
            # Add card provider to the database and fetch its ID
            card_provider_id = add_card_provider(card_provider)

            # Add billing address and get its ID
            billing_address_id = add_billing_address(building_number, line1, line2, postcode)

            # Add payment card details and get its ID
            payment_card_id = add_payment_card(cardholder_name, card_number, start_date, end_date, card_provider_id, billing_address_id, password)

            # Link the payment card to the customer (replace with actual logged-in customer ID)
            link_card_to_customer(payment_card_id, customer_id)

            # Show success message
            tk.messagebox.showinfo("Success", "Card added successfully!")
            add_card_window.destroy()  # Assuming this is the window where the form is located

        except Exception as e:
            # Show error message if something goes wrong
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

        # Open the payment methods window after success
        payment_methods_window()  

    # Create a new window
    add_card_window = tk.Toplevel()
    add_card_window.title("Add Card")
    add_card_window.geometry('400x740')
    sv_ttk.set_theme("light")
    centre_window(add_card_window, 400, 740) 
    add_card_window.resizable(False, False)  

    # Cardholder name
    tk.Label(add_card_window, text="Cardholder Name:").pack(pady=5)
    entry_cardholder_name = ttk.Entry(add_card_window, width=30)
    entry_cardholder_name.pack()

    # Card number
    tk.Label(add_card_window, text="Card Number:").pack(pady=5)
    entry_card_number = ttk.Entry(add_card_window, width=30)
    entry_card_number.pack()

    # Start date
    tk.Label(add_card_window, text="Start Date (MM/YY):").pack(pady=5)
    entry_start_date = ttk.Entry(add_card_window, width=30)
    entry_start_date.pack()

    # End date
    tk.Label(add_card_window, text="End Date (MM/YY):").pack(pady=5)
    entry_end_date = ttk.Entry(add_card_window, width=30)
    entry_end_date.pack()

    # Card provider
    tk.Label(add_card_window, text="Card Provider:").pack(pady=5)
    combo_card_provider = ttk.Combobox(add_card_window, values=["Visa", "MasterCard", "AmEx"], width=27)
    combo_card_provider.pack()

    # Billing Address
    tk.Label(add_card_window, text="Building Number:").pack(pady=5)
    entry_building_number = ttk.Entry(add_card_window, width=30)
    entry_building_number.pack()

    tk.Label(add_card_window, text="Address Line 1:").pack(pady=5)
    entry_line1 = ttk.Entry(add_card_window, width=30)
    entry_line1.pack()

    tk.Label(add_card_window, text="Address Line 2:").pack(pady=5)
    entry_line2 = ttk.Entry(add_card_window, width=30)
    entry_line2.pack()

    # Postcode
    tk.Label(add_card_window, text="Postcode:").pack(pady=5)
    entry_postcode = ttk.Entry(add_card_window, width=30)
    entry_postcode.pack()

    # Password
    tk.Label(add_card_window, text="CVV:").pack(pady=5)
    entry_password = ttk.Entry(add_card_window, show="*", width=30)
    entry_password.pack()

    # Create a style object
    style = ttk.Style()
    
    # Configure button styles
    style.configure("Green.TButton", background="white", foreground="green", font=("Arial", 12, "bold"), width=13)

    # Submit button
    ttk.Button(add_card_window, text="Submit", command=submit_card, style='Green.TButton', width=13).pack(pady=20)

    # Button to close the window
    close_button = ttk.Button(add_card_window, text="← Back" , command=lambda: (add_card_window.destroy(), payment_methods_window()), width=10)
    close_button.pack()

# Function to edit cards
def edit_card():
    
    # Fetch the customer's cards
    cards = get_customer_cards(customer_id)  

    if not cards:
        tk.messagebox.showerror("No Cards", "You have no cards to edit.")
        payment_methods_window()
        return

    # Function to handle the new data
    def submit_edit():
        # Fetch user input
        old_cardholder_name = combo_card_selector.get()
        cardholder_name = entry_cardholder_name.get()
        card_number = entry_card_number.get()
        start_date = entry_start_date.get()
        end_date = entry_end_date.get()
        card_provider = combo_card_provider.get()
        building_number = entry_building_number.get()
        line1 = entry_line1.get()
        line2 = entry_line2.get()
        postcode = entry_postcode.get()
        password = entry_password.get()

        # Clean the cardholder name with regex
        old_cardholder_name = re.sub(r" - .*$", "", old_cardholder_name)
        
        # Retrieve card id
        card_id = get_card_id(old_cardholder_name)

        # Check if all required fields are filled
        if not (cardholder_name and card_number and start_date and end_date and card_provider and building_number and line1 and postcode and password):
            tk.messagebox.showerror("Input Error", "All fields are required except Address Line 2!")
            return

        # Validate Cardholder Name alphabetic with spaces
        if not all(x.isalpha() or x.isspace() for x in cardholder_name):
            tk.messagebox.showerror("Input Error", "Cardholder Name should contain only letters and spaces!")
            return

        # Validate Card Number (16 digits)
        if not card_number.isdigit() or len(card_number) != 16:
            tk.messagebox.showerror("Input Error", "Card Number must be exactly 16 digits!")
            return

        # Validate Start Date and End Date (MM/YY format)
        date_pattern = r"^(0[1-9]|1[0-2])/[0-9]{2}$"  # Validates MM/YY format
        if not re.match(date_pattern, start_date):
            tk.messagebox.showerror("Input Error", "Start Date must be in MM/YY format!")
            return
        if not re.match(date_pattern, end_date):
            tk.messagebox.showerror("Input Error", "End Date must be in MM/YY format!")
            return

        # Validate Card Provider (non-empty)
        if not card_provider:
            tk.messagebox.showerror("Input Error", "Card Provider is required!")
            return

        # Validate Building Number (only digits)
        if not building_number.isdigit():
            tk.messagebox.showerror("Input Error", "Building Number must contain only digits!")
            return

        # Validate Address Line 1 (non-empty)
        if not line1:
            tk.messagebox.showerror("Input Error", "Address Line 1 is required!")
            return

        # Validate Postcode 
        postcode_pattern = r"^BT[0-9]{1,4}[A-Z]{2}$"
        if not re.match(postcode_pattern, postcode):
            tk.messagebox.showerror("Input Error", "Postcode is not valid! Must match format like BT440AY.")
            return

        # Validate Password (CVV) - exactly 3 digits
        if len(password) != 3 or not password.isdigit():  # Modified
            tk.messagebox.showerror("Input Error", "CVV must be exactly 3 digits!")
            return

        # Validate Expiry Date is in the future - New validation
        try:
            expiry_month, expiry_year = map(int, end_date.split('/'))
            expiry_date = datetime(2000 + expiry_year, expiry_month, 1) + relativedelta(day=31)
            if expiry_date < datetime.now():
                tk.messagebox.showerror("Input Error", "Card has expired!")
                return
        except ValueError:
            tk.messagebox.showerror("Input Error", "Invalid expiration date format!")
            return

        try:
            # Update the card details in the database
            update_card(card_id, cardholder_name, card_number, start_date, end_date, card_provider,
                        building_number, line1, line2, postcode, password)

            tk.messagebox.showinfo("Success", "Card updated successfully!")
            edit_card_window.destroy()
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

        # Close and reopen window to update
        edit_card_window.destroy()
        payment_methods_window()


    # Create the edit card window
    edit_card_window = tk.Toplevel()
    edit_card_window.title("Edit Card")
    edit_card_window.geometry('420x800')
    sv_ttk.set_theme("light")
    centre_window(edit_card_window, 420, 800) 
    edit_card_window.resizable(False, False)  

    # Card selector
    tk.Label(edit_card_window, text="Select Card:").pack(pady=5)
    combo_card_selector = ttk.Combobox(edit_card_window, values=[
        f"{card['cardholder_name']} - **** {str(card['card_number'])[-4:]}" for card in cards], width=27)
    combo_card_selector.pack()

    # Cardholder name
    tk.Label(edit_card_window, text="Cardholder Name:").pack(pady=5)
    entry_cardholder_name = ttk.Entry(edit_card_window, width=30)
    entry_cardholder_name.pack()

    # Card number
    tk.Label(edit_card_window, text="Card Number:").pack(pady=5)
    entry_card_number = ttk.Entry(edit_card_window, width=30)
    entry_card_number.pack()

    # Start date
    tk.Label(edit_card_window, text="Start Date (MM/YY):").pack(pady=5)
    entry_start_date = ttk.Entry(edit_card_window, width=30)
    entry_start_date.pack()

    # End date
    tk.Label(edit_card_window, text="End Date (MM/YY):").pack(pady=5)
    entry_end_date = ttk.Entry(edit_card_window, width=30)
    entry_end_date.pack()

    # Card provider
    tk.Label(edit_card_window, text="Card Provider:").pack(pady=5)
    combo_card_provider = ttk.Combobox(edit_card_window, values=["Visa", "MasterCard", "AmEx"], width=27)
    combo_card_provider.pack()

    # Billing Address
    tk.Label(edit_card_window, text="Building Number:").pack(pady=5)
    entry_building_number = ttk.Entry(edit_card_window, width=30)
    entry_building_number.pack()

    tk.Label(edit_card_window, text="Address Line 1:").pack(pady=5)
    entry_line1 = ttk.Entry(edit_card_window, width=30)
    entry_line1.pack()

    tk.Label(edit_card_window, text="Address Line 2:").pack(pady=5)
    entry_line2 = ttk.Entry(edit_card_window, width=30)
    entry_line2.pack()

    tk.Label(edit_card_window, text="Postcode:").pack(pady=5)
    entry_postcode = ttk.Entry(edit_card_window, width=30)
    entry_postcode.pack()

    # Password
    tk.Label(edit_card_window, text="CVV:").pack(pady=5)
    entry_password = ttk.Entry(edit_card_window, show="*", width=30)
    entry_password.pack()

    # Create a style object
    style = ttk.Style()
    
    # Configure button styles
    style.configure("Green.TButton", background="white", foreground="green", font=("Arial", 12, "bold"), width=13)

    # Submit button
    ttk.Button(edit_card_window, text="Submit", command=submit_edit, style='Green.TButton').pack(pady=20)

    # Button to close the window
    close_button = ttk.Button(edit_card_window, text="← Back" , command=lambda: (edit_card_window.destroy(), payment_methods_window()), width=10)
    close_button.pack()

# function to delete cards
def delete_card():
    # Fetch the selected card's details
    cards = get_customer_cards(customer_id)  

    if not cards:
        messagebox.showerror("No Cards", "You have no cards to delete.")
        payment_methods_window()
        return

    # Function to delete card after confirmation
    def submit_delete():
        # Get selected cardholder name
        selected_card = combo_card_selector.get()
        # Get the name before the card number part
        cardholder_name = selected_card.split(" - ")[0]
        # Retrieve the card ID
        card_id = get_card_id(cardholder_name) 

        # Confirmation
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the card for {cardholder_name}?"):
            try:
                # Delete the card from the database
                delete_card_from_db(card_id)
                messagebox.showinfo("Success", f"Card for {cardholder_name} deleted successfully.")
                delete_card_window.destroy()  # Close the delete window
                payment_methods_window()       # Refresh the payment methods window
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    # Create the delete card window
    delete_card_window = tk.Toplevel()
    delete_card_window.title("Delete Card")
    delete_card_window.geometry('400x320')
    sv_ttk.set_theme("light")  # Set theme
    delete_card_window.resizable(False, False)  

    # Main container frame
    main_frame = ttk.Frame(delete_card_window)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Delete Card", font=("Helvetica", 16, "bold"), foreground="#2c3e50")
    header_label.pack(pady=(0, 20))

    # Frame to hold the card selector
    selector_frame = ttk.LabelFrame(main_frame, text="Select Card", padding=10)
    selector_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Card selector label and dropdown
    tk.Label(selector_frame, text="Select Card to Delete:").pack(pady=5)
    combo_card_selector = ttk.Combobox(selector_frame, values=[f"{card['cardholder_name']} - **** {str(card['card_number'])[-4:]}" for card in cards], width=40, state="readonly")
    combo_card_selector.pack(pady=5)
    combo_card_selector.current(0)

    # Buttons container
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=20)

    # Create a style object for button styling
    style = ttk.Style()
    style.configure("Red.TButton", background="white", foreground="red", font=("Arial", 12, "bold"), width=18)

    # Submit Delete Button
    delete_button = ttk.Button(buttons_frame, text="Delete Card", command=submit_delete, style="Red.TButton")
    delete_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    # Back Button
    back_button = ttk.Button(buttons_frame, text="← Back", command=lambda: (delete_card_window.destroy(), payment_methods_window()))
    back_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    # Configure grid columns
    buttons_frame.columnconfigure(0, weight=1)

    centre_window(delete_card_window, 400, 320) 

# function to allow tables to be sorted by order descending
def sortby(treeview, col, descending):
    data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
    data.sort(reverse=descending)
    
    for ix, item in enumerate(data):
        treeview.move(item[1], '', ix)
    
    treeview.heading(col, command=lambda _col=col: sortby(treeview, _col, not descending))

# ƒunction to open live prices window
def open_live_window(customer_id):
    new_window = tk.Toplevel()
    new_window.title("Live Price and P/L")
    new_window.geometry('400x250')
    centre_window(new_window, 400, 250)
    new_window.resizable(False, False)  
    
    # Fetch current trades
    try:
        trades = fetch_all_orders_primary_key(customer_id)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch orders: {e}")
        new_window.destroy()
        return

    if not trades:
        messagebox.showinfo("No Trades", "No current trades available.")
        new_window.destroy()
        return

    orders_dict = {
        f"Order ID {trade[0]}: {trade[2]} {trade[3]} {trade[4]} units @ {trade[5]}": trade
        for trade in trades
    }
    
    tk.Label(new_window, text="Select a Trade:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
    selected_trade = tk.StringVar()
    selected_trade.set(list(orders_dict.keys())[0])
    trade_dropdown = ttk.Combobox(new_window, textvariable=selected_trade, state="readonly", font=("Arial", 11))
    trade_dropdown['values'] = list(orders_dict.keys())
    trade_dropdown.pack(pady=5)
    
    price_label = ttk.Label(new_window, text="Current Price: -", font=("Arial", 14, "bold"))
    price_label.pack(pady=(15, 0))

    pl_label = ttk.Label(new_window, text="Live P/L: -", font=("Arial", 20, "bold"))
    pl_label.pack(pady=(5, 15))
    
    update_job = None
    last_price = None
    last_trade_key = None

    # Function to update live price and p/l
    def update_prices():
        nonlocal update_job, last_price, last_trade_key

        if update_job is not None:
            new_window.after_cancel(update_job)
            update_job = None

        trade_key = selected_trade.get()
        if trade_key != last_trade_key:
            last_price = None
            last_trade_key = trade_key

        trade = orders_dict.get(trade_key)
        if not trade:
            price_label.config(text="Current Price: N/A")
            pl_label.config(text="Live P/L: N/A", foreground="black")
            return

        order_id, pair = trade[0], trade[2]
        ticker = currency_pairs.get(pair)
        if not ticker:
            price_label.config(text="Current Price: N/A")
            pl_label.config(text="Live P/L: N/A", foreground="black")
            return

        try:
            data = yf.download(ticker, period='1d', interval='1m')
            current_price = float(round(data['Open'].iloc[-1].item(), 4)) if not data.empty else "N/A"
        except Exception:
            current_price = "N/A"

        price_label.config(text=f"Current Price: {current_price}")

        if current_price != "N/A" and (current_price != last_price or trade_key != last_trade_key):
            try:
                pl_value = calculate_pl(order_id, current_price, customer_id)
                pl_color = "green" if pl_value > 0 else "red" if pl_value < 0 else "black"
                pl_label.config(text=f"Live P/L: {pl_value:.4f}", foreground=pl_color)
            except Exception:
                pl_label.config(text="Live P/L: N/A", foreground="black")
            last_price = current_price
        
        update_job = new_window.after(5000, update_prices)
    
    # Helper function to  close the trade
    def close_trade_handler():
        order_desc = selected_trade.get()
        if not order_desc:
            messagebox.showwarning("Warning", "Please select an order to close.")
            return

        order_id = orders_dict[order_desc][0]
        major = get_currency_pair(order_id)
        major_ticker = currency_pairs[major]

        try:
            forex_data_minute = yf.download(major_ticker, period='1d', interval='1m')
            close_price = forex_data_minute['Open'].iloc[-1].item()
            close_trade(order_id, close_price, customer_id)
            messagebox.showinfo("Success", "Trade closed successfully.")
            del orders_dict[order_desc]
            trade_dropdown['values'] = list(orders_dict.keys())
            selected_trade.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to close trade: {e}")
    
    ttk.Button(new_window, text="Close Trade", command=close_trade_handler, width=11).pack(pady=10)
    ttk.Button(new_window, text="← Back", command=lambda: [new_window.destroy(), current_orders_window()], width=11).pack()
    
    selected_trade.trace_add('write', lambda *args: update_prices())
    update_prices()
    new_window.protocol("WM_DELETE_WINDOW", new_window.destroy)

# Function to view ongoing orders
def current_orders_window():

    # Create the new window for current orders
    new_window = tk.Toplevel()
    new_window.title("Current Orders")
    new_window.geometry('870x500')  
    new_window.resizable(True, True)  
    sv_ttk.set_theme("light")  
    centre_window(new_window, 870, 500) 

    # Create a style for the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"),
                    background="#f3f3f3",
                    foreground="#333333")

    # Create Treeview widget
    tree = ttk.Treeview(new_window, columns=("Currency Pair", "Order Type", "Amount", "Price", "Order Time"),show="headings", style="Treeview")

    # Define column headings and make columns stretchable
    tree.heading("Currency Pair", text="Currency Pair", command=lambda: sortby(tree, "Currency Pair", False))
    tree.heading("Order Type", text="Order Type", command=lambda: sortby(tree, "Order Type", False))
    tree.heading("Amount", text="Amount", command=lambda: sortby(tree, "Amount", False))
    tree.heading("Price", text="Price", command=lambda: sortby(tree, "Price", False))
    tree.heading("Order Time", text="Order Time", command=lambda: sortby(tree, "Order Time", False))

    tree.column("Currency Pair", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Type", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Amount", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Price", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Time", anchor=tk.CENTER, stretch=tk.YES)

    # Add vertical and horizontal scrollbars
    y_scroll = ttk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(new_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Add alternating row tags
    tree.tag_configure("oddrow", background="#f9f9f9")
    tree.tag_configure("evenrow", background="#e8e8e8")

    # Pack Treeview to fill available space
    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the Treeview with orders
    orders = fetch_orders(customer_id)
    for index, order in enumerate(orders):
        tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=order, tags=(tag,))

    # Buttons
    modify_button = ttk.Button(new_window, text="Modify trades", command=lambda: (new_window.destroy(), modify_orders_window()), width=10)
    modify_button.pack(padx=10, pady=10)

    live_button = ttk.Button(new_window, text="Live View", command=lambda: (new_window.destroy(), open_live_window(customer_id) ), width=10)
    live_button.pack(padx=10, pady=10)

    close_button = ttk.Button(new_window, text="← Back" , command=lambda: (new_window.destroy(), manage_orders_window()), width=10)
    close_button.pack(padx=10, pady=10)

    new_window.mainloop()

# Function to sidplay all open orders
def all_current_orders_window():
    # Create the new window for current orders
    new_window = tk.Toplevel()
    new_window.title("Current Orders")
    new_window.geometry('870x440')  
    new_window.resizable(True, True)  
    sv_ttk.set_theme("light")  
    centre_window(new_window, 870, 440) 

    # Create a style for the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"),
                    background="#f3f3f3",
                    foreground="#333333")

    # Create Treeview widget
    tree = ttk.Treeview(new_window, columns=("Order ID", "Customer ID", "Currency Pair",
                                             "Order Type", "Amount", "Price", "Order Time"),
                        show="headings", style="Treeview")

    # Define column headings and add sorting functionality
    tree.heading("Order ID", text="Order ID", command=lambda: sortby(tree, "Order ID", False))
    tree.heading("Customer ID", text="Customer ID", command=lambda: sortby(tree, "Customer ID", False))
    tree.heading("Currency Pair", text="Currency Pair", command=lambda: sortby(tree, "Currency Pair", False))
    tree.heading("Order Type", text="Order Type", command=lambda: sortby(tree, "Order Type", False))
    tree.heading("Amount", text="Amount", command=lambda: sortby(tree, "Amount", False))
    tree.heading("Price", text="Price", command=lambda: sortby(tree, "Price", False))
    tree.heading("Order Time", text="Order Time", command=lambda: sortby(tree, "Order Time", False))

    # Define column widths and make columns stretchable
    tree.column("Order ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Customer ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Currency Pair", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Type", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Amount", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Price", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Time", anchor=tk.CENTER, stretch=tk.YES)

    # Add vertical and horizontal scrollbars
    y_scroll = ttk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(new_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Add alternating row tags
    tree.tag_configure("oddrow", background="#f9f9f9")
    tree.tag_configure("evenrow", background="#e8e8e8")

    # Fetch orders from your database or data source
    orders = fetch_all_orders()  

    # Add data to the Treeview
    for index, order in enumerate(orders):
        tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=order, tags=(tag,))

    # Pack Treeview into the window
    tree.pack(fill=tk.BOTH, expand=True)

    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: (new_window.destroy(), open_home_staff(staff_id)), width=10)
    close_button.pack(pady=10)

    # Run the Tkinter main loop for the new window
    new_window.mainloop()

# Function to manage onging orders, Close order etc
def modify_orders_window():

    # Create the new window for order modification
    new_window = tk.Toplevel()
    new_window.title("Modify Order")
    new_window.geometry('400x250')
    sv_ttk.set_theme("light") 
    centre_window(new_window, 400, 250) 
    new_window.resizable(False, False)  

    # Fetch current orders
    try:
        orders = fetch_all_orders_primary_key(customer_id)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch orders: {e}")
        return

    if not orders:
        messagebox.showinfo("No Orders", "No current orders available.")
        new_window.destroy()
        return

    # Dropdown label
    tk.Label(new_window, text="Select an Order to Modify:").pack(pady=10)

    # Create a dictionary for dropdown mapping
    orders_dict = {
        f"Order ID {order[0]}: {order[2]} {order[3]} {order[4]} units @ {order[5]}": order[0]
        for order in orders
    }

    # Dropdown menu
    selected_order = tk.StringVar(new_window)
    order_dropdown = ttk.Combobox(new_window, textvariable=selected_order, state="readonly")
    order_dropdown['values'] = list(orders_dict.keys())
    order_dropdown.pack(pady=10)

    # Function to work alongside close_trade() in data_access.py to help close trades and store data in database
    def close_trade_handler():

        global order_id
        
        order_desc = selected_order.get()
        order_id = orders_dict[order_desc]

        # Fetch major from db
        major = get_currency_pair(order_id)

        # convert to ticker value for yfinance
        major_ticker = currency_pairs[major]

        # download from yfinance
        forex_data_minute = yf.download(major_ticker, period='1d', interval='1m')
        close_price = forex_data_minute['Open'].iloc[-1].item()

        # validate an order has been selected
        if not order_desc:
            messagebox.showwarning("Warning", "Please select an order to close.")
            return

        try:
            # Close the trade using the db function
            close_trade(order_id, close_price, customer_id)
            messagebox.showinfo("Success", "Trade closed successfully.")

            # Refresh the dropdown by removing the closed trade
            del orders_dict[order_desc]
            order_dropdown['values'] = list(orders_dict.keys())
            selected_order.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to close trade: {e}")

    # Close Trade Button
    ttk.Button(new_window, text="Close Trade", command=close_trade_handler, width=11).pack(pady=10)
    
    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: (new_window.destroy(), current_orders_window()), width=11)
    close_button.pack()

# Function to open history window
def history_window():
    # Create the new window for order history
    new_window = tk.Toplevel()
    new_window.title("Trade History")
    new_window.geometry('900x420')  
    new_window.resizable(True, True)  
    sv_ttk.set_theme("light")  
    centre_window(new_window, 900, 420) 

    # Create a style for the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"),
                    background="#f3f3f3",
                    foreground="#333333")

    # Create Treeview widget
    tree = ttk.Treeview(new_window, columns=("Currency Pair", "Order Type", "Amount", "Price", "Order Time Close", "Pip Difference", "Profit/Loss"),
                        show="headings", style="Treeview")

    # Define column headings and add sorting functionality
    tree.heading("Currency Pair", text="Currency Pair", command=lambda: sortby(tree, "Currency Pair", False))
    tree.heading("Order Type", text="Order Type", command=lambda: sortby(tree, "Order Type", False))
    tree.heading("Amount", text="Amount", command=lambda: sortby(tree, "Amount", False))
    tree.heading("Price", text="Price", command=lambda: sortby(tree, "Price", False))
    tree.heading("Order Time Close", text="Order Time Close", command=lambda: sortby(tree, "Order Time Close", False))
    tree.heading("Pip Difference", text="Pip Difference", command=lambda: sortby(tree, "Pip Difference", False))
    tree.heading("Profit/Loss", text="Profit/Loss", command=lambda: sortby(tree, "Profit/Loss", False))

    # Define column widths and make columns stretchable
    tree.column("Currency Pair", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Type", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Amount", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Price", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Time Close", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Pip Difference", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Profit/Loss", anchor=tk.CENTER, stretch=tk.YES)

    # Add vertical and horizontal scrollbars
    y_scroll = ttk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(new_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Add alternating row tags
    tree.tag_configure("oddrow", background="#f9f9f9")
    tree.tag_configure("evenrow", background="#e8e8e8")

    # Add data to the Treeview
    history_records = fetch_history(customer_id)  # Fetch history records

    for index, record in enumerate(history_records):
        tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=record, tags=(tag,))

    # Pack Treeview into the window
    tree.pack(fill=tk.BOTH, expand=True)

    # Button to export customer history to CSV
    export_button = ttk.Button(new_window, text="Export to CSV", command=lambda: export_customer_history(), width=10)
    export_button.pack(pady=10)

    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back", command=lambda: (new_window.destroy(), open_home(customer_id)), width=11)
    close_button.pack(pady=10)

    # Run the Tkinter main loop for the new window
    new_window.mainloop()

# Function to export customer history
def export_customer_history():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Trade History As"
    )
    if file_path:
        if export_history_to_csv(customer_id, file_path):
            messagebox.showinfo("Success", "CSV exported successfully!")
        else:
            messagebox.showerror("Error", "Failed to export CSV.")

# Function to open history window
def history_window_staff():
    # Create the new window for trade history
    new_window = tk.Toplevel()
    new_window.title("Trade History")
    new_window.geometry('900x420') 
    new_window.resizable(True, True)  
    sv_ttk.set_theme("light")
    centre_window(new_window, 900, 420)  

    # Create a style for the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"),
                    background="#f3f3f3",
                    foreground="#333333")

    # Create Treeview widget
    tree = ttk.Treeview(new_window, columns=("History ID", "Order ID", "Currency Pair", "Customer ID", "Order Type", "Amount", 
                                             "Price", "Order Time Close", "Pip Difference", "Profit/Loss"),
                        show="headings", style="Treeview")

    # Define column headings and add sorting functionality
    tree.heading("History ID", text="History ID", command=lambda: sortby(tree, "History ID", False))
    tree.heading("Order ID", text="Order ID", command=lambda: sortby(tree, "Order ID", False))
    tree.heading("Customer ID", text="Customer ID", command=lambda: sortby(tree, "Customer ID", False))
    tree.heading("Currency Pair", text="Currency Pair", command=lambda: sortby(tree, "Currency Pair", False))
    tree.heading("Order Type", text="Order Type", command=lambda: sortby(tree, "Order Type", False))
    tree.heading("Amount", text="Amount", command=lambda: sortby(tree, "Amount", False))
    tree.heading("Price", text="Price", command=lambda: sortby(tree, "Price", False))
    tree.heading("Order Time Close", text="Order Time Close", command=lambda: sortby(tree, "Order Time Close", False))
    tree.heading("Pip Difference", text="Pip Difference", command=lambda: sortby(tree, "Pip Difference", False))
    tree.heading("Profit/Loss", text="Profit/Loss", command=lambda: sortby(tree, "Profit/Loss", False))

    # Define column widths and make columns stretchable
    tree.column("History ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Customer ID", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Currency Pair", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Type", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Amount", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Price", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Order Time Close", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Pip Difference", anchor=tk.CENTER, stretch=tk.YES)
    tree.column("Profit/Loss", anchor=tk.CENTER, stretch=tk.YES)

    # Add vertical and horizontal scrollbars
    y_scroll = ttk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(new_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Add alternating row tags
    tree.tag_configure("oddrow", background="#f9f9f9")
    tree.tag_configure("evenrow", background="#e8e8e8")

    # Add data to the Treeview
    history_records = fetch_all_history()  # Fetch history records

    for index, record in enumerate(history_records):
        tag = "oddrow" if index % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=record, tags=(tag,))

    # Pack Treeview into the window
    tree.pack(fill=tk.BOTH, expand=True)

    # Button to export all history to CSV
    export_button = ttk.Button(new_window, text="Export to CSV", command=lambda: export_all_history(), width=10)
    export_button.pack(pady=10)

    # Button to close the window
    close_button = ttk.Button(new_window, text="← Back" , command=lambda: (new_window.destroy(), open_home_staff(staff_id)), width=10)
    close_button.pack(pady=10)

    # Run the Tkinter main loop for the new window
    new_window.mainloop()

# Function to export all customer history
def export_all_history():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save All Trade History As"
    )
    if file_path:
        if export_history_to_csv(None, file_path):  # None exports all data
            messagebox.showinfo("Success", "Full CSV exported successfully!")
        else:
            messagebox.showerror("Error", "Failed to export CSV.")

# Function to centre windows
def centre_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)
    root.geometry(f'{width}x{height}+{position_right}+{position_top}')

def toggle_password_visibility():
    if show_password_var.get():
        entry_password.config(show='')
    else:
        entry_password.config(show='*')

# Create the main window
root = tk.Tk()
root.title("Investor Centre LTD")
root.geometry("600x450")  
sv_ttk.set_theme("light")
root.resizable(False, False)  

# Define a custom font
custom_font = font.Font(family="Helvetica", size=28, weight="bold")

# Configure the grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)

# Title page
title_label = tk.Label(root, text='Investor Centre LTD', font=custom_font, padx=20, pady=20)
title_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

# Username label and entry
label_username = tk.Label(root, text="Username")
label_username.grid(row=1, column=0, sticky="e", pady=10, padx=5)

entry_username = tk.Entry(root)
entry_username.grid(row=1, column=1, sticky="w", pady=10, padx=5)

# Password label and entry
label_password = tk.Label(root, text="Password")
label_password.grid(row=2, column=0, sticky="e", pady=10, padx=5)

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=2, column=1, sticky="w", pady=10, padx=5)

# Show Password Checkbox
show_password_var = tk.BooleanVar()
show_password_check = ttk.Checkbutton(root, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
show_password_check.grid(row=3, column=0, columnspan=3, pady=5)

# Login button
login_button = ttk.Button(root, text="Login", command=login)
login_button.grid(row=4, column=2, pady=20, padx=5, sticky="w")

# Create account button
create_button = ttk.Button(root, text="Create account", command=lambda: [create_account_window(), root.withdraw()])
create_button.grid(row=4, column=0, pady=20, padx=5, sticky="e")

centre_window(root, 600, 450) 

# Run the application
root.mainloop()


