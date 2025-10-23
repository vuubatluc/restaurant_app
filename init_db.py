"""
Database initialization script
Run this script to create the database schema, tables, triggers, procedures, and default data.
"""

from database import initialize_database


if __name__ == "__main__":
    print("\n🚀 Starting database initialization...\n")
    
    success = initialize_database()
    
    if success:
        print("\n✅ You can now run the application with: python main.py")
    else:
        print("\n❌ Initialization failed. Please check the error messages above.")
