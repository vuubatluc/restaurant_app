# Sơ đồ phụ thuộc các module

```
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
| `database.py` | Truy vấn database, format tiền tệ |
| `utils.py` | Xử lý chuỗi, ngày tháng |
| `dialogs.py` | UI dialogs |
| `managers.py` | CRUD cho menu và categories |
| `invoice_manager.py` | Quản lý hóa đơn |
| `reports.py` | Báo cáo doanh thu |
| `main_app.py` | Logic ứng dụng chính, UI chính |
| `main.py` | Entry point |
