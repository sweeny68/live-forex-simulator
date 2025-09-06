# Forex Trading Simulation

A Python-based Forex application that fetches live exchange rates and allows users to place simulated trades in real time as well as administrative access for managing data.

![forex1](https://github.com/user-attachments/assets/24dfd375-aec0-4b7e-aae3-fda3736c50ed)

![forex2](https://github.com/user-attachments/assets/ee3556da-e984-4b3f-b1c9-c48981165832)

---


## Table of Contents


- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Admin Login](#admin-login)
- [Project Structure](#project-structure)


---


## Features


- Fetches real-time exchange rates using yfinance and the ExchangeRate Host API
- Plots real-time financial data using mplfinance
- Stores data in a local SQLite database (`main.db`)
- Provides an admin interface with login credentials
- Built using Python 3 and modular design


---


## Installation


1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Forex
```


2. **Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```


3. **Install dependencies**
```bash
pip install -r other/requirements.txt
```


---


## Configuration


1. Obtain an API key from [ExchangeRate Host](https://exchangerate.host/#/).


2. Create a `config.json` file in the project root directory with the following content:


```json
{
"EXCHANGE_RATE_API_KEY": "your_api_key_here"
}
```


Replace `"your_api_key_here"` with your actual API key.


---


## Usage


Run the main script:


```bash
python main.py
```


---

## Admin Login


Use the following credentials to log in as an administrator:


- **Username:** admin
- **Password:** 123


---


## Project Structure


```
Forex/
├── config.json # API key configuration
├── data_access.py # Database access functions
├── db_setup.py # Database setup scripts
├── main.db # SQLite database file
├── main.py # Main application script
├── other/
│ └── requirements.txt # Python dependencies
├── __pycache__/ # Compiled Python files
└── README.md # Project documentation
```


---
