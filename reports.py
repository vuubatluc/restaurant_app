"""Report generation modules"""
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from database import get_conn, query_all, query_one, money


class ReportMonthly:
    """Monthly revenue report window"""
    
    @staticmethod
    def open(parent):
        win = Toplevel(parent)
        win.title("Báo cáo doanh thu theo tháng")
        win.geometry("720x440")
        win.transient(parent)
        
        frm = ttk.Frame(win, padding=8)
        frm.pack(fill=X)
        ttk.Label(frm, text="Năm:").pack(side=LEFT)
        ent_year = ttk.Entry(frm, width=6)
        ent_year.pack(side=LEFT, padx=6)
        ttk.Label(frm, text="Tháng (1-12):").pack(side=LEFT)
        ent_month = ttk.Entry(frm, width=4)
        ent_month.pack(side=LEFT, padx=6)

        def load():
            try:
                y = int(ent_year.get())
                m = int(ent_month.get())
                if not (1 <= m <= 12):
                    raise ValueError()
            except:
                messagebox.showerror("Lỗi", "Năm/Tháng không hợp lệ.")
                return
            
            conn = get_conn()
            cur = conn.cursor()
            tree.delete(*tree.get_children())
            total_sub = total_tax = total_srv = total_sum = 0
            
            try:
                try:
                    cur.callproc("sp_revenue_by_month", [y, m])
                    results = list(cur.stored_results())
                    if not results:
                        raise mysql.connector.Error(msg="No results from sp_revenue_by_month")
                    for result in results:
                        rows = result.fetchall()
                        for ngay, so_don, sub, tax, srv, ttl in rows:
                            sub = sub or 0
                            tax = tax or 0
                            srv = srv or 0
                            ttl = ttl or 0
                            total_sub += float(sub)
                            total_tax += float(tax)
                            total_srv += float(srv)
                            total_sum += float(ttl)
                            tree.insert("", END, values=(str(ngay), so_don or 0, money(sub), money(tax), money(srv), money(ttl)))
                except mysql.connector.Error as e:
                    msg = str(e).lower()
                    if "doesn't exist" in msg or "does not exist" in msg or "no results" in msg:
                        rows = query_all(
                            """
                            SELECT DATE(created_at) AS ngay,
                                   COUNT(*) AS so_don,
                                   SUM(subtotal) AS sub,
                                   SUM(tax) AS tax,
                                   SUM(service) AS srv,
                                   SUM(total) AS ttl
                            FROM orders
                            WHERE status='PAID' AND YEAR(created_at)=%s AND MONTH(created_at)=%s
                            GROUP BY DATE(created_at)
                            ORDER BY DATE(created_at)
                            """, (y, m))
                        for ngay, so_don, sub, tax, srv, ttl in rows:
                            sub = sub or 0
                            tax = tax or 0
                            srv = srv or 0
                            ttl = ttl or 0
                            total_sub += float(sub)
                            total_tax += float(tax)
                            total_srv += float(srv)
                            total_sum += float(ttl)
                            tree.insert("", END, values=(str(ngay), so_don or 0, money(sub), money(tax), money(srv), money(ttl)))
                    else:
                        messagebox.showerror("Lỗi báo cáo", f"Không thể tải báo cáo tháng:\n{e}")
                        return
                
                # Totals row
                tree.insert("", END, values=("TỔNG", "", money(total_sub), money(total_tax), money(total_srv), money(total_sum)))
            finally:
                cur.close()
                conn.close()

        ttk.Button(frm, text="Xem báo cáo", command=load).pack(side=LEFT, padx=8)
        
        cols = ("ngay", "so_don", "subtotal", "tax", "service", "total")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=14)
        headers = ["Ngày", "Số đơn", "Tạm tính", "Thuế", "Service", "Tổng cộng"]
        widths = [110, 70, 110, 100, 100, 120]
        for ccol, h, w in zip(cols, headers, widths):
            tree.heading(ccol, text=h)
            tree.column(ccol, width=w, anchor="e" if ccol != "ngay" else "w")
        tree.pack(fill=BOTH, expand=True, padx=8, pady=6)
        
        today = datetime.now()
        ent_year.insert(0, str(today.year))
        ent_month.insert(0, str(today.month))


