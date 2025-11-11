
import os
import sys
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django  
django.setup()  

from db.models import Product  

def populate_if_empty():
    if Product.objects.count() == 0:
        demo = [
            ("036000291452", "Kleenex Tissues (120ct)", Decimal("3.49")),
            ("078742041320", "Whole Milk 3.25% 2L",  Decimal("4.59")),
            ("012345678905", "Organic Bananas (1lb)",  Decimal("1.29")),
            ("049000050103", "Coca-Cola 500ml",       Decimal("1.99")),
        ]
        for upc, name, price in demo:
            Product.objects.update_or_create(
                upc=upc, defaults={"name": name, "price": price}
            )

import tkinter as tk 
from tkinter import ttk, messagebox  

class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cash Register (Django ORM)")
        self.geometry("680x520")
        self.minsize(620, 480)

        self.lines = []  
        self.total = Decimal("0.00")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Scan UPC", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))

        top = ttk.Frame(self)
        top.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        top.columnconfigure(0, weight=1)

        self.upc_var = tk.StringVar()
        self.entry = ttk.Entry(top, textvariable=self.upc_var, font=("Consolas", 14))
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.focus_set()

        scan_btn = ttk.Button(top, text="Scan (Enter)", command=self.scan_current)
        scan_btn.grid(row=0, column=1, padx=(8, 0))

        clear_btn = ttk.Button(top, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=2, padx=(8, 0))

        self.feedback = ttk.Label(self, text="", foreground="#0b7a0b")
        self.feedback.grid(row=2, column=0, sticky="ew", padx=16)

        table_frame = ttk.Frame(self)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(6, 6))
        self.rowconfigure(3, weight=1)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("upc", "name", "price"),
            show="headings",
            height=10,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("upc", text="UPC")
        self.tree.heading("name", text="Product")
        self.tree.heading("price", text="Price")

        self.tree.column("upc", width=180, anchor="w")
        self.tree.column("name", width=360, anchor="w")
        self.tree.column("price", width=80, anchor="e")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscroll=yscroll.set)

        bottom = ttk.Frame(self)
        bottom.grid(row=4, column=0, sticky="ew", padx=16, pady=(8, 14))
        bottom.columnconfigure(0, weight=1)

        self.total_label = ttk.Label(
            bottom, text="Total: $0.00", font=("Segoe UI", 14, "bold")
        )
        self.total_label.grid(row=0, column=1, sticky="e")

        remove_btn = ttk.Button(bottom, text="Remove Selected", command=self.remove_selected)
        remove_btn.grid(row=0, column=0, sticky="w")

        self.entry.bind("<Return>", lambda e: self.scan_current())
        self.bind("<Control-l>", lambda e: self.clear_all()) 

    def scan_current(self):
        upc = self.upc_var.get().strip().replace(" ", "")
        if not upc:
            self.flash_feedback("Please enter a UPC.", bad=True)
            self.bell()
            return

        product = Product.objects.filter(upc=upc).first()
        self.upc_var.set("")  
        self.entry.focus_set()

        if not product:
            self.flash_feedback(f"Not found: {upc}", bad=True)
            self.bell()
            return

        self.lines.append((product.upc, product.name, product.price))
        self.tree.insert("", "end", values=(product.upc, product.name, f"{product.price:.2f}"))
        self.total += Decimal(product.price)
        self.update_total()
        self.flash_feedback(f"Added: {product.name} — ${product.price:.2f}")

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item_id in sel:
            vals = self.tree.item(item_id, "values")

            try:
                price = Decimal(str(vals[2]))
            except Exception:
                price = Decimal("0.00")
            self.total -= price
            self.tree.delete(item_id)
        self.update_total()
        self.flash_feedback("Removed selected line(s).")

    def clear_all(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.lines.clear()
        self.total = Decimal("0.00")
        self.update_total()
        self.flash_feedback("Cleared all.")

    def update_total(self):
        self.total_label.config(text=f"Total: ${self.total:.2f}")

    def flash_feedback(self, text, bad=False):
        self.feedback.config(text=text, foreground=("#b00020" if bad else "#0b7a0b"))
        self.after(3000, lambda: self.feedback.config(text=""))

def main():
    populate_if_empty()
    app = POSApp()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        message = (
            f"{e}\n\n"
            "If this is a settings/migration issue, run:\n"
            "  python manage.py makemigrations db\n"
            "  python manage.py migrate\n"
        )
        print(message, file=sys.stderr)
        raise
