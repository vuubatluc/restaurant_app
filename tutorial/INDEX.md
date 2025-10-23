# 📖 Documentation Index

Chào mừng đến với Restaurant Order Manager! Dưới đây là danh sách tài liệu hướng dẫn.

## 🚀 Bắt đầu nhanh

1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ BẮT ĐẦU TỪ ĐÂY!
   - Hướng dẫn setup từng bước
   - Cấu hình database
   - Khởi tạo và chạy ứng dụng
   - Troubleshooting

## 📚 Tài liệu chính

2. **[README.md](README.md)** 📋 Tổng quan dự án
   - Cấu trúc dự án
   - Mô tả các file/module
   - Yêu cầu hệ thống
   - Cài đặt dependencies

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ Kiến trúc hệ thống
   - Sơ đồ phụ thuộc modules
   - Luồng dữ liệu
   - Database initialization flow
   - Phân tách trách nhiệm

4. **[MIGRATION.md](MIGRATION.md)** 🔄 Database Migration
   - Chi tiết chuyển đổi SQL → Python
   - Các hàm mới trong database.py
   - Ưu điểm của phương pháp mới
   - Migration guide

## 🛠️ Scripts & Tools

### Application

5. **`main.py`** - Chạy ứng dụng ⭐
   ```bash
   python main.py
   ```
   - **Tự động kiểm tra và khởi tạo database**
   - Tạo database nếu chưa tồn tại
   - Chạy ứng dụng

### Database Management (Optional)

6. **`init_db.py`** - Khởi tạo database thủ công
   ```bash
   python init_db.py
   ```
   - Tạo database mới
   - Tạo tables, triggers, procedures
   - Insert dữ liệu mẫu
   - ⚠️ Xóa database cũ nếu có

## 📁 Cấu trúc Project

```
restaurant_app/
├── 📚 Documentation
│   ├── README.md           # Tổng quan
│   ├── QUICKSTART.md       # Hướng dẫn nhanh ⭐
│   ├── ARCHITECTURE.md     # Kiến trúc
│   ├── MIGRATION.md        # Database migration
│   └── INDEX.md           # File này
│
├── 🔧 Scripts
│   ├── init_db.py         # Khởi tạo database
│   ├── check_db.py        # Kiểm tra database
│   └── test_db.py         # Test database
│
├── 🎯 Application
│   ├── main.py            # Entry point
│   ├── main_app.py        # Main application
│   ├── config.py          # Configuration
│   ├── database.py        # Database layer
│   ├── utils.py           # Utilities
│   ├── dialogs.py         # Dialog windows
│   ├── managers.py        # Menu/Category managers
│   ├── invoice_manager.py # Invoice manager
│   └── reports.py         # Reports
│
└── 📄 Other
    └── .gitignore         # Git ignore rules
```

## 🎯 Quick Reference

### First Time Setup
```bash
# 1. Install dependencies
pip install mysql-connector-python

# 2. Edit config.py (set your MySQL password)

# 3. Run application (auto-init database)
python main.py
```

### Daily Development
```bash
# Just run the application
python main.py
```

### Reset Database (if needed)
```bash
# This will DELETE all data!
python init_db.py
```

## 🆘 Cần giúp đỡ?

### Lỗi kết nối MySQL
→ Xem **QUICKSTART.md** phần Troubleshooting

### Không biết bắt đầu từ đâu
→ Đọc **QUICKSTART.md** từ đầu đến cuối

### Muốn hiểu kiến trúc
→ Xem **ARCHITECTURE.md**

### Muốn biết code hoạt động thế nào
→ Xem **README.md** phần "Mô tả các file"

### Muốn biết cách migrate database
→ Xem **MIGRATION.md**

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra **QUICKSTART.md** → Troubleshooting
2. Chạy `python check_db.py` để kiểm tra database
3. Chạy `python test_db.py` để test functions
4. Xem error message và Google search

## 🎓 Learning Path

### Người mới bắt đầu
1. QUICKSTART.md → Setup
2. main.py → Chạy app và thử nghiệm
3. README.md → Hiểu cấu trúc

### Developer
1. README.md → Tổng quan
2. ARCHITECTURE.md → Kiến trúc
3. Đọc code trong các file .py

### DevOps/DBA
1. MIGRATION.md → Hiểu database setup
2. init_db.py → Xem cách tạo database
3. db.sql → Reference schema

---

**Happy Coding! 🎉**
