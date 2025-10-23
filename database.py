"""Database layer - handles all database connections and queries"""
import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CURRENCY


def get_server_conn(database=None):
    """Get connection to MySQL server with optional database selection"""
    cfg = dict(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=True)
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)


def get_raw_conn(database=None):
    """Get connection without autocommit for transaction control"""
    cfg = dict(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=False)
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


# ========================= DATABASE INITIALIZATION =========================

def drop_and_create_database():
    """Drop existing database and create new one"""
    conn = get_server_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DROP DATABASE IF EXISTS restaurant_app")
        cursor.execute("CREATE DATABASE restaurant_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Database created successfully")
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Create all database tables"""
    conn = get_conn()
    cursor = conn.cursor()
    
    tables = [
        # Categories table
        """
        CREATE TABLE IF NOT EXISTS categories (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        
        # Menu items table
        """
        CREATE TABLE IF NOT EXISTS menu_items (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(255) NOT NULL,
          category_id INT,
          price DECIMAL(12,2) NOT NULL,
          is_available TINYINT(1) NOT NULL DEFAULT 1,
          description TEXT,
          CONSTRAINT fk_menu_cat FOREIGN KEY (category_id) REFERENCES categories(id)
            ON UPDATE RESTRICT ON DELETE SET NULL
        )
        """,
        
        # Dining tables table
        """
        CREATE TABLE IF NOT EXISTS dining_tables (
          id INT AUTO_INCREMENT PRIMARY KEY,
          label VARCHAR(255) NOT NULL UNIQUE,
          seats INT DEFAULT 4
        )
        """,
        
        # Orders table
        """
        CREATE TABLE IF NOT EXISTS orders (
          id INT AUTO_INCREMENT PRIMARY KEY,
          table_id INT,
          created_at DATETIME NOT NULL,
          subtotal DECIMAL(14,2) NOT NULL DEFAULT 0,
          tax DECIMAL(14,2) NOT NULL DEFAULT 0,
          service DECIMAL(14,2) NOT NULL DEFAULT 0,
          total DECIMAL(14,2) NOT NULL DEFAULT 0,
          status ENUM('OPEN','PAID','CANCELLED') NOT NULL,
          note TEXT,
          CONSTRAINT fk_orders_table FOREIGN KEY (table_id) REFERENCES dining_tables(id)
            ON UPDATE RESTRICT ON DELETE SET NULL
        )
        """,
        
        # Order items table
        """
        CREATE TABLE IF NOT EXISTS order_items (
          id INT AUTO_INCREMENT PRIMARY KEY,
          order_id INT NOT NULL,
          item_id INT NOT NULL,
          item_name VARCHAR(255) NOT NULL,
          quantity INT NOT NULL,
          unit_price DECIMAL(12,2) NOT NULL,
          line_total DECIMAL(14,2) NOT NULL DEFAULT 0,
          CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id)
            ON UPDATE CASCADE ON DELETE CASCADE,
          CONSTRAINT fk_oi_item FOREIGN KEY (item_id) REFERENCES menu_items(id)
            ON UPDATE RESTRICT ON DELETE RESTRICT
        )
        """,
        
        # Settings table
        """
        CREATE TABLE IF NOT EXISTS settings (
          `key` VARCHAR(64) PRIMARY KEY,
          `value` VARCHAR(128)
        )
        """,
        
        # Order audit table
        """
        CREATE TABLE IF NOT EXISTS order_audit(
          id INT AUTO_INCREMENT PRIMARY KEY,
          action VARCHAR(64) NOT NULL,
          order_id INT NOT NULL,
          changed_at DATETIME NOT NULL,
          note TEXT
        )
        """
    ]
    
    try:
        for table_sql in tables:
            cursor.execute(table_sql)
        print("✓ Tables created successfully")
    finally:
        cursor.close()
        conn.close()


