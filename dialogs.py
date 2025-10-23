"""Dialog windows for the application"""
from tkinter import *
from tkinter import ttk, messagebox


class MenuItemDialog(Toplevel):
    """Dialog for adding/editing menu items"""
    
    def __init__(self, master, categories, item=None):
        super().__init__(master)
        self.title("Món ăn / đồ uống")
        self.item = item

        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Tên món:").grid(row=0, column=0, sticky="w")
        self.ent_name = ttk.Entry(frm, width=40)
        self.ent_name.grid(row=0, column=1, sticky="we", pady=3)

        ttk.Label(frm, text="Danh mục:").grid(row=1, column=0, sticky="w")
        self.cmb_cat = ttk.Combobox(frm, state="readonly", values=[c[1] for c in categories], width=37)
        self.cmb_cat.grid(row=1, column=1, sticky="we", pady=3)

        ttk.Label(frm, text="Giá (VND):").grid(row=2, column=0, sticky="w")
        self.ent_price = ttk.Entry(frm, width=20)
        self.ent_price.grid(row=2, column=1, sticky="w", pady=3)

        self.var_avail = BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Đang bán", variable=self.var_avail).grid(row=3, column=1, sticky="w", pady=3)

        ttk.Label(frm, text="Mô tả:").grid(row=4, column=0, sticky="nw")
        self.txt_desc = Text(frm, width=40, height=3)
        self.txt_desc.grid(row=4, column=1, sticky="we", pady=3)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(btns, text="Lưu", command=self.on_save).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Hủy", command=self.destroy).grid(row=0, column=1, padx=5)

        if item:
            self.ent_name.insert(0, item["name"])
            try:
                idx = [c[0] for c in categories].index(item["category_id"])
                self.cmb_cat.current(idx)
            except:
                if categories:
                    self.cmb_cat.current(0)
            self.ent_price.insert(0, str(item["price"]))
            self.var_avail.set(bool(item["is_available"]))
            if item.get("description"):
                self.txt_desc.insert("1.0", item["description"])
        else:
            if categories:
                self.cmb_cat.current(0)

    def on_save(self):
        """Validate and save the menu item"""
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên món.")
            return
        cat_name = self.cmb_cat.get()
        if not cat_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn danh mục.")
            return
        try:
            price = float(self.ent_price.get())
        except:
            messagebox.showwarning("Sai định dạng", "Giá phải là số.")
            return

        self.result = {
            "name": name,
            "category_name": cat_name,
            "price": price,
            "is_available": 1 if self.var_avail.get() else 0,
            "description": self.txt_desc.get("1.0", "end").strip(),
        }
        self.destroy()
