"""Database access for the website. Same SQL Server database as the desktop app.

Override with environment variables if needed (e.g. SQL login instead of Windows auth):
  VR_SERVER, VR_DATABASE, VR_USER, VR_PASSWORD
"""
import os
import pyodbc


def get_connection():
    server = os.environ.get("VR_SERVER", "localhost")
    database = os.environ.get("VR_DATABASE", "VehicleRental")
    user = os.environ.get("VR_USER")
    if user:
        auth = f"UID={user};PWD={os.environ.get('VR_PASSWORD', '')};"
    else:
        auth = "Trusted_Connection=yes;"
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};DATABASE={database};{auth}"
        "TrustServerCertificate=yes;"
    )


def query(sql, params=()):
    """Run a SELECT, return a list of dicts."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def query_one(sql, params=()):
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    """Run INSERT/UPDATE/DELETE; commits on success. Returns rowcount."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.rowcount
