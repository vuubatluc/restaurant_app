"""Main Restaurant Application"""
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, simpledialog, filedialog

from config import APP_TITLE
from database import query_all, query_one, execute, exec_many, get_setting, set_setting, money
from managers import MenuManager
from invoice_manager import InvoiceManager
from reports import ReportDaily, ReportMonthly
from utils import parse_money_str


class RestaurantApp(Tk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(1040, 640)
        self.default_font = ("Segoe UI", 9)
        self.header_font = ("Segoe UI", 10, "bold")
        self.title_font = ("Segoe UI", 12, "bold")

        self.style = ttk.Style(self)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")

        self.option_add("*Font", self.default_font)
        self.option_add("*Menu*Font", self.default_font)
        self.option_add("*Listbox*Font", self.default_font)
        self.option_add("*Text*Font", self.default_font)
        self.option_add("*Entry*Font", self.default_font)

        self.style.configure("Treeview", font=self.default_font)
        self.style.configure("Treeview.Heading", font=self.header_font)

        self.current_table_id = None
        self.cart = {}
        self.categories = []
        self.editing_order_id = None

        self._build_menu_bar()
        self._build_layout()
        self.refresh_categories()
        self.refresh_tables()
        self.refresh_menu()
        self.load_rates_into_ui()

    def _build_menu_bar(self):
        """Build the application menu bar"""
        menubar = Menu(self)
        self.config(menu=menubar)

        m_manage = Menu(menubar, tearoff=False)
        m_manage.add_command(label="Quản lý món (CRUD)", command=self.open_menu_manager)
        m_manage.add_command(label="Thiết lập thuế & service", command=self.open_settings_dialog)
        menubar.add_cascade(label="Quản lý", menu=m_manage)

        m_report = Menu(menubar, tearoff=False)
        m_report.add_command(label="Doanh thu hôm nay", command=lambda: ReportDaily.open(self, default_today=True))
        m_report.add_command(label="Doanh thu theo ngày…", command=lambda: ReportDaily.open(self, default_today=False))
        m_report.add_command(label="Doanh thu theo tháng…", command=lambda: ReportMonthly.open(self))
        menubar.add_cascade(label="Báo cáo", menu=m_report)

        m_orders = Menu(menubar, tearoff=False)
        m_orders.add_command(label="Quản lý hóa đơn…", command=self.open_invoice_manager)
        menubar.add_cascade(label="Hóa đơn", menu=m_orders)

        m_help = Menu(menubar, tearoff=False)
        m_help.add_command(
            label="Giới thiệu",
            command=lambda: messagebox.showinfo(
                APP_TITLE,
                "Ứng dụng quản lý đặt món (MySQL)\n- CRUD + Giỏ hàng + Triggers + Stored Procedures\n- Báo cáo ngày/tháng\n- Quản lý hóa đơn (mở đơn OPEN vào giỏ, xuất hóa đơn chưa thanh toán)",
            ),
        )
        menubar.add_cascade(label="Trợ giúp", menu=m_help)

    def _build_layout(self):
        """Build the main application layout"""
        # Left: Tables + Filters
        left = ttk.Frame(self, padding=8)
        left.pack(side=LEFT, fill=Y)

        ttk.Label(left, text="Chọn bàn", font=self.header_font).pack(anchor="w")
        self.lst_tables = Listbox(left, height=12, exportselection=False)
        self.lst_tables.pack(fill=X, pady=(2, 8))
        self.lst_tables.bind("<<ListboxSelect>>", self.on_select_table)

        # Filter / search
        ttk.Label(left, text="Danh mục").pack(anchor="w")
        self.cmb_category = ttk.Combobox(left, state="readonly")
        self.cmb_category.pack(fill=X, pady=(2, 8))
        self.cmb_category.bind("<<ComboboxSelected>>", lambda e: self.refresh_menu())

        ttk.Label(left, text="Tìm món").pack(anchor="w")
        self.ent_search = ttk.Entry(left)
        self.ent_search.pack(fill=X, pady=(2, 8))
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh_menu())

        ttk.Button(left, text="Xóa lọc", command=self.clear_filters).pack(fill=X)

        # Center: Menu list
        center = ttk.Frame(self, padding=8)
        center.pack(side=LEFT, fill=BOTH, expand=True)

        self.tree_menu = ttk.Treeview(center, columns=("name", "price", "avail", "desc"), show="headings", height=20)
        self.tree_menu.heading("name", text="Tên món")
        self.tree_menu.column("name", width=200, anchor="w")
        self.tree_menu.heading("price", text="Giá")
        self.tree_menu.column("price", width=100, anchor="e")
        self.tree_menu.heading("avail", text="Trạng thái")
        self.tree_menu.column("avail", width=100, anchor="center")
        self.tree_menu.heading("desc", text="Mô tả")
        self.tree_menu.column("desc", width=250, anchor="w")
        self.tree_menu["displaycolumns"] = ("name", "price", "avail")
        self.tree_menu.pack(fill=BOTH, expand=True)
        self.tree_menu.bind("<Double-1>", lambda e: self.add_selected_item())

        # Action buttons
        act = ttk.Frame(center)
        act.pack(fill=X, pady=6)
        ttk.Button(act, text="Thêm vào giỏ", command=self.add_selected_item).pack(side=LEFT, padx=3)
        ttk.Button(act, text="Xem/ẩn mô tả", command=self.toggle_desc_col).pack(side=LEFT, padx=3)

        # Right: Cart + totals
        right = ttk.Frame(self, padding=8)
        right.pack(side=LEFT, fill=Y)

        ttk.Label(right, text="Giỏ hàng (đơn hiện tại)", font=self.header_font).pack(anchor="w")
        self.tree_cart = ttk.Treeview(right, columns=("name", "qty", "price", "total"), show="headings", height=16)
        headers = [("name", "Tên món", "w", 220), ("qty", "SL", "center", 60), ("price", "Đơn giá", "e", 110), ("total", "Thành tiền", "e", 120)]
        for col, txt, anc, w in headers:
            self.tree_cart.heading(col, text=txt)
            self.tree_cart.column(col, width=w, anchor=anc)
        self.tree_cart.pack(fill=BOTH, expand=False)
        self.tree_cart.bind("<Double-1>", self.edit_cart_item_qty)

        cart_btns = ttk.Frame(right)
        cart_btns.pack(fill=X, pady=6)
        ttk.Button(cart_btns, text="Xóa món", command=self.remove_cart_item).pack(side=LEFT, padx=3)
        ttk.Button(cart_btns, text="Xóa giỏ", command=self.clear_cart).pack(side=LEFT, padx=3)

        # Totals
        sums = ttk.LabelFrame(right, text="Tổng kết", padding=8)
        sums.pack(fill=X, pady=(6, 0))

        self.var_subtotal = StringVar(value="0")
        self.var_tax = StringVar(value="0")
        self.var_service = StringVar(value="0")
        self.var_total = StringVar(value="0")

        row = 0
        for label, var in [("Tạm tính:", self.var_subtotal), ("Thuế:", self.var_tax), ("Service:", self.var_service), ("Thanh toán:", self.var_total)]:
            label_font = self.header_font if label == "Thanh toán:" else self.default_font
            ttk.Label(sums, text=label, font=label_font).grid(row=row, column=0, sticky="w")
            ttk.Label(sums, textvariable=var, font=label_font).grid(row=row, column=1, sticky="e")
            row += 1

        # Rates
        rfrm = ttk.Frame(sums)
        rfrm.grid(row=3, column=0, columnspan=2, sticky="we", pady=(6, 0))
        ttk.Label(rfrm, text="Thuế %:").pack(side=LEFT)
        self.ent_tax_rate = ttk.Entry(rfrm, width=6)
        self.ent_tax_rate.pack(side=LEFT, padx=(6, 12))
        ttk.Label(rfrm, text="Service %:").pack(side=LEFT)
        self.ent_service_rate = ttk.Entry(rfrm, width=6)
        self.ent_service_rate.pack(side=LEFT, padx=(6, 0))

        chk = ttk.Frame(right)
        chk.pack(fill=X, pady=8)
        ttk.Button(chk, text="Lưu tạm (OPEN)", command=self.save_draft).pack(side=LEFT, padx=3)

    # ----- Data loading -----
    def refresh_categories(self):
        """Reload categories from database"""
        self.categories = query_all("SELECT id, name FROM categories ORDER BY name")
        names = ["(Tất cả)"] + [c[1] for c in self.categories]
        self.cmb_category["values"] = names
        if not self.cmb_category.get():
            self.cmb_category.current(0)

    def refresh_tables(self):
        """Reload tables from database"""
        self.lst_tables.delete(0, END)
        rows = query_all("SELECT id, label FROM dining_tables ORDER BY id")
        for _id, label in rows:
            self.lst_tables.insert(END, f"{_id}: {label}")

    def refresh_menu(self):
        """Reload menu items based on filters"""
        search = self.ent_search.get().strip().lower()
        cat = self.cmb_category.get()

        q = """SELECT mi.id, mi.name, mi.price, mi.is_available, IFNULL(mi.description,''), c.name
               FROM menu_items mi LEFT JOIN categories c ON c.id = mi.category_id
               WHERE 1=1"""
        params = []
        if cat and cat != "(Tất cả)":
            q += " AND c.name = %s"
            params.append(cat)
        if search:
            q += " AND (LOWER(mi.name) LIKE %s OR LOWER(IFNULL(mi.description,'')) LIKE %s)"
            params += [f"%{search}%", f"%{search}%"]
        q += " ORDER BY mi.name"

        rows = query_all(q, tuple(params))

        self.tree_menu.delete(*self.tree_menu.get_children())
        for _id, name, price, avail, desc, cat_name in rows:
            avail_txt = "Đang bán" if avail else "Hết món"
            self.tree_menu.insert("", END, iid=str(_id), values=(name, money(price), avail_txt, desc))

    def load_rates_into_ui(self):
        """Load tax and service rates from settings"""
        tax = get_setting("tax_rate", 0.10)
        service = get_setting("service_rate", 0.05)
        self.ent_tax_rate.delete(0, END)
        self.ent_tax_rate.insert(0, str(int(float(tax) * 100)))
        self.ent_service_rate.delete(0, END)
        self.ent_service_rate.insert(0, str(int(float(service) * 100)))

    # ----- Filters & selections -----
    def clear_filters(self):
        """Clear search and category filters"""
        if self.categories:
            self.cmb_category.current(0)
        self.ent_search.delete(0, END)
        self.refresh_menu()

    def on_select_table(self, event=None):
        """Handle table selection"""
        sel = self.lst_tables.curselection()
        if not sel:
            self.current_table_id = None
            return
        text = self.lst_tables.get(sel[0])
        try:
            tid = int(text.split(":")[0])
        except:
            tid = None
        self.current_table_id = tid

    # ----- Cart handling -----
    def add_selected_item(self):
        """Add selected menu item to cart"""
        sel = self.tree_menu.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn món", "Hãy chọn một món trong danh sách.")
            return
        item_id = int(sel[0])
        row = query_one("""SELECT id, name, price FROM menu_items WHERE id=%s""", (item_id,))
        if not row:
            return
        _id, name, price = row
        qty = simpledialog.askinteger("Số lượng", f"Nhập số lượng cho '{name}':", minvalue=1, initialvalue=1, parent=self)
        if not qty:
            return
        if _id in self.cart:
            self.cart[_id]["qty"] += qty
        else:
            self.cart[_id] = {"name": name, "qty": qty, "price": float(price)}

        self.refresh_cart_tree()
        self.recalc_totals()

    def edit_cart_item_qty(self, event=None):
        """Edit quantity of item in cart"""
        sel = self.tree_cart.selection()
        if not sel:
            return
        item_id = int(sel[0])
        item = self.cart.get(item_id)
        if not item:
            return
        new_qty = simpledialog.askinteger("Số lượng", f"Sửa số lượng cho '{item['name']}':", minvalue=0, initialvalue=item["qty"], parent=self)
        if new_qty is None:
            return
        if new_qty <= 0:
            del self.cart[item_id]
        else:
            self.cart[item_id]["qty"] = new_qty

        self.refresh_cart_tree()
        self.recalc_totals()

    def remove_cart_item(self):
        """Remove selected item from cart"""
        sel = self.tree_cart.selection()
        if not sel:
            return
        item_id = int(sel[0])
        if item_id in self.cart:
            del self.cart[item_id]
            self.refresh_cart_tree()
            self.recalc_totals()

    def clear_cart(self):
        """Clear entire cart"""
        if not self.cart:
            return
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ giỏ hàng hiện tại?"):
            self.cart.clear()
            self.refresh_cart_tree()
            self.recalc_totals()
            self.editing_order_id = None

    def refresh_cart_tree(self):
        """Refresh cart display"""
        self.tree_cart.delete(*self.tree_cart.get_children())
        for iid, data in self.cart.items():
            qty = data["qty"]
            price = data["price"]
            total = qty * price
            self.tree_cart.insert("", END, iid=str(iid), values=(data["name"], qty, money(price), money(total)))

    def recalc_totals(self):
        """Recalculate and display totals"""
        try:
            tax_pct = float(self.ent_tax_rate.get()) / 100.0
        except:
            tax_pct = 0.10
            self.ent_tax_rate.delete(0, END)
            self.ent_tax_rate.insert(0, str(int(tax_pct * 100)))

        try:
            service_pct = float(self.ent_service_rate.get()) / 100.0
        except:
            service_pct = 0.05
            self.ent_service_rate.delete(0, END)
            self.ent_service_rate.insert(0, str(int(service_pct * 100)))

        set_setting("tax_rate", tax_pct)
        set_setting("service_rate", service_pct)

        subtotal = sum(v["qty"] * v["price"] for v in self.cart.values())
        tax = max(0.0, subtotal * tax_pct)
        service = max(0.0, subtotal * service_pct)
        total = max(0.0, subtotal + tax + service)

        self.var_subtotal.set(money(subtotal))
        self.var_tax.set(money(tax))
        self.var_service.set(money(service))
        self.var_total.set(money(total))

    # ----- Persist order -----
    def _ensure_table_selected(self):
        """Validate table selection"""
        if not self.current_table_id:
            messagebox.showwarning("Chưa chọn bàn", "Vui lòng chọn bàn trước khi lưu.")
            return False
        return True

    def _ensure_cart_not_empty(self):
        """Validate cart is not empty"""
        if not self.cart:
            messagebox.showwarning("Giỏ hàng trống", "Vui lòng thêm món vào giỏ.")
            return False
        return True

    def _persist_order(self, status="PAID", note=None, export_receipt=True):
        """Save or update order in database"""
        if not (self._ensure_table_selected() and self._ensure_cart_not_empty()):
            return

        subtotal = parse_money_str(self.var_subtotal.get())
        tax = parse_money_str(self.var_tax.get())
        service = parse_money_str(self.var_service.get())
        total = parse_money_str(self.var_total.get())
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.editing_order_id:
            order_id = self.editing_order_id
            exec_many([
                ("""UPDATE orders
                    SET table_id=%s, subtotal=%s, tax=%s, service=%s,
                        total=%s, status=%s, note=%s
                    WHERE id=%s""",
                 (self.current_table_id, subtotal, tax, service, total, status, note, order_id)),
                ("DELETE FROM order_items WHERE order_id=%s", (order_id,)),
            ])
            for iid, data in self.cart.items():
                qty = data["qty"]
                price = float(data["price"])
                line_total = qty * price
                execute("""INSERT INTO order_items(order_id, item_id, item_name, quantity, unit_price, line_total)
                           VALUES(%s,%s,%s,%s,%s,%s)""",
                        (order_id, iid, data["name"], qty, price, line_total))
        else:
            order_id = execute("""INSERT INTO orders(table_id, created_at, subtotal, tax, service, total, status, note)
                                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                               (self.current_table_id, created, subtotal, tax, service, total, status, note))
            for iid, data in self.cart.items():
                qty = data["qty"]
                price = float(data["price"])
                line_total = qty * price
                execute("""INSERT INTO order_items(order_id, item_id, item_name, quantity, unit_price, line_total)
                           VALUES(%s,%s,%s,%s,%s,%s)""",
                        (order_id, iid, data["name"], qty, price, line_total))

        if export_receipt:
            self.export_receipt(order_id)

        messagebox.showinfo("Thành công", f"Đã lưu đơn #{order_id} (trạng thái: {status}).")
        self.clear_cart()

    def checkout(self):
        """Checkout and mark order as PAID"""
        self.recalc_totals()
        self._persist_order(status="PAID", note=None, export_receipt=True)

    def save_draft(self):
        """Save order as draft (OPEN status)"""
        self.recalc_totals()
        self._persist_order(status="OPEN", note="Bản lưu tạm (cập nhật).", export_receipt=False)

    def export_receipt(self, order_id):
        """Export receipt to text file"""
        order = query_one("SELECT id, table_id, created_at, subtotal, tax, service, total, status FROM orders WHERE id=%s",
                          (order_id,))
        items = query_all("SELECT item_id, item_name, quantity, unit_price, line_total FROM order_items WHERE order_id=%s",
                          (order_id,))

        trow = query_one("SELECT label FROM dining_tables WHERE id=%s", (order[1],))
        table_label = trow[0] if trow else f"Bàn {order[1]}"
        status = order[7]

        lines = []
        lines.append("===== HÓA ĐƠN THANH TOÁN =====")
        lines.append(f"Mã đơn: {order[0]}   Bàn: {table_label}")
        lines.append(f"Trạng thái: {status}")
        lines.append(f"Thời gian: {order[2]}")
        lines.append("-" * 50)
        lines.append(f"{'Mã':>4} {'Tên món':25} {'SL':>3} {'Đơn giá':>10} {'Thành tiền':>10}")
        lines.append("-" * 50)

        for item_id, name, qty, price, line_total in items:
            display_name = (name[:25]) if len(name) <= 25 else (name[:22] + "...")
            lines.append(f"{item_id:>4} {display_name:25} {qty:>3} {int(price):>10,d} {int(line_total):>10,d}".replace(",", "."))

        lines.append("-" * 50)
        lines.append(f"{'Tạm tính:':40} {int(order[3]):>10,d}".replace(",", "."))
        lines.append(f"{'Thuế:':40} {int(order[4]):>10,d}".replace(",", "."))
        lines.append(f"{'Service:':40} {int(order[5]):>10,d}".replace(",", "."))
        lines.append("=" * 50)
        lines.append(f"{'TỔNG CỘNG:':40} {int(order[6]):>10,d}".replace(",", "."))
        lines.append("=" * 50)
        if status != "PAID":
            lines.append("** HÓA ĐƠN TẠM TÍNH - CHƯA THANH TOÁN **")

        total_items = sum(qty for _, _, qty, _, _ in items)
        lines.append(f"Tổng số món: {len(items)} loại, {total_items} phần")
        lines.append("Xin cảm ơn quý khách!")

        fname = f"receipt_{order_id}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        try:
            save_to = filedialog.asksaveasfilename(
                defaultextension=".txt", initialfile=f"receipt_{order_id}.txt",
                filetypes=[("Text files", "*.txt")], title="Lưu hóa đơn"
            )
            if save_to:
                with open(save_to, "w", encoding="utf-8") as f2:
                    f2.write("\n".join(lines))
        except:
            pass

    # ----- Menu windows -----
    def open_menu_manager(self):
        """Open menu manager window"""
        MenuManager.open(self, on_refresh_menu=self.refresh_menu, on_refresh_categories=self.refresh_categories)

    def open_settings_dialog(self):
        """Open settings dialog"""
        win = Toplevel(self)
        win.title("Thiết lập")
        win.resizable(False, False)
        win.transient(self)
        
        frm = ttk.Frame(win, padding=10)
        frm.grid(row=0, column=0)
        ttk.Label(frm, text="Thuế (%):").grid(row=0, column=0, sticky="e")
        ent_tax = ttk.Entry(frm, width=8)
        ent_tax.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(frm, text="Service (%):").grid(row=1, column=0, sticky="e")
        ent_service = ttk.Entry(frm, width=8)
        ent_service.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ent_tax.insert(0, str(int(float(get_setting("tax_rate", 0.10)) * 100)))
        ent_service.insert(0, str(int(float(get_setting("service_rate", 0.05)) * 100)))

        def save():
            try:
                t = float(ent_tax.get()) / 100.0
                s = float(ent_service.get()) / 100.0
            except:
                messagebox.showerror("Lỗi", "Giá trị không hợp lệ.")
                return
            set_setting("tax_rate", t)
            set_setting("service_rate", s)
            self.load_rates_into_ui()
            self.recalc_totals()
            win.destroy()

        ttk.Button(frm, text="Lưu", command=save).grid(row=2, column=0, columnspan=2, pady=(8, 0))

    def open_invoice_manager(self):
        """Open invoice manager window"""
        InvoiceManager.open(
            self, 
            on_load_order_to_cart=self.load_order_into_cart,
            on_export_receipt=self.export_receipt
        )

    def load_order_into_cart(self, order_id: int):
        """Load an existing OPEN order into cart for editing"""
        ordrow = query_one("""SELECT table_id, status FROM orders WHERE id=%s""", (order_id,))
        if not ordrow:
            messagebox.showerror("Lỗi", f"Không tìm thấy đơn #{order_id}.")
            return
        if ordrow[1] != "OPEN":
            messagebox.showwarning("Không thể mở", "Chỉ hỗ trợ mở đơn ở trạng thái OPEN.")
            return

        table_id, _status = ordrow

        items = query_all("""SELECT item_id, item_name, quantity, unit_price FROM order_items WHERE order_id=%s""",
                          (order_id,))

        self.current_table_id = table_id
        try:
            for idx in range(self.lst_tables.size()):
                text = self.lst_tables.get(idx)
                if int(text.split(":")[0]) == table_id:
                    self.lst_tables.selection_clear(0, END)
                    self.lst_tables.selection_set(idx)
                    self.lst_tables.see(idx)
                    break
        except:
            pass

        self.cart.clear()
        for item_id, item_name, qty, price in items:
            self.cart[int(item_id)] = {"name": item_name, "qty": int(qty), "price": float(price)}

        self.editing_order_id = int(order_id)
        self.refresh_cart_tree()
        self.recalc_totals()
        
        messagebox.showinfo(
            "Đã mở vào giỏ",
            f"Đơn #{order_id} đã được mở vào giỏ hàng. Giỏ hàng hiện có {len(self.cart)} món.\nBạn có thể tiếp tục chỉnh sửa và Lưu tạm hoặc Thanh toán.",
        )

    # ----- Helpers -----
    def toggle_desc_col(self):
        """Toggle description column visibility"""
        shown = self.tree_menu["displaycolumns"]
        if "desc" in shown:
            self.tree_menu["displaycolumns"] = ("name", "price", "avail")
        else:
            self.tree_menu["displaycolumns"] = ("name", "price", "avail", "desc")
