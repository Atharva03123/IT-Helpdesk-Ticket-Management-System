# IT Helpdesk & Ticket Management System

A web-based IT Helpdesk and Ticket Management System built using Python, Streamlit, and PostgreSQL to manage technical support requests, track ticket status, monitor SLA targets, and analyze support operations.

## Project Overview

This application helps IT support teams manage employee technical issues through a centralized ticket management platform. Support engineers can create, assign, update, and track tickets while monitoring resolution performance.

## Key Features

- **Dashboard:** Monitor total, open, in-progress, and resolved tickets.
- **Ticket Management:** Create and update technical support tickets.
- **Priority Management:** Categorize tickets as Critical, High, Medium, or Low.
- **SLA Monitoring:** Track resolution deadlines based on ticket priority.
- **Engineer Workload:** Monitor pending tickets assigned to support engineers.
- **Root Cause Analysis:** Record and analyze reasons behind resolved issues.
- **Search and Filtering:** Find tickets by ID, title, requester, status, and priority.
- **CSV Export:** Download ticket records for further analysis.
- **Knowledge Base:** Access troubleshooting guidance for common IT issues.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| PostgreSQL | Database |
| SQL | Database operations |
| Pandas | Data processing |
| Altair | Data visualization |
| HTML & CSS | UI styling |
| pg8000 | PostgreSQL connectivity |

## SLA Configuration

| Priority | Target Resolution Time |
|---|---:|
| Critical | 4 hours |
| High | 8 hours |
| Medium | 24 hours |
| Low | 48 hours |

*These are the configurable demo targets used in this project.*

## Project Structure

```text
IT-Helpdesk-Ticket-Management-System/
│
├── app.py
├── database.py
├── insert_sample_tickets.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Atharva03123/IT-Helpdesk-Ticket-Management-System.git
cd IT-Helpdesk-Ticket-Management-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named `it_helpdesk`.

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=it_helpdesk
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
```

Replace the password with your own PostgreSQL password.

**Important:** Never upload your `.env` file or database credentials to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

## Learning Outcomes

- Python application development
- PostgreSQL database connectivity
- SQL-based CRUD operations
- IT support ticket lifecycle management
- SLA monitoring and tracking
- Dashboard development and data visualization
- Basic troubleshooting workflow design

## Author

**Atharva Shivangi**

- GitHub: [Atharva03123](https://github.com/Atharva03123)

---

*Developed as a portfolio project to demonstrate Python development, database management, dashboard development, and IT support workflow automation.*
