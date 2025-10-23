"""Main entry point for Restaurant Order Manager"""
import mysql.connector
from tkinter import messagebox
from database import get_conn, get_server_conn, initialize_database
from config import DB_NAME


def check_and_init_database():
    """Check if database exists, if not initialize it"""
    try:
        # Try to connect to the database
        conn = get_conn()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # If no tables, initialize database
        if len(tables) == 0:
            print("\n⚠️  Database is empty. Initializing...")
            initialize_database()
            return True
        
        return True
        
    except mysql.connector.Error as e:
        # Database doesn't exist or other error
        if e.errno == 1049:  # Unknown database
            print(f"\n⚠️  Database '{DB_NAME}' does not exist. Creating...")
            try:
                initialize_database()
                return True
            except Exception as init_error:
                messagebox.showerror(
                    "Lỗi khởi tạo database",
                    f"Không thể tạo database:\n{init_error}\n\nVui lòng kiểm tra:\n- MySQL Server đang chạy\n- Username/Password trong config.py\n- Quyền tạo database"
                )
                return False
        else:
            messagebox.showerror(
                "Lỗi MySQL", 
                f"Không thể kết nối MySQL Server:\n{e}\n\nVui lòng kiểm tra:\n- MySQL Server đang chạy\n- Thông tin trong config.py"
            )
            return False


def main():
    """Main application entry point"""
    # Check and initialize database if needed
    if not check_and_init_database():
        return
    
    # Import and run application
    from main_app import RestaurantApp
    app = RestaurantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
