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

```bash
python main.py
```

## Yêu cầu

- Python 3.x
- MySQL Server
- mysql-connector-python
- tkinter (thường có sẵn trong Python)

## Cài đặt dependencies

```bash
pip install mysql-connector-python
```

## Lưu ý

- Đảm bảo database đã được import schema trước khi chạy
- Cấu hình thông tin database trong `config.py`
