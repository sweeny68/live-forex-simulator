# Project Setup Guide

## Installation Steps

1. **Install dependencies**  
   Open your terminal and run:  

   pip install -r requirements.txt

2. **API Key Setup (Exchange Rate API)**

This project requires an API key from ExchangeRate Host.

    Sign up at ExchangeRate Host and obtain your API key.

    Create a config.json file in the project root directory.

    Add the following content (replace your_api_key_here with your actual API key):

{
    "EXCHANGE_RATE_API_KEY": "your_api_key_here"
}

3. **Start the Application**
Run the main script:

    python main.py

**Admin Login Credentials**

    Username: admin
    Password: 123