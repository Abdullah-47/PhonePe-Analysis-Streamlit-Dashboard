# PhonePe Analysis Streamlit Dashboard

This project provides an interactive dashboard for analyzing PhonePe data using Python and Streamlit. Follow the steps below to set up the project from scratch.

## Prerequisites

- **MySQL Workbench** (for database management):  
  [Download and Install MySQL Workbench](https://dev.mysql.com/downloads/workbench/)
- **Python 3.x** (recommended: 3.8+)

---

## Setup Instructions

### 1. Create the Database and Tables

- Open **MySQL Workbench**.
- Copy all the SQL code from `DB_Creation.sql` (located in this repository).
- Paste the code into a new SQL tab in MySQL Workbench and execute it to create the database and tables.

### 2. Install Required Python Libraries

- Open a terminal in the project directory.
- Run the following command to install all dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Load the Database with Data

- Ensure your local MySQL database server is running.
- Edit the database connection details (username, host, password, db_name) in `load_sql.py` as per your environment, or pass them when prompted.
- Execute the following command to load data from the CSV/JSON files into your database:
  ```bash
  python load_sql.py
  ```
  (This script will read the necessary files and populate your database.)

### 4. Configure Streamlit Secrets

- Create a folder named `.streamlit` in the project root directory (if it doesn't already exist).
- Inside `.streamlit`, create a file named `secrets.toml`.
- Add your MySQL credentials to `secrets.toml` as follows:

  ```toml
  [mysql]
  host = ""        # your hostname, e.g., "localhost"
  port = 0000      # your port, e.g., 3306
  database = "phonepe_db"  # your database name
  username = ""    # your MySQL username
  password = ""    # your MySQL password
  ```

### 5. Run the Streamlit Dashboard

- From the project directory, launch the dashboard with:
  ```bash
  streamlit run phonepe_dashboard.py
  ```
- This will open the PhonePe Analysis dashboard in your default web browser.

---

## Project Structure

- `DB_Creation.sql` — SQL script to create all tables and the database
- `load_sql.py` — Python script to load data from CSV/JSON files into the database
- `.streamlit/secrets.toml` — Configuration file for database connection secrets
- `requirements.txt` — List of required Python libraries
- `phonepe_dashboard.py` — Main Streamlit dashboard application

---

## License

Licensed under the [CDLA-Permissive-2.0 open data license](https://github.com/PhonePe/pulse/blob/LICENSE)

---

**Happy Analyzing!**
