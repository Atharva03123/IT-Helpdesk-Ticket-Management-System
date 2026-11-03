
import os
import pg8000.dbapi
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# PostgreSQL configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "it_helpdesk")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD is missing. Check your .env file.")


def get_connection():
    """Create and return a PostgreSQL connection."""
    return pg8000.dbapi.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    """Create tickets table and ensure required columns exist."""

    sql = """
    CREATE TABLE IF NOT EXISTS tickets (
        id SERIAL PRIMARY KEY,
        requester VARCHAR(120) NOT NULL,
        email VARCHAR(255),
        category VARCHAR(30) NOT NULL,
        priority VARCHAR(20) NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Open',
        assigned_to VARCHAR(120),
        resolution_notes TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    ALTER TABLE tickets
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;
    """

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
    finally:
        conn.close()


def create_ticket(requester, email, category, priority, title, description):
    """Insert a ticket safely and return its new ID."""

    sql = """
    INSERT INTO tickets
        (requester, email, category, priority, title, description)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id;
    """

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            requester,
            email,
            category,
            priority,
            title,
            description
        ))
        ticket_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return ticket_id
    finally:
        conn.close()


def fetch_tickets():
    """Return tickets as dictionaries, newest first."""

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets ORDER BY created_at DESC;")
        columns = [column[0] for column in cur.description]
        rows = cur.fetchall()
        cur.close()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def update_ticket(ticket_id, status, assigned_to, resolution_notes):
    """Update ticket and maintain its resolution timestamp."""

    sql = """
    UPDATE tickets
    SET status = %s,
        assigned_to = %s,
        resolution_notes = %s,
        updated_at = CURRENT_TIMESTAMP,
        resolved_at = CASE
            WHEN %s = 'Resolved'
            THEN COALESCE(resolved_at, CURRENT_TIMESTAMP)
            ELSE NULL
        END
    WHERE id = %s;
    """

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            status,
            assigned_to,
            resolution_notes,
            status,
            ticket_id
        ))
        conn.commit()
        cur.close()
    finally:
        conn.close()