def create_triggers_and_procedures():
    """Create database triggers and stored procedures"""
    conn = get_raw_conn(DB_NAME)
    cursor = conn.cursor()
    
    # First, drop existing triggers and procedures
    drops = [
        "DROP TRIGGER IF EXISTS bi_menu_items_price",
        "DROP TRIGGER IF EXISTS bu_menu_items_price",
        "DROP TRIGGER IF EXISTS bi_order_items_guard",
        "DROP TRIGGER IF EXISTS bu_order_items_guard",
        "DROP TRIGGER IF EXISTS bi_order_items_calc_line_total",
        "DROP TRIGGER IF EXISTS bu_order_items_calc_line_total",
        "DROP TRIGGER IF EXISTS ai_order_items_recalc",
        "DROP TRIGGER IF EXISTS au_order_items_recalc",
        "DROP TRIGGER IF EXISTS ad_order_items_recalc",
        "DROP TRIGGER IF EXISTS au_orders_status_audit",
        "DROP PROCEDURE IF EXISTS sp_recalc_order_totals",
        "DROP PROCEDURE IF EXISTS sp_revenue_by_month",
        "DROP PROCEDURE IF EXISTS sp_revenue_by_date",
    ]
    
    for drop_sql in drops:
        try:
            cursor.execute(drop_sql)
        except:
            pass
    
    # Create triggers and procedures
    objects = [
        # Trigger: Check menu item price on insert
        """
        CREATE TRIGGER bi_menu_items_price
        BEFORE INSERT ON menu_items
        FOR EACH ROW
        BEGIN
          IF NEW.price < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Giá phải >= 0';
          END IF;
        END
        """,
        
        # Trigger: Check menu item price on update
        """
        CREATE TRIGGER bu_menu_items_price
        BEFORE UPDATE ON menu_items
        FOR EACH ROW
        BEGIN
          IF NEW.price < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Giá phải >= 0';
          END IF;
        END
        """,
        
        # Trigger: Guard order items on insert
        """
        CREATE TRIGGER bi_order_items_guard
        BEFORE INSERT ON order_items
        FOR EACH ROW
        BEGIN
          IF NEW.quantity <= 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Số lượng phải > 0';
          END IF;
          IF NEW.unit_price < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Đơn giá phải >= 0';
          END IF;
        END
        """,
        
        # Trigger: Guard order items on update
        """
        CREATE TRIGGER bu_order_items_guard
        BEFORE UPDATE ON order_items
        FOR EACH ROW
        BEGIN
          IF NEW.quantity <= 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Số lượng phải > 0';
          END IF;
          IF NEW.unit_price < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Đơn giá phải >= 0';
          END IF;
        END
        """,
        
        # Trigger: Calculate line total on insert
        """
        CREATE TRIGGER bi_order_items_calc_line_total
        BEFORE INSERT ON order_items
        FOR EACH ROW
        BEGIN
          SET NEW.line_total = NEW.quantity * NEW.unit_price;
        END
        """,
        
        # Trigger: Calculate line total on update
        """
        CREATE TRIGGER bu_order_items_calc_line_total
        BEFORE UPDATE ON order_items
        FOR EACH ROW
        BEGIN
          SET NEW.line_total = NEW.quantity * NEW.unit_price;
        END
        """,
        
        # Stored Procedure: Recalculate order totals
        """
        CREATE PROCEDURE sp_recalc_order_totals(IN p_order_id INT)
        BEGIN
          DECLARE v_sub DECIMAL(14,2);
          DECLARE v_tax_rate DECIMAL(8,4);
          DECLARE v_service_rate DECIMAL(8,4);

          SELECT IFNULL(SUM(line_total),0) INTO v_sub FROM order_items WHERE order_id=p_order_id;
          SELECT CAST(value AS DECIMAL(8,4)) INTO v_tax_rate FROM settings WHERE `key`='tax_rate';
          SELECT CAST(value AS DECIMAL(8,4)) INTO v_service_rate FROM settings WHERE `key`='service_rate';

          UPDATE orders
          SET subtotal=v_sub,
              tax=v_sub*v_tax_rate,
              service=v_sub*v_service_rate,
              total=v_sub + v_sub*v_tax_rate + v_sub*v_service_rate
          WHERE id=p_order_id;
        END
        """,
        
        # Trigger: Recalculate order after insert order item
        """
        CREATE TRIGGER ai_order_items_recalc
        AFTER INSERT ON order_items
        FOR EACH ROW
        BEGIN
          CALL sp_recalc_order_totals(NEW.order_id);
        END
        """,
        
        # Trigger: Recalculate order after update order item
        """
        CREATE TRIGGER au_order_items_recalc
        AFTER UPDATE ON order_items
        FOR EACH ROW
        BEGIN
          CALL sp_recalc_order_totals(NEW.order_id);
        END
        """,
        
        # Trigger: Recalculate order after delete order item
        """
        CREATE TRIGGER ad_order_items_recalc
        AFTER DELETE ON order_items
        FOR EACH ROW
        BEGIN
          CALL sp_recalc_order_totals(OLD.order_id);
        END
        """,
        
        # Trigger: Audit order status changes
        """
        CREATE TRIGGER au_orders_status_audit
        AFTER UPDATE ON orders
        FOR EACH ROW
        BEGIN
          IF NEW.status <> OLD.status THEN
            INSERT INTO order_audit(action, order_id, changed_at, note)
            VALUES ('STATUS_CHANGED', NEW.id, NOW(), NEW.status);
          END IF;
        END
        """,
        
        # Stored Procedure: Revenue by month
        """
        CREATE PROCEDURE sp_revenue_by_month(IN p_year INT, IN p_month INT)
        BEGIN
          SELECT DATE(created_at) AS ngay,
                 COUNT(*) AS so_don,
                 SUM(subtotal) AS subtotal,
                 SUM(tax) AS tax,
                 SUM(service) AS service,
                 SUM(total) AS total
          FROM orders
          WHERE status='PAID'
            AND YEAR(created_at)=p_year AND MONTH(created_at)=p_month
          GROUP BY DATE(created_at)
          ORDER BY DATE(created_at);
        END
        """,
        
        # Stored Procedure: Revenue by date
        """
        CREATE PROCEDURE sp_revenue_by_date(IN p_date DATE)
        BEGIN
          -- Totals row
          SELECT DATE(created_at) AS ngay,
                 COUNT(*) AS so_don,
                 SUM(subtotal) AS subtotal,
                 SUM(tax) AS tax,
                 SUM(service) AS service,
                 SUM(total) AS total
          FROM orders
          WHERE DATE(created_at)=p_date AND status='PAID';

          -- Detail rows
          SELECT id AS order_id, created_at, table_id, subtotal, tax, service, total
          FROM orders
          WHERE DATE(created_at)=p_date AND status='PAID'
          ORDER BY created_at;
        END
        """
    ]
    
    try:
        for obj_sql in objects:
            cursor.execute(obj_sql)
        conn.commit()
        print("✓ Triggers and procedures created successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating triggers/procedures: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def insert_default_data():
    """Insert default settings, categories, tables, and menu items"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Insert default settings
        cursor.execute("""
            INSERT INTO settings(`key`,`value`) VALUES ('tax_rate','0.10')
            ON DUPLICATE KEY UPDATE value=VALUES(value)
        """)
        cursor.execute("""
            INSERT INTO settings(`key`,`value`) VALUES ('service_rate','0.05')
            ON DUPLICATE KEY UPDATE value=VALUES(value)
        """)
        
        # Insert categories
        cursor.execute("""
            INSERT INTO categories(name) VALUES ('Khai vị'),('Món chính'),('Đồ uống'),('Tráng miệng')
            ON DUPLICATE KEY UPDATE name=VALUES(name)
        """)
        
        # Insert dining tables
        for i in range(1, 11):
            cursor.execute("""
                INSERT INTO dining_tables(label, seats) VALUES (%s, 4)
                ON DUPLICATE KEY UPDATE seats=VALUES(seats)
            """, (f"Bàn {i}",))
        
        # Insert menu items
        menu_items = [
            ('Gỏi cuốn tôm', 'Khai vị', 35000),
            ('Chả giò', 'Khai vị', 40000),
            ('Bò lúc lắc', 'Món chính', 120000),
            ('Cơm gà xối mỡ', 'Món chính', 70000),
            ('Phở bò tái', 'Món chính', 65000),
            ('Nước cam', 'Đồ uống', 30000),
            ('Trà chanh', 'Đồ uống', 20000),
            ('Bánh flan', 'Tráng miệng', 25000),
        ]
        
        for item_name, cat_name, price in menu_items:
            cursor.execute("""
                INSERT INTO menu_items(name, category_id, price, is_available)
                SELECT %s, c.id, %s, 1 FROM categories c WHERE c.name=%s
                ON DUPLICATE KEY UPDATE price=VALUES(price)
            """, (item_name, price, cat_name))
        
        print("✓ Default data inserted successfully")
    finally:
        cursor.close()
        conn.close()


def initialize_database():
    """Complete database initialization - creates database, tables, triggers, and default data"""
    try:
        print("=" * 60)
        print("INITIALIZING RESTAURANT DATABASE")
        print("=" * 60)
        
        print("\n1. Creating database...")
        drop_and_create_database()
        
        print("\n2. Creating tables...")
        create_tables()
        
        print("\n3. Creating triggers and procedures...")
        create_triggers_and_procedures()
        
        print("\n4. Inserting default data...")
        insert_default_data()
        
        print("\n" + "=" * 60)
        print("✓ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        return False
