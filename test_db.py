"""
Simple test script for database functions
Run this after init_db.py to verify everything works
"""

from database import query_all, query_one, execute, get_setting, set_setting, money


def test_database_functions():
    """Test basic database operations"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE FUNCTIONS")
    print("=" * 60)
    
    try:
        # Test 1: Query all categories
        print("\n1. Testing query_all() - Get all categories:")
        categories = query_all("SELECT id, name FROM categories ORDER BY name")
        for cat_id, cat_name in categories:
            print(f"   - {cat_name} (ID: {cat_id})")
        
        # Test 2: Query one
        print("\n2. Testing query_one() - Get first menu item:")
        item = query_one("SELECT id, name, price FROM menu_items LIMIT 1")
        if item:
            print(f"   - {item[1]} - {money(item[2])}")
        
        # Test 3: Get settings
        print("\n3. Testing get_setting():")
        tax = get_setting("tax_rate", 0.10)
        service = get_setting("service_rate", 0.05)
        print(f"   - Tax rate: {float(tax)*100}%")
        print(f"   - Service rate: {float(service)*100}%")
        
        # Test 4: Count records
        print("\n4. Testing data counts:")
        categories_count = query_one("SELECT COUNT(*) FROM categories")[0]
        tables_count = query_one("SELECT COUNT(*) FROM dining_tables")[0]
        menu_count = query_one("SELECT COUNT(*) FROM menu_items")[0]
        print(f"   - Categories: {categories_count}")
        print(f"   - Dining tables: {tables_count}")
        print(f"   - Menu items: {menu_count}")
        
        # Test 5: Money formatting
        print("\n5. Testing money() function:")
        amounts = [0, 1000, 15000, 250000, 1500000]
        for amount in amounts:
            print(f"   - {amount:>10} → {money(amount)}")
        
        # Test 6: Menu items with categories
        print("\n6. Testing JOIN query - Menu with categories:")
        items = query_all("""
            SELECT mi.name, c.name, mi.price, mi.is_available
            FROM menu_items mi
            LEFT JOIN categories c ON c.id = mi.category_id
            ORDER BY c.name, mi.name
        """)
        current_cat = None
        for item_name, cat_name, price, is_available in items:
            if cat_name != current_cat:
                current_cat = cat_name
                print(f"\n   [{cat_name}]")
            status = "✓" if is_available else "✗"
            print(f"   {status} {item_name:20} - {money(price)}")
        
        # Test 7: Dining tables
        print("\n7. Testing tables query:")
        tables = query_all("SELECT label, seats FROM dining_tables ORDER BY id")
        for label, seats in tables[:5]:  # Show first 5
            print(f"   - {label} ({seats} chỗ)")
        print(f"   ... and {len(tables)-5} more tables")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n💡 Database is working correctly. You can run: python main.py")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\n💡 Make sure you ran: python init_db.py")
        return False


if __name__ == "__main__":
    test_database_functions()
