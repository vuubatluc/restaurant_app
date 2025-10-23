"""Main entry point for Restaurant Order Manager"""
from tkinter import messagebox
from database import get_conn
from config import DB_NAME
from main_app import RestaurantApp


def main():
    """Main application entry point"""
    try:
        # Test database connection
        c = get_conn()
        c.close()
    except Exception as e:
        messagebox.showerror("Lỗi MySQL", f"Không thể kết nối DB '{DB_NAME}'.\n{e}\nHãy import schema & patch trước.")
        return

    app = RestaurantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
