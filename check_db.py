"""
Database verification script
Check if database is properly initialized
"""

import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def check_database():
    """Check if database exists and has all required tables"""
    try:
        # Try to connect to server
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print("✓ Connected to MySQL server")
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
        if not cursor.fetchone():
            print(f"✗ Database '{DB_NAME}' does not exist")
            print("\n💡 Run: python init_db.py")
            return False
        
        print(f"✓ Database '{DB_NAME}' exists")
        
        # Connect to our database
        cursor.close()
        conn.close()
        
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Check tables
        required_tables = [
            'categories', 'menu_items', 'dining_tables', 
            'orders', 'order_items', 'settings', 'order_audit'
        ]
        
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"✗ Missing tables: {', '.join(missing_tables)}")
            print("\n💡 Run: python init_db.py")
            return False
        
        print(f"✓ All required tables exist ({len(required_tables)} tables)")
        
        # Check if we have data
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dining_tables")
        table_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        menu_count = cursor.fetchone()[0]
        
        print(f"✓ Categories: {cat_count}")
        print(f"✓ Dining tables: {table_count}")
        print(f"✓ Menu items: {menu_count}")
        
        # Check procedures
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (DB_NAME,))
        procedures = cursor.fetchall()
        print(f"✓ Stored procedures: {len(procedures)}")
        
        # Check triggers
        cursor.execute("""
            SELECT TRIGGER_NAME 
            FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = %s
        """, (DB_NAME,))
        triggers = cursor.fetchall()
        print(f"✓ Triggers: {len(triggers)}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE IS READY!")
        print("=" * 60)
        print("\n💡 You can now run: python main.py")
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ MySQL Error: {e}")
        if e.errno == 1045:
            print("\n💡 Check your username and password in config.py")
        elif e.errno == 2003:
            print("\n💡 Make sure MySQL server is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🔍 Checking database status...\n")
    print("=" * 60)
    check_database()
