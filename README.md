# IT Helpdesk & Ticket Management System

A beginner-friendly helpdesk ticketing application built with Python, Streamlit and PostgreSQL.

## Features
- Dashboard showing ticket totals by status
- Create support tickets
- Categorize issues (Hardware, Software, Network, Account, Other)
- Assign priority (Low, Medium, High, Critical)
- Update ticket status and support engineer
- Store troubleshooting and resolution notes

## Requirements
- Python 3.9+
- PostgreSQL
- VS Code (recommended)

## Setup on Windows (PowerShell)

### 1. Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install packages
```powershell
python -m pip install -r requirements.txt
```

### 3. Create the PostgreSQL database
Open pgAdmin or psql and run:
```sql
CREATE DATABASE it_helpdesk;
```

### 4. Configure your PostgreSQL password
Open `database.py` and replace `CHANGE_ME` with the password for your local PostgreSQL `postgres` user.

Do not upload your real database password to GitHub. For a safer setup, set the `DB_PASSWORD` environment variable in your terminal instead.

PowerShell example:
```powershell
$env:DB_PASSWORD = "your_local_postgres_password"
```

If your PostgreSQL username is not `postgres`, set `DB_USER` too:
```powershell
$env:DB_USER = "your_postgres_username"
```

### 5. Run the application
```powershell
streamlit run app.py
```

Streamlit will show a local URL, usually http://localhost:8501.

## How to test
1. Open **Create Ticket**.
2. Enter a sample issue such as "Laptop cannot connect to Wi-Fi".
3. Submit the ticket and note its ID.
4. Open **Manage Tickets**.
5. Assign an engineer, add troubleshooting notes, and change status to In Progress or Resolved.
6. Return to **Dashboard** to see the updated counts.

## Learning note
This is a learning/demo project, not a production-ready service desk. A production system would need authentication, role-based access, audit logs, stronger secret management, input controls, SLA rules, backups and deployment hardening.