class ReportDaily:
    """Daily revenue report window"""
    
    @staticmethod
    def open(parent, default_today=True):
        win = Toplevel(parent)
        win.title("Doanh thu trong ngày")
        win.geometry("800x520")
        win.transient(parent)
        
        frm = ttk.Frame(win, padding=8)
        frm.pack(fill=X)

        ttk.Label(frm, text="Ngày (YYYY-MM-DD):").pack(side=LEFT)
        ent_date = ttk.Entry(frm, width=12)
        ent_date.pack(side=LEFT, padx=6)

        def load():
            try:
                p_date = ent_date.get().strip()
                datetime.strptime(p_date, "%Y-%m-%d")
            except Exception:
                messagebox.showerror("Lỗi", "Ngày không hợp lệ. Định dạng YYYY-MM-DD.")
                return

            conn = get_conn()
            cur = conn.cursor()
            tree_detail.delete(*tree_detail.get_children())
            var_ngay.set("")
            var_so_don.set("0")
            var_sub.set("0")
            var_tax.set("0")
            var_srv.set("0")
            var_ttl.set("0")
            
            try:
                try:
                    cur.callproc("sp_revenue_by_date", [p_date])
                    result_sets = list(cur.stored_results())
                    if len(result_sets) >= 1:
                        totals = result_sets[0].fetchone()
                        if totals:
                            ngay, so_don, subtotal, tax, service, total = totals
                            var_ngay.set(str(ngay))
                            var_so_don.set(str(so_don or 0))
                            var_sub.set(money(subtotal or 0))
                            var_tax.set(money(tax or 0))
                            var_srv.set(money(service or 0))
                            var_ttl.set(money(total or 0))
                    if len(result_sets) >= 2:
                        for row in result_sets[1].fetchall():
                            order_id, created_at, table_id, sub, tax, srv, ttl = row
                            tree_detail.insert("", END, values=(order_id, str(created_at), table_id, money(sub), money(tax), money(srv), money(ttl)))
                except mysql.connector.Error as e:
                    msg = str(e).lower()
                    if "doesn't exist" in msg or "does not exist" in msg:
                        # Fallback totals
                        tot = query_one(
                            """
                            SELECT DATE(created_at) AS ngay,
                                   COUNT(*) AS so_don,
                                   SUM(subtotal) AS subtotal,
                                   SUM(tax) AS tax,
                                   SUM(service) AS service,
                                   SUM(total) AS total
                            FROM orders
                            WHERE DATE(created_at)=%s AND status='PAID'
                            """, (p_date,))
                        if tot and any(tot):
                            ngay, so_don, subtotal, tax, service, total = tot
                            var_ngay.set(str(ngay))
                            var_so_don.set(str(so_don or 0))
                            var_sub.set(money(subtotal or 0))
                            var_tax.set(money(tax or 0))
                            var_srv.set(money(service or 0))
                            var_ttl.set(money(total or 0))
                        # Fallback details
                        rows = query_all(
                            """
                            SELECT id AS order_id, created_at, table_id, subtotal, tax, service, total
                            FROM orders
                            WHERE DATE(created_at)=%s AND status='PAID'
                            ORDER BY created_at
                            """, (p_date,))
                        for order_id, created_at, table_id, sub, tax, srv, ttl in rows:
                            tree_detail.insert("", END, values=(order_id, str(created_at), table_id, money(sub or 0), money(tax or 0), money(srv or 0), money(ttl or 0)))
                    else:
                        messagebox.showerror("Lỗi báo cáo", f"Không thể tải báo cáo ngày:\n{e}")
                        return
            finally:
                cur.close()
                conn.close()

        ttk.Button(frm, text="Tính doanh thu", command=load).pack(side=LEFT, padx=8)
        if default_today:
            ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        totals = ttk.LabelFrame(win, text="Tổng kết ngày", padding=8)
        totals.pack(fill=X, padx=8, pady=(6, 2))
        var_ngay = StringVar()
        var_so_don = StringVar()
        var_sub = StringVar()
        var_tax = StringVar()
        var_srv = StringVar()
        var_ttl = StringVar()
        grid = ttk.Frame(totals)
        grid.pack(fill=X)
        labels = [("Ngày:", var_ngay), ("Số đơn:", var_so_don), ("Tạm tính:", var_sub), ("Thuế:", var_tax),
                  ("Service:", var_srv), ("TỔNG CỘNG:", var_ttl)]
        for i, (txt, var) in enumerate(labels):
            ttk.Label(grid, text=txt).grid(row=i // 4, column=(i % 4) * 2, sticky="w", padx=4, pady=2)
            ttk.Label(grid, textvariable=var).grid(row=i // 4, column=(i % 4) * 2 + 1, sticky="w", padx=4, pady=2)

        cols = ("order_id", "created_at", "table_id", "subtotal", "tax", "service", "total")
        tree_detail = ttk.Treeview(win, columns=cols, show="headings", height=14)
        headers = ["Mã đơn", "Thời gian", "Bàn", "Tạm tính", "Thuế", "Service", "Tổng cộng"]
        widths = [80, 150, 60, 100, 90, 90, 110]
        for c, h, w in zip(cols, headers, widths):
            tree_detail.heading(c, text=h)
            tree_detail.column(c, width=w, anchor="e" if c not in ("order_id", "created_at", "table_id") else "w")
        tree_detail.pack(fill=BOTH, expand=True, padx=8, pady=6)
