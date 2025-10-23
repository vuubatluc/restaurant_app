# Sơ đồ phụ thuộc các module

```
init_db.py (Database initialization)
  └── database.py (initialize_database, create_tables, create_triggers_and_procedures)

check_db.py (Database verification)
  └── config.py + mysql.connector

main.py
  └── main_app.py (RestaurantApp)
       ├── config.py (DB_CONFIG, APP_TITLE, CURRENCY)
       ├── database.py (query_all, query_one, execute, money, settings)
       ├── utils.py (parse_money_str, parse_date)
       ├── managers.py
       │    ├── MenuManager
       │    │    └── dialogs.py (MenuItemDialog)
       │    └── CategoryManager
       ├── invoice_manager.py (InvoiceManager)
       └── reports.py
            ├── ReportDaily
            └── ReportMonthly
```

## Luồng dữ liệu chính

### 1. Khởi động ứng dụng
```
main.py → kiểm tra DB → RestaurantApp.__init__()
```

### 2. Tải dữ liệu ban đầu
```
RestaurantApp.__init__()
  → refresh_categories() → database.query_all()
  → refresh_tables() → database.query_all()
  → refresh_menu() → database.query_all()
  → load_rates_into_ui() → database.get_setting()
```

### 3. Thêm món vào giỏ
```
User double-click menu item
  → add_selected_item()
  → database.query_one() (lấy thông tin món)
  → simpledialog.askinteger() (nhập số lượng)
  → cart[item_id] = {...}
  → refresh_cart_tree()
  → recalc_totals() → database.set_setting()
```

### 4. Lưu đơn hàng
```
save_draft() / checkout()
  → recalc_totals()
  → _persist_order(status="OPEN"/"PAID")
    → parse_money_str() (từ utils.py)
    → database.execute() / database.exec_many()
    → export_receipt() (nếu PAID)
    → clear_cart()
```

### 5. Quản lý món ăn
```
Menu: Quản lý → Quản lý món (CRUD)
  → managers.MenuManager.open()
    → dialogs.MenuItemDialog (thêm/sửa)
    → database.execute() (CRUD operations)
    → managers.CategoryManager (quản lý danh mục)
```

### 6. Báo cáo
```
Menu: Báo cáo → Doanh thu theo ngày/tháng
  → reports.ReportDaily.open() / ReportMonthly.open()
    → database.get_conn().cursor().callproc()
    → hoặc database.query_all() (fallback)
```

### 7. Quản lý hóa đơn
```
Menu: Hóa đơn → Quản lý hóa đơn
  → invoice_manager.InvoiceManager.open()
    → Xem, lọc, hủy, xuất hóa đơn
    → Mở đơn OPEN → load_order_into_cart()
```

## Phân tách trách nhiệm

| Module | Trách nhiệm |
|--------|------------|
| `config.py` | Cấu hình tĩnh |
| `database.py` | Truy vấn database, format tiền tệ, **khởi tạo database** |
| `utils.py` | Xử lý chuỗi, ngày tháng |
| `dialogs.py` | UI dialogs |
| `managers.py` | CRUD cho menu và categories |
| `invoice_manager.py` | Quản lý hóa đơn |
| `reports.py` | Báo cáo doanh thu |
| `main_app.py` | Logic ứng dụng chính, UI chính |
| `main.py` | Entry point |
| `init_db.py` | **Script khởi tạo database** |
| `check_db.py` | **Script kiểm tra database** |

## Database Initialization Flow

```
init_db.py
  └── database.initialize_database()
       ├── drop_and_create_database()
       │    └── DROP DATABASE + CREATE DATABASE
       │
       ├── create_tables()
       │    ├── CREATE TABLE categories
       │    ├── CREATE TABLE menu_items
       │    ├── CREATE TABLE dining_tables
       │    ├── CREATE TABLE orders
       │    ├── CREATE TABLE order_items
       │    ├── CREATE TABLE settings
       │    └── CREATE TABLE order_audit
       │
       ├── create_triggers_and_procedures()
       │    ├── CREATE TRIGGER (price validation)
       │    ├── CREATE TRIGGER (quantity validation)
       │    ├── CREATE TRIGGER (auto calculate line_total)
       │    ├── CREATE TRIGGER (auto recalculate order totals)
       │    ├── CREATE TRIGGER (audit log)
       │    ├── CREATE PROCEDURE sp_recalc_order_totals
       │    ├── CREATE PROCEDURE sp_revenue_by_month
       │    └── CREATE PROCEDURE sp_revenue_by_date
       │
       └── insert_default_data()
            ├── INSERT settings (tax_rate, service_rate)
            ├── INSERT categories (4 categories)
            ├── INSERT dining_tables (10 tables)
            └── INSERT menu_items (8 items)
```

## Cách sử dụng

### Lần đầu setup
```bash
# 1. Kiểm tra kết nối MySQL
python check_db.py

# 2. Khởi tạo database (sẽ xóa database cũ nếu có)
python init_db.py

# 3. Chạy ứng dụng
python main.py
```

### Kiểm tra database sau khi setup
```bash
python check_db.py
```
