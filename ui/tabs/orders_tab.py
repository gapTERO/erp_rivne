from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QHeaderView, QFrame, QLineEdit, QComboBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QMessageBox, QDoubleSpinBox,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from ui.styles import *
from ui.sortable_table import SortableTable
from ui.dialogs import confirm, info, warning

try:
    from database.db import db_cursor
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False


def make_badge(status):
    colors = STATUS_COLORS.get(status, {"bg": "#f1f5f9", "text": "#64748b"})
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(4, 0, 4, 0)
    l.setAlignment(Qt.AlignCenter)
    lbl = QLabel(status)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background:{colors['bg']}; color:{colors['text']};"
        f"border-radius:10px; padding:3px 10px; font-size:11px; font-weight:600;"
    )
    l.addWidget(lbl)
    return w


class OrderDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id  = order_id
        self.customers = []
        self.products  = []
        self.setWindowTitle("Редагувати замовлення" if order_id else "Нове замовлення")
        self.setFixedSize(500, 540)
        self.setStyleSheet(MAIN_STYLE + f"QDialog {{ background:{WHITE}; }}")
        self._build()
        if order_id:
            self._load_order()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{TEXT_PRIMARY};")
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.cmb_customer = QComboBox()
        self._load_customers()
        form.addRow("Клієнт *:", self.cmb_customer)

        self.cmb_product = QComboBox()
        self._load_products()
        self.cmb_product.currentIndexChanged.connect(self._recalc)
        form.addRow("Продукт *:", self.cmb_product)

        self.spin_qty = QDoubleSpinBox()
        self.spin_qty.setRange(1, 999999)
        self.spin_qty.setSuffix(" кг")
        self.spin_qty.setValue(1000)
        self.spin_qty.setDecimals(0)
        self.spin_qty.valueChanged.connect(self._recalc)
        form.addRow("Кількість *:", self.spin_qty)

        self.lbl_price = QLabel("—")
        self.lbl_price.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px;")
        form.addRow("Ціна за кг:", self.lbl_price)

        self.lbl_total = QLabel("—")
        self.lbl_total.setStyleSheet(f"color:{ACCENT}; font-size:15px; font-weight:700;")
        form.addRow("Сума:", self.lbl_total)

        self.date_delivery = QDateEdit()
        self.date_delivery.setDate(QDate.currentDate().addDays(3))
        self.date_delivery.setCalendarPopup(True)
        form.addRow("Дата доставки:", self.date_delivery)

        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Нове", "В роботі", "Виконано", "Скасовано"])
        form.addRow("Статус:", self.cmb_status)

        self.txt_responsible = QLineEdit()
        self.txt_responsible.setPlaceholderText("ПІБ відповідального")
        form.addRow("Відповідальний:", self.txt_responsible)

        self.txt_comment = QTextEdit()
        self.txt_comment.setFixedHeight(60)
        self.txt_comment.setPlaceholderText("Коментар...")
        form.addRow("Коментар:", self.txt_comment)

        root.addLayout(form)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setObjectName("secondary")
        btn_cancel.setFixedHeight(36)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Зберегти")
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

        self._recalc()

    def _load_customers(self):
        if DB_AVAILABLE:
            try:
                with db_cursor() as cur:
                    cur.execute("SELECT id, name FROM customers ORDER BY name")
                    self.customers = list(cur.fetchall())
            except Exception:
                pass
        if not self.customers:
            self.customers = [
                {"id":1,"name":"АТБ-Маркет"}, {"id":2,"name":"Сільпо"},
                {"id":3,"name":"Новус"}, {"id":4,"name":"ФОП Ковальчук В.М."},
                {"id":5,"name":"Хліб Рівненський"},
            ]
        for c in self.customers:
            self.cmb_customer.addItem(c["name"], c["id"])

    def _load_products(self):
        if DB_AVAILABLE:
            try:
                with db_cursor() as cur:
                    cur.execute("SELECT id, name, price_per_kg FROM products ORDER BY name")
                    self.products = list(cur.fetchall())
            except Exception:
                pass
        if not self.products:
            self.products = [
                {"id":1,"name":"Борошно вищий сорт","price_per_kg":18.50},
                {"id":2,"name":"Борошно 1-й сорт",  "price_per_kg":16.00},
                {"id":3,"name":"Борошно 2-й сорт",  "price_per_kg":13.50},
                {"id":4,"name":"Висівки пшеничні",   "price_per_kg":6.00},
            ]
        for p in self.products:
            self.cmb_product.addItem(p["name"], p["id"])

    def _recalc(self):
        idx = self.cmb_product.currentIndex()
        if 0 <= idx < len(self.products):
            price = float(self.products[idx]["price_per_kg"])
            qty   = self.spin_qty.value()
            self.lbl_price.setText(f"{price:.2f} грн / кг")
            self.lbl_total.setText(f"{price*qty:,.0f} грн".replace(",", " "))

    def _load_order(self):
        if not DB_AVAILABLE:
            return
        try:
            with db_cursor() as cur:
                cur.execute("SELECT * FROM orders WHERE id=%s", (self.order_id,))
                o = cur.fetchone()
            if not o:
                return
            for i in range(self.cmb_customer.count()):
                if self.cmb_customer.itemData(i) == o["customer_id"]:
                    self.cmb_customer.setCurrentIndex(i); break
            for i in range(self.cmb_product.count()):
                if self.cmb_product.itemData(i) == o["product_id"]:
                    self.cmb_product.setCurrentIndex(i); break
            self.spin_qty.setValue(float(o["quantity_kg"]))
            idx = self.cmb_status.findText(o["status"])
            if idx >= 0: self.cmb_status.setCurrentIndex(idx)
            self.txt_responsible.setText(o.get("responsible") or "")
            self.txt_comment.setPlainText(o.get("comment") or "")
            if o.get("delivery_date"):
                d = o["delivery_date"]
                self.date_delivery.setDate(QDate(d.year, d.month, d.day))
        except Exception as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def _save(self):
        customer_id = self.cmb_customer.currentData()
        product_id  = self.cmb_product.currentData()
        qty         = self.spin_qty.value()
        status      = self.cmb_status.currentText()
        responsible = self.txt_responsible.text().strip()
        comment     = self.txt_comment.toPlainText().strip()
        d           = self.date_delivery.date()
        delivery    = f"{d.year()}-{d.month():02d}-{d.day():02d}"
        idx         = self.cmb_product.currentIndex()
        price       = float(self.products[idx]["price_per_kg"]) if 0<=idx<len(self.products) else 0
        total       = price * qty

        if not customer_id or not product_id:
            QMessageBox.warning(self, "Помилка", "Оберіть клієнта та продукт!")
            return

        if DB_AVAILABLE:
            try:
                with db_cursor() as cur:
                    if self.order_id:
                        cur.execute("""
                            UPDATE orders SET customer_id=%s,product_id=%s,quantity_kg=%s,
                            total_price=%s,status=%s,responsible=%s,comment=%s,delivery_date=%s
                            WHERE id=%s
                        """, (customer_id,product_id,qty,total,status,responsible,comment,delivery,self.order_id))
                    else:
                        cur.execute("SELECT COALESCE(MAX(id),1000)+1 AS n FROM orders")
                        n = cur.fetchone()["n"]
                        cur.execute("""
                            INSERT INTO orders(order_number,customer_id,product_id,quantity_kg,
                            total_price,status,responsible,comment,delivery_date)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (f"#{n:04d}",customer_id,product_id,qty,total,status,responsible,comment,delivery))
                info(self, "Успіх", "Замовлення збережено успішно!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Помилка БД", str(e))
        else:
            info(self, "Демо-режим", "База даних не підключена.")
            self.accept()


class OrdersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_data    = []
        self.sorted_data = []
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)

        # ── Фільтри ──────────────────────────
        ff = QFrame()
        ff.setStyleSheet(f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;")
        fl = QHBoxLayout(ff)
        fl.setContentsMargins(14,10,14,10)
        fl.setSpacing(10)

        lbl = QLabel("Пошук:")
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px; border:none;")
        fl.addWidget(lbl)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Клієнт або № замовлення")
        self.search_box.setFixedWidth(260)
        self.search_box.textChanged.connect(self._apply_filter)
        fl.addWidget(self.search_box)

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedWidth(160)
        self.cmb_status_filter.addItems(["Всі статуси","Нове","В роботі","Виконано","Скасовано"])
        self.cmb_status_filter.currentIndexChanged.connect(self._apply_filter)
        fl.addWidget(self.cmb_status_filter)

        fl.addStretch()
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px; border:none;")
        fl.addWidget(self.lbl_count)
        root.addWidget(ff)

        # ── Кнопки дій ───────────────────────
        bf = QFrame()
        bf.setStyleSheet("background:transparent;")
        bl = QHBoxLayout(bf)
        bl.setContentsMargins(0,0,0,0)
        bl.setSpacing(8)

        bl.addWidget(self._btn("➕  Нове замовлення", self._new_order,    primary=True))
        bl.addWidget(self._btn("✏️  Редагувати",      self._edit_order))
        bl.addWidget(self._btn("❌  Скасувати",       self._cancel_order, danger=True))
        bl.addWidget(self._btn("🗑  Видалити",         self._delete_order, danger=True))
        bl.addStretch()
        bl.addWidget(self._btn("🔄  Оновити",         self.refresh))
        root.addWidget(bf)

        # ── Таблиця з клікабельними заголовками ─
        self.table = SortableTable()
        self.table.set_headers([
            "№","Дата","Клієнт","Продукт",
            "Кількість (кг)","Сума (грн)","Статус","Відповідальний"
        ])
        # Callback при кліку на заголовок — тільки пересортовуємо дані
        self.table.set_sort_callback(self._on_sort)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color:#fafafa; }")
        root.addWidget(self.table)

    def _btn(self, text, slot, primary=False, danger=False):
        b = QPushButton(text)
        b.setFixedHeight(36)
        if danger:
            b.setStyleSheet(f"""
                QPushButton {{background:{DANGER};color:white;border:none;
                border-radius:6px;font-size:13px;font-weight:500;padding:0 14px;}}
                QPushButton:hover{{background:#dc2626;}}""")
        elif primary:
            b.setStyleSheet(f"""
                QPushButton {{background:{ACCENT};color:white;border:none;
                border-radius:6px;font-size:13px;font-weight:500;padding:0 14px;}}
                QPushButton:hover{{background:{ACCENT_HOVER};}}""")
        else:
            b.setStyleSheet(f"""
                QPushButton {{background:{WHITE};color:{TEXT_PRIMARY};
                border:1px solid {BORDER};border-radius:6px;
                font-size:13px;font-weight:500;padding:0 14px;}}
                QPushButton:hover{{background:{BG_LIGHT};}}""")
        b.clicked.connect(slot)
        return b

    # ── Сортування через callback ─────────────
    def _on_sort(self, col: int, asc: bool):
        """Викликається з SortableTable при кліку на заголовок."""
        # Ключ сортування
        col_keys = {0:"order_number",1:"date",2:"customer",3:"product",
                    4:"quantity_kg",5:"total_price",6:"status",7:"responsible"}
        key_name = col_keys.get(col)
        if not key_name:
            return

        def sort_key(row):
            val = row.get(key_name, "") or ""
            try:
                return (0, float(str(val).replace(" ","")))
            except (ValueError, TypeError):
                return (1, str(val).lower())

        self.sorted_data = sorted(self.sorted_data, key=sort_key, reverse=not asc)
        self._fill_table(self.sorted_data)

    # ── Дані ─────────────────────────────────
    def refresh(self):
        self.all_data = []
        if DB_AVAILABLE:
            try:
                with db_cursor() as cur:
                    cur.execute("""
                        SELECT o.id, o.order_number,
                               o.created_at::date AS date,
                               c.name AS customer,
                               p.name AS product,
                               o.quantity_kg, o.total_price,
                               o.status, o.responsible
                        FROM orders o
                        JOIN customers c ON o.customer_id=c.id
                        JOIN products  p ON o.product_id=p.id
                        ORDER BY o.created_at DESC
                    """)
                    self.all_data = [dict(r) for r in cur.fetchall()]
            except Exception:
                pass

        if not self.all_data:
            self.all_data = [
                {"id":1,"order_number":"#1042","date":"2026-04-15","customer":"АТБ-Маркет",
                 "product":"Борошно вищий сорт","quantity_kg":5000,"total_price":92500,
                 "status":"Виконано","responsible":"Мельник І.П."},
                {"id":2,"order_number":"#1043","date":"2026-04-15","customer":"Новус",
                 "product":"Борошно 1-й сорт","quantity_kg":2000,"total_price":32000,
                 "status":"В роботі","responsible":"Ковальчук О.С."},
                {"id":3,"order_number":"#1044","date":"2026-04-14","customer":"ФОП Ковальчук",
                 "product":"Висівки пшеничні","quantity_kg":800,"total_price":4800,
                 "status":"Нове","responsible":""},
                {"id":4,"order_number":"#1045","date":"2026-04-14","customer":"Сільпо",
                 "product":"Борошно вищий сорт","quantity_kg":10000,"total_price":185000,
                 "status":"В роботі","responsible":"Мельник І.П."},
                {"id":5,"order_number":"#1041","date":"2026-04-13","customer":"Хліб Рівненський",
                 "product":"Борошно 2-й сорт","quantity_kg":3000,"total_price":40500,
                 "status":"Виконано","responsible":"Ковальчук О.С."},
            ]
        self._apply_filter()

    def _apply_filter(self):
        text   = self.search_box.text().lower()
        status = self.cmb_status_filter.currentText()
        self.sorted_data = [
            r for r in self.all_data
            if (not text or text in str(r["customer"]).lower()
                         or text in str(r["order_number"]).lower())
            and (status == "Всі статуси" or r["status"] == status)
        ]
        self._fill_table(self.sorted_data)

    def _fill_table(self, data):
        """Заповнює таблицю БЕЗ очищення через setRowCount(0)."""
        # Встановлюємо потрібну кількість рядків
        self.table.setRowCount(len(data))

        for r, row in enumerate(data):
            num_item = QTableWidgetItem(str(row["order_number"]))
            num_item.setData(Qt.UserRole, row.get("id"))
            self.table.setItem(r, 0, num_item)
            self.table.setItem(r, 1, QTableWidgetItem(str(row.get("date",""))))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["customer"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(row["product"])))
            qty   = int(float(row["quantity_kg"]))
            total = float(row.get("total_price") or 0)
            self.table.setItem(r, 4, QTableWidgetItem(f"{qty:,}".replace(",", " ")))
            self.table.setItem(r, 5, QTableWidgetItem(f"{total:,.0f}".replace(",", " ")))
            self.table.setCellWidget(r, 6, make_badge(row["status"]))
            self.table.setItem(r, 7, QTableWidgetItem(str(row.get("responsible") or "")))
            self.table.setRowHeight(r, 38)

        self.lbl_count.setText(f"Показано: {len(data)} замовлень")

    # ── Вибір рядка ──────────────────────────
    def _selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount():
            return None, None
        item = self.table.item(row, 0)
        if not item:
            return None, None
        return row, item.data(Qt.UserRole)

    # ── Дії ──────────────────────────────────
    def _new_order(self):
        if OrderDialog(self).exec_() == QDialog.Accepted:
            self.refresh()

    def _edit_order(self):
        row, oid = self._selected()
        if row is None:
            info(self, "Увага", "Оберіть замовлення зі списку.")
            return
        if OrderDialog(self, order_id=oid).exec_() == QDialog.Accepted:
            self.refresh()

    def _cancel_order(self):
        row, oid = self._selected()
        if row is None:
            info(self, "Увага", "Оберіть замовлення зі списку.")
            return
        num = self.table.item(row, 0).text()
        for d in self.sorted_data:
            if str(d["order_number"]) == num and d["status"] == "Виконано":
                warning(self, "Помилка", "Не можна скасувати виконане замовлення.")
                return
        if not confirm(self, "Скасувати замовлення",
                       f"Скасувати замовлення {num}?",
                       confirm_text="Так, скасувати"):
            return
        if DB_AVAILABLE and oid:
            try:
                with db_cursor() as cur:
                    cur.execute("UPDATE orders SET status='Скасовано' WHERE id=%s", (oid,))
            except Exception as e:
                QMessageBox.critical(self, "Помилка БД", str(e))
                return
        else:
            for d in self.all_data:
                if str(d["order_number"]) == num:
                    d["status"] = "Скасовано"
        self.refresh()

    def _delete_order(self):
        row, oid = self._selected()
        if row is None:
            info(self, "Увага", "Оберіть замовлення зі списку.")
            return
        num = self.table.item(row, 0).text()
        if not confirm(self, "Видалити замовлення",
                       f"Видалити замовлення {num}?",
                       confirm_text="Так, видалити",
                       danger=True,
                       detail="Цю дію не можна скасувати."):
            return
        if DB_AVAILABLE and oid:
            try:
                with db_cursor() as cur:
                    cur.execute("DELETE FROM orders WHERE id=%s", (oid,))
            except Exception as e:
                QMessageBox.critical(self, "Помилка БД", str(e))
                return
        else:
            self.all_data = [d for d in self.all_data if str(d["order_number"]) != num]
        self.refresh()
