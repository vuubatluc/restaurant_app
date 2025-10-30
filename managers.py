"""Menu and category management modules"""
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from database import query_all, query_one, execute
from dialogs import MenuItemDialog


class MenuManager:
    """Menu items CRUD manager"""
    
    @staticmethod
    def open(parent, on_refresh_menu=None, on_refresh_categories=None):
        win = Toplevel(parent)
        win.title("Quản lý món")
        win.geometry("700x500")
        win.transient(parent)
        
        top = ttk.Frame(win, padding=8)
        top.pack(fill=X)
        ttk.Label(top, text="Danh mục:").pack(side=LEFT)
        cmb = ttk.Combobox(top, state="readonly")
        cmb.pack(side=LEFT, padx=6)
        ttk.Label(top, text="Tìm:").pack(side=LEFT)
        ent = ttk.Entry(top, width=30)
        ent.pack(side=LEFT, padx=6)

        def refresh():
            if on_refresh_categories:
                on_refresh_categories()
            categories = query_all("SELECT id, name FROM categories ORDER BY name")
            cmb["values"] = ["(Tất cả)"] + [c[1] for c in categories]
            if not cmb.get():
                cmb.current(0)

            search = ent.get().strip().lower()
            cat = cmb.get()
            q = """SELECT mi.id, mi.name, c.name, mi.price, mi.is_available, IFNULL(mi.description,'')
                   FROM menu_items mi LEFT JOIN categories c ON c.id = mi.category_id
                   WHERE 1=1"""
            params = []
            if cat and cat != "(Tất cả)":
                q += " AND c.name=%s"
                params.append(cat)
            if search:
                q += " AND (LOWER(mi.name) LIKE %s OR LOWER(IFNULL(mi.description,'')) LIKE %s)"
                params += [f"%{search}%", f"%{search}%"]
            q += " ORDER BY mi.name"
            rows = query_all(q, tuple(params))
            tree.delete(*tree.get_children())
            for _id, name, cat_name, price, avail, desc in rows:
                tree.insert("", END, iid=str(_id), values=(name, cat_name, price, "Đang bán" if avail else "Hết món", desc))

        cmb.bind("<<ComboboxSelected>>", lambda e: refresh())
        ent.bind("<KeyRelease>", lambda e: refresh())

        cols = ("name", "cat", "price", "avail", "desc")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for ccol, t in zip(cols, ("Tên", "Danh mục", "Giá", "Trạng thái", "Mô tả")):
            tree.heading(ccol, text=t)
        tree.column("name", width=180)
        tree.column("cat", width=120)
        tree.column("price", width=80, anchor="e")
        tree.column("avail", width=80, anchor="center")
        tree.column("desc", width=200)
        tree.pack(fill=BOTH, expand=True, padx=8, pady=4)

        def menu_add():
            cats = query_all("SELECT id, name FROM categories ORDER BY name")
            dlg = MenuItemDialog(win, cats)
            win.wait_window(dlg)
            if not hasattr(dlg, "result"):
                return
            r = dlg.result
            row = query_one("SELECT id FROM categories WHERE name=%s", (r["category_name"],))
            cat_id = row[0] if row else None
            execute("""INSERT INTO menu_items(name, category_id, price, is_available, description)
                       VALUES(%s,%s,%s,%s,%s)""",
                    (r["name"], cat_id, r["price"], r["is_available"], r["description"]))
            refresh()
            if on_refresh_menu:
                on_refresh_menu()

        def menu_edit():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Chọn dòng", "Hãy chọn một món để sửa.")
                return
            iid = int(sel[0])
            row = query_one("SELECT id, name, category_id, price, is_available, IFNULL(description,'') FROM menu_items WHERE id=%s", (iid,))
            cats = query_all("SELECT id, name FROM categories ORDER BY name")
            item = {"id": row[0], "name": row[1], "category_id": row[2], "price": row[3], "is_available": row[4], "description": row[5]}
            dlg = MenuItemDialog(win, cats, item=item)
            win.wait_window(dlg)
            if not hasattr(dlg, "result"):
                return
            r = dlg.result
            cat_id = query_one("SELECT id FROM categories WHERE name=%s", (r["category_name"],))[0]
            execute("""UPDATE menu_items SET name=%s, category_id=%s, price=%s, is_available=%s, description=%s
                       WHERE id=%s""",
                    (r["name"], cat_id, r["price"], r["is_available"], r["description"], iid))
            refresh()
            if on_refresh_menu:
                on_refresh_menu()

        def menu_delete():
            sel = tree.selection()
            if not sel:
                return
            iid = int(sel[0])
            if messagebox.askyesno("Xác nhận", "Xóa món này?"):
                execute("DELETE FROM menu_items WHERE id=%s", (iid,))
                refresh()
                if on_refresh_menu:
                    on_refresh_menu()

        btns = ttk.Frame(win, padding=8)
        btns.pack(fill=X)
        ttk.Button(btns, text="Thêm món", command=menu_add).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Sửa món", command=menu_edit).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Xóa món", command=menu_delete).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Quản lý danh mục", command=lambda: CategoryManager.open(win, refresh)).pack(side=RIGHT, padx=4)
        refresh()


class CategoryManager:
    """Category CRUD manager"""
    
    @staticmethod
    def open(parent, on_refresh=None):
        win = Toplevel(parent)
        win.title("Danh mục")
        win.geometry("400x320")
        win.transient(parent)
        
        lst = Listbox(win)
        lst.pack(fill=BOTH, expand=True, padx=8, pady=8)

        def refresh():
            lst.delete(0, END)
            rows = query_all("SELECT id, name FROM categories ORDER BY id")
            for _id, name in rows:
                lst.insert(END, f"{_id}: {name}")

        def add_cat():
            name = simpledialog.askstring("Thêm danh mục", "Tên danh mục:", parent=win)
            if name:
                try:
                    execute("INSERT INTO categories(name) VALUES(%s)", (name.strip(),))
                    refresh()
                    if on_refresh:
                        on_refresh()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thêm được: {e}")

        def edit_cat():
            sel = lst.curselection()
            if not sel:
                return
            text = lst.get(sel[0])
            _id = int(text.split(":")[0])
            cur = query_one("SELECT name FROM categories WHERE id=%s", (_id,))[0]
            name = simpledialog.askstring("Sửa danh mục", "Tên danh mục:", initialvalue=cur, parent=win)
            if name:
                try:
                    execute("UPDATE categories SET name=%s WHERE id=%s", (name.strip(), _id))
                    refresh()
                    if on_refresh:
                        on_refresh()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không sửa được: {e}")

        def delete_cat():
            sel = lst.curselection()
            if not sel:
                return
            text = lst.get(sel[0])
            _id = int(text.split(":")[0])
            if messagebox.askyesno("Xác nhận", "Xóa danh mục này? (Món thuộc danh mục sẽ để trống)"):
                execute("UPDATE menu_items SET category_id=NULL WHERE category_id=%s", (_id,))
                execute("DELETE FROM categories WHERE id=%s", (_id,))
                refresh()
                if on_refresh:
                    on_refresh()

        frm_btn = ttk.Frame(win)
        frm_btn.pack(fill=X, pady=(0, 8), padx=8)
        ttk.Button(frm_btn, text="Thêm", command=add_cat).pack(side=LEFT, padx=4)
        ttk.Button(frm_btn, text="Sửa", command=edit_cat).pack(side=LEFT, padx=4)
        ttk.Button(frm_btn, text="Xóa", command=delete_cat).pack(side=LEFT, padx=4)
        refresh()
