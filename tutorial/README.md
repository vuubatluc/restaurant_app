# Restaurant Order Manager

Ứng dụng quản lý đặt món nhà hàng với Python + MySQL + Tkinter

## Cấu trúc dự án

```
restaurant_app/
├── main.py                 # Điểm khởi chạy chính
├── config.py              # Cấu hình database và ứng dụng
├── database.py            # Lớp truy cập database
├── utils.py               # Các hàm tiện ích
├── dialogs.py             # Các dialog window
├── managers.py            # Menu và Category manager
├── invoice_manager.py     # Quản lý hóa đơn
├── reports.py             # Báo cáo doanh thu
└── main_app.py            # Ứng dụng chính (RestaurantApp)
```

## Mô tả các file

### `main.py`
- Điểm khởi chạy ứng dụng
- Kiểm tra kết nối database
- Khởi tạo và chạy RestaurantApp

### `config.py`
- Cấu hình kết nối database (host, user, password, database name)
- Các hằng số ứng dụng (APP_TITLE, CURRENCY)

### `database.py`
- `get_conn()` - Lấy kết nối database
- `query_all()` - Thực thi SELECT và trả về tất cả kết quả
- `query_one()` - Thực thi SELECT và trả về 1 kết quả
- `execute()` - Thực thi INSERT/UPDATE/DELETE
- `exec_many()` - Thực thi nhiều câu lệnh
- `get_setting()`, `set_setting()` - Quản lý settings
- `money()` - Format số thành tiền tệ

### `utils.py`
- `parse_money_str()` - Chuyển chuỗi tiền về số
- `parse_date()` - Kiểm tra và parse ngày tháng

### `dialogs.py`
- `MenuItemDialog` - Dialog thêm/sửa món ăn

### `managers.py`
- `MenuManager` - Quản lý CRUD món ăn
- `CategoryManager` - Quản lý danh mục

### `invoice_manager.py`
- `InvoiceManager` - Quản lý hóa đơn
  - Xem danh sách hóa đơn
  - Lọc theo ngày, trạng thái
  - Hủy đơn
  - Xuất hóa đơn
  - Mở đơn OPEN vào giỏ hàng

### `reports.py`
- `ReportDaily` - Báo cáo doanh thu theo ngày
- `ReportMonthly` - Báo cáo doanh thu theo tháng

### `main_app.py`
- `RestaurantApp` - Class ứng dụng chính
  - Giao diện chính với 3 cột: Bàn/Lọc | Menu | Giỏ hàng
  - Quản lý giỏ hàng
  - Tính toán tổng tiền, thuế, service
  - Lưu đơn hàng (PAID/OPEN)
  - Xuất hóa đơn

## Cách chạy

### Bước 1: Cài đặt dependencies

```bash
pip install mysql-connector-python
```

### Bước 2: Cấu hình database

Mở file `config.py` và cập nhật thông tin kết nối MySQL:

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "restaurant_app"
```

### Bước 3: Khởi tạo database

```bash
python init_db.py
```

Script này sẽ:
- Tạo database `restaurant_app`
- Tạo tất cả các bảng
- Tạo triggers và stored procedures
- Insert dữ liệu mẫu (categories, tables, menu items)

### Bước 4: Chạy ứng dụng

```bash
python main.py
```

## Yêu cầu

- Python 3.x
- MySQL Server 5.7+ hoặc 8.0+
- mysql-connector-python
- tkinter (thường có sẵn trong Python)

## Cấu trúc Database

### Bảng chính
- `categories` - Danh mục món ăn
- `menu_items` - Món ăn/đồ uống
- `dining_tables` - Bàn ăn
- `orders` - Đơn hàng
- `order_items` - Chi tiết đơn hàng
- `settings` - Cài đặt hệ thống
- `order_audit` - Lịch sử thay đổi đơn hàng

### Triggers
- Kiểm tra giá món phải >= 0
- Kiểm tra số lượng phải > 0
- Tự động tính line_total
- Tự động tính lại tổng đơn hàng khi có thay đổi
- Ghi log khi trạng thái đơn thay đổi

### Stored Procedures
- `sp_recalc_order_totals` - Tính lại tổng đơn hàng
- `sp_revenue_by_month` - Báo cáo doanh thu theo tháng
- `sp_revenue_by_date` - Báo cáo doanh thu theo ngày

## Lưu ý

- Đảm bảo MySQL Server đang chạy trước khi khởi tạo database
- Chạy `init_db.py` sẽ **xóa database cũ** nếu đã tồn tại
- Nếu chỉ muốn import schema mà không xóa data, có thể dùng file `db.sql` trực tiếp
