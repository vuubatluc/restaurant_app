"""Database layer - handles all database connections and queries"""
import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CURRENCY


def get_server_conn(database=None):
    """Get connection to MySQL server with optional database selection"""
    cfg = dict(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=True)
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)


def get_conn():
    """Get connection to the restaurant database"""
    return get_server_conn(DB_NAME)


def query_all(q, params=()):
    """Execute a SELECT query and return all rows"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(q, params)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


def query_one(q, params=()):
    """Execute a SELECT query and return one row"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(q, params)
        row = cur.fetchone()
        return row
    finally:
        cur.close()
        conn.close()


def execute(q, params=()):
    """Execute an INSERT/UPDATE/DELETE query and return last row ID"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(q, params)
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def exec_many(ops):
    """Execute multiple queries in sequence"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        for q, p in ops:
            cur.execute(q, p)
    finally:
        cur.close()
        conn.close()


def get_setting(key, default=None):
    """Get a setting value from the settings table"""
    row = query_one("SELECT value FROM settings WHERE `key`=%s", (key,))
    if row is None:
        return default
    try:
        return float(row[0])
    except:
        return row[0]


def set_setting(key, value):
    """Set a setting value in the settings table"""
    execute(
        "INSERT INTO settings(`key`, `value`) VALUES(%s,%s) ON DUPLICATE KEY UPDATE value=VALUES(value)",
        (key, str(value)),
    )


def money(x):
    """Format a number as currency"""
    try:
        x = float(x)
    except:
        return str(x)
    return f"{int(x):,} {CURRENCY}".replace(",", ".")
