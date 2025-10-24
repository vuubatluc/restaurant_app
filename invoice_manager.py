"""Invoice/Order management module"""
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from database import query_all, query_one, execute, money
from utils import parse_date


class InvoiceManager:
    """Invoice manager window - view, cancel, export, and load orders into cart"""
    
    @staticmethod
    def open(parent, on_load_order_to_cart=None, on_export_receipt=None):
        win = Toplevel(parent)
        win.title("Quản lý hóa đơn")
        win.geometry("1200x580")
        win.transient(parent)

        # Filters
        filters = ttk.LabelFrame(win, text="Bộ lọc", padding=8)
        filters.pack(fill=X, padx=8, pady=8)
        ttk.Label(filters, text="Từ ngày (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        ent_from = ttk.Entry(filters, width=12)
        ent_from.grid(row=0, column=1, padx=6)
        ttk.Label(filters, text="Đến ngày (YYYY-MM-DD):").grid(row=0, column=2, sticky="w")
        ent_to = ttk.Entry(filters, width=12)
        ent_to.grid(row=0, column=3, padx=6)

        ttk.Label(filters, text="Trạng thái:").grid(row=0, column=4, sticky="e")
        cmb_status = ttk.Combobox(filters, state="readonly", values=["(Tất cả)", "OPEN", "PAID", "CANCELLED"], width=12)
        cmb_status.grid(row=0, column=5, padx=6)
        cmb_status.current(0)

        ttk.Label(filters, text="Tìm (mã đơn / bàn / ghi chú):").grid(row=0, column=6, sticky="e")
        ent_search = ttk.Entry(filters, width=22)
        ent_search.grid(row=0, column=7, padx=6)

        btn_filter = ttk.Button(filters, text="🔍 Lọc")
        btn_filter.grid(row=0, column=8, padx=6)

        # Table
        cols = ("id", "created_at", "table", "status", "subtotal", "tax", "service", "total", "note")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)
        headers = ["Mã", "Thời gian", "Bàn", "Trạng thái", "Tạm tính", "Thuế", "Service", "Tổng", "Ghi chú"]
        widths = [70, 150, 120, 100, 100, 90, 90, 110, 200]
        for c, h, w in zip(cols, headers, widths):
            tree.heading(c, text=h)
            tree.column(c, width=w, anchor="e" if c in ("subtotal", "tax", "service", "total") else "w")
        tree.pack(fill=BOTH, expand=True, padx=8, pady=(0, 8))

        def get_selected_order_id():
            sel = tree.selection()
            if not sel:
                return None
            try:
                return int(sel[0])
            except:
                return None

        def load():
            tree.delete(*tree.get_children())
            q = """SELECT o.id, o.created_at, dt.label, o.status, o.subtotal, o.tax, o.service, o.total, IFNULL(o.note,'')
                   FROM orders o LEFT JOIN dining_tables dt ON dt.id=o.table_id
                   WHERE 1=1"""
            params = []
            dfrom = parse_date(ent_from.get())
            dto = parse_date(ent_to.get())
            if dfrom:
                q += " AND DATE(o.created_at) >= %s"
                params.append(dfrom)
            if dto:
                q += " AND DATE(o.created_at) <= %s"
                params.append(dto)
            st = cmb_status.get()
            if st and st != "(Tất cả)":
                q += " AND o.status = %s"
                params.append(st)
            s = ent_search.get().strip().lower()
            if s:
                q += " AND (LOWER(IFNULL(dt.label,'')) LIKE %s OR LOWER(IFNULL(o.note,'')) LIKE %s OR CAST(o.id AS CHAR) LIKE %s)"
                like = f"%{s}%"
                params += [like, like, like]
            q += " ORDER BY o.created_at DESC, o.id DESC"
            for row in query_all(q, tuple(params)):
                oid, ts, table_label, status, sub, tax, srv, ttl, note = row
                tree.insert("", END, iid=str(oid), values=(oid, str(ts), table_label or "", status,
                                                           money(sub), money(tax), money(srv), money(ttl), note))

        def view_detail():
            oid = get_selected_order_id()
            if not oid:
                messagebox.showinfo("Chọn hóa đơn", "Hãy chọn một hóa đơn.")
                return
            detail = Toplevel(win)
            detail.title(f"Chi tiết đơn #{oid}")
            detail.geometry("800x420")
            detail.transient(win)
            cols2 = ("item_id", "item_name", "qty", "unit_price", "line_total")
            t2 = ttk.Treeview(detail, columns=cols2, show="headings", height=16)
            for c, h, w in zip(cols2, ["Mã món", "Tên món", "SL", "Đơn giá", "Thành tiền"], [80, 240, 60, 120, 140]):
                t2.heading(c, text=h)
                t2.column(c, width=w, anchor="e" if c == "item_name" else "center")
            t2.pack(fill=BOTH, expand=True, padx=8, pady=8)
            for item_id, name, qty, unit_price, line_total in query_all(
                "SELECT item_id, item_name, quantity, unit_price, line_total FROM order_items WHERE order_id=%s", (oid,)
            ):
                t2.insert("", END, values=(item_id, name, qty, money(unit_price), money(line_total)))

        def cancel_order():
            oid = get_selected_order_id()
            if not oid:
                messagebox.showinfo("Chọn hóa đơn", "Hãy chọn một hóa đơn.")
                return
            cur_status = query_one("SELECT status FROM orders WHERE id=%s", (oid,))
            if not cur_status:
                return
            if cur_status[0] == "PAID":
                messagebox.showwarning("Không thể hủy", "Đơn đã thanh toán không thể hủy.")
                return
            if messagebox.askyesno("Xác nhận", f"Hủy đơn #{oid}?"):
                execute("UPDATE orders SET status='CANCELLED' WHERE id=%s", (oid,))
                load()

        def export_selected_paid():
            oid = get_selected_order_id()
            if not oid:
                messagebox.showinfo("Chọn hóa đơn", "Hãy chọn một hóa đơn.")
                return
            row = query_one("SELECT status FROM orders WHERE id=%s", (oid,))
            if not row:
                return
            st = row[0]
            if st == "CANCELLED":
                messagebox.showwarning("Không thể xuất", "Đơn đã hủy không thể xuất hóa đơn.")
                return
            if st != "PAID":
                if not messagebox.askyesno("Xác nhận", f"Xuất hóa đơn và đánh dấu ĐÃ THANH TOÁN cho đơn #{oid}?"):
                    return
                execute("UPDATE orders SET status='PAID' WHERE id=%s", (oid,))
            if on_export_receipt:
                on_export_receipt(oid)
            load()

        def open_to_cart():
            oid = get_selected_order_id()
            if not oid:
                messagebox.showinfo("Chọn hóa đơn", "Hãy chọn một hóa đơn.")
                return
            row = query_one("SELECT status FROM orders WHERE id=%s", (oid,))
            if not row:
                return
            if row[0] != "OPEN":
                messagebox.showwarning("Không thể mở", "Chỉ mở được hoá đơn ở trạng thái OPEN.")
                return

            if on_load_order_to_cart:
                on_load_order_to_cart(oid)
            win.destroy()

        actions = ttk.Frame(win)
        actions.pack(fill=X, padx=8, pady=(0, 8))
        ttk.Button(actions, text="Xem chi tiết", command=view_detail).pack(side=LEFT, padx=4)
        ttk.Button(actions, text="Hủy đơn", command=cancel_order).pack(side=LEFT, padx=4)
        ttk.Button(actions, text="Mở đơn vào giỏ (OPEN)", command=open_to_cart).pack(side=LEFT, padx=4)
        ttk.Button(actions, text="Xuất hóa đơn…", command=export_selected_paid).pack(side=RIGHT, padx=4)

        # Bind filter button and Enter key to load function
        btn_filter.config(command=load)
        ent_search.bind("<Return>", lambda e: load())

        today = datetime.now().strftime("%Y-%m-%d")
        ent_from.insert(0, today)
        ent_to.insert(0, today)
        load()
