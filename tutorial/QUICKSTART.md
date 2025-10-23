# 🚀 Quick Start Guide

## Bước 1: Cài đặt

```bash
# Clone repository (nếu chưa có)
git clone <your-repo-url>
cd restaurant_app

# Cài đặt dependencies
pip install mysql-connector-python
```

## Bước 2: Cấu hình Database

Mở `config.py` và chỉnh sửa thông tin kết nối:

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "YOUR_PASSWORD_HERE"  # ← Thay đổi đây
DB_NAME = "restaurant_app"
```

## Bước 3: Chạy ứng dụng

```bash
python main.py
```

**Ứng dụng sẽ tự động khởi tạo database!**

Kết quả mong đợi:
```
⚠️  Database 'restaurant_app' does not exist. Creating...
============================================================
INITIALIZING RESTAURANT DATABASE
============================================================

1. Creating database...
✓ Database created successfully

2. Creating tables...
✓ Tables created successfully

3. Creating triggers and procedures...
✓ Triggers and procedures created successfully

4. Inserting default data...
✓ Default data inserted successfully

============================================================
✓ DATABASE INITIALIZATION COMPLETE!
============================================================
```

Sau đó ứng dụng sẽ tự động mở.

**Khởi tạo thủ công (nếu cần):**

```bash
python init_db.py
```

## ⚠️ Lưu ý quan trọng

- **`init_db.py` sẽ XÓA database cũ** nếu đã tồn tại
- Đảm bảo MySQL Server đang chạy
- Nếu gặp lỗi kết nối, kiểm tra username/password trong `config.py`

## 🎯 Dữ liệu mẫu sau khi init

- **4 categories**: Khai vị, Món chính, Đồ uống, Tráng miệng
- **10 bàn ăn**: Bàn 1 đến Bàn 10
- **8 món ăn**: Gỏi cuốn, Chả giò, Bò lúc lắc, v.v.
- **Settings**: tax_rate=10%, service_rate=5%

## 🔧 Troubleshooting

### Lỗi: `Access denied for user`
```bash
# Kiểm tra lại username/password trong config.py
```

### Lỗi: `Can't connect to MySQL server`
```bash
# Đảm bảo MySQL đang chạy
# Windows: Kiểm tra Services → MySQL
# Linux/Mac: sudo service mysql status
```

### Lỗi: `Unknown database`
```bash
# Không cần lo! main.py sẽ tự động tạo database
# Hoặc chạy thủ công:
python init_db.py
```

## 📚 Tài liệu khác

- `README.md` - Tổng quan dự án
- `ARCHITECTURE.md` - Kiến trúc và luồng dữ liệu
- `db.sql` - Raw SQL schema (tham khảo)
