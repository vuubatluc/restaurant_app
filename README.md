# 🍽️ Restaurant Order Manager

Ứng dụng quản lý đặt món nhà hàng với Python, MySQL và Tkinter - Hệ thống quản lý hoàn chỉnh với giỏ hàng, báo cáo doanh thu, và quản lý hóa đơn.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Cài đặt nhanh](#-cài-đặt-nhanh)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Cơ sở dữ liệu](#-cơ-sở-dữ-liệu)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
- [Troubleshooting](#-troubleshooting)
- [Đóng góp](#-đóng-góp)

---

## ✨ Tính năng

### 🎯 Tính năng chính

- **Quản lý Menu**
  - ✅ CRUD món ăn/đồ uống
  - ✅ Phân loại theo danh mục
  - ✅ Quản lý giá và tình trạng còn/hết món
  - ✅ Tìm kiếm và lọc món

- **Quản lý Đặt món**
  - ✅ Chọn bàn và thêm món vào giỏ hàng
  - ✅ Tính toán tự động: thuế và phí phục vụ
  - ✅ Lưu đơn tạm (OPEN) và thanh toán (PAID)
  - ✅ Xuất hóa đơn ra file text

- **Quản lý Hóa đơn**
  - ✅ Xem danh sách tất cả hóa đơn
  - ✅ Lọc theo ngày, trạng thái
  - ✅ Hủy đơn chưa thanh toán
  - ✅ Mở đơn OPEN để chỉnh sửa
  - ✅ Xuất hóa đơn chi tiết

- **Báo cáo Doanh thu**
  - ✅ Báo cáo theo ngày
  - ✅ Báo cáo theo tháng
  - ✅ Thống kê chi tiết từng đơn hàng
  - ✅ Tổng hợp thuế và phí phục vụ

### 🔐 Tính năng kỹ thuật

- **Database Features**
  - ✅ 10 Triggers tự động validate và tính toán
  - ✅ 3 Stored Procedures cho báo cáo
  - ✅ Foreign Keys đảm bảo tính toàn vẹn
  - ✅ Audit log tự động

- **Auto-initialization**
  - ✅ Tự động kiểm tra và tạo database
  - ✅ Tự động tạo tables, triggers, procedures
  - ✅ Tự động import dữ liệu mẫu

---

## 🚀 Cài đặt nhanh

### Yêu cầu hệ thống

- Python 3.7 trở lên
- MySQL Server 5.7+ hoặc 8.0+
- Tkinter (thường có sẵn với Python)

### Bước 1: Cài đặt dependencies

```bash
pip install mysql-connector-python
```

Hoặc dùng requirements.txt:

```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình database

Mở file `config.py` và chỉnh sửa thông tin kết nối MySQL:

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "YOUR_PASSWORD_HERE"  # ← Thay đổi mật khẩu của bạn
DB_NAME = "restaurant_app"
```

### Bước 3: Chạy ứng dụng

```bash
python main.py
```

**Chỉ cần vậy thôi!** 🎉

Ứng dụng sẽ tự động:
- Kiểm tra database có tồn tại không
- Tạo database nếu chưa có
- Tạo tất cả tables, triggers, và procedures
- Import dữ liệu mẫu (4 categories, 10 bàn, 8 món ăn)

### Kết quả mong đợi

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

Sau đó cửa sổ ứng dụng sẽ tự động mở.

---

## 📁 Cấu trúc dự án

```
restaurant_app/
│
├── 📄 main.py                  # Entry point - Khởi chạy ứng dụng
├── 📄 config.py                # Cấu hình database và app
├── 📄 database.py              # Database layer (queries, init, utilities)
├── 📄 main_app.py              # RestaurantApp - Giao diện chính
│
├── 📄 dialogs.py               # Dialog windows (MenuItemDialog)
├── 📄 managers.py              # Menu & Category managers
├── 📄 invoice_manager.py       # Invoice management
├── 📄 reports.py               # Revenue reports
├── 📄 utils.py                 # Utility functions
│
├── 📄 init_db.py               # Manual database initialization
├── 📄 requirements.txt         # Python dependencies
└── 📄 README.md                # Tài liệu này
```

### Mô tả các module chính

| File | Mô tả | Trách nhiệm chính |
|------|-------|-------------------|
| `main.py` | Entry point | Khởi động app, auto-init database |
| `config.py` | Configuration | DB credentials, app settings |
| `database.py` | Database layer | Queries, connections, init functions |
| `main_app.py` | Main application | UI chính, business logic |
| `managers.py` | CRUD managers | Menu items, categories management |
| `invoice_manager.py` | Invoice manager | Order management, export receipts |
| `reports.py` | Reports | Daily/monthly revenue reports |
| `dialogs.py` | UI dialogs | Input forms, popups |
| `utils.py` | Utilities | Helper functions (date, money parsing) |

---

## 🏗️ Kiến trúc hệ thống

### Sơ đồ phụ thuộc

```
main.py (Auto-init + Run)
    ↓
    ├─→ database.initialize_database() [nếu DB chưa có]
    │       ├─→ create_tables()
    │       ├─→ create_triggers_and_procedures()
    │       └─→ insert_default_data()
    │
    └─→ main_app.RestaurantApp()
            ├─→ managers.MenuManager
            │       └─→ dialogs.MenuItemDialog
            ├─→ managers.CategoryManager
            ├─→ invoice_manager.InvoiceManager
            ├─→ reports.ReportDaily
            ├─→ reports.ReportMonthly
            └─→ database (queries)
```

### Luồng xử lý chính

#### 1. Khởi động ứng dụng
```
main.py
  → Kiểm tra DB tồn tại?
     ├─ Yes → Mở RestaurantApp
     └─ No  → Initialize DB → Mở RestaurantApp
```

#### 2. Thêm món vào giỏ
```
User double-click món
  → query_one() lấy thông tin món
  → Nhập số lượng
  → Thêm vào cart{}
  → refresh_cart_tree()
  → recalc_totals() (tính thuế, service)
```

#### 3. Lưu đơn hàng
```
Click "Lưu tạm" hoặc "Thanh toán"
  → Validate bàn + giỏ hàng
  → INSERT INTO orders
  → INSERT INTO order_items (nhiều dòng)
  → Triggers tự động tính totals
  → Export receipt (nếu PAID)
  → Clear cart
```

#### 4. Quản lý món ăn
```
Menu → Quản lý món (CRUD)
  → MenuManager.open()
     ├─ Thêm món → MenuItemDialog → INSERT
     ├─ Sửa món → MenuItemDialog → UPDATE
     └─ Xóa món → Confirm → DELETE
```

#### 5. Báo cáo doanh thu
```
Menu → Báo cáo
  → ReportDaily/ReportMonthly.open()
     ├─ Try: callproc('sp_revenue_by_date/month')
     └─ Fallback: query_all() với GROUP BY
```

---

## 💾 Cơ sở dữ liệu

### Schema Overview

#### Tables (7 bảng)

| Bảng | Mô tả | Quan hệ |
|------|-------|---------|
| `categories` | Danh mục món ăn | 1-N với menu_items |
| `menu_items` | Món ăn/đồ uống | N-1 với categories |
| `dining_tables` | Bàn ăn | 1-N với orders |
| `orders` | Đơn hàng | N-1 với dining_tables<br>1-N với order_items |
| `order_items` | Chi tiết đơn hàng | N-1 với orders<br>N-1 với menu_items |
| `settings` | Cài đặt hệ thống | Key-value pairs |
| `order_audit` | Audit log | History của orders |

#### Triggers (10 triggers)

**Validation Triggers:**
- `bi_menu_items_price` - Kiểm tra giá >= 0 (INSERT)
- `bu_menu_items_price` - Kiểm tra giá >= 0 (UPDATE)
- `bi_order_items_guard` - Kiểm tra số lượng > 0, giá >= 0 (INSERT)
- `bu_order_items_guard` - Kiểm tra số lượng > 0, giá >= 0 (UPDATE)

**Auto-calculation Triggers:**
- `bi_order_items_calc_line_total` - Tự động tính line_total = qty × price (INSERT)
- `bu_order_items_calc_line_total` - Tự động tính line_total = qty × price (UPDATE)

**Recalculation Triggers:**
- `ai_order_items_recalc` - Tính lại tổng đơn sau INSERT order_items
- `au_order_items_recalc` - Tính lại tổng đơn sau UPDATE order_items
- `ad_order_items_recalc` - Tính lại tổng đơn sau DELETE order_items

**Audit Trigger:**
- `au_orders_status_audit` - Log thay đổi status vào order_audit

#### Stored Procedures (3 procedures)

**1. sp_recalc_order_totals(order_id)**
- Tính lại subtotal, tax, service, total cho một đơn hàng
- Được gọi tự động bởi triggers

**2. sp_revenue_by_month(year, month)**
- Báo cáo doanh thu theo từng ngày trong tháng
- Trả về: ngày, số đơn, subtotal, tax, service, total

**3. sp_revenue_by_date(date)**
- Báo cáo doanh thu chi tiết trong một ngày
- Result set 1: Tổng kết
- Result set 2: Chi tiết từng đơn

### Dữ liệu mẫu

Sau khi khởi tạo, database có sẵn:

**Categories (4):**
- Khai vị
- Món chính
- Đồ uống
- Tráng miệng

**Dining Tables (10):**
- Bàn 1 đến Bàn 10 (mỗi bàn 4 chỗ)

**Menu Items (8):**
- Gỏi cuốn tôm (35,000 VND)
- Chả giò (40,000 VND)
- Bò lúc lắc (120,000 VND)
- Cơm gà xối mỡ (70,000 VND)
- Phở bò tái (65,000 VND)
- Nước cam (30,000 VND)
- Trà chanh (20,000 VND)
- Bánh flan (25,000 VND)

**Settings:**
- tax_rate: 10%
- service_rate: 5%

---

## 📖 Hướng dẫn sử dụng

### Màn hình chính

Giao diện chia làm 3 cột:

```
┌─────────────┬───────────────────┬──────────────┐
│   Bàn ăn    │    Danh sách món  │  Giỏ hàng    │
│   + Lọc     │                   │  + Tổng tiền │
└─────────────┴───────────────────┴──────────────┘
```

#### Cột trái: Bàn và Bộ lọc
- Danh sách 10 bàn ăn
- Lọc theo danh mục
- Tìm kiếm món theo tên

#### Cột giữa: Danh sách món
- Hiển thị tất cả món ăn
- Double-click để thêm vào giỏ
- Nút "Thêm vào giỏ"
- Toggle hiển thị mô tả món

#### Cột phải: Giỏ hàng
- Danh sách món đã chọn
- Số lượng, đơn giá, thành tiền
- Tạm tính, thuế, service
- **Tổng thanh toán**
- Nút "Lưu tạm (OPEN)"

### Quy trình đặt món

1. **Chọn bàn** (cột trái)
2. **Chọn món** (double-click hoặc nút "Thêm vào giỏ")
3. **Nhập số lượng** trong popup
4. **Kiểm tra giỏ hàng** (cột phải)
   - Double-click để sửa số lượng
   - Nút "Xóa món" để xóa từng món
5. **Lưu đơn:**
   - "Lưu tạm (OPEN)" - Đơn chưa thanh toán
   - Menu → Quản lý → Thanh toán → Xuất hóa đơn

### Menu chức năng

#### Menu "Quản lý"
- **Quản lý món (CRUD)**
  - Thêm/Sửa/Xóa món ăn
  - Quản lý danh mục
- **Thiết lập thuế & service**
  - Điều chỉnh % thuế
  - Điều chỉnh % phí phục vụ

#### Menu "Báo cáo"
- **Doanh thu hôm nay**
  - Tổng quan ngày hiện tại
  - Chi tiết từng đơn hàng
- **Doanh thu theo ngày**
  - Chọn ngày bất kỳ
  - Thống kê chi tiết
- **Doanh thu theo tháng**
  - Chọn tháng/năm
  - Báo cáo theo từng ngày

#### Menu "Hóa đơn"
- **Quản lý hóa đơn**
  - Xem tất cả hóa đơn
  - Lọc theo ngày, trạng thái
  - Xem chi tiết đơn hàng
  - Hủy đơn (OPEN only)
  - Mở đơn OPEN vào giỏ để chỉnh sửa
  - Xuất hóa đơn

### Các trạng thái đơn hàng

| Status | Mô tả | Hành động được phép |
|--------|-------|---------------------|
| **OPEN** | Đơn tạm, chưa thanh toán | Mở vào giỏ, Chỉnh sửa, Hủy, Thanh toán |
| **PAID** | Đã thanh toán | Xem, Xuất hóa đơn |
| **CANCELLED** | Đã hủy | Chỉ xem |

---

## 🔧 Troubleshooting

### Lỗi: "Access denied for user"

**Nguyên nhân:** Sai username hoặc password MySQL

**Giải pháp:**
```python
# Kiểm tra lại trong config.py
DB_USER = "root"           # Username đúng?
DB_PASSWORD = "your_pass"  # Password đúng?
```

### Lỗi: "Can't connect to MySQL server"

**Nguyên nhân:** MySQL Server chưa chạy

**Giải pháp:**

**Windows:**
```powershell
# Mở Services → Tìm MySQL → Start
# Hoặc dùng lệnh:
net start MySQL80
```

**Linux/Mac:**
```bash
sudo service mysql start
# hoặc
sudo systemctl start mysql
```

### Lỗi: "Unknown database"

**Nguyên nhân:** Database chưa được tạo

**Giải pháp:**
```bash
# App sẽ tự động tạo database
# Hoặc tạo thủ công:
python init_db.py
```

### Lỗi: "ModuleNotFoundError: No module named 'mysql'"

**Nguyên nhân:** Chưa cài mysql-connector-python

**Giải pháp:**
```bash
pip install mysql-connector-python
```

### Lỗi khi xuất hóa đơn

**Nguyên nhân:** Không có quyền ghi file

**Giải pháp:**
- Kiểm tra quyền ghi trong thư mục
- Chọn vị trí khác khi lưu file

### Database bị lỗi/corrupted

**Giải pháp:**
```bash
# Reset lại database từ đầu
python init_db.py
```

⚠️ **Lưu ý:** Lệnh này sẽ **XÓA TẤT CẢ DỮ LIỆU** hiện có!

### Ứng dụng chạy chậm

**Giải pháp:**
- Kiểm tra số lượng records trong database
- Restart MySQL Server
- Tối ưu queries nếu cần

---

## 🛠️ Development

### Reset Database

Để reset database về trạng thái ban đầu với dữ liệu mẫu:

```bash
python init_db.py
```

### Backup Database

```bash
# Backup
mysqldump -u root -p restaurant_app > backup.sql

# Restore
mysql -u root -p restaurant_app < backup.sql
```

### Thêm món ăn mới

Cách 1: Qua giao diện
```
Menu → Quản lý → Quản lý món (CRUD) → Thêm món
```

Cách 2: Qua SQL
```sql
INSERT INTO menu_items (name, category_id, price, is_available, description)
VALUES ('Tên món', 1, 50000, 1, 'Mô tả món');
```

### Thêm bàn mới

```sql
INSERT INTO dining_tables (label, seats) VALUES ('Bàn 11', 6);
```

### Chỉnh sửa thuế và service

Cách 1: Qua giao diện
```
Menu → Quản lý → Thiết lập thuế & service
```

Cách 2: Qua SQL
```sql
UPDATE settings SET value='0.08' WHERE `key`='tax_rate';      -- 8%
UPDATE settings SET value='0.10' WHERE `key`='service_rate';  -- 10%
```

---

## 📊 Các tính năng kỹ thuật nổi bật

### 1. Auto-initialization
- Tự động phát hiện database chưa tồn tại
- Tự động tạo schema, triggers, procedures
- Tự động import dữ liệu mẫu
- Không cần chạy SQL file thủ công

### 2. Database Triggers
- **Validation triggers:** Đảm bảo data integrity
- **Calculation triggers:** Tự động tính toán line_total
- **Recalculation triggers:** Tự động cập nhật order totals
- **Audit triggers:** Tự động log thay đổi

### 3. Stored Procedures
- Tối ưu performance cho báo cáo
- Tính toán phức tạp trên server-side
- Fallback mechanism nếu procedure không tồn tại

### 4. Foreign Keys & Constraints
- Đảm bảo referential integrity
- Cascade delete cho order_items
- Prevent orphaned records

### 5. Clean Architecture
- Separation of concerns
- Modular design
- Easy to maintain and extend

---

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Để đóng góp:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Ý tưởng cải tiến

- [ ] Thêm authentication/authorization
- [ ] Export báo cáo ra Excel/PDF
- [ ] Dashboard với charts
- [ ] Mobile responsive UI
- [ ] REST API
- [ ] Multi-language support
- [ ] Cloud deployment

---

## 📄 License

Dự án này được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

---

## 👨‍💻 Tác giả

**Restaurant App Team**

- GitHub: [@vuubatluc](https://github.com/vuubatluc)

---

## 🙏 Acknowledgments

- Python Tkinter Documentation
- MySQL Documentation
- Stack Overflow Community

---

## 📞 Liên hệ & Hỗ trợ

- **Issues:** [GitHub Issues](https://github.com/vuubatluc/restaurant_app/issues)
- **Email:** support@example.com

---

<div align="center">

**Made with ❤️ using Python + MySQL + Tkinter**

⭐ Star this repo if you find it helpful!

</div>
