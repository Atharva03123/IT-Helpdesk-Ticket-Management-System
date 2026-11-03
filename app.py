import html
import re
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

try:
    import altair as alt
except ImportError:  # charts fall back to Streamlit's default style
    alt = None

from database import (
    create_ticket,
    fetch_tickets,
    get_connection,
    init_db,
    update_ticket,
)

st.set_page_config(
    page_title="IT Helpdesk",
    page_icon="🎫",
    layout="wide"
)

# ---------------- THEME (colours, animation, transitions) ----------------
THEME_CSS = """
<style>
:root {
    --cyan: #22d3ee;
    --blue: #3b82f6;
    --violet: #8b5cf6;
    --green: #34d399;
    --amber: #fbbf24;
    --red: #f87171;
    --text: #e6edf7;
    --muted: #94a3b8;
    --glass: rgba(255, 255, 255, 0.06);
    --glass-border: rgba(255, 255, 255, 0.14);
}

/* ---------- Animated background ---------- */
.stApp {
    background: linear-gradient(-45deg, #07101f, #0b2545, #0b4a5e, #2b1a63, #07101f);
    background-size: 400% 400%;
    animation: bgShift 22s ease infinite;
    color: var(--text);
}
.stApp::before {               /* faint "circuit grid" overlay */
    content: "";
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(34, 211, 238, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34, 211, 238, 0.045) 1px, transparent 1px);
    background-size: 46px 46px;
    pointer-events: none;
    z-index: 0;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { position: relative; z-index: 1; padding-top: 2rem; }

@keyframes bgShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}
@keyframes pulseDot {
    0%   { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
    70%  { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
    100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.55); }
    50%      { box-shadow: 0 0 14px 2px rgba(248, 113, 113, 0.55); }
}

/* ---------- Header banner ---------- */
.hero {
    display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
    padding: 22px 26px; margin-bottom: 18px;
    border-radius: 20px;
    background: linear-gradient(120deg, rgba(34, 211, 238, 0.16), rgba(139, 92, 246, 0.18));
    border: 1px solid var(--glass-border);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(10px);
    animation: slideDown 0.7s ease both;
}
.hero-icon {
    font-size: 2.2rem; width: 62px; height: 62px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    box-shadow: 0 6px 22px rgba(34, 211, 238, 0.35);
    transition: transform 0.4s ease;
}
.hero:hover .hero-icon { transform: rotate(-8deg) scale(1.08); }
.hero-text { flex: 1; min-width: 240px; }
.hero h1 {
    margin: 0; padding: 0; font-size: 1.9rem; font-weight: 800; line-height: 1.2;
    background: linear-gradient(90deg, #ffffff, var(--cyan), var(--violet), #ffffff);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    animation: shimmer 6s linear infinite;
}
.hero p { margin: 6px 0 0 0; color: var(--muted); font-size: 0.95rem; }
.live-pill {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    color: #d1fae5; background: rgba(52, 211, 153, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.4);
}
.live-pill .dot {
    width: 9px; height: 9px; border-radius: 50%; background: var(--green);
    animation: pulseDot 1.8s infinite;
}

/* ---------- Text ---------- */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: #f1f5f9; letter-spacing: 0.2px; }
.stApp h2 { border-left: 4px solid var(--cyan); padding-left: 12px; }
.stApp .stMarkdown p, .stApp .stMarkdown li { color: #d5deeb; }
.stApp [data-testid="stWidgetLabel"] p, .stApp label p { color: #cbd5e1; }
.stApp [data-testid="stCaptionContainer"] { color: var(--muted); }
.stApp hr { border-color: rgba(255, 255, 255, 0.12); }

/* ---------- Page transition: elements fade up ---------- */
[data-testid="stElementContainer"] { animation: fadeUp 0.5s ease both; }

/* ---------- Metric cards ---------- */
[data-testid="stMetric"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-left: 4px solid var(--cyan);
    border-radius: 16px;
    padding: 16px 18px;
    backdrop-filter: blur(8px);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 34px rgba(34, 211, 238, 0.22);
    border-color: rgba(34, 211, 238, 0.6);
}
[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"],
[data-testid="column"]:nth-child(1) [data-testid="stMetric"] { border-left-color: #22d3ee; }
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"],
[data-testid="column"]:nth-child(2) [data-testid="stMetric"] { border-left-color: #fbbf24; }
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"],
[data-testid="column"]:nth-child(3) [data-testid="stMetric"] { border-left-color: #8b5cf6; }
[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"],
[data-testid="column"]:nth-child(4) [data-testid="stMetric"] { border-left-color: #34d399; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color: var(--muted) !important; font-weight: 600; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div {
    color: #ffffff !important; font-weight: 800; text-shadow: 0 0 18px rgba(34, 211, 238, 0.35);
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08162b 0%, #0d2b4a 55%, #1a1b4b 100%);
    border-right: 1px solid rgba(34, 211, 238, 0.25);
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 10px 14px; border-radius: 12px; cursor: pointer;
    border: 1px solid transparent;
    transition: background 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 211, 238, 0.12); transform: translateX(6px);
    border-color: rgba(34, 211, 238, 0.4);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(34, 211, 238, 0.3), rgba(139, 92, 246, 0.3));
    border-color: rgba(34, 211, 238, 0.7);
    box-shadow: 0 0 18px rgba(34, 211, 238, 0.25);
}
[data-testid="stSidebar"] [role="radiogroup"] label p { color: #e6edf7 !important; font-weight: 600; }
.side-title { color: var(--muted); font-size: 0.78rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; margin: 6px 0 8px; }
.sla-chip {
    display: flex; align-items: center; gap: 10px; padding: 8px 12px; margin-bottom: 6px;
    border-radius: 10px; background: var(--glass); border: 1px solid var(--glass-border);
    color: #e6edf7; font-size: 0.9rem;
    transition: transform 0.2s ease, background 0.2s ease;
}
.sla-chip:hover { transform: translateX(4px); background: rgba(255, 255, 255, 0.11); }
.sla-chip .dot { width: 10px; height: 10px; border-radius: 50%; }
.sla-chip .hrs { margin-left: auto; font-weight: 700; color: #ffffff; }

/* ---------- Forms, inputs, buttons ---------- */
[data-testid="stForm"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 18px; padding: 22px;
    backdrop-filter: blur(8px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.28);
}
.stApp input, .stApp textarea, .stApp [data-baseweb="select"] > div {
    border-radius: 10px !important;
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
}
.stApp input:focus, .stApp textarea:focus {
    box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.55) !important;
}
.stApp .stButton > button,
.stApp [data-testid="stFormSubmitButton"] button,
.stApp [data-testid="stDownloadButton"] button {
    background: linear-gradient(90deg, #06b6d4, #6366f1, #8b5cf6);
    background-size: 200% auto;
    color: #ffffff; font-weight: 700; border: none; border-radius: 12px;
    padding: 0.55rem 1.4rem;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35);
    transition: transform 0.2s ease, box-shadow 0.25s ease, background-position 0.5s ease;
}
.stApp .stButton > button:hover,
.stApp [data-testid="stFormSubmitButton"] button:hover,
.stApp [data-testid="stDownloadButton"] button:hover {
    background-position: right center;
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 12px 28px rgba(34, 211, 238, 0.4);
    color: #ffffff;
}
.stApp .stButton > button:active,
.stApp [data-testid="stFormSubmitButton"] button:active,
.stApp [data-testid="stDownloadButton"] button:active { transform: scale(0.97); }

/* ---------- Expanders, tables, alerts ---------- */
[data-testid="stExpander"] {
    background: var(--glass); border: 1px solid var(--glass-border) !important;
    border-radius: 14px; overflow: hidden;
    transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(34, 211, 238, 0.6) !important;
    box-shadow: 0 8px 26px rgba(34, 211, 238, 0.16);
    transform: translateY(-2px);
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: #f1f5f9 !important; font-weight: 600; }
[data-testid="stExpander"] details[open] > div { animation: fadeUp 0.4s ease both; }
[data-testid="stDataFrame"] {
    border: 1px solid var(--glass-border); border-radius: 14px; overflow: hidden;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.3);
}
[data-testid="stAlert"] {
    border-radius: 14px; backdrop-filter: blur(6px);
    border: 1px solid var(--glass-border);
    animation: fadeUp 0.45s ease both;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] div, [data-testid="stAlert"] svg {
    color: #f8fafc !important; fill: #f8fafc;
}
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: rgba(251, 191, 36, 0.18); border-color: rgba(251, 191, 36, 0.65); }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: rgba(52, 211, 153, 0.18); border-color: rgba(52, 211, 153, 0.65); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"])    { background: rgba(34, 211, 238, 0.16); border-color: rgba(34, 211, 238, 0.6); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"])   { background: rgba(248, 113, 113, 0.2); border-color: rgba(248, 113, 113, 0.7); }
.stApp .stMarkdown a { color: #67e8f9; text-decoration-color: rgba(103, 232, 249, 0.5); transition: color 0.2s ease; }
.stApp .stMarkdown a:hover { color: #ffffff; }

/* ---------- Badges ---------- */
.badge {
    display: inline-block; padding: 4px 13px; margin: 0 8px 8px 0;
    border-radius: 999px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.3px;
    border: 1px solid transparent;
    transition: transform 0.2s ease;
}
.badge:hover { transform: scale(1.08); }
.b-critical { color: #fecaca; background: rgba(248, 113, 113, 0.18); border-color: rgba(248, 113, 113, 0.6); }
.b-high     { color: #fed7aa; background: rgba(251, 146, 60, 0.18);  border-color: rgba(251, 146, 60, 0.6); }
.b-medium   { color: #a5f3fc; background: rgba(34, 211, 238, 0.16);  border-color: rgba(34, 211, 238, 0.55); }
.b-low      { color: #bbf7d0; background: rgba(52, 211, 153, 0.16);  border-color: rgba(52, 211, 153, 0.55); }
.b-open     { color: #fde68a; background: rgba(251, 191, 36, 0.16);  border-color: rgba(251, 191, 36, 0.55); }
.b-progress { color: #c7d2fe; background: rgba(99, 102, 241, 0.2);   border-color: rgba(129, 140, 248, 0.6); }
.b-hold     { color: #e9d5ff; background: rgba(168, 85, 247, 0.18);  border-color: rgba(168, 85, 247, 0.55); }
.b-resolved { color: #bbf7d0; background: rgba(52, 211, 153, 0.16);  border-color: rgba(52, 211, 153, 0.55); }
.b-breach   { color: #fecaca; background: rgba(248, 113, 113, 0.2);  border-color: rgba(248, 113, 113, 0.7); animation: pulseGlow 1.8s infinite; }
.b-ok       { color: #bbf7d0; background: rgba(52, 211, 153, 0.16);  border-color: rgba(52, 211, 153, 0.55); }

/* ---------- Scrollbar + reduced motion ---------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: linear-gradient(var(--cyan), var(--violet)); border-radius: 8px; }
::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.04); }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
# Target resolution time (hours) for each priority
SLA_HOURS = {"Critical": 4, "High": 8, "Medium": 24, "Low": 48}

STATUSES = ["Open", "In Progress", "On Hold", "Resolved"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
CATEGORIES = ["Hardware", "Software", "Network", "Account", "Other"]
ROOT_CAUSES = [
    "Not identified",
    "User error",
    "Software issue",
    "Hardware failure",
    "Network issue",
    "Account / access issue",
    "Configuration issue",
    "Other",
]

# Standard troubleshooting guides (Knowledge Base)
KB_ARTICLES = [
    {
        "title": "Wi-Fi connected but no internet",
        "category": "Network",
        "symptoms": "Device shows connected to Wi-Fi but websites do not open.",
        "steps": [
            "Check whether other devices on the same Wi-Fi have internet.",
            "Run 'ping 8.8.8.8'. If it works but websites fail, the problem is DNS.",
            "Run 'ipconfig /flushdns' (Windows) and try again.",
            "Run 'ipconfig /release' then 'ipconfig /renew' to get a fresh IP address.",
            "Restart the router. If still failing, escalate to L2 (network team).",
        ],
    },
    {
        "title": "VPN not connecting",
        "category": "Network",
        "symptoms": "VPN client fails to connect or drops repeatedly.",
        "steps": [
            "Confirm the user has working internet without the VPN.",
            "Check username, password and MFA code, and make sure the account is not locked.",
            "Close and reopen the VPN client, then try a different network if possible.",
            "Update or reinstall the VPN client.",
            "If it still fails, escalate to the network team with the client error message.",
        ],
    },
    {
        "title": "Laptop running slow",
        "category": "Hardware",
        "symptoms": "Laptop takes a long time to start or applications freeze.",
        "steps": [
            "Open Task Manager and check CPU, memory and disk usage.",
            "End or uninstall the process or application using excessive resources.",
            "Disable unnecessary startup programs.",
            "Check free disk space (keep at least 15% free) and run Disk Cleanup.",
            "Install pending Windows updates and restart. If disk stays at 100%, escalate for a hardware check.",
        ],
    },
    {
        "title": "Printer offline or not printing",
        "category": "Hardware",
        "symptoms": "Print jobs are stuck in the queue or the printer shows as offline.",
        "steps": [
            "Check power, paper, cables and network connection of the printer.",
            "Clear stuck jobs from the print queue and restart the Print Spooler service.",
            "Make sure the correct printer is the default and 'Use printer offline' is unchecked.",
            "Reinstall or update the printer driver.",
            "Print a test page. If it fails, escalate for hardware repair.",
        ],
    },
    {
        "title": "Blue screen (BSOD) error",
        "category": "Hardware",
        "symptoms": "Windows shows a blue screen and restarts unexpectedly.",
        "steps": [
            "Note the stop code shown on the blue screen.",
            "Boot into Safe Mode and uninstall recently installed drivers, updates or software.",
            "Run 'sfc /scannow' and check memory and disk health.",
            "Update device drivers.",
            "If it keeps happening, escalate to L2 for hardware diagnostics.",
        ],
    },
    {
        "title": "Forgot password / account locked",
        "category": "Account",
        "symptoms": "User cannot log in or sees an 'account locked' message.",
        "steps": [
            "Verify the user's identity using the approved verification steps.",
            "Check whether the account is locked or the password has expired.",
            "Reset the password and force a change at next login.",
            "Ask the user to sign in again and confirm access.",
            "Document the ticket. Repeated lockouts may mean an old saved password on another device.",
        ],
    },
    {
        "title": "Outlook not opening or not syncing",
        "category": "Software",
        "symptoms": "Outlook crashes at start, stays on 'Loading profile' or does not receive mail.",
        "steps": [
            "Check internet connection and confirm Outlook is not in Offline mode.",
            "Start Outlook in safe mode ('outlook.exe /safe') to rule out add-ins.",
            "Disable recently added add-ins.",
            "Create a new mail profile from Control Panel > Mail.",
            "If the issue continues, run Office Quick Repair, then escalate to L2.",
        ],
    },
    {
        "title": "Application crashing on launch",
        "category": "Software",
        "symptoms": "An application closes immediately or shows an error when opened.",
        "steps": [
            "Note the exact error message and when it started.",
            "Check Event Viewer > Windows Logs > Application for the error entry.",
            "Restart the computer and try again.",
            "Repair or reinstall the application and install pending updates.",
            "If the error repeats for several users, escalate to L2 with the log details.",
        ],
    },
]


# ---------------- HELPERS ----------------
def server_now():
    """Current time as the database sees it, so SLA maths matches stored timestamps."""
    try:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT LOCALTIMESTAMP")
            now = cur.fetchone()[0]
            cur.close()
            return now
        finally:
            conn.close()
    except Exception:
        return datetime.now()


def split_notes(notes):
    """Notes are stored as an optional first line 'Root cause: X' followed by the notes."""
    notes = notes or ""
    match = re.match(r"^Root cause: (.+)\n?", notes)
    if match:
        return match.group(1).strip(), notes[match.end():].lstrip("\n")
    return "Not identified", notes


def join_notes(root_cause, notes):
    notes = notes.strip()
    if root_cause == "Not identified":
        return notes
    return f"Root cause: {root_cause}\n{notes}" if notes else f"Root cause: {root_cause}"


def hours_text(hours):
    total_minutes = int(abs(hours) * 60)
    return f"{total_minutes // 60}h {total_minutes % 60:02d}m"



def add_sla_fields(raw_tickets, now):
    """Calculate SLA deadline, breach status and resolution duration."""

    tickets = []

    for raw in raw_tickets:
        t = dict(raw)

        resolved = t["status"] == "Resolved"

        due = t["created_at"] + timedelta(
            hours=SLA_HOURS.get(t["priority"], 24)
        )

        # Use actual resolution timestamp for resolved tickets
        if resolved:
            end = t.get("resolved_at") or t["updated_at"]
        else:
            end = now

        t["sla_due"] = due
        t["sla_breached"] = end > due

        # Calculate elapsed time
        t["age_hours"] = round(
            (end - t["created_at"]).total_seconds() / 3600,
            1
        )

        t["sla_left_hours"] = (
            due - now
        ).total_seconds() / 3600

        t["root_cause"], t["notes_text"] = split_notes(
            t["resolution_notes"]
        )

        t["engineer"] = t["assigned_to"] or "Unassigned"

        tickets.append(t)

    return tickets



PRIORITY_COLORS = {
    "Critical": "#f87171", "High": "#fb923c", "Medium": "#22d3ee", "Low": "#34d399",
}
STATUS_COLORS = {
    "Open": "#fbbf24", "In Progress": "#818cf8", "On Hold": "#c084fc", "Resolved": "#34d399",
}
CHART_PALETTE = ["#22d3ee", "#8b5cf6", "#34d399", "#fbbf24", "#f472b6", "#60a5fa", "#fb923c", "#a3e635"]
BADGE_CLASS = {
    "Critical": "b-critical", "High": "b-high", "Medium": "b-medium", "Low": "b-low",
    "Open": "b-open", "In Progress": "b-progress", "On Hold": "b-hold", "Resolved": "b-resolved",
}


def badge(text, css_class=None):
    """Small coloured pill. Text is escaped before it goes into HTML."""
    css_class = css_class or BADGE_CLASS.get(text, "b-medium")
    return f'<span class="badge {css_class}">{html.escape(str(text))}</span>'


def bar(series, order=None, colors=None, height=250):
    """Coloured bar chart with a transparent background (matches the dark theme)."""
    if alt is None or len(series) == 0:
        st.bar_chart(series)
        return
    data = pd.DataFrame({"label": [str(i) for i in series.index], "count": series.values})
    domain = order or list(data["label"])
    colors = colors or {}
    palette = [colors.get(name, CHART_PALETTE[i % len(CHART_PALETTE)]) for i, name in enumerate(domain)]
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7, size=36)
        .encode(
            x=alt.X("label:N", sort=domain, title=None,
                    axis=alt.Axis(labelAngle=-20, labelLimit=120)),
            y=alt.Y("count:Q", title=None, axis=alt.Axis(tickMinStep=1)),
            color=alt.Color("label:N", scale=alt.Scale(domain=domain, range=palette), legend=None),
            tooltip=[alt.Tooltip("label:N", title="Name"), alt.Tooltip("count:Q", title="Tickets")],
        )
        .properties(height=height)
        .configure(background="transparent")
        .configure_axis(
            labelColor="#cbd5e1", gridColor="rgba(148,163,184,0.15)",
            domainColor="rgba(148,163,184,0.3)", tickColor="rgba(148,163,184,0.3)",
            labelFontSize=12,
        )
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True, theme=None)


# ---------------- PAGE HEADER ----------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-icon">🎫</div>
        <div class="hero-text">
            <h1>IT Helpdesk &amp; Ticket Management System</h1>
            <p>IT Support Operations | Ticket Tracking, SLA Monitoring &amp; Resolution</p>
        </div>
        <div class="live-pill"><span class="dot"></span> Help desk online</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize database
try:
    init_db()
    db_ready = True
except Exception as exc:
    db_ready = False
    st.error("Could not connect to PostgreSQL.")
    st.exception(exc)

if db_ready:

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Create Ticket", "Manage Tickets", "Knowledge Base"]
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        '<div class="side-title">SLA targets (resolution time)</div>'
        + "".join(
            f'<div class="sla-chip"><span class="dot" style="background:{PRIORITY_COLORS[level]}"></span>'
            f'{level}<span class="hrs">{hours} h</span></div>'
            for level, hours in SLA_HOURS.items()
        ),
        unsafe_allow_html=True,
    )

    # Fetch tickets
    now = server_now()
    tickets = add_sla_fields(fetch_tickets(), now)
    df = pd.DataFrame(tickets)

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":

        st.header("Support Operations Dashboard")

        if not tickets:
            st.info("No tickets yet. Create your first support ticket.")
        else:
            df["sla_status"] = df["sla_breached"].map(
                {True: "Breached", False: "Within SLA"}
            )
            df["created_at"] = pd.to_datetime(df["created_at"])

            total = len(df)
            resolved_df = df[df["status"] == "Resolved"]
            open_df = df[df["status"] != "Resolved"]

            open_count = int((df["status"] == "Open").sum())
            progress_count = int((df["status"] == "In Progress").sum())
            breach_rate = round(df["sla_breached"].mean() * 100, 1)
            avg_resolution = (
                round(resolved_df["age_hours"].mean(), 1) if len(resolved_df) else None
            )
            critical_open = int((open_df["priority"] == "Critical").sum())

            # KPI Cards
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Tickets", total)
            c2.metric("Open Tickets", open_count)
            c3.metric("In Progress", progress_count)
            c4.metric("Resolved", len(resolved_df))

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("SLA Breach Rate", f"{breach_rate}%")
            c6.metric(
                "Avg Resolution Time",
                f"{avg_resolution} h" if avg_resolution is not None else "-"
            )
            c7.metric("Open Critical Tickets", critical_open)
            c8.metric("Open Tickets Past SLA", int(open_df["sla_breached"].sum()))

            # Tickets that need attention
            at_risk = open_df[open_df["sla_breached"]]
            if len(at_risk):
                st.warning(
                    f"{len(at_risk)} open ticket(s) have breached their SLA. "
                    "Escalate them to the next support level."
                )
                st.dataframe(
                    at_risk[["id", "title", "priority", "status", "engineer", "age_hours"]]
                    .rename(columns={"engineer": "assigned_to", "age_hours": "open_for_hours"}),
                    use_container_width=True,
                    hide_index=True
                )

            st.divider()

            # Priority and Category Analysis
            left, right = st.columns(2)

            with left:
                st.subheader("Tickets by Priority")
                bar(
                    df["priority"].value_counts().reindex(PRIORITIES, fill_value=0),
                    order=PRIORITIES, colors=PRIORITY_COLORS
                )

                st.subheader("Tickets by Status")
                bar(
                    df["status"].value_counts().reindex(STATUSES, fill_value=0),
                    order=STATUSES, colors=STATUS_COLORS
                )

            with right:
                st.subheader("Tickets by Category")
                bar(df["category"].value_counts())

                st.subheader("Open Workload by Engineer")
                if len(open_df):
                    bar(open_df["engineer"].value_counts())
                else:
                    st.caption("No open tickets.")

            st.subheader("Root Causes (resolved tickets)")
            if len(resolved_df):
                bar(resolved_df["root_cause"].value_counts())
            else:
                st.caption("Root causes appear here once tickets are resolved.")

            st.divider()

            # Search Tickets
            st.subheader("Search and Filter Tickets")

            f1, f2, f3 = st.columns([2, 1, 1])
            search = f1.text_input("Search by ticket ID, title or requester")
            status_filter = f2.selectbox("Filter by Status", ["All"] + STATUSES)
            priority_filter = f3.selectbox("Filter by Priority", ["All"] + PRIORITIES)

            filtered_df = df.copy()

            if search.strip():
                s = search.strip().lower()
                filtered_df = filtered_df[
                    filtered_df["id"].astype(str).str.contains(s, regex=False)
                    | filtered_df["title"].str.lower().str.contains(s, regex=False)
                    | filtered_df["requester"].str.lower().str.contains(s, regex=False)
                ]

            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]

            if priority_filter != "All":
                filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

            table_df = filtered_df[
                ["id", "title", "requester", "category", "priority", "status",
                 "engineer", "sla_status", "created_at"]
            ].rename(columns={"engineer": "assigned_to"})
            table_df["created_at"] = table_df["created_at"].dt.strftime("%d %b %Y %H:%M")

            def cell_color(value):
                colors = {
                    **{k: f"{v}" for k, v in PRIORITY_COLORS.items()},
                    **STATUS_COLORS,
                    "Breached": "#f87171", "Within SLA": "#34d399",
                }
                color = colors.get(value)
                return f"color: {color}; font-weight: 700" if color else ""

            styler = table_df.style
            apply_cells = getattr(styler, "map", None) or styler.applymap
            styled_df = apply_cells(cell_color, subset=["priority", "status", "sla_status"])

            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(f"Showing {len(filtered_df)} of {total} tickets")

            st.download_button(
                "Download tickets as CSV",
                data=table_df.to_csv(index=False).encode("utf-8"),
                file_name="helpdesk_tickets.csv",
                mime="text/csv"
            )

    # ---------------- CREATE TICKET ----------------
    elif menu == "Create Ticket":

        st.subheader("Report a Technical Issue")

        with st.form("create_ticket_form", clear_on_submit=True):

            requester = st.text_input("Your name")
            email = st.text_input("Email address")

            category = st.selectbox("Issue category", CATEGORIES)

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High", "Critical"],
                index=1
            )

            title = st.text_input(
                "Issue title",
                placeholder="Example: Laptop cannot connect to Wi-Fi"
            )

            description = st.text_area(
                "Describe the issue",
                placeholder="What happened, when it started, the error message and what you already tried"
            )

            submitted = st.form_submit_button("Submit Ticket")

            if submitted:

                if (
                    not requester.strip()
                    or not title.strip()
                    or not description.strip()
                ):
                    st.warning(
                        "Please fill in your name, issue title and description."
                    )

                elif email.strip() and "@" not in email:
                    st.warning("Please enter a valid email address.")

                else:
                    try:
                        ticket_id = create_ticket(
                            requester.strip(),
                            email.strip(),
                            category,
                            priority,
                            title.strip(),
                            description.strip()
                        )

                        st.success(
                            f"Ticket created successfully! Your ticket ID is #{ticket_id}. "
                            f"Target resolution time: {SLA_HOURS[priority]} hours."
                        )

                    except Exception as exc:
                        st.error("Ticket could not be saved.")
                        st.exception(exc)

    # ---------------- MANAGE TICKETS ----------------
    elif menu == "Manage Tickets":

        st.subheader("Manage Support Tickets")

        if not tickets:
            st.info("No tickets available. Create a ticket first.")

        else:
            ids = [t["id"] for t in tickets]

            selected_id = st.selectbox(
                "Select Ticket ID",
                ids
            )

            ticket = next(
                t for t in tickets if t["id"] == selected_id
            )

            st.markdown(f"### Ticket #{ticket['id']}: {ticket['title']}")

            if ticket["status"] == "Resolved":
                sla_badge = badge("SLA breached", "b-breach") if ticket["sla_breached"] else badge("SLA met", "b-ok")
            elif ticket["sla_breached"]:
                sla_badge = badge("SLA breached", "b-breach")
            else:
                sla_badge = badge("Within SLA", "b-ok")
            st.markdown(
                badge(ticket["priority"]) + badge(ticket["status"]) + sla_badge,
                unsafe_allow_html=True,
            )

            info_left, info_right = st.columns(2)

            with info_left:
                st.write(f"**Requester:** {ticket['requester']}")
                st.write(f"**Email:** {ticket['email'] or 'Not provided'}")
                st.write(f"**Category:** {ticket['category']}")
                st.write(f"**Priority:** {ticket['priority']}")

            with info_right:
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Created:** {ticket['created_at'].strftime('%d %b %Y %H:%M')}")
                st.write(f"**SLA target:** {SLA_HOURS.get(ticket['priority'], 24)} hours")

                if ticket["status"] == "Resolved":
                    outcome = "Breached" if ticket["sla_breached"] else "Met"
                    st.write(
                        f"**SLA result:** {outcome} "
                        f"(resolved in {hours_text(ticket['age_hours'])})"
                    )
                elif ticket["sla_left_hours"] >= 0:
                    st.write(
                        f"**SLA:** {hours_text(ticket['sla_left_hours'])} remaining"
                    )
                else:
                    st.write(
                        f"**SLA:** Breached by {hours_text(ticket['sla_left_hours'])}"
                    )
                    st.warning(
                        "SLA breached. Escalate this ticket to the next support level (L2)."
                    )

            st.write(f"**Description:** {ticket['description']}")

            related = [a for a in KB_ARTICLES if a["category"] == ticket["category"]]
            if related:
                with st.expander(
                    f"Suggested fixes from the Knowledge Base ({ticket['category']})"
                ):
                    for article in related:
                        st.markdown(f"**{article['title']}**")
                        for number, step in enumerate(article["steps"], start=1):
                            st.write(f"{number}. {step}")

            st.divider()

            with st.form("update_ticket_form"):

                u1, u2 = st.columns(2)

                status = u1.selectbox(
                    "Ticket Status",
                    STATUSES,
                    index=STATUSES.index(ticket["status"])
                    if ticket["status"] in STATUSES else 0
                )

                root_cause = u2.selectbox(
                    "Root Cause",
                    ROOT_CAUSES,
                    index=ROOT_CAUSES.index(ticket["root_cause"])
                    if ticket["root_cause"] in ROOT_CAUSES else 0
                )

                assigned_to = st.text_input(
                    "Assigned Support Engineer",
                    value=ticket["assigned_to"] or ""
                )

                resolution_notes = st.text_area(
                    "Troubleshooting / Resolution Notes",
                    value=ticket["notes_text"],
                    placeholder="Steps taken, what fixed the issue and any follow-up"
                )

                updated = st.form_submit_button("Update Ticket")

                if updated:
                    if status == "Resolved" and not resolution_notes.strip():
                        st.warning(
                            "Add troubleshooting / resolution notes before resolving a ticket."
                        )
                    else:
                        try:
                            update_ticket(
                                selected_id,
                                status,
                                assigned_to.strip(),
                                join_notes(root_cause, resolution_notes)
                            )

                            st.success("Ticket updated successfully!")
                            st.rerun()

                        except Exception as exc:
                            st.error("Could not update ticket.")
                            st.exception(exc)

    # ---------------- KNOWLEDGE BASE ----------------
    elif menu == "Knowledge Base":

        st.subheader("Troubleshooting Knowledge Base")
        st.caption("Standard fixes for common issues. Try these before escalating a ticket.")

        k1, k2 = st.columns([2, 1])
        kb_search = k1.text_input("Search articles")
        kb_category = k2.selectbox("Category", ["All"] + CATEGORIES)

        articles = KB_ARTICLES

        if kb_category != "All":
            articles = [a for a in articles if a["category"] == kb_category]

        if kb_search.strip():
            q = kb_search.strip().lower()
            articles = [
                a for a in articles
                if q in a["title"].lower()
                or q in a["symptoms"].lower()
                or any(q in step.lower() for step in a["steps"])
            ]

        if not articles:
            st.info("No articles match your search.")

        for article in articles:
            with st.expander(f"{article['title']}  ({article['category']})"):
                st.markdown(f"**Symptoms:** {article['symptoms']}")
                st.markdown("**Resolution steps:**")
                for number, step in enumerate(article["steps"], start=1):
                    st.write(f"{number}. {step}")