
import random
from database import create_ticket, init_db

# Initialize database
init_db()

# Sample realistic IT support data
requesters = [
    ("Rahul Sharma", "rahul@gmail.com"),
    ("Priya Patil", "priya@gmail.com"),
    ("Amit Deshmukh", "amit@gmail.com"),
    ("Sneha Kulkarni", "sneha@gmail.com"),
    ("Rohit Joshi", "rohit@gmail.com"),
    ("Neha Shah", "neha@gmail.com"),
    ("Akash More", "akash@gmail.com"),
    ("Pooja Pawar", "pooja@gmail.com"),
    ("Vikas Gupta", "vikas@gmail.com"),
    ("Anjali Singh", "anjali@gmail.com"),
]

issues = {
    "Hardware": [
        ("Laptop running slow", "Laptop takes several minutes to start."),
        ("Keyboard not working", "Some keyboard keys are not responding."),
        ("Monitor not displaying", "Monitor shows a black screen."),
        ("Printer offline", "Printer is connected but not printing."),
        ("Battery draining quickly", "Laptop battery drains unusually fast."),
    ],
    "Software": [
        ("Outlook not opening", "Outlook crashes when the user opens it."),
        ("Application crashing", "Business application closes unexpectedly."),
        ("Excel not responding", "Excel freezes while opening large files."),
        ("Windows update failed", "Windows update repeatedly shows an error."),
        ("Browser not working", "Browser crashes while accessing websites."),
    ],
    "Network": [
        ("Wi-Fi not connecting", "Laptop cannot connect to office Wi-Fi."),
        ("VPN connection failed", "VPN disconnects during remote work."),
        ("Slow internet", "Internet speed is very slow."),
        ("Network drive inaccessible", "User cannot access the shared drive."),
        ("DNS resolution error", "Websites cannot be reached by domain name."),
    ],
    "Account": [
        ("Password reset required", "User forgot their account password."),
        ("Account locked", "Account locked after multiple failed attempts."),
        ("Email login failed", "User cannot sign in to their email account."),
        ("Access permission denied", "User cannot access a required folder."),
        ("MFA verification issue", "User cannot complete multi-factor authentication."),
    ],
    "Other": [
        ("System performance issue", "Computer performance has become unstable."),
        ("Software installation request", "User needs approved software installed."),
        ("New employee setup", "New employee requires workstation configuration."),
        ("Data backup request", "User needs assistance with file backup."),
        ("IT support request", "User needs help with a technical issue."),
    ],
}

priorities = ["Critical", "High", "Medium", "Low"]
statuses = ["Open", "In Progress", "On Hold", "Resolved"]

engineers = [
    "Atharva",
    "Rahul",
    "Priya",
    "Amit",
    "Unassigned",
]

resolution_notes = {
    "Open": "",
    "In Progress": "Initial troubleshooting completed. Further investigation is ongoing.",
    "On Hold": "Waiting for user confirmation or additional information.",
    "Resolved": "Issue diagnosed and resolved. Solution tested with the user.",
}

# Generate 100 sample tickets
random.seed(42)

inserted = 0

for i in range(100):
    requester, email = random.choice(requesters)

    category = random.choice(list(issues.keys()))
    title, description = random.choice(issues[category])

    priority = random.choices(
        priorities,
        weights=[10, 20, 40, 30]
    )[0]

    status = random.choices(
        statuses,
        weights=[30, 25, 10, 35]
    )[0]

    assigned_to = random.choice(engineers)

    notes = resolution_notes[status]

    try:
        ticket_id = create_ticket(
            requester,
            email,
            category,
            priority,
            title,
            description,
        )

        # Apply the selected status and assignment
        if status != "Open" or assigned_to != "Unassigned":
            from database import update_ticket

            update_ticket(
                ticket_id,
                status,
                "" if assigned_to == "Unassigned" else assigned_to,
                notes,
            )

        inserted += 1
        print(f"Inserted ticket #{ticket_id}: {title}")

    except Exception as error:
        print(f"Failed to insert ticket: {error}")

print(f"\nCompleted! {inserted} sample tickets inserted.")
